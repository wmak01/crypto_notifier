import time
import yaml
import sys
import os
from price_fetcher import get_price
from decision_engine import evaluate
from modules.notifier_telegram import send_telegram_message, format_alert
from utils_core import load_pending, save_pending, add_price_to_history, calculate_moving_average, get_current_timestamp, check_time_gap, clear_price_history
from modules.historical_analyzer import fetch_historical_data, analyze_price_action
from modules.trailing_stop_manager import TrailingStopManager
from modules.pattern_analyzer import calculate_rsi, detect_capitulation, generate_buy_conviction_score, generate_sell_signal_with_explanation
from modules.signal_state_tracker import SignalStateTracker

# Fix encoding for Windows terminal
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Get state file from command line argument, default to data/state.txt
STATE_FILE = os.path.join("data", sys.argv[1]) if len(sys.argv) > 1 else "data/state.txt"
PRICE_HISTORY_FILE_BASE = os.path.join("data", sys.argv[1].replace('.txt', '')) if len(sys.argv) > 1 else "data/state"

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

print("[STARTUP] Crypto Notifier - Advanced Multi-Factor Analysis")
print(f"[INFO] Interval: {config['check_interval_sec']}s | Hold Band: ±{config['hold_band_pct']}% | MA Ready at: 100 iterations")
print(f"[INFO] State File: {STATE_FILE}")
print(f"[INFO] Features: Trailing Stops | Historical Data | Pattern Recognition | Multi-Factor Scoring")
print("-" * 80)

# Initialize price history file for this instance
from utils_core import set_price_history_file
set_price_history_file(PRICE_HISTORY_FILE_BASE)

# Initialize trailing stop manager
trailing_stop_manager = TrailingStopManager(STATE_FILE)

# Initialize signal state tracker (prevents duplicate messages)
signal_tracker = SignalStateTracker(STATE_FILE)

# Check for time gap on startup
if check_time_gap():
    print("[RESTART] Time gap detected - clearing stale price history")
    clear_price_history()

