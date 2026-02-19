"""
Historical price analyzer for crypto assets.
Fetches 30/60/90 day data from CoinGecko and analyzes trends, support/resistance levels.
"""

import json
import os
from datetime import datetime, timedelta
import requests

# CoinGecko API endpoint for historical data
COINGECKO_API = "https://api.coingecko.com/api/v3"

def fetch_historical_data(crypto_id, days=90, cache_file=None):
    """
    Fetch historical price data from CoinGecko.
    
    Args:
        crypto_id: 'ethereum' or 'bitcoin'
        days: 1, 7, 30, 90, 365 (CoinGecko limits)
        cache_file: JSON file to cache data locally
    
    Returns:
        dict with 'prices', 'volumes', 'market_caps' or None if error
    """
    if cache_file and os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                # Check if cache is fresh (within 6 hours)
                cache_time = datetime.fromisoformat(cached.get('_cached_at', '1970-01-01'))
                if (datetime.now() - cache_time).total_seconds() < 21600:  # 6 hours
                    return cached['data']
        except (json.JSONDecodeError, KeyError):
            pass
    
    try:
        url = f"{COINGECKO_API}/coins/{crypto_id}/market_chart"
        params = {
            'vs_currency': 'hkd',
            'days': days,
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Cache the data
        if cache_file:
            cache_data = {
                'data': data,
                '_cached_at': datetime.now().isoformat()
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        
        return data
    
    except Exception as e:
        print(f"[ERROR] Failed to fetch historical data: {e}")
        return None


def analyze_support_resistance(prices):
    """
    Find support and resistance levels from price data.
    
    Args:
        prices: List of [timestamp, price] pairs
    
    Returns:
        dict with 'support', 'resistance', 'pivot'
    """
    if not prices or len(prices) < 5:
        return {'support': None, 'resistance': None, 'pivot': None}
    
    # Extract just the price values
    price_values = [p[1] for p in prices]
    
    # Recent high/low (last 30 data points)
    recent_high = max(price_values[-30:])
    recent_low = min(price_values[-30:])
    
    # Historical high/low (all data)
    hist_high = max(price_values)
    hist_low = min(price_values)
    
    # Pivot point = (high + low + close) / 3
    current_price = price_values[-1]
    pivot = (recent_high + recent_low + current_price) / 3
    
    # Support = lower recent low + buffer
    support = recent_low * 0.98  # 2% buffer below recent low
    
    # Resistance = upper recent high + buffer
    resistance = recent_high * 1.02  # 2% buffer above recent high
    
    return {
        'support': support,
        'resistance': resistance,
        'pivot': pivot,
        'recent_high': recent_high,
        'recent_low': recent_low,
        'hist_high': hist_high,
        'hist_low': hist_low,
        'current_price': current_price
    }


def detect_trend(prices):
    """
    Detect if price is in uptrend or downtrend.
    Uses "higher lows" (uptrend) vs "lower lows" (downtrend).
    
    Args:
        prices: List of [timestamp, price] pairs
    
    Returns:
        dict with 'trend', 'strength', 'lower_lows_count', 'higher_lows_count'
    """
    if not prices or len(prices) < 10:
        return {'trend': 'insufficient_data', 'strength': 0, 'lower_lows_count': 0, 'higher_lows_count': 0}
    
    price_values = [p[1] for p in prices]
    
    # Find local lows (troughs)
    lows = []
    for i in range(1, len(price_values) - 1):
        if price_values[i] < price_values[i-1] and price_values[i] < price_values[i+1]:
            lows.append(price_values[i])
    
    if len(lows) < 3:
        return {'trend': 'insufficient_data', 'strength': 0, 'lower_lows_count': 0, 'higher_lows_count': 0}
    
    # Count higher lows vs lower lows
    higher_lows = 0
    lower_lows = 0
    
    for i in range(1, len(lows)):
        if lows[i] > lows[i-1]:
            higher_lows += 1
        else:
            lower_lows += 1
    
    total = higher_lows + lower_lows
    strength = (higher_lows - lower_lows) / total if total > 0 else 0
    
    if strength > 0.3:
        trend = 'uptrend'
    elif strength < -0.3:
        trend = 'downtrend'
    else:
        trend = 'sideways'
    
    return {
        'trend': trend,
        'strength': strength,
        'higher_lows_count': higher_lows,
        'lower_lows_count': lower_lows
    }


def analyze_volume(volumes):
    """
    Analyze volume patterns to detect capitulation or distribution.
    
    Args:
        volumes: List of [timestamp, volume] pairs
    
    Returns:
        dict with 'avg_volume', 'current_volume', 'spike_factor', 'volume_signal'
    """
    if not volumes or len(volumes) < 5:
        return {'avg_volume': 0, 'current_volume': 0, 'spike_factor': 1.0, 'volume_signal': 'insufficient_data'}
    
    volume_values = [v[1] for v in volumes]
    
    # Average of past 20 days (excluding today)
    avg_volume = sum(volume_values[-21:-1]) / 20 if len(volume_values) > 20 else sum(volume_values) / len(volume_values)
    current_volume = volume_values[-1]
    
    spike_factor = current_volume / avg_volume if avg_volume > 0 else 1.0
    
    # High volume spike = possible capitulation (on down days) or breakout (on up days)
    if spike_factor > 1.8:
        volume_signal = 'extreme_spike'
    elif spike_factor > 1.3:
        volume_signal = 'high_spike'
    elif spike_factor > 0.7:
        volume_signal = 'normal'
    else:
        volume_signal = 'low_volume'
    
    return {
        'avg_volume': avg_volume,
        'current_volume': current_volume,
        'spike_factor': round(spike_factor, 2),
        'volume_signal': volume_signal
    }


def calculate_volatility(prices):
    """
    Calculate price volatility (standard deviation of % changes).
    
    Args:
        prices: List of [timestamp, price] pairs
    
    Returns:
        dict with '7day_vol', '30day_vol', 'current_vol_level'
    """
    if not prices or len(prices) < 5:
        return {'7day_vol': 0, '30day_vol': 0, 'current_vol_level': 'insufficient_data'}
    
    price_values = [p[1] for p in prices]
    
    # Calculate daily % changes
    pct_changes = []
    for i in range(1, len(price_values)):
        pct_change = ((price_values[i] - price_values[i-1]) / price_values[i-1]) * 100
        pct_changes.append(abs(pct_change))  # Use absolute values for volatility
    
    # 7-day and 30-day rolling volatility
    vol_7 = sum(pct_changes[-7:]) / 7 if len(pct_changes) >= 7 else sum(pct_changes) / len(pct_changes)
    vol_30 = sum(pct_changes[-30:]) / 30 if len(pct_changes) >= 30 else sum(pct_changes) / len(pct_changes)
    
    # Current day volatility
    current_vol = pct_changes[-1] if pct_changes else 0
    
    # Volatility level classification
    if vol_30 > 5.0:
        vol_level = 'extreme'
    elif vol_30 > 3.5:
        vol_level = 'high'
    elif vol_30 > 2.0:
        vol_level = 'moderate'
    else:
        vol_level = 'low'
    
    return {
        '7day_vol': round(vol_7, 2),
        '30day_vol': round(vol_30, 2),
        'current_vol': round(current_vol, 2),
        'vol_level': vol_level
    }


def get_price_percentile(current_price, prices):
    """
    Calculate where current price ranks in historical range (0-100).
    
    Args:
        current_price: Current price
        prices: List of [timestamp, price] pairs
    
    Returns:
        int: Percentile (0 = cheapest, 100 = most expensive)
    """
    if not prices or len(prices) < 2:
        return 50
    
    price_values = [p[1] for p in prices]
    min_price = min(price_values)
    max_price = max(price_values)
    
    if max_price == min_price:
        return 50
    
    percentile = ((current_price - min_price) / (max_price - min_price)) * 100
    return max(0, min(100, int(percentile)))


def analyze_price_action(prices):
    """
    Comprehensive price action analysis combining all metrics.
    
    Args:
        prices: List of [timestamp, price] pairs
    
    Returns:
        dict with all analyses combined
    """
    if not prices or len(prices) < 5:
        return None
    
    support_res = analyze_support_resistance(prices)
    trend = detect_trend(prices)
    volatility = calculate_volatility(prices)
    current_price = prices[-1][1]
    percentile = get_price_percentile(current_price, prices)
    
    # Calculate distance from support as percentage
    if support_res['support']:
        dist_to_support = ((current_price - support_res['support']) / support_res['support']) * 100
    else:
        dist_to_support = None
    
    return {
        'support_resistance': support_res,
        'trend': trend,
        'volatility': volatility,
        'percentile': percentile,
        'distance_to_support_pct': dist_to_support,
        'analyzed_at': datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Test the analyzer
    print("Testing historical analyzer...")
    data = fetch_historical_data('ethereum', days=30, cache_file='test_cache.json')
    
    if data:
        prices = data.get('prices', [])
        volumes = data.get('volumes', [])
        
        print(f"\nFetched {len(prices)} price points")
        
        analysis = analyze_price_action(prices)
        print(json.dumps(analysis, indent=2))
