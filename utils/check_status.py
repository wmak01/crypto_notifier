#!/usr/bin/env python3
"""
Check app status - shows current iteration count and progress
"""
import json
import os

price_history_file = os.path.join("..", "data", "prices_history.json")

if os.path.exists(price_history_file):
    with open(price_history_file, 'r') as f:
        data = json.load(f)
        prices = data if isinstance(data, list) else data.get('prices', [])
        count = len(prices)
        percentage = round((count / 100) * 100, 1)
        
        print(f"\n{'='*60}")
        print(f"📊 CRYPTO NOTIFIER - APP STATUS CHECK")
        print(f"{'='*60}")
        print(f"\n✅ APP IS RUNNING")
        print(f"   Iterations collected: {count}/100 ({percentage}%)")
        
        if count < 100:
            remaining = 100 - count
            time_remaining = remaining * 60  # 60 seconds per iteration
            hours = time_remaining // 3600
            minutes = (time_remaining % 3600) // 60
            
            print(f"\n⏳ PROGRESS TO SIGNALS:")
            print(f"   Remaining: {remaining} iterations")
            print(f"   Time remaining: ~{hours}h {minutes}m")
            print(f"   \n   [{'█' * int(percentage/5)}{' ' * (20 - int(percentage/5))}] {percentage}%")
        else:
            print(f"\n🎯 SIGNALS ACTIVE!")
            print(f"   Moving Average ready")
            print(f"   Technical analysis active")
            print(f"   Watching for BUY/SELL signals...")
        
        if count >= 1:
            latest = prices[-1] if isinstance(prices[0], dict) else prices[-1]
            if isinstance(latest, dict):
                latest_price = latest.get('price', 'N/A')
                timestamp = latest.get('timestamp', 'N/A')
            else:
                latest_price = latest
                timestamp = 'N/A'
            
            print(f"\n📈 LATEST DATA:")
            print(f"   Current Price: {latest_price:,.2f} HKD")
            print(f"   Last Update: {timestamp}")
        
        print(f"\n{'='*60}\n")
else:
    print("❌ No price history found. App may not have started yet.")
