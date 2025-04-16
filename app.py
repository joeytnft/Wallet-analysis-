from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime

app = Flask(__name__)

def fetch_token_transfers(wallet_address, api_key):
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions?api-key={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch transactions")
    return response.json()

def label_by_hold_time(hours_held, avg_hours):
    if hours_held < 0.25 * avg_hours:
        return "Ultra Jeet"
    elif hours_held < 0.75 * avg_hours:
        return "Trench Jeet"
    elif hours_held <= 1.25 * avg_hours:
        return "Battle Buddy"
    elif hours_held <= 2.0 * avg_hours:
        return "Steady Soldier"
    else:
        return "Diamond Fren"

def label_sprite(label):
    slug = label.lower().replace(" ", "_")
    return f"/static/sprites/{slug}.png"

def analyze_wallet(wallet_address, api_key):
    txs = fetch_token_transfers(wallet_address, api_key)
    held_tokens = {}
    hold_times = []

    for tx in txs:
        if "tokenTransfers" not in tx:
            continue
        timestamp = datetime.fromisoformat(tx["timestamp"])
        for transfer in tx["tokenTransfers"]:
            token = transfer["mint"]
            if transfer["fromUserAccount"] == wallet_address and token in held_tokens:
                duration = (timestamp - held_tokens[token]).total_seconds() / 3600
                hold_times.append((token, duration))
                del held_tokens[token]
            elif transfer["toUserAccount"] == wallet_address:
                held_tokens[token] = timestamp

    recent = hold_times[-100:] if len(hold_times) > 100 else hold_times
    if not recent:
        return []

    avg_hours = sum(ht[1] for ht in recent) / len(recent)

    results = []
    for token, hours_held in recent:
        label = label_by_hold_time(hours_held, avg_hours)
        results.append({
            "token": token,
            "held_for_hours": round(hours_held, 2),
            "label": label,
            "sprite": label_sprite(label)
        })

    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    wallet = data.get("wallet")
    api_key = data.get("api_key")

    if not wallet or not api_key:
        return jsonify({"error": "Missing wallet or api_key"}), 400

    try:
        result = analyze_wallet(wallet, api_key)
        return jsonify({
            "wallet": wallet,
            "tokens_analyzed": len(result),
            "analysis": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)