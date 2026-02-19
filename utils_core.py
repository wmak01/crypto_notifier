import json
import os
from datetime import datetime

PENDING_FILE = "pending.json"
MAX_PRICE_HISTORY = 100  # Keep last 100 prices
TIME_GAP_THRESHOLD = 300  # 5 minutes in seconds

# Will be set dynamically per instance
PRICE_HISTORY_FILE = "prices_history.json"

def set_price_history_file(base_name):
    """Set the price history file based on state file (e.g., state_btc.txt -> prices_history_btc.json)"""
    global PRICE_HISTORY_FILE
    PRICE_HISTORY_FILE = f"prices_history_{base_name}.json" if base_name != "state" else "prices_history.json"

def load_pending():
    if not os.path.exists(PENDING_FILE):
        return {"pending": False}
    with open(PENDING_FILE) as f:
        return json.load(f)

def save_pending(data):
    with open(PENDING_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_price_history():
    """Load price history from file. Returns list of {price, timestamp} dicts."""
    if not os.path.exists(PRICE_HISTORY_FILE):
        return []
    try:
        with open(PRICE_HISTORY_FILE) as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []

def check_time_gap():
    """Check if there's a significant time gap since last price was recorded.
    Returns True if gap detected (more than TIME_GAP_THRESHOLD seconds).
    This indicates a restart after a long break - history should be cleared."""
    prices = load_price_history()
    if not prices:
        return False
    
    last_price = prices[-1]
    last_timestamp_str = last_price["timestamp"]
    last_timestamp = datetime.fromisoformat(last_timestamp_str)
    current_time = datetime.now()
    time_diff = (current_time - last_timestamp).total_seconds()
    
    return time_diff > TIME_GAP_THRESHOLD

def clear_price_history():
    """Clear all price history - used when time gap detected."""
    if os.path.exists(PRICE_HISTORY_FILE):
        os.remove(PRICE_HISTORY_FILE)

def save_price_history(prices):
    """Save price history to file. Keep only the last MAX_PRICE_HISTORY entries."""
    prices = prices[-MAX_PRICE_HISTORY:]  # Keep last 100
    with open(PRICE_HISTORY_FILE, "w") as f:
        json.dump(prices, f, indent=2)

def calculate_moving_average(prices):
    """Calculate moving average from price list. Returns None if not enough data."""
    if not prices or len(prices) < 10:  # Need at least 10 prices
        return None
    price_values = [p["price"] for p in prices]
    return sum(price_values) / len(price_values)

def add_price_to_history(price):
    """Add new price with timestamp to history and return updated list."""
    prices = load_price_history()
    prices.append({
        "price": price,
        "timestamp": datetime.now().isoformat()
    })
    save_price_history(prices)
    return prices

def get_current_timestamp():
    """Get current timestamp in readable format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
