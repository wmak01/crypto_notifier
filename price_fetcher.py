import requests

def get_price(asset):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": asset.lower(),
        "vs_currencies": "hkd"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()[asset.lower()]["hkd"]
