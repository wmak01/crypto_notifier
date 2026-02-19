"""
PRACTICAL GUIDE: What You'll Actually See on Telegram

This shows real examples of how the confidence level system works
with YOUR exact portfolio numbers and current market prices.
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    YOUR TELEGRAM WILL NOW SHOW THIS                        ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

# Real Portfolio Data
portfolio = {
    'eth_price_current': 21400,
    'eth_holdings': 0.46669,
    'eth_cost_basis': 30743,
    'eth_loss_pct': -30.4,
    'cash_available': 19000,
    'btc_holdings': 0.00480371,
}

print(f"""
YOUR PORTFOLIO RIGHT NOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ETH: {portfolio['eth_holdings']:.5f} ETH @ {portfolio['eth_price_current']:,} HKD = {portfolio['eth_loss_pct']:.1f}% loss
Cost basis: {portfolio['eth_cost_basis']:,} HKD
Available cash: {portfolio['cash_available']:,} HKD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("\n" + "="*80)
print("SCENARIO 1: Low Confidence BUY Signal (35%)")
print("="*80)

print("""
🟢 BUY SIGNAL - ETH
━━━━━━━━━━━━━━━━━━━━━━━

CONFIDENCE: 🟡 35% - Medium-Low Confidence
Somewhat uncertain - small position

Price: 21,400 HKD
Suggested Amount: 500 HKD
Action: Average down

Your Portfolio Status:
• Current loss: -30.4%
• Cost basis: 30,743 HKD
• RSI: 32 (oversold but not extreme)
• Support level: 21,200 HKD (only 0.9% below current)

What Does This Confidence Mean?
"Somewhat uncertain - small position"
SMALL - Conservative entry

Your Options:
🔴 Skip - Wait for higher confidence (you have time)
🟠 Micro - Gamble with $500 (risky, but could work)
🟡 Small - Conservative $1,000 (safer)
🟢 Normal - Standard $3,000
🟢 Large - More aggressive $5,000

← YOUR SITUATION:
You're down 30%, so:
  • SKIP if you want confirmation
  • MICRO if you want to test
  • SMALL if you want to average down safely

YOUR DECISION: ____________________
(Text back your choice to confirm)
""")

print("\n" + "="*80)
print("SCENARIO 2: Medium Confidence BUY Signal (62%)")
print("="*80)

print("""
🟢 BUY SIGNAL - ETH
━━━━━━━━━━━━━━━━━━━━━━━

CONFIDENCE: 🟡 62% - Medium Confidence
Reasonable signal - normal position

Price: 20,800 HKD (price dropped 2.9%)
Suggested Amount: 3,000 HKD
Action: Average down

Your Portfolio Status:
• Current loss at this price: -32.4%
• RSI: 28 (oversold - good for buying)
• Support level: 20,200 HKD (already below current price)
• Trend: Stabilizing (higher lows forming)

What Does This Confidence Mean?
"Reasonable signal - normal position"
NORMAL - Standard position size

Your Options:
🔴 Skip - Wait for higher confidence
🟠 Micro - $500 (conservative approach)
🟡 Small - $1,000 (safety first)
🟢 Normal - $3,000 ← Suggested
🟢 Large - $5,000 (aggressive)

← YOUR SITUATION:
You're deeper in loss (-32%), signal is medium confidence:
  • SMALL if scared of averaging down more
  • NORMAL if comfortable with averaging strategy
  • LARGE if you believe in the dip

YOUR DECISION: ____________________
(Text back your choice to confirm)
""")

print("\n" + "="*80)
print("SCENARIO 3: High Confidence BUY Signal (76%)")
print("="*80)

print("""
🟢 BUY SIGNAL - ETH
━━━━━━━━━━━━━━━━━━━━━━━

CONFIDENCE: 🟢 76% - High Confidence
Strong signal - go for it

Price: 19,500 HKD (price dropped 8.9% from current)
Suggested Amount: 4,500 HKD
Action: Average down

Your Portfolio Status:
• Current loss at this price: -36.6%
• RSI: 18 (VERY oversold - capitulation signal)
• Volume spike detected (panic selling)
• Support level: 19,200 HKD (just below price)
• Trend: Reversal signals starting (bottom forming)

What Does This Confidence Mean?
"Strong signal - go for it"
LARGE - Increase position size

Your Options:
🔴 Skip - No reason to skip, this is good
🟠 Micro - $500 (too small for this signal)
🟡 Small - $1,500 (conservative but okay)
🟢 Normal - $3,000 (safe)
🟢 Large - $4,500 ← Suggested (confident)

← YOUR SITUATION:
76% confidence, price down 37%, volume spike, oversold:
  • This is a STRONG buying opportunity
  • LARGE or NORMAL are both good
  • You can even go LARGER if you believe
  • This is the moment you've been waiting for

YOUR DECISION: ____________________
(Text back your choice to confirm)
""")

