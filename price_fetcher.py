import requests

# Mapping of common crypto symbols to CoinGecko IDs
CRYPTO_MAPPING = {
    "ETH": "ethereum",
    "BTC": "bitcoin",
    "BNB": "binancecoin",
    "SOL": "solana",
    "ADA": "cardano",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "USDT": "tether",
    "USDC": "usd-coin"
}

def get_price(asset):
    # Convert symbol to CoinGecko ID
    coingecko_id = CRYPTO_MAPPING.get(asset.upper(), asset.lower())
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coingecko_id,
        "vs_currencies": "hkd"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()[coingecko_id]["hkd"]

