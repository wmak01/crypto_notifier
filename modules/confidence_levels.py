"""
Confidence level mapping - converts numerical confidence (0-100) to human-readable descriptions.
Helps traders understand signal strength and choose appropriate action levels.
"""


def get_confidence_level(conviction_score):
    """
    Convert conviction score (0-100) to readable confidence level.
    
    Args:
        conviction_score: Numerical score from 0-100
        
    Returns:
        dict with 'level', 'emoji', 'description', 'recommendation'
    """
    score = max(0, min(100, conviction_score))  # Clamp 0-100
    
    if score < 15:
        return {
            'level': 'Very Low Confidence',
            'emoji': '⚫',
            'percentage': f'{score}%',
            'description': 'Highly uncertain - wait for better setup',
            'recommendation': 'SKIP - Too risky, wait for higher conviction',
            'color': '🔴'
        }
    elif score < 30:
        return {
            'level': 'Low Confidence',
            'emoji': '🟠',
            'percentage': f'{score}%',
            'description': 'Not sure - use micro position only',
            'recommendation': 'MICRO - Only if you want to gamble',
            'color': '🟠'
        }
    elif score < 50:
        return {
            'level': 'Medium-Low Confidence',
            'emoji': '🟡',
            'percentage': f'{score}%',
            'description': 'Somewhat uncertain - small position',
            'recommendation': 'SMALL - Conservative entry',
            'color': '🟡'
        }
    elif score < 65:
        return {
            'level': 'Medium Confidence',
            'emoji': '🟡',
            'percentage': f'{score}%',
            'description': 'Reasonable signal - normal position',
            'recommendation': 'NORMAL - Standard position size',
            'color': '🟡'
        }
    elif score < 80:
        return {
            'level': 'High Confidence',
            'emoji': '🟢',
            'percentage': f'{score}%',
            'description': 'Strong signal - go for it',
            'recommendation': 'LARGE - Increase position size',
            'color': '🟢'
        }
    else:
        return {
            'level': 'Very High Confidence',
            'emoji': '🟢',
            'percentage': f'{score}%',
            'description': 'Very strong signal - excellent setup',
            'recommendation': 'MAXIMUM - Full confidence entry',
            'color': '🟢'
        }


def format_confidence_display(conviction_score):
    """
    Format confidence for easy reading in messages.
    
    Returns: Formatted string like "72% - High Confidence - Strong signal"
    """
    conf = get_confidence_level(conviction_score)
    return f"{conf['emoji']} <b>{conf['percentage']}</b> - {conf['level']}\n{conf['description']}"


def generate_confidence_range_scenarios(conviction_thresholds=None):
    """
    Generate scenarios showing what signal would be at different conviction levels.
    
    Args:
        conviction_thresholds: List of scores to evaluate. 
                              Defaults to [20, 40, 60, 80, 100]
    
    Returns:
        dict mapping each threshold to its confidence info
    """
    if conviction_thresholds is None:
        conviction_thresholds = [20, 40, 60, 80, 100]
    
    scenarios = {}
    for score in conviction_thresholds:
        scenarios[score] = get_confidence_level(score)
    
    return scenarios


def format_decision_table(asset, signal_type, conviction_score):
    """
    Format a table showing possible actions at different conviction levels.
    
    Args:
        asset: 'ETH' or 'BTC'
        signal_type: 'BUY' or 'SELL'
        conviction_score: Current conviction percentage
    
    Returns:
        Formatted message showing decision table
    """
    scenarios = generate_confidence_range_scenarios([20, 40, 60, 80, 100])
    
    message = f"""
<b>📊 DECISION GUIDE - {asset.upper()} {signal_type}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current confidence: <b>{conviction_score}%</b>

<b>Choose your risk level:</b>
"""
    
    for score in [20, 40, 60, 80, 100]:
        conf = scenarios[score]
        is_current = "✅ CURRENT" if abs(score - conviction_score) < 5 else ""
        message += f"\n{conf['emoji']} <b>{score}%</b> {conf['level']}\n   → {conf['recommendation']} {is_current}"
    
    message += f"\n\n<b>Your choice:</b>"
    return message


def format_confidence_explanation(signal_type, conviction_score, technical_factors):
    """
    Format detailed explanation with confidence level and what it means.
    
    Args:
        signal_type: 'BUY', 'SELL', or 'HOLD'
        conviction_score: 0-100
        technical_factors: dict with 'ma_distance', 'rsi', 'support', 'trend', etc.
    
    Returns:
        Formatted message with confidence info
    """
    conf = get_confidence_level(conviction_score)
    
    message = f"""
<b>🎯 {signal_type} SIGNAL - {conf['level']}</b>
{conf['emoji']} <b>Confidence: {conf['percentage']}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{conf['description']}

<b>What does this mean?</b>
{conf['recommendation']}

<b>Technical Factors:</b>"""
    
    if technical_factors:
        for factor, value in technical_factors.items():
            message += f"\n• {factor}: {value}"
    
    message += f"""

<b>Next Step:</b>
If you agree with this {conf['level'].lower()} signal, proceed.
If you want to wait for higher conviction (80%+), skip and monitor.
"""
    
    return message
