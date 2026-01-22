def evaluate(price, ref_price, balance, cash, config):
    decisions = []

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
