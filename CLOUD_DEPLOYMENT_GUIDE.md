# ☁️ CLOUD DEPLOYMENT GUIDE - PythonAnywhere

## Why PythonAnywhere?

✅ **FREE tier available**  
✅ **Runs 24/7** (no need to keep PC on)  
✅ **Python 3.9+ supported**  
✅ **Easy to use** (web-based interface)  
✅ **File upload** (upload your entire project)  
✅ **Scheduled tasks** (run your scripts automatically)  

---

## 📋 Step-by-Step Deployment

### Step 1: Create Free Account

1. Go to: https://www.pythonanywhere.com
2. Click "Start running Python online in less than a minute!"
3. Sign up for **Beginner Account** (FREE)
4. Verify your email

---

### Step 2: Upload Your Files

**Option A: Via Web Interface**

1. Login to PythonAnywhere
2. Go to **Files** tab
3. Create folder: `crypto_notifier`
4. Upload these files:
   ```
   ✅ main.py
   ✅ config.yaml
   ✅ state.txt
   ✅ state_btc.txt
   ✅ price_fetcher.py
   ✅ decision_engine.py
   ✅ notifier_telegram.py
   ✅ utils.py
   ✅ state_updater.py
   ✅ trade_logger.py
   ✅ historical_analyzer.py
   ✅ pattern_analyzer.py
   ✅ trailing_stop_manager.py
   ✅ signal_state_tracker.py
   ✅ confidence_levels.py
   ✅ requirements.txt
   ```

**Option B: Via Console** (faster for multiple files)

1. Go to **Consoles** tab
2. Start a **Bash console**
3. Run:
   ```bash
   mkdir crypto_notifier
   cd crypto_notifier
   
   # Then upload via Files tab or use git
   git clone <your-repo-url>  # if you have it on GitHub
   ```

---

### Step 3: Install Requirements

1. Go to **Consoles** tab
2. Start a **Bash console**
3. Run:
   ```bash
   cd crypto_notifier
   pip3.9 install --user -r requirements.txt
   ```

Or install manually:
```bash
pip3.9 install --user pyyaml requests
```

---

### Step 4: Test Your Setup

In the Bash console:
```bash
cd crypto_notifier
python3.9 main.py state.txt
```

If it runs without errors, press Ctrl+C and continue.

---

### Step 5: Create Always-On Tasks

**Important:** Free tier allows **ONE** always-on task.

#### Option A: Run ETH Only
1. Go to **Tasks** tab
2. Create new task:
   ```bash
   cd /home/YOUR_USERNAME/crypto_notifier && python3.9 main.py state.txt
   ```
3. Set to run **every hour** or **every day**

#### Option B: Run Both ETH and BTC (Advanced)

Create a wrapper script `run_both.sh`:
```bash
#!/bin/bash
cd /home/YOUR_USERNAME/crypto_notifier
python3.9 main.py state.txt &
python3.9 main.py state_btc.txt &
wait
```

Then schedule:
```bash
bash /home/YOUR_USERNAME/crypto_notifier/run_both.sh
```

---

### Step 6: Schedule as Cron Job (Better)

1. Go to **Tasks** tab
2. Scroll to **Scheduled tasks**
3. Add task:
   ```
   Command: cd /home/YOUR_USERNAME/crypto_notifier && python3.9 main.py state.txt
   Hour: 00  (runs at midnight)
   Minute: 00
   ```

Or for continuous running, use **Always-on task** (paid feature).

---

## ⚠️ Important Considerations

### Free Tier Limitations

| Feature | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Always-on tasks | ❌ No | ✅ Yes |
| Scheduled tasks | ✅ Yes (daily) | ✅ Yes (any interval) |
| Console time | 100 seconds | Unlimited |
| Disk space | 512 MB | More |
| Internet access | Limited sites | All sites |

### Workarounds for Free Tier

**Problem:** Can't run 24/7  
**Solution:** Schedule to run hourly/daily, each run collects data for analysis

**Problem:** Limited console time  
**Solution:** Run as scheduled task instead of manually

**Problem:** Only 1 always-on task  
**Solution:** Run ETH and BTC sequentially or choose one

---

## 🎯 Recommended Setup for FREE Tier

### Option 1: Hourly Collection (Recommended)

Create `run_hourly.py`:
```python
#!/usr/bin/env python3
import subprocess
import time

# Run ETH tracker for 60 iterations (~1 hour)
subprocess.run(['python3.9', 'main.py', 'state.txt'])
```

Schedule to run **every hour**.

### Option 2: Daily Deep Analysis

Run once per day, collect all historical data, analyze, send signals.

Modify config to:
```yaml
check_interval_sec: 300  # 5 minutes
historical_data:
  enabled: true
  fetch_interval_hours: 1
```

---

## 🚀 Alternative: GitHub Actions (FREE, 24/7)

If you want TRUE 24/7 free hosting:

1. **Push to GitHub**
2. **Create workflow**: `.github/workflows/crypto.yml`
   ```yaml
   name: Crypto Tracker
   
   on:
     schedule:
       - cron: '*/5 * * * *'  # Every 5 minutes
   
   jobs:
     track:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-python@v2
           with:
             python-version: '3.9'
         - run: pip install -r requirements.txt
         - run: python main.py state.txt
   ```

3. **Add secrets**: Telegram bot token, etc.

---

## 📱 Best Solution: VPS (Cheap)

If you want 24/7 for $5-10/month:

**DigitalOcean** ($6/month)
**Linode** ($5/month)
**Vultr** ($5/month)
**AWS Lightsail** ($3.50/month)

Setup:
```bash
# SSH into VPS
ssh root@your-server-ip

# Install Python
apt update
apt install python3 python3-pip

# Upload files
scp -r crypto_notifier root@your-server-ip:/root/

# Install deps
cd /root/crypto_notifier
pip3 install -r requirements.txt

# Run with screen (keeps running after disconnect)
screen -S eth
python3 main.py state.txt
# Press Ctrl+A then D to detach

screen -S btc
python3 main.py state_btc.txt
# Press Ctrl+A then D to detach
```

---

## 🎯 My Recommendation

### For Testing (FREE)
Use **PythonAnywhere** with scheduled tasks (hourly)

### For Production (Best)
Use **$5/month VPS** for true 24/7 operation

### For Zero Cost
Use **GitHub Actions** with cron schedules

---

## 📝 Quick Start: PythonAnywhere NOW

1. **Sign up**: https://www.pythonanywhere.com
2. **Upload files** via Files tab
3. **Install packages**: `pip3.9 install --user pyyaml requests`
4. **Test**: `python3.9 main.py state.txt`
5. **Schedule**: Create hourly task in Tasks tab

Done! Your bot runs in the cloud! ☁️

---

## ✨ Summary

| Method | Cost | 24/7 | Difficulty | Best For |
|--------|------|------|------------|----------|
| PythonAnywhere | FREE | ❌ | Easy | Testing |
| GitHub Actions | FREE | ✅ | Medium | Automation |
| VPS (Digital Ocean) | $5-10/mo | ✅ | Medium | Production |
| Your PC | FREE | ⚠️ | Easy | Development |

Choose based on your needs! Want me to help with any specific deployment?
