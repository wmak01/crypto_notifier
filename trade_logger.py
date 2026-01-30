import json
import os
from datetime import datetime

def get_trade_history_file(asset):
    """Get trade history filename based on asset"""
    return f"trade_history_{asset.lower()}.json"

def load_trade_history(asset):
    """Load trade history for specific asset"""
    filename = get_trade_history_file(asset)
    if not os.path.exists(filename):
        return []
    try:
        with open(filename) as f:
            return json.load(f)
    except:
        return []

def save_trade_history(asset, trades):
    """Save trade history for specific asset"""
    filename = get_trade_history_file(asset)
    with open(filename, "w") as f:
        json.dump(trades, f, indent=2)

def log_trade(asset, trade_type, price, amount_hkd=None, amount_crypto=None, cost_basis=None, trigger_pct=None, reason=""):
    """
    Log a trade signal with P/L calculation
    
    Args:
        asset: ETH or BTC
        trade_type: BUY or SELL
        price: Current price in HKD
        amount_hkd: Amount in HKD (for buys)
        amount_crypto: Amount in crypto (for sells)
        cost_basis: Average cost basis
        trigger_pct: Trigger percentage
        reason: Reason for trade
    """
    trades = load_trade_history(asset)
    
    # Calculate P/L for sells
    pnl_hkd = None
    pnl_pct = None
    if trade_type == "SELL" and cost_basis:
        pnl_pct = ((price - cost_basis) / cost_basis) * 100
        if amount_crypto:
            pnl_hkd = (price - cost_basis) * amount_crypto
    
    trade = {
        "timestamp": datetime.now().isoformat(),
        "type": trade_type,
        "price": price,
        "cost_basis": cost_basis,
        "trigger_pct": trigger_pct,
        "reason": reason
    }
    
    if amount_hkd:
        trade["amount_hkd"] = amount_hkd
    if amount_crypto:
        trade["amount_crypto"] = amount_crypto
    if pnl_hkd is not None:
        trade["pnl_hkd"] = round(pnl_hkd, 2)
    if pnl_pct is not None:
        trade["pnl_pct"] = round(pnl_pct, 2)
    
    trades.append(trade)
    save_trade_history(asset, trades)
    
    return trade

def get_trade_stats(asset):
    """Get trading statistics for an asset"""
    trades = load_trade_history(asset)
    
    if not trades:
        return {
            "total_trades": 0,
            "total_pnl": 0,
            "win_rate": 0,
            "avg_pnl": 0
        }
    
    total_trades = len(trades)
    sells = [t for t in trades if t["type"] == "SELL" and "pnl_hkd" in t]
    
    if not sells:
        return {
            "total_trades": total_trades,
            "total_pnl": 0,
            "win_rate": 0,
            "avg_pnl": 0
        }
    
    total_pnl = sum(t["pnl_hkd"] for t in sells)
    wins = len([t for t in sells if t["pnl_hkd"] > 0])
    win_rate = (wins / len(sells)) * 100 if sells else 0
    avg_pnl = total_pnl / len(sells) if sells else 0
    
    return {
        "total_trades": total_trades,
        "total_sells": len(sells),
        "total_pnl": round(total_pnl, 2),
        "win_rate": round(win_rate, 1),
        "avg_pnl": round(avg_pnl, 2)
    }