print("\n" + "="*80)
print("SCENARIO 4: SELL Signal - Low Confidence (38%)")
print("="*80)

print("""
🔴 SELL SIGNAL - ETH
━━━━━━━━━━━━━━━━━━━━━━━

CONFIDENCE: 🟠 38% - Medium-Low Confidence
Somewhat uncertain - small position

Price: 32,000 HKD (price up 49.8% from 21,400)
Amount to Sell: 0.46669 ETH
Profit: +4.1%

Your Profit/Loss:
• Profit: +1,904 HKD
• Expected proceeds: 14,934 HKD
• Cost basis was: 30,743 HKD
• RSI: 62 (getting warm, not overbought)
• Resistance: 32,500 HKD (only 1.6% above current)

What Does This Confidence Mean?
"Somewhat uncertain - small position"
SMALL - Conservative entry (into sell)

Your Options:
🔴 Hold - Wait for higher confidence (better strategy)
🟠 Partial - Sell 25% only ($116 profit locked)
🟡 Half - Sell 50% ($952 profit locked)
🟢 Full - Sell all 100% ($1,904 profit locked)

← YOUR SITUATION:
Only 38% confident, small profit, price close to resistance:
  • HOLD if you want higher profit
  • PARTIAL if you want to lock some gains
  • Not recommended to FULL SELL at this confidence

YOUR DECISION: ____________________
(Text back your choice to confirm)
""")

print("\n" + "="*80)
print("SCENARIO 5: SELL Signal - High Confidence (77%)")
print("="*80)

print("""
🔴 SELL SIGNAL - ETH
━━━━━━━━━━━━━━━━━━━━━━━

CONFIDENCE: 🟢 77% - High Confidence
Strong signal - go for it

Price: 34,500 HKD (price up 61.2% from 21,400)
Amount to Sell: 0.46669 ETH
Profit: +12.1%

Your Profit/Loss:
• Profit: +5,080 HKD
• Expected proceeds: 16,091 HKD
• Cost basis was: 30,743 HKD
• RSI: 78 (OVERBOUGHT - top signal)
• Resistance: 35,000 HKD (1.5% above current)
• Divergence: Price high but volume declining

What Does This Confidence Mean?
"Strong signal - go for it"
LARGE - Increase position size (take big profit)

Your Options:
🔴 Hold - Don't sell, but signal is strong
🟠 Partial - Sell 25% ($1,270 profit)
🟡 Half - Sell 50% ($2,540 profit)
🟢 Full - Sell all 100% ← Suggested ($5,080 profit)

← YOUR SITUATION:
77% confident, 12% profit, overbought, reversed cost basis:
  • This is EXCELLENT profit-taking opportunity
  • FULL SELL makes sense to lock in 12% gain
  • You'll have $16,091 HKD back (85% more than started)
  • Can re-buy on next dip

YOUR DECISION: ____________________
(Text back your choice to confirm)
""")

print("\n" + "="*80)
print("KEY TAKEAWAYS FOR YOU")
print("="*80)

print("""
1. BUYING (Averaging Down):
   • Low confidence (35%): Skip or micro only
   • Medium (62%): Small to normal
   • High (76%): Large (jump in!)
   • Deeper the loss, more you should buy (if confident)

2. SELLING (Taking Profit):
   • Low confidence (38%): Hold or partial only
   • Medium (62%): Half position
   • High (77%): Full sell (lock gains!)
   • Bigger the profit, more you should sell

3. YOUR OPTIONS ALWAYS:
   🔴 Conservative: Skip high-confidence, only act on 80%+
   🟠 Moderate: Act on 60%+ confidence signals
   🟢 Aggressive: Act on any signal you believe in

4. YOU'RE ALWAYS IN CONTROL:
   • The program suggests, you decide
   • No trades without your approval
   • See confidence level before acting
   • Can wait for higher confidence
   • Can gamble on low confidence

5. CONFIDENCE LEVELS MEAN:
   🟠 35% = Skip (too risky)
   🟡 62% = Normal (reasonable)
   🟢 76% = Large (strong signal)
   🟢 85%+ = Maximum (excellent)

Ready to use the system?
1. Get a signal on Telegram
2. See confidence level with emoji
3. Read the English description
4. Review your options
5. Reply with YOUR choice
6. That's it!

The power is in YOUR hands now. 💪
""")

print("="*80 + "\n")
