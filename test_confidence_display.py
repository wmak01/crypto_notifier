#!/usr/bin/env python3
"""
Test confidence level display to show you how different conviction scores
translate to human-readable confidence levels and decision scenarios.
"""

from confidence_levels import (
    get_confidence_level,
    format_confidence_display,
    generate_confidence_range_scenarios
)


def print_confidence_table():
    """Display the full confidence level table."""
    print("\n" + "="*80)
    print("CONFIDENCE LEVEL REFERENCE TABLE")
    print("="*80)
    
    test_scores = [5, 15, 25, 35, 45, 55, 65, 75, 85, 95]
    
    print(f"\n{'Score':<8} {'Level':<25} {'Emoji':<8} {'Description':<40}")
    print("-" * 80)
    
    for score in test_scores:
        conf = get_confidence_level(score)
        print(f"{score:<8} {conf['level']:<25} {conf['emoji']:<8} {conf['description']:<40}")
    
    print("\n" + "="*80)


def show_buy_scenarios():
    """Show what different conviction levels mean for BUY decisions."""
    print("\n" + "="*80)
    print("BUY SIGNAL DECISION SCENARIOS")
    print("="*80)
    
    scenarios = {
        15: ("Very risky signal", "SKIP - Wait for better setup"),
        35: ("Uncertain signal", "Micro position ($200-500) if you want to gamble"),
        55: ("Reasonable signal", "Small position ($1000-2000) conservative approach"),
        75: ("Strong signal", "Normal position ($3000-5000) suggested amount"),
        95: ("Excellent signal", "Large position ($5000+) aggressive averaging")
    }
    
    print("\nYour ETH position: 0.46669 ETH (down -30.4%)")
    print("Available cash: 19,000 HKD")
    print("Current price: 21,400 HKD\n")
    
    for conviction, (meaning, action) in scenarios.items():
        conf = get_confidence_level(conviction)
        print(f"\n{conf['emoji']} {conviction}% Confidence - {conf['level']}")
        print(f"   What it means: {meaning}")
        print(f"   ➜ {action}")


def show_sell_scenarios():
    """Show what different conviction levels mean for SELL decisions."""
    print("\n" + "="*80)
    print("SELL SIGNAL DECISION SCENARIOS")
    print("="*80)
    
    scenarios = {
        20: ("Very uncertain profit", "SKIP - Keep holding, wait for higher conviction"),
        40: ("Weak profit signal", "Partial sell (25% of position) - cautious"),
        60: ("Okay profit signal", "Half sell (50% of position) - balanced"),
        75: ("Good profit signal", "Full sell (100% of position) - confident"),
        90: ("Excellent profit signal", "Full sell + consider buying back on dip")
    }
    
    print("\nYour ETH if price reaches 32,000 HKD (4.1% profit):")
    print("Position: 0.46669 ETH")
    print("Profit: ~1,904 HKD\n")
    
    for conviction, (meaning, action) in scenarios.items():
        conf = get_confidence_level(conviction)
        print(f"\n{conf['emoji']} {conviction}% Confidence - {conf['level']}")
        print(f"   What it means: {meaning}")
        print(f"   ➜ {action}")


def show_range_table():
    """Show side-by-side comparison of all conviction levels."""
    print("\n" + "="*80)
    print("CONVICTION DECISION REFERENCE CARD")
    print("="*80)
    
    levels = [
        (20, "🔴 AVOID", "Skip - Risk too high"),
        (30, "🟠 GAMBLE", "Micro if risky"),
        (40, "🟠 LOW", "Small position"),
        (50, "🟡 MEDIUM-LOW", "Conservative"),
        (60, "🟡 MEDIUM", "Normal position"),
        (70, "🟢 HIGH", "Larger position"),
        (80, "🟢 VERY HIGH", "Maximum position"),
        (100, "🟢 CERTAIN", "All-in confidence")
    ]
    
    print("\n<BUY CONFIDENCE GUIDE>")
    print("-" * 80)
    for score, emoji_level, recommendation in levels:
        conf = get_confidence_level(score)
        print(f"{score:>3}% | {emoji_level:<20} | {recommendation}")
    
    print("\n<HOLD PATTERN>")
    print("-" * 80)
    print("0-20%  : Skip entirely - not ready")
    print("20-40% : Micro gambling - risky")
    print("40-60% : Small/conservative - safe entry")
    print("60-80% : Normal/standard - typical trade")
    print("80%+   : Large/aggressive - high conviction")


def show_current_example():
    """Show a real example with current portfolio."""
    print("\n" + "="*80)
    print("YOUR CURRENT PORTFOLIO EXAMPLE")
    print("="*80)
    
    print("\n📊 Current Status:")
    print("   • ETH Price: 21,400 HKD")
    print("   • Cost Basis: 30,743 HKD")
    print("   • Loss: -30.4%")
    print("   • Holdings: 0.46669 ETH")
    print("   • Available Cash: 19,000 HKD")
    
    print("\n" + "-"*80)
    print("🔍 Signal arrives with 65% Confidence (MEDIUM):")
    
    conf = get_confidence_level(65)
    print(f"\n{conf['emoji']} {conf['percentage']} - {conf['level']}")
    print(f"   {conf['description']}")
    print(f"   {conf['recommendation']}")
    
    buy_amount_eth = 0.88  # Rough estimate based on position sizing
    buy_amount_hkd = buy_amount_eth * 21400
    new_cost_basis = (30743 * 0.46669 + buy_amount_hkd) / (0.46669 + buy_amount_eth)
    
    print(f"\n💰 If you BUY at {conf['level'].lower()}:")
    print(f"   • Standard buy amount: ~{buy_amount_hkd:,.0f} HKD")
    print(f"   • This gets you: ~{buy_amount_eth:.4f} ETH")
    print(f"   • New cost basis: ~{new_cost_basis:,.0f} HKD (down from 30,743)")
    print(f"   • New average loss: ~{((21400 - new_cost_basis) / new_cost_basis * 100):.1f}%")
    
    print(f"\n🎯 Your Choice:")
    print(f"   [SKIP] If you want 80%+ confidence")
    print(f"   [BUY MICRO] $500 if gambling {buy_amount_hkd * 0.15:,.0f} HKD")
    print(f"   [BUY SMALL] $1,500 conservative {buy_amount_hkd * 0.50:,.0f} HKD")
    print(f"   [BUY NORMAL] ${buy_amount_hkd:,.0f} as suggested")
    print(f"   [BUY LARGE] $5,000+ aggressive {buy_amount_hkd * 1.50:,.0f} HKD")


if __name__ == "__main__":
    print("\n🤖 CONFIDENCE LEVEL DEMONSTRATION")
    print("Shows how conviction % translates to readable confidence levels\n")
    
    print_confidence_table()
    show_range_table()
    show_current_example()
    show_buy_scenarios()
    show_sell_scenarios()
    
    print("\n" + "="*80)
    print("END OF CONFIDENCE LEVEL REFERENCE")
    print("="*80 + "\n")
