from flask import Flask, request, jsonify, render_template
import os
import requests

app = Flask(__name__)

# Example endpoint for wallet analysis
@app.route("/analyze", methods=["POST"])
def analyze_wallet():
    wallet_address = request.json.get("wallet_address")
    if not wallet_address:
        return jsonify({"error": "Wallet address is required"}), 400

    api_key = '54073ad4-6694-4096-84aa-318992a9bc4a'  # Your Helius API Key
    url = f"https://api.helius.xyz/v1/wallets/{wallet_address}/transactions"
    
    headers = {'Authorization': f'Bearer {api_key}'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from Helius API"}), 500

    return jsonify(response.json())

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
