#!/usr/bin/env python3
"""
Dual Asset Dashboard - Monitor ETH and BTC running simultaneously
Shows progress, prices, and status for both assets on one screen
"""
import json
import os

def get_price_data(filename):
    """Get price history data"""
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            prices = data if isinstance(data, list) else data.get('prices', [])
            return prices
    except:
        return None

def format_progress_bar(percentage):
    """Create visual progress bar"""
    filled = int(percentage / 5)
    empty = 20 - filled
    return f"[{'█' * filled}{' ' * empty}] {percentage:.1f}%"

def main():
    print("\n" + "="*80)
    print("🎯 DUAL ASSET TRACKER - ETH & BTC LIVE")
    print("="*80)
    
    # Check ETH
    eth_data = get_price_data("prices_history.json")
    eth_count = len(eth_data) if eth_data else 0
    eth_pct = round((eth_count / 100) * 100, 1)
    
    # Check BTC
    btc_data = get_price_data("prices_history_state_btc.json")
    btc_count = len(btc_data) if btc_data else 0
    btc_pct = round((btc_count / 100) * 100, 1)
    
    print(f"\n{'ETHEREUM (ETH)':<40} {'BITCOIN (BTC)':<40}")
    print("-" * 80)
    
    # Progress
    eth_progress = format_progress_bar(eth_pct) if eth_data else "Waiting..."
    btc_progress = format_progress_bar(btc_pct) if btc_data else "Waiting..."
    
    print(f"Progress: {eth_progress:<35} | {btc_progress}")
    print(f"Iterations: {eth_count}/100 ({eth_pct}%){' '*22} | {btc_count}/100 ({btc_pct}%)")
    
    # Latest prices
    if eth_data:
        latest_eth = eth_data[-1]
        eth_price = latest_eth.get('price', 'N/A') if isinstance(latest_eth, dict) else latest_eth
        eth_time = latest_eth.get('timestamp', 'N/A') if isinstance(latest_eth, dict) else 'N/A'
    else:
        eth_price = "N/A"
        eth_time = "N/A"
    
    if btc_data:
        latest_btc = btc_data[-1]
        btc_price = latest_btc.get('price', 'N/A') if isinstance(latest_btc, dict) else latest_btc
        btc_time = latest_btc.get('timestamp', 'N/A') if isinstance(latest_btc, dict) else 'N/A'
    else:
        btc_price = "N/A"
        btc_time = "N/A"
    
    print(f"\nPrice: ${eth_price:>13,.2f} HKD        | ${btc_price:>13,.2f} HKD")
    print(f"Updated: {str(eth_time):<35} | {str(btc_time)}")
    
    # Status
    if eth_count >= 100:
        eth_status = "🟢 SIGNALS ACTIVE"
    elif eth_count > 0:
        eth_status = f"🟡 COLLECTING ({eth_count}/100)"
    else:
        eth_status = "⚫ STARTING..."
    
    if btc_count >= 100:
        btc_status = "🟢 SIGNALS ACTIVE"
    elif btc_count > 0:
        btc_status = f"🟡 COLLECTING ({btc_count}/100)"
    else:
        btc_status = "⚫ STARTING..."
    
    print(f"\nStatus: {eth_status:<37} | {btc_status}")
    
    # Telegram Status
    print(f"\n{'='*80}")
    print("📱 TELEGRAM NOTIFICATIONS")
    print("-" * 80)
    print("When signals arrive, you'll get messages like:")
    print("\n  🟢 BUY SIGNAL - ETH @ 19,500 HKD")
    print("  CONFIDENCE: 65% - Strong signal")
    print("  Your Options: Skip / Micro / Small / Normal / Large")
    print("\n  🔴 SELL SIGNAL - BTC @ 635,000 HKD")  
    print("  CONFIDENCE: 78% - Strong signal")
    print("  Your Options: Hold / Partial / Half / Full")
    print("\nBoth assets send to the SAME Telegram chat.")
    print("Each runs independently and sends its own signals.")
    
    # Next milestones
    print(f"\n{'='*80}")
    print("⏱️ NEXT MILESTONES")
    print("-" * 80)
    
    if eth_count < 100:
        eth_remaining = (100 - eth_count) * 60
        eth_hours = eth_remaining // 3600
        eth_mins = (eth_remaining % 3600) // 60
        print(f"ETH Signals: {eth_remaining//60} iterations (~{eth_hours}h {eth_mins}m)")
    else:
        print(f"ETH Signals: 🟢 ACTIVE NOW")
    
    if btc_count < 100:
        btc_remaining = (100 - btc_count) * 60
        btc_hours = btc_remaining // 3600
        btc_mins = (btc_remaining % 3600) // 60
        print(f"BTC Signals: {btc_remaining//60} iterations (~{btc_hours}h {btc_mins}m)")
    else:
        print(f"BTC Signals: 🟢 ACTIVE NOW")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
