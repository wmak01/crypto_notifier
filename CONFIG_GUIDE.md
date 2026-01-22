# Configuration Guide

## Ping Interval (Check Frequency)

Edit `config.yaml` to change how often the program checks the price:

```yaml
check_interval_sec: 60  # Change this value
```

### Recommended Values

| Interval | Calls/Min | Risk Level | Best For |
|----------|-----------|-----------|----------|
| **60 seconds** | 1 | ✅ Very Safe | Conservative trading, low network load |
| **30 seconds** | 2 | ✅ Safe | Balanced monitoring |
| **15 seconds** | 4 | ✅ Safe | Active trading, quick signals |
| **10 seconds** | 6 | ⚠️ Caution | Risky, close to limits |
| **<5 seconds** | 12+ | ❌ Dangerous | Will hit rate limits |

## CoinGecko API Limits

**Free Tier:**
- Rate limit: ~10-50 calls per minute (varies)
- No authentication required
- **NO PREMIUM FEES** - completely free
- Sufficient for most users with intervals ≥10 seconds

**When You Might Hit Limits:**
- Checking every second (60 calls/min)
- Multiple concurrent instances
- Running multiple different assets in parallel

## Moving Average Strategy

The program now automatically calculates a **100-price moving average** as your reference price.

**Timeline:**
- If checking every 60 seconds: ~100 minutes of data (≈1.67 hours)
- If checking every 30 seconds: ~50 minutes of data
- If checking every 15 seconds: ~25 minutes of data

**No More Manual Updates Needed!**
- ✅ LAST_REFERENCE_PRICE will auto-update
- ✅ Remove manual reference price updates
- ✅ Only update balance & cash after executing trades

## File Structure

```
prices_history.json      # Auto-maintained price history with timestamps
state.txt                # Your current portfolio state (update after trading)
config.yaml              # Edit check_interval_sec here
pending.json             # Tracks if waiting for manual trade execution
```

## Changing Interval Examples

```yaml
# Conservative (1 check per minute)
check_interval_sec: 60

# Balanced (1 check every 30 seconds)
check_interval_sec: 30

# Active (1 check every 15 seconds)
check_interval_sec: 15

# Very Active (1 check every 10 seconds)
check_interval_sec: 10
```

⚠️ **Not Recommended:** Below 5 seconds risks API rate limiting.
