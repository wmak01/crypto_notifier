#!/usr/bin/env python3
"""
Launch both ETH and BTC trackers in separate background processes
"""
import subprocess
import sys
import time
import os

def main():
    print("\n" + "="*60)
    print("🚀 LAUNCHING DUAL ASSET TRACKERS")
    print("="*60)
    
    # Launch ETH tracker
    print("\n📊 Starting ETH tracker...")
    eth_process = subprocess.Popen(
        [sys.executable, os.path.join("..", "main.py"), "state.txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    print(f"✅ ETH tracker started (PID: {eth_process.pid})")
    time.sleep(2)
    
    # Launch BTC tracker
    print("\n📊 Starting BTC tracker...")
    btc_process = subprocess.Popen(
        [sys.executable, os.path.join("..", "main.py"), "state_btc.txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    print(f"✅ BTC tracker started (PID: {btc_process.pid})")
    
    print("\n" + "="*60)
    print("✅ BOTH TRACKERS RUNNING")
    print("="*60)
    print("\n📊 Monitoring:")
    print("   - ETH: Tracking data/state.txt")
    print("   - BTC: Tracking data/state_btc.txt")
    print("\n💡 To check status: python dual_dashboard.py")
    print("💡 To stop: Ctrl+C or close this window")
    print("\n" + "="*60)
    
    try:
        # Keep script running and show output
        while True:
            # Read ETH output
            eth_line = eth_process.stdout.readline()
            if eth_line:
                print(f"[ETH] {eth_line.strip()}")
            
            # Read BTC output
            btc_line = btc_process.stdout.readline()
            if btc_line:
                print(f"[BTC] {btc_line.strip()}")
            
            # Check if processes are still alive
            if eth_process.poll() is not None or btc_process.poll() is not None:
                print("\n⚠️  One of the trackers stopped!")
                break
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Stopping both trackers...")
        eth_process.terminate()
        btc_process.terminate()
        print("✅ Both trackers stopped")

if __name__ == "__main__":
    main()
