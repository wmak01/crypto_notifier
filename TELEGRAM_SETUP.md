# 🚀 Telegram Notifications Setup Guide

## Step-by-Step Instructions for Your Phone

### **Step 1: Download Telegram on Your Phone** (2 minutes)

1. Go to App Store (iOS) or Google Play (Android)
2. Search for "Telegram"
3. Install the official Telegram app by Telegram LLC
4. Open it and verify your phone number

---

### **Step 2: Create Your Trading Bot** (3 minutes)

**On your phone, open Telegram and follow these steps:**

1. **Open Telegram** and search for **`@BotFather`** (exact name)
   - Or click this link: https://t.me/botfather

2. **Start the conversation**
   - Tap on BotFather
   - Click "START" button (bottom of screen)

3. **Create a new bot**
   - Type: `/newbot`
   - BotFather asks: "What should your bot be called?"
   - Type: `CryptoNotifier` (or any name you like)
   - BotFather asks: "What should your bot's username be?"
   - Type: `CryptoNotifier_YourName_Bot` (must end with `_bot`, replace YourName with something unique)

4. **BotFather gives you:**
   - A **TOKEN** (long string like: `123456:ABCDEFGhijklmnopqrstuvwxyz`)
   - **SAVE THIS** - you'll need it!

---

### **Step 3: Get Your Chat ID** (2 minutes)

1. **Search for your new bot** in Telegram
   - Search for the username you just created (e.g., `CryptoNotifier_YourName_Bot`)

2. **Start the bot**
   - Click on your bot
   - Tap "START" button

3. **Get your Chat ID**
   - Still on your phone, go to this link: https://api.telegram.org/bot**TOKEN**/getUpdates
   - Replace **TOKEN** with your bot token from Step 2
   - Open this link in your phone's browser
   - You'll see JSON data - look for: `"chat":{"id":123456789}`
   - The number is your **CHAT ID** (e.g., `123456789`)
   - **SAVE THIS** - you'll need it!

---

### **Step 4: Add Bot Token and Chat ID to Your Program** (1 minute)

1. **On your computer**, open the file: `config.yaml`

2. **Find this section:**
```yaml
telegram:
  enabled: true
  bot_token: ""
  chat_id: ""
  notify_buy: true
  notify_sell: true
  notify_hold: false
```

3. **Paste your values:**
```yaml
telegram:
  enabled: true
  bot_token: "123456:ABCDEFGhijklmnopqrstuvwxyz"      # Your token from BotFather
  chat_id: "123456789"                                # Your chat ID from browser
  notify_buy: true
  notify_sell: true
  notify_hold: false
```

4. **Save the file**

---

### **Step 5: Test the Connection** (1 minute)

1. **Stop the program** if it's running (Ctrl+C)

2. **Run this test command:**
```powershell
cd "C:\Users\chunw\OneDrive\Documents\VS Code\Python\crypto_notifier"
python -c "
from notifier_telegram import send_telegram_message
from config import config
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

bot_token = config['telegram']['bot_token']
chat_id = config['telegram']['chat_id']

success = send_telegram_message(bot_token, chat_id, '✅ <b>Crypto Notifier is Connected!</b>\n\nYou will now receive trading alerts on this chat.')

if success:
    print('[SUCCESS] Telegram connection working!')
else:
    print('[ERROR] Check your token and chat ID')
"
```

3. **Check your Telegram** - you should get a message immediately!

---

### **Step 6: Let the Program Run** ✅

1. **Start the program again:**
```powershell
python main.py state.txt
```

2. **Now when BUY or SELL signals trigger, you'll get notifications on Telegram!**

---

## 📬 What You'll Receive

### **BUY Signal Example:**
```
🟢 BUY SIGNAL - ETH
━━━━━━━━━━━━━━━━━━━━━━━
Price: 21,400 HKD
Amount: 3,500 HKD
Action: Average down

Analysis:
• Current loss: -30.4%
• Cost basis: 30,743 HKD
• RSI: 28 (oversold)
• Support: 20,500 HKD (-4.1%)

Reason: Smart BUY | Oversold with support nearby

2026-02-01 13:45
```

### **SELL Signal Example:**
```
🔴 SELL SIGNAL - ETH
━━━━━━━━━━━━━━━━━━━━━━━
Price: 32,000 HKD
Amount: 0.46669 ETH
Action: Take profit

Analysis:
• Profit: +4.10%
• Cost basis: 30,743 HKD
• RSI: 72 (overbought)
• Resistance: 32,500 HKD (+1.6%)

Reason: Profit taking at resistance

2026-02-01 14:30
```

---

## 🔐 Security Notes

✅ **Your data is safe:**
- Your bot token is only stored locally in `config.yaml`
- Messages are encrypted by Telegram
- Only YOU receive the messages
- Never upload `config.yaml` to public repos

⚠️ **Best practices:**
- Keep your `config.yaml` on your computer only
- Don't share your bot token
- If you accidentally expose the token, delete the bot and create a new one

---

## 🆘 Troubleshooting

**Not receiving messages?**
1. Check `config.yaml` - verify token and chat ID are exactly correct (no spaces)
2. Verify bot is activated on your phone (you saw the START button)
3. Run the test command again
4. Check Telegram settings - allow notifications

**Token/Chat ID not working?**
1. Go back to BotFather (`@BotFather`)
2. Type `/mybots` to see your bot
3. Type `/start` in your new bot again
4. Get new Chat ID from: https://api.telegram.org/bot**TOKEN**/getUpdates

---

## ✨ Advanced Options

**To disable certain alerts, edit `config.yaml`:**

```yaml
telegram:
  notify_buy: true      # Get BUY alerts
  notify_sell: true     # Get SELL alerts
  notify_hold: false    # Disable HOLD updates (too frequent)
```

---

Done! Your crypto trading bot will now notify you instantly on Telegram! 🎉

