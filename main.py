import time
import yaml
import sys
from price_fetcher import get_price
from decision_engine import evaluate
from notifier import send_email
from utils import load_pending, save_pending, add_price_to_history, calculate_moving_average, get_current_timestamp, check_time_gap, clear_price_history

# Fix encoding for Windows terminal
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_state():
    state = {}
    with open("state.txt") as f:
        for line in f:
            k, v = line.strip().split("=")
            # Convert to float for numeric values, keep as string otherwise
            try:
                state[k] = float(v)
            except ValueError:
                state[k] = v
    return state

config = yaml.safe_load(open("config.yaml"))

print("[STARTUP] Crypto Notifier - Testing Mode (No Email)")
print(f"[INFO] Interval: {config['check_interval_sec']}s | Hold Band: ±{config['hold_band_pct']}% | MA Ready at: 100 iterations")
print("-" * 80)

# Check for time gap on startup
if check_time_gap():
    print("[RESTART] Time gap detected - clearing stale price history")
    clear_price_history()

iteration = 0

while True:
    iteration += 1
    
    state = load_state()
    asset = state["ASSET"]
    
    try:
        price = get_price(asset)
    except Exception as e:
        print(f"[ERROR] {get_current_timestamp()} - Failed to fetch price: {e}")
        time.sleep(config["check_interval_sec"])
        continue

    # Add price to history and get moving average
    prices = add_price_to_history(price)
    moving_avg = calculate_moving_average(prices)
    num_prices = len(prices)
    
    # Clean output - only essential info
    timestamp = get_current_timestamp()
    
    if num_prices < 100:
        # Before MA is ready - minimal output
        pct_collected = round((num_prices / 100) * 100, 1)
        print(f"[{timestamp}] ITER {iteration} | Price: {price:,.2f} HKD | MA Status: {pct_collected}% ({num_prices}/100)")
    else:
        # After MA is ready - show detailed info
        pct_change = ((price - moving_avg) / moving_avg) * 100
        portfolio_value = (state['CURRENT_BALANCE'] * price) + state['AVAILABLE_CASH_HKD']
        print(f"[{timestamp}] ITER {iteration} | Price: {price:,.2f} HKD | MA: {moving_avg:,.2f} HKD | Change: {pct_change:+.2f}% | Portfolio: {portfolio_value:,.2f} HKD")

    # Use moving average as reference price (or use manual one if MA not ready)
    ref_price = moving_avg if moving_avg else state["LAST_REFERENCE_PRICE"]
    
    # Only evaluate trading signals after 100 iterations
    if iteration >= 100:
        decisions = evaluate(
            price,
            ref_price,
            state["CURRENT_BALANCE"],
            state["AVAILABLE_CASH_HKD"],
            config
        )

        if decisions:
            decision = decisions[0]  # only one at a time
            
            # Handle HOLD state
            if decision["type"] == "HOLD":
                print(f"  HOLD | {decision['reason']}")
            else:
                # BUY or SELL signal
                print(f"  SIGNAL: {decision['type']} | Trigger: {decision['trigger_pct']}%", end="")
                if decision["type"] == "BUY":
                    print(f" | Amount: {decision['amount_hkd']:,.2f} HKD")
                else:
                    print(f" | Amount: {decision['amount_eth']:.6f} {asset.upper()}")
                
                # Log decision
                save_pending({
                    "pending": False,
                    "decision": decision,
                    "reference_price": ref_price,
                    "timestamp": timestamp,
                    "note": "Testing mode - email disabled"
                })
    else:
        # Before 100 iterations - don't show signals yet
        pass

    time.sleep(config["check_interval_sec"])

