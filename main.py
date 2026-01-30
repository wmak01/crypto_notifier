import time
import yaml
import sys
import os
from price_fetcher import get_price
from decision_engine import evaluate
from notifier import send_email
from utils import load_pending, save_pending, add_price_to_history, calculate_moving_average, get_current_timestamp, check_time_gap, clear_price_history
from trade_logger import log_trade, get_trade_stats
from state_updater import update_cost_basis_after_buy, update_balance_after_sell, calculate_days_to_breakeven

# Fix encoding for Windows terminal
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Get state file from command line argument, default to state.txt
STATE_FILE = sys.argv[1] if len(sys.argv) > 1 else "state.txt"
PRICE_HISTORY_FILE_BASE = STATE_FILE.replace('.txt', '')

def load_state():
    state = {}
    with open(STATE_FILE) as f:
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
print(f"[INFO] State File: {STATE_FILE}")
print("-" * 80)

# Initialize price history file for this instance
from utils import set_price_history_file
set_price_history_file(PRICE_HISTORY_FILE_BASE)

# Check for time gap on startup
if check_time_gap():
    print("[RESTART] Time gap detected - clearing stale price history")
    clear_price_history()

iteration = 0

while True:
    iteration += 1
    
    state = load_state()
    asset = state["ASSET"]
    cost_basis = state.get("COST_BASIS")  # Get cost basis if available
    
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
        # After MA is ready - show detailed info with P/L
        pct_change = ((price - moving_avg) / moving_avg) * 100
        portfolio_value = (state['CURRENT_BALANCE'] * price) + state['AVAILABLE_CASH_HKD']
        
        # Calculate unrealized P/L
        unrealized_pnl = None
        unrealized_pnl_pct = None
        days_to_breakeven = None
        
        if cost_basis:
            unrealized_pnl = (price - cost_basis) * state['CURRENT_BALANCE']
            unrealized_pnl_pct = ((price - cost_basis) / cost_basis) * 100
            
            # Estimate days to breakeven based on MA trend
            if num_prices >= 20:
                # Calculate average daily change from recent prices
                recent_prices = [p["price"] for p in prices[-20:]]
                avg_price_old = sum(recent_prices[:10]) / 10
                avg_price_new = sum(recent_prices[10:]) / 10
                avg_daily_change_pct = ((avg_price_new - avg_price_old) / avg_price_old) * 100 / 10
                days_to_breakeven = calculate_days_to_breakeven(price, cost_basis, avg_daily_change_pct)
        
        output = f"[{timestamp}] ITER {iteration} | Price: {price:,.2f} HKD | MA: {moving_avg:,.2f} HKD | Change: {pct_change:+.2f}% | Portfolio: {portfolio_value:,.2f} HKD"
        
        if unrealized_pnl is not None:
            output += f" | P/L: {unrealized_pnl:+,.2f} HKD ({unrealized_pnl_pct:+.2f}%)"
            
            # Show days to breakeven if in loss
            if unrealized_pnl_pct < -0.5:
                if days_to_breakeven is not None and days_to_breakeven > 0:
                    output += f" | Breakeven: ~{days_to_breakeven}d"
                elif days_to_breakeven is None:
                    output += f" | Breakeven: N/A (declining)"
        
        print(output)

    # Use moving average as reference price (or use manual one if MA not ready)
    ref_price = moving_avg if moving_avg else state["LAST_REFERENCE_PRICE"]
    
    # Only evaluate trading signals after 100 iterations
    if iteration >= 100:
        decisions = evaluate(
            price,
            ref_price,
            state["CURRENT_BALANCE"],
            state["AVAILABLE_CASH_HKD"],
            config,
            cost_basis  # Pass cost basis for profit checking
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
                    
                    # Update cost basis automatically (weighted average)
                    if cost_basis:
                        print(f"\n  [AUTO-UPDATE] Recalculating cost basis...", end="")
                        new_cost_basis, new_balance = update_cost_basis_after_buy(
                            STATE_FILE,
                            state["CURRENT_BALANCE"],
                            cost_basis,
                            decision['amount_hkd'],
                            price
                        )
                        print(f" Old: {cost_basis:,.2f} HKD → New: {new_cost_basis:,.2f} HKD")
                    
                    # Log buy trade
                    log_trade(
                        asset=asset,
                        trade_type="BUY",
                        price=price,
                        amount_hkd=decision['amount_hkd'],
                        cost_basis=cost_basis,
                        trigger_pct=decision['trigger_pct'],
                        reason=f"Price {decision['trigger_pct']}% below MA"
                    )
                else:
                    amount_crypto = decision.get('amount_eth', decision.get('amount_btc', 0))
                    print(f" | Amount: {amount_crypto:.6f} {asset.upper()}")
                    
                    # Calculate and show expected profit
                    if cost_basis:
                        expected_pnl = (price - cost_basis) * amount_crypto
                        expected_pnl_pct = ((price - cost_basis) / cost_basis) * 100
                        print(f" | Expected P/L: {expected_pnl:+,.2f} HKD ({expected_pnl_pct:+.2f}%)")
                    
                    # Update balance after sell
                    print(f"\n  [AUTO-UPDATE] Updating balance after sell...")
                    new_balance = update_balance_after_sell(
                        STATE_FILE,
                        state["CURRENT_BALANCE"],
                        amount_crypto
                    )
                    
                    # Log sell trade
                    log_trade(
                        asset=asset,
                        trade_type="SELL",
                        price=price,
                        amount_crypto=amount_crypto,
                        cost_basis=cost_basis,
                        trigger_pct=decision['trigger_pct'],
                        reason=f"Price {decision['trigger_pct']}% above MA"
                    )
                
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

