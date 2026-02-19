"""
Pattern recognition and advanced signal generation.
Detects trading patterns, divergences, and risk factors.
"""

import json
from datetime import datetime, timedelta


def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI) for overbought/oversold detection.
    
    Args:
        prices: List of prices
        period: RSI period (14 standard)
    
    Returns:
        float: RSI value 0-100
    """
    if not prices or len(prices) < period + 1:
        return None
    
    price_list = [p[1] if isinstance(p, list) else p for p in prices]
    
    # Calculate deltas
    deltas = []
    for i in range(1, len(price_list)):
        deltas.append(price_list[i] - price_list[i-1])
    
    # Separate gains and losses
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [abs(d) if d < 0 else 0 for d in deltas]
    
    # Average gain and loss
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def detect_capitulation(prices, volumes, price_drop_pct=5.0):
    """
    Detect capitulation events (panic selling with high volume).
    
    Args:
        prices: List of [timestamp, price] pairs
        volumes: List of [timestamp, volume] pairs
        price_drop_pct: Minimum price drop to consider
    
    Returns:
        dict with capitulation probability and severity
    """
    if not prices or not volumes or len(prices) < 5:
        return {'is_capitulation': False, 'probability': 0, 'severity': 0}
    
    price_values = [p[1] for p in prices]
    volume_values = [v[1] for v in volumes]
    
    # Check if today's price is down significantly
    pct_change = ((price_values[-1] - price_values[-2]) / price_values[-2]) * 100
    
    if pct_change > -price_drop_pct:
        return {'is_capitulation': False, 'probability': 0, 'severity': 0}
    
    # Check volume
    avg_volume = sum(volume_values[-20:-1]) / 19 if len(volume_values) > 20 else sum(volume_values) / len(volume_values)
    current_volume = volume_values[-1]
    volume_spike = current_volume / avg_volume if avg_volume > 0 else 1.0
    
    # Capitulation signals
    signals = 0
    max_signals = 4
    
    if pct_change < -price_drop_pct:
        signals += 1
    
    if volume_spike > 1.5:
        signals += 1
    
    if volume_spike > 2.0:
        signals += 1
    
    # Price hitting new lows
    recent_low = min(price_values[-10:])
    if price_values[-1] <= recent_low * 0.99:
        signals += 1
    
    probability = (signals / max_signals) * 100
    severity = min(100, (abs(pct_change) / 5.0) * 100)  # Normalized to 5% drop = 100
    
    return {
        'is_capitulation': probability > 60,
        'probability': round(probability, 1),
        'severity': round(severity, 1),
        'signals_detected': signals
    }


def detect_breakout(prices, resistance_level, confirmation_volume_multiplier=1.5):
    """
    Detect if price is breaking out above resistance with volume.
    
    Args:
        prices: List of [timestamp, price] pairs
        resistance_level: Resistance price level
        confirmation_volume_multiplier: Volume must be this much above average
    
    Returns:
        dict with breakout probability and direction
    """
    if not prices or len(prices) < 5:
        return {'breakout_detected': False, 'probability': 0, 'direction': None}
    
    price_values = [p[1] for p in prices]
    current_price = price_values[-1]
    
    # Check if price is above resistance
    if current_price <= resistance_level * 1.002:  # Within 0.2% buffer
        return {'breakout_detected': False, 'probability': 0, 'direction': None}
    
    # Check momentum (last 3 days trending up)
    recent_trend = price_values[-3:] if len(price_values) >= 3 else price_values
    is_trending_up = recent_trend[-1] > recent_trend[0]
    
    probability = 50 if is_trending_up else 30
    
    return {
        'breakout_detected': probability > 50,
        'probability': probability,
        'direction': 'upward',
        'pct_above_resistance': round(((current_price - resistance_level) / resistance_level) * 100, 2)
    }


def analyze_price_convergence_divergence(prices, short_period=12, long_period=26):
    """
    Calculate MACD-like convergence/divergence for trend signals.
    
    Args:
        prices: List of prices
        short_period: Fast EMA period
        long_period: Slow EMA period
    
    Returns:
        dict with MACD signal
    """
    if not prices or len(prices) < long_period:
        return {'macd': None, 'signal_line': None, 'histogram': None, 'signal': 'insufficient_data'}
    
    price_list = [p[1] if isinstance(p, list) else p for p in prices]
    
    # Simplified EMA calculation
    def ema(data, period):
        if len(data) < period:
            return sum(data) / len(data)
        multiplier = 2 / (period + 1)
        ema_val = sum(data[:period]) / period
        for price in data[period:]:
            ema_val = price * multiplier + ema_val * (1 - multiplier)
        return ema_val
    
    short_ema = ema(price_list, short_period)
    long_ema = ema(price_list, long_period)
    
    macd = short_ema - long_ema
    signal_line = macd  # Simplified
    histogram = macd - signal_line
    
    signal = 'bullish' if histogram > 0 else 'bearish'
    
    return {
        'macd': round(macd, 2),
        'signal_line': round(signal_line, 2),
        'histogram': round(histogram, 2),
        'signal': signal
    }


def generate_buy_conviction_score(price, cost_basis, current_rsi, volatility_level, 
                                  is_near_support, trend_direction, volume_signal, 
                                  percentile, macd_signal):
    """
    Generate a comprehensive buy conviction score (0-100%).
    
    Args:
        price: Current price
        cost_basis: Your cost basis
        current_rsi: Current RSI value
        volatility_level: 'low', 'moderate', 'high', 'extreme'
        is_near_support: Boolean, is price within 3% of support?
        trend_direction: 'uptrend', 'downtrend', 'sideways'
        volume_signal: 'extreme_spike', 'high_spike', 'normal', 'low_volume'
        percentile: Price percentile (0-100, lower = cheaper)
        macd_signal: 'bullish' or 'bearish'
    
    Returns:
        int: Conviction score 0-100
    """
    score = 0
    
    # Price relative to cost basis (10 points max)
    loss_pct = abs(((price - cost_basis) / cost_basis) * 100)
    if loss_pct > 30:
        score += 10  # Deep dip
    elif loss_pct > 20:
        score += 8
    elif loss_pct > 10:
        score += 5
    elif loss_pct > 5:
        score += 2
    
    # RSI oversold signal (25 points max)
    if current_rsi and current_rsi < 25:
        score += 25  # Severely oversold
    elif current_rsi and current_rsi < 30:
        score += 20
    elif current_rsi and current_rsi < 35:
        score += 10
    elif current_rsi and current_rsi < 40:
        score += 5
    
    # Support level proximity (20 points max)
    if is_near_support:
        score += 20
    
    # Trend analysis (15 points max)
    if trend_direction == 'uptrend':
        score += 15
    elif trend_direction == 'sideways':
        score += 8
    # downtrend gets 0
    
    # Volume signal (15 points max)
    if volume_signal == 'extreme_spike':
        score += 15  # Capitulation signal
    elif volume_signal == 'high_spike':
        score += 10
    elif volume_signal == 'normal':
        score += 5
    # low_volume gets 0
    
    # Price percentile (10 points max - lower is better)
    if percentile < 20:
        score += 10
    elif percentile < 30:
        score += 8
    elif percentile < 40:
        score += 5
    
    # MACD signal (5 points max)
    if macd_signal == 'bullish':
        score += 5
    
    # Cap score at 100
    return min(100, max(0, score))


def generate_sell_signal_with_explanation(current_price, cost_basis, peak_price,
                                         current_rsi, days_held, is_trend_change,
                                         near_resistance, volume_signal):
    """
    Generate sell signal with full explanation.
    
    Args:
        current_price: Current price
        cost_basis: What you paid
        peak_price: Peak since entry
        current_rsi: Current RSI
        days_held: How long position held
        is_trend_change: Boolean, did trend reverse?
        near_resistance: Boolean, near resistance?
        volume_signal: Volume quality
    
    Returns:
        dict with sell recommendation and reasoning
    """
    profit_pct = ((current_price - cost_basis) / cost_basis) * 100
    from_peak_pct = ((current_price - peak_price) / peak_price) * 100
    
    reasons = []
    sell_score = 0
    
    # Profit taking at good levels
    if profit_pct >= 5 and profit_pct <= 15:
        sell_score += 20
        reasons.append(f"Solid profit: +{profit_pct:.1f}% (safe exit zone)")
    
    # RSI overbought
    if current_rsi and current_rsi > 70:
        sell_score += 25
        reasons.append(f"Overbought: RSI {current_rsi}")
    
    # Price retreating from peak
    if from_peak_pct < -5:
        sell_score += 20
        reasons.append(f"Retracing: {from_peak_pct:.1f}% from peak")
    
    # Trend reversal
    if is_trend_change:
        sell_score += 30
        reasons.append("Trend reversal detected")
    
    # At resistance
    if near_resistance and profit_pct > 2:
        sell_score += 15
        reasons.append("At resistance with profit")
    
    # Weak volume
    if volume_signal == 'low_volume':
        sell_score += 10
        reasons.append("Weak volume on move up (suspicious)")
    
    recommendation = 'STRONG_SELL' if sell_score >= 80 else \
                   'SELL' if sell_score >= 60 else \
                   'HOLD' if sell_score >= 40 else \
                   'HOLD_OR_ADD'
    
    return {
        'recommendation': recommendation,
        'sell_score': sell_score,
        'profit_pct': round(profit_pct, 2),
        'from_peak_pct': round(from_peak_pct, 2),
        'reasons': reasons
    }


if __name__ == "__main__":
    # Test pattern analyzer
    print("Testing pattern analyzer...")
    
    # Test RSI
    prices = [100, 101, 102, 103, 104, 103, 102, 101, 102, 103, 104, 105, 104, 103, 102]
    rsi = calculate_rsi(prices, period=14)
    print(f"RSI: {rsi}")
    
    # Test buy conviction
    score = generate_buy_conviction_score(
        price=20800,
        cost_basis=30743,
        current_rsi=28,
        volatility_level='moderate',
        is_near_support=True,
        trend_direction='uptrend',
        volume_signal='high_spike',
        percentile=35,
        macd_signal='bullish'
    )
    print(f"Buy Conviction Score: {score}/100")