iteration = 0
last_historical_fetch = 0
HISTORICAL_FETCH_INTERVAL = 3600  # Fetch historical data every 1 hour

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
    
    # Fetch historical data periodically for pattern analysis
    historical_analysis = None
    current_time = time.time()
    
    if iteration >= 100 and config.get('historical_data', {}).get('enabled', True):
        if current_time - last_historical_fetch > HISTORICAL_FETCH_INTERVAL:
            try:
                asset_id = 'ethereum' if asset.lower() == 'eth' else 'bitcoin'
                cache_file = f'historical_{asset}.json'
                data = fetch_historical_data(asset_id, days=90, cache_file=cache_file)
                
                if data:
                    historical_analysis = analyze_price_action(data.get('prices', []))
                    last_historical_fetch = current_time
                    print(f"[{get_current_timestamp()}] Historical data refreshed (90-day analysis)")
            except Exception as e:
                print(f"[WARNING] Historical data fetch failed: {e}")
    
    # Calculate RSI and other technical indicators
    current_rsi = None
    volumes_data = []
    
    if num_prices >= 14:
        price_list = [p['price'] if isinstance(p, dict) else p for p in prices]
        current_rsi = calculate_rsi(price_list, period=14)
    
    # Extract volatility and trend info from historical analysis
    volatility_level = 'moderate'
    support_level = None
    resistance_level = None
    trend_direction = 'sideways'
    percentile = 50
    volume_signal = 'normal'
    
    if historical_analysis:
        vol_data = historical_analysis.get('volatility', {})
        volatility_level = vol_data.get('vol_level', 'moderate')
        
        sr_data = historical_analysis.get('support_resistance', {})
        support_level = sr_data.get('support')
        resistance_level = sr_data.get('resistance')
        
        trend_data = historical_analysis.get('trend', {})
        trend_direction = trend_data.get('trend', 'sideways')
        
        percentile = historical_analysis.get('percentile', 50)
    
    # Clean output - only essential info
    timestamp = get_current_timestamp()
    
    if num_prices < 100:
        # Before MA is ready - minimal output
        pct_collected = round((num_prices / 100) * 100, 1)
        print(f"[{timestamp}] ITER {iteration} | Price: {price:,.2f} HKD | MA Status: {pct_collected}% ({num_prices}/100)")
    else:
        # After MA is ready - show detailed info with P/L and technical analysis
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
                recent_prices = [p["price"] if isinstance(p, dict) else p for p in prices[-20:]]
                avg_price_old = sum(recent_prices[:10]) / 10
                avg_price_new = sum(recent_prices[10:]) / 10
                avg_daily_change_pct = ((avg_price_new - avg_price_old) / avg_price_old) * 100 / 10
                days_to_breakeven = calculate_days_to_breakeven(price, cost_basis, avg_daily_change_pct)
        
        # Build main output line
        output = f"[{timestamp}] ITER {iteration} | Price: {price:,.2f} HKD | MA: {moving_avg:,.2f} HKD | Change: {pct_change:+.2f}%"
        
        # Add technical indicators
        if current_rsi:
            output += f" | RSI: {current_rsi}"
        
        output += f" | Trend: {trend_direction}"
        
        if unrealized_pnl is not None:
            output += f" | P/L: {unrealized_pnl:+,.2f} HKD ({unrealized_pnl_pct:+.2f}%)"
            
            # Show days to breakeven if in loss
            if unrealized_pnl_pct < -0.5:
                if days_to_breakeven is not None and days_to_breakeven > 0:
                    output += f" | Breakeven: ~{days_to_breakeven}d"
        
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
                print(f"  └─ HOLD | {decision['reason']}")
            else:
                # BUY or SELL signal
                print(f"\n  └─ SIGNAL: {decision['type']}", end="")
                
                if decision["type"] == "BUY":
                    amount_hkd = decision.get('amount_hkd', 0)
                    
                    # Calculate conviction score for this BUY signal
                    conviction_score = 50  # Default
                    if historical_analysis and current_rsi:
                        conviction_score = generate_buy_conviction_score(
                            price=price,
                            moving_avg=moving_avg,
                            rsi=current_rsi,
                            support=support_level,
                            trend=trend_direction,
                            percentile=percentile,
                            historical_data=historical_analysis
                        )
                    
                    print(f" @ {price:,.0f} HKD | Amount: {amount_hkd:,.2f} HKD | Conviction: {conviction_score}%")
                    
                    # Show reasoning
                    if 'reason' in decision:
                        print(f"     Reason: {decision['reason']}")
                    if 'loss_pct' in decision:
                        print(f"     Averaging down: {decision['loss_pct']:.1f}%")
                    
                    # Show technical context
                    if support_level:
                        dist_to_support = ((price - support_level) / support_level) * 100
                        print(f"     Support: {support_level:,.0f} HKD ({dist_to_support:+.1f}%)")
                    if current_rsi:
                        print(f"     RSI: {current_rsi} (oversold zone)")
                    
                    # Check if we should send alert (using signal state tracker)
                    should_send, reason, is_change = signal_tracker.should_send_alert(
                        'BUY', conviction_score, price
                    )
                    
                    # Send Telegram notification only if state changed meaningfully
                    if should_send and config.get('telegram', {}).get('enabled') and config.get('telegram', {}).get('notify_buy'):
                        buy_data = {
                            'price': price,
                            'amount_hkd': amount_hkd,
                            'asset': asset,
                            'cost_basis': cost_basis,
                            'loss_pct': decision.get('loss_pct', 0),
                            'rsi': current_rsi,
                            'support': support_level,
                            'reason': decision.get('reason', 'Smart averaging down'),
                            'conviction': conviction_score
                        }
                        message = format_alert('BUY', buy_data)
                        send_telegram_message(
                            config['telegram']['bot_token'],
                            config['telegram']['chat_id'],
                            message
                        )
                        # Update signal state after sending
                        signal_tracker.update_state('BUY', conviction_score, price)
                        print(f"     [TELEGRAM] Message sent ({reason})")
                    else:
                        if not should_send:
                            print(f"     [SPAM FILTER] Not sending: {reason}")
                    
                    # Update cost basis automatically (weighted average)
                    if cost_basis:
                        print(f"     [AUTO-UPDATE] Recalculating cost basis...", end="")
                        new_cost_basis, new_balance = update_cost_basis_after_buy(
                            STATE_FILE,
                            state["CURRENT_BALANCE"],
                            cost_basis,
                            amount_hkd,
                            price
                        )
                        print(f" {cost_basis:,.2f} → {new_cost_basis:,.2f} HKD")
                    
                    # Log buy trade
                    log_trade(
                        asset=asset,
                        trade_type="BUY",
                        price=price,
                        amount_hkd=amount_hkd,
                        cost_basis=cost_basis,
                        trigger_pct=decision.get('trigger_pct', -20),
                        reason=decision.get('reason', 'Average down opportunity')
                    )
                
                else:  # SELL
                    amount_crypto = decision.get('amount_eth', decision.get('amount_btc', 0))
                    
                    # Calculate conviction score for this SELL signal
                    conviction_score, reason_detailed = generate_sell_signal_with_explanation(
                        price=price,
                        moving_avg=moving_avg,
                        rsi=current_rsi,
                        resistance=resistance_level,
                        cost_basis=cost_basis,
                        current_balance=state["CURRENT_BALANCE"],
                        trend=trend_direction,
                        historical_data=historical_analysis
                    )
                    
                    print(f" @ {price:,.0f} HKD | Amount: {amount_crypto:.6f} {asset.upper()} | Conviction: {conviction_score}%")
                    
                    # Show reasoning
                    if 'reason' in decision:
                        print(f"     Reason: {decision['reason']}")
                    if 'profit_pct' in decision:
                        print(f"     Profit: +{decision['profit_pct']:.2f}%")
                    
                    # Show technical context
                    if resistance_level:
                        dist_to_resist = ((price - resistance_level) / resistance_level) * 100
                        print(f"     Resistance: {resistance_level:,.0f} HKD ({dist_to_resist:+.1f}%)")
                    if current_rsi:
                        print(f"     RSI: {current_rsi}")
                    
                    # Check if we should send alert (using signal state tracker)
                    should_send, reason_spam, is_change = signal_tracker.should_send_alert(
                        'SELL', conviction_score, price
                    )
                    
                    # Send Telegram notification only if state changed meaningfully
                    if should_send and config.get('telegram', {}).get('enabled') and config.get('telegram', {}).get('notify_sell'):
                        sell_data = {
                            'price': price,
                            'amount_crypto': amount_crypto,
                            'asset': asset,
                            'cost_basis': cost_basis,
                            'profit_pct': decision.get('profit_pct', 0),
                            'rsi': current_rsi,
                            'resistance': resistance_level,
                            'reason': decision.get('reason', 'Profit taking'),
                            'conviction': conviction_score
                        }
                        message = format_alert('SELL', sell_data)
                        send_telegram_message(
                            config['telegram']['bot_token'],
                            config['telegram']['chat_id'],
                            message
                        )
                        # Update signal state after sending
                        signal_tracker.update_state('SELL', conviction_score, price)
                        print(f"     [TELEGRAM] Message sent ({reason_spam})")
                    else:
                        if not should_send:
                            print(f"     [SPAM FILTER] Not sending: {reason_spam}")
                    
                    # Update balance after sell
                    print(f"     [AUTO-UPDATE] Updating balance after sell...")
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
                        trigger_pct=decision.get('trigger_pct', 20),
                        reason=decision.get('reason', 'Profit taking')
                    )
                
                # Log decision
                save_pending({
                    "pending": False,
                    "decision": decision,
                    "reference_price": ref_price,
                    "timestamp": timestamp,
                    "historical_analysis": bool(historical_analysis)
                })
        else:
            # No signals - just hold
            pass
    
    time.sleep(config["check_interval_sec"])


