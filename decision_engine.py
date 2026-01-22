def evaluate(price, ref_price, balance, cash, config):
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

    # SELL LOGIC
    for step in config["sell_steps"]:
        trigger_price = ref_price * (1 + step["trigger_pct"] / 100) * config["buffer"]["sell"]
        if price >= trigger_price:
            decisions.append({
                "type": "SELL",
                "amount_eth": round(balance * step["sell_pct"], 6),
                "trigger_pct": step["trigger_pct"],
                "price": round(price, 2)
            })

    # BUY LOGIC
    for step in config["buy_steps"]:
        trigger_price = ref_price * (1 + step["trigger_pct"] / 100) * config["buffer"]["buy"]
        if price <= trigger_price:
            decisions.append({
                "type": "BUY",
                "amount_hkd": round(cash * step["buy_pct"], 2),
                "trigger_pct": step["trigger_pct"],
                "price": round(price, 2)
            })

    return decisions

