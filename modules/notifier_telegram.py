"""
Telegram bot notifier for crypto trading alerts.
Sends formatted trading signals directly to your Telegram.
Shows confidence levels and decision scenarios.
"""

import requests
import json
from datetime import datetime
from .confidence_levels import get_confidence_level, format_confidence_display

TELEGRAM_API_URL = "https://api.telegram.org/bot"


def send_telegram_message(bot_token, chat_id, message, parse_mode="HTML"):
    """
    Send a message to Telegram.
    
    Args:
        bot_token: Telegram bot token from BotFather
        chat_id: Your Telegram chat ID (where messages go)
        message: Message text (supports HTML formatting)
        parse_mode: "HTML" or "Markdown"
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not bot_token or not chat_id:
        print("[ERROR] Telegram credentials missing - configure in config.yaml")
        return False
    
    try:
        url = f"{TELEGRAM_API_URL}{bot_token}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            print(f"[ERROR] Telegram send failed: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"[ERROR] Telegram connection error: {e}")
        return False


def format_buy_signal(price, amount_hkd, asset, cost_basis, loss_pct, 
                      rsi=None, support=None, reason="", conviction=0):
    """
    Format a BUY signal for Telegram with confidence level and decision table.
    
    Returns: Formatted message string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    conf = get_confidence_level(conviction)
    
    message = f"""🟢 <b>BUY SIGNAL - {asset.upper()}</b>
━━━━━━━━━━━━━━━━━━━━━━━

<b>CONFIDENCE: {conf['emoji']} {conviction}% - {conf['level']}</b>
{conf['description']}

<b>Price:</b> {price:,.0f} HKD
<b>Suggested Amount:</b> {amount_hkd:,.0f} HKD
<b>Action:</b> Average down

<b>Your Portfolio Status:</b>
• Current loss: {loss_pct:.1f}%
• Cost basis: {cost_basis:,.0f} HKD"""
    
    if rsi:
        message += f"\n• RSI: {rsi} (oversold)"
    
    if support:
        dist = ((price - support) / support) * 100
        message += f"\n• Support level: {support:,.0f} HKD ({dist:+.1f}%)"
    
    message += f"""

<b>What Does This Confidence Mean?</b>
{conf['recommendation']}

<b>Your Options:</b>
🔴 Skip - Wait for 80%+ confidence
🟠 Micro - Gamble with small amount
🟡 Small - Conservative entry
🟢 <u>NORMAL - Suggested amount above</u>
🟢 Large - More aggressive averaging

Choose based on your risk comfort.
<i>Your decision = {timestamp}</i>"""
    
    return message


def format_sell_signal(price, amount_crypto, asset, cost_basis, profit_pct,
                       rsi=None, resistance=None, reason="", conviction=0):
    """
    Format a SELL signal for Telegram with confidence level and decision table.
    
    Returns: Formatted message string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    conf = get_confidence_level(conviction)
    
    message = f"""🔴 <b>SELL SIGNAL - {asset.upper()}</b>
━━━━━━━━━━━━━━━━━━━━━━━

<b>CONFIDENCE: {conf['emoji']} {conviction}% - {conf['level']}</b>
{conf['description']}

<b>Price:</b> {price:,.0f} HKD
<b>Amount to Sell:</b> {amount_crypto:.6f} {asset.upper()}
<b>Action:</b> Take profit

<b>Your Profit/Loss:</b>
• <b>Profit: {profit_pct:+.2f}%</b>
• Expected proceeds: {(price * amount_crypto):,.0f} HKD
• Cost basis: {cost_basis:,.0f} HKD"""
    
    if rsi:
        message += f"\n• RSI: {rsi} (overbought)"
    
    if resistance:
        dist = ((price - resistance) / resistance) * 100
        message += f"\n• Resistance level: {resistance:,.0f} HKD ({dist:+.1f}%)"
    
    message += f"""

<b>What Does This Confidence Mean?</b>
{conf['recommendation']}

<b>Your Options:</b>
🔴 Hold - Wait for 80%+ confidence
🟠 Partial - Sell small amount
🟡 Half - Sell half position
🟢 <u>FULL - Sell all {amount_crypto:.6f} as suggested</u>

Choose based on your profit-taking strategy.
<i>Your decision = {timestamp}</i>"""
    
    return message


def format_hold_signal(price, asset, moving_avg, reason=""):
    """
    Format a HOLD status for Telegram (optional, less frequent).
    
    Returns: Formatted message string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    pct_diff = ((price - moving_avg) / moving_avg) * 100
    
    message = f"""⏸️ <b>HOLD - {asset.upper()}</b>
━━━━━━━━━━━━━━━━━━━━━━━
<b>Price:</b> {price:,.0f} HKD
<b>MA:</b> {moving_avg:,.0f} HKD
<b>Diff:</b> {pct_diff:+.2f}%

<b>Status:</b> {reason}

<i>{timestamp}</i>"""
    
    return message


def format_alert(alert_type, data):
    """
    Generic alert formatter.
    
    Args:
        alert_type: 'BUY', 'SELL', 'HOLD', 'ERROR'
        data: dict with alert details
    
    Returns:
        Formatted message string
    """
    if alert_type == 'BUY':
        return format_buy_signal(
            price=data.get('price', 0),
            amount_hkd=data.get('amount_hkd', 0),
            asset=data.get('asset', 'ETH'),
            cost_basis=data.get('cost_basis', 0),
            loss_pct=data.get('loss_pct', 0),
            rsi=data.get('rsi'),
            support=data.get('support'),
            reason=data.get('reason', ''),
            conviction=data.get('conviction', 0)
        )
    
    elif alert_type == 'SELL':
        return format_sell_signal(
            price=data.get('price', 0),
            amount_crypto=data.get('amount_crypto', 0),
            asset=data.get('asset', 'ETH'),
            cost_basis=data.get('cost_basis', 0),
            profit_pct=data.get('profit_pct', 0),
            rsi=data.get('rsi'),
            resistance=data.get('resistance'),
            reason=data.get('reason', ''),
            conviction=data.get('conviction', 0)
        )
    
    elif alert_type == 'HOLD':
        return format_hold_signal(
            price=data.get('price', 0),
            asset=data.get('asset', 'ETH'),
            moving_avg=data.get('moving_avg', 0),
            reason=data.get('reason', '')
        )
    
    else:
        return f"<b>⚠️ {alert_type}</b>\n{data.get('message', 'No details')}"


if __name__ == "__main__":
    # Test the formatter
    print("Testing Telegram message formatter...")
    
    buy_data = {
        'price': 21400,
        'amount_hkd': 3500,
        'asset': 'ETH',
        'cost_basis': 30743,
        'loss_pct': -30.4,
        'rsi': 28,
        'support': 20500,
        'reason': 'Smart BUY | Conviction: 78/100 | Oversold with support nearby',
        'conviction': 78
    }
    
    message = format_alert('BUY', buy_data)
    print(message)
    print("\n" + "="*50 + "\n")
    
    sell_data = {
        'price': 32000,
        'amount_crypto': 0.46669,
        'asset': 'ETH',
        'cost_basis': 30743,
        'profit_pct': 4.1,
        'rsi': 72,
        'resistance': 32500,
        'reason': 'Profit taking at resistance',
        'conviction': 65
    }
    
    message = format_alert('SELL', sell_data)
    print(message)
