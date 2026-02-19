from pattern_analyzer import (
    calculate_rsi, 
    generate_buy_conviction_score,
    generate_sell_signal_with_explanation
)


def evaluate(price, ref_price, balance, cash, config, cost_basis=None):
    """
    Evaluate trading signals using multi-factor analysis.
    New intelligent system that scores buy/sell decisions.
    """
    decisions = []
    
    # If reference price is not available yet, no trading signals
    if ref_price is None:
        return decisions

    # HOLD LOGIC - Check if price is in neutral band first
    hold_band = config.get("hold_band_pct", 5) / 100  # Convert to decimal (default ±5%)
    hold_lower = ref_price * (1 - hold_band)
    hold_upper = ref_price * (1 + hold_band)
    
    if hold_lower <= price <= hold_upper:
        decisions.append({
            "type": "HOLD",
            "reason": f"Price within ±{config.get('hold_band_pct', 5)}% neutral band",
            "price": round(price, 2)
        })
        return decisions  # Exit early, no buy/sell when in HOLD zone

    # SELL LOGIC - Intelligent profit taking
    if ref_price and price > ref_price:
        profit_pct = ((price - cost_basis) / cost_basis * 100) if cost_basis else 0
        min_profit = config.get('buy_strategy', {}).get('min_profit_threshold', 0.005)
        
        if cost_basis and price <= cost_basis * (1 + min_profit):
            # Not enough profit yet
            pass
        else:
            # Use traditional steps for legacy support
            for step in config.get("sell_steps", []):
                trigger_price = ref_price * (1 + step["trigger_pct"] / 100) * config.get("buffer", {}).get("sell", 1.015)
                
                if price >= trigger_price and balance > 0:
                    decisions.append({
                        "type": "SELL",
                        "amount_eth": round(balance * step["sell_pct"], 6),
                        "trigger_pct": step["trigger_pct"],
                        "price": round(price, 2),
                        "cost_basis": cost_basis,
                        "profit_pct": round(profit_pct, 2),
                        "reason": f"Profit taking: +{profit_pct:.1f}%"
                    })

    # BUY LOGIC - Intelligent buying based on conviction score
    if ref_price and price < ref_price:
        # For now, use traditional buy steps
        # In enhanced version with historical data, this will use conviction scoring
        for step in config.get("buy_steps", []):
            trigger_price = ref_price * (1 + step["trigger_pct"] / 100) * config.get("buffer", {}).get("buy", 0.985)
            
            if price <= trigger_price and cash > 0:
                loss_pct = ((price - cost_basis) / cost_basis * 100) if cost_basis else 0
                decisions.append({
                    "type": "BUY",
                    "amount_hkd": round(cash * step["buy_pct"], 2),
                    "trigger_pct": step["trigger_pct"],
                    "price": round(price, 2),
                    "loss_pct": round(loss_pct, 2),
                    "reason": f"Average down: {loss_pct:.1f}%"
                })

    return decisions

