"""
Quick Telegram Chat ID getter - run this to get your chat ID
"""

import requests
import sys

print("=" * 60)
print("🤖 Telegram Chat ID Getter")
print("=" * 60)

# Get bot token from user
bot_token = input("\n📝 Paste your bot TOKEN from BotFather: ").strip()

if not bot_token or len(bot_token) < 10:
    print("❌ Invalid token!")
    sys.exit(1)

print("\n⏳ Waiting for messages from your bot...")
print("   (Go to your bot on Telegram and click START or send any message)")
print("   (Keep this window open!)\n")

while True:
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            print("❌ Invalid token or API error")
            sys.exit(1)
        
        data = response.json()
        
        if data.get("ok") and data.get("result"):
            # Found messages!
            for update in data["result"]:
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    first_name = update["message"]["chat"].get("first_name", "User")
                    
                    print("=" * 60)
                    print("✅ SUCCESS! Found your Chat ID:")
                    print("=" * 60)
                    print(f"\n🆔 Chat ID: {chat_id}")
                    print(f"👤 User: {first_name}")
                    print("\n📋 Copy this and paste in config.yaml:")
                    print(f"\ntelegram:")
                    print(f"  chat_id: \"{chat_id}\"")
                    print(f"  bot_token: \"{bot_token}\"\n")
                    print("=" * 60)
                    sys.exit(0)
        
        print("⏳ Waiting... (checking every 2 seconds)")
        import time
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
