#!/usr/bin/env python3
"""
Test how Telegram messages look with confidence levels.
Shows BUY and SELL signals with confidence display and decision options.
"""

from notifier_telegram import format_buy_signal, format_sell_signal


def display_telegram_message(title, message):
    """Display message with formatting."""
    print("\n" + "="*80)
    print(f"📱 TELEGRAM MESSAGE: {title}")
    print("="*80)
    print(message)
    print("="*80)


if __name__ == "__main__":
    print("\n🤖 TELEGRAM MESSAGE PREVIEW WITH CONFIDENCE LEVELS\n")
    
    # BUY Signal with 65% confidence
    buy_msg_65 = format_buy_signal(
        price=21400,
        amount_hkd=3000,
        asset='ETH',
        cost_basis=30743,
        loss_pct=-30.4,
        rsi=28,
        support=20500,
        conviction=65,
        reason="Oversold + support level + downtrend stabilization"
    )
    display_telegram_message("BUY at 65% Confidence (MEDIUM-HIGH)", buy_msg_65)
    
    # BUY Signal with 35% confidence (very uncertain)
    buy_msg_35 = format_buy_signal(
        price=21400,
        amount_hkd=500,
        asset='ETH',
        cost_basis=30743,
        loss_pct=-30.4,
        rsi=32,
        support=21200,
        conviction=35,
        reason="Slight oversold, weak support, uncertain trend"
    )
    display_telegram_message("BUY at 35% Confidence (LOW - GAMBLE)", buy_msg_35)
    
    # BUY Signal with 85% confidence (very certain)
    buy_msg_85 = format_buy_signal(
        price=21400,
        amount_hkd=5000,
        asset='ETH',
        cost_basis=30743,
        loss_pct=-30.4,
        rsi=20,
        support=20400,
        conviction=85,
        reason="Strong oversold + strong support + capitulation pattern + reversal setup"
    )
    display_telegram_message("BUY at 85% Confidence (VERY HIGH - STRONG)", buy_msg_85)
    
    # SELL Signal with 60% confidence (medium)
    sell_msg_60 = format_sell_signal(
        price=32000,
        amount_crypto=0.46669,
        asset='ETH',
        cost_basis=30743,
        profit_pct=4.1,
        rsi=68,
        resistance=32500,
        conviction=60,
        reason="Price at resistance, RSI elevated, moderate convergence signal"
    )
    display_telegram_message("SELL at 60% Confidence (MEDIUM)", sell_msg_60)
    
    # SELL Signal with 25% confidence (low - don't sell yet)
    sell_msg_25 = format_sell_signal(
        price=32000,
        amount_crypto=0.46669,
        asset='ETH',
        cost_basis=30743,
        profit_pct=4.1,
        rsi=58,
        resistance=32800,
        conviction=25,
        reason="Weak resistance, RSI near midpoint, uncertain trend"
    )
    display_telegram_message("SELL at 25% Confidence (LOW - HOLD LONGER)", sell_msg_25)
    
    # SELL Signal with 88% confidence (very high - strong profit)
    sell_msg_88 = format_sell_signal(
        price=34000,
        amount_crypto=0.46669,
        asset='ETH',
        cost_basis=30743,
        profit_pct=10.6,
        rsi=78,
        resistance=33500,
        conviction=88,
        reason="Strong overbought + clear resistance + reversal signals + 10% profit"
    )
    display_telegram_message("SELL at 88% Confidence (VERY HIGH - LOCK PROFIT)", sell_msg_88)
    
    print("\n💡 KEY DIFFERENCES:")
    print("-" * 80)
    print("• Low Confidence (35%): Suggests MICRO position or SKIP")
    print("• Medium Confidence (65%): Shows decision options, suggests NORMAL")
    print("• High Confidence (85%): Shows confidence level with recommendation")
    print("\nEach message now lets YOU choose:")
    print("  - Skip if you want higher confidence (80%+)")
    print("  - Micro if you want to gamble")
    print("  - Small/Normal/Large based on your risk appetite")
    print("\n✅ You're NOT forced into fixed positions anymore!")
    print("✅ You can see different conviction levels before deciding!")
    print("="*80 + "\n")
