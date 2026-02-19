"""
Trailing stop loss manager for dynamic profit taking.
Tracks peak profits and determines optimal exit points.
"""

import json
import os
from datetime import datetime


class TrailingStopManager:
    """Manages trailing stops for positions to lock in profits dynamically."""
    
    def __init__(self, state_file):
        """
        Initialize trailing stop manager.
        
        Args:
            state_file: Path to state file (e.g., 'state.txt' or 'state_btc.txt')
        """
        self.state_file = state_file
        self.trailing_stops_file = state_file.replace('.txt', '_trailing_stops.json')
        self.load_trailing_stops()
    
    def load_trailing_stops(self):
        """Load trailing stop data from file."""
        if os.path.exists(self.trailing_stops_file):
            try:
                with open(self.trailing_stops_file, 'r') as f:
                    self.stops = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.stops = self._init_stops()
        else:
            self.stops = self._init_stops()
    
    def _init_stops(self):
        """Initialize empty trailing stops."""
        return {
            'positions': {},
            'last_updated': None
        }
    
    def save_trailing_stops(self):
        """Save trailing stop data to file."""
        self.stops['last_updated'] = datetime.now().isoformat()
        with open(self.trailing_stops_file, 'w') as f:
            json.dump(self.stops, f, indent=2)
    
    def record_buy(self, cost_basis, amount):
        """
        Record a new buy position for trailing stop tracking.
        
        Args:
            cost_basis: Cost basis of the position
            amount: Amount of asset purchased
        """
        position_id = f"pos_{len(self.stops['positions']) + 1}"
        
        self.stops['positions'][position_id] = {
            'cost_basis': cost_basis,
            'amount': amount,
            'entry_time': datetime.now().isoformat(),
            'peak_price': cost_basis,
            'peak_time': datetime.now().isoformat(),
            'trailing_stop_price': cost_basis * 0.95,  # Initial 5% stop
            'status': 'active',
            'profit_locked': None
        }
        
        self.save_trailing_stops()
        return position_id
    
    def update_peak_and_stop(self, current_price, volatility_level='moderate'):
        """
        Update peak price and calculate trailing stop for all active positions.
        
        Args:
            current_price: Current market price
            volatility_level: 'low', 'moderate', 'high', 'extreme'
        
        Returns:
            dict with position updates and sell signals
        """
        # Trailing stop percentage based on volatility
        trailing_pct_map = {
            'low': 0.03,      # 3% trail in low volatility
            'moderate': 0.06,  # 6% trail in moderate volatility
            'high': 0.10,      # 10% trail in high volatility
            'extreme': 0.15    # 15% trail in extreme volatility (give it more room)
        }
        
        trailing_pct = trailing_pct_map.get(volatility_level, 0.06)
        
        signals = []
        
        for pos_id, position in self.stops['positions'].items():
            if position['status'] != 'active':
                continue
            
            # Update peak price if current is higher
            if current_price > position['peak_price']:
                position['peak_price'] = current_price
                position['peak_time'] = datetime.now().isoformat()
            
            # Calculate new trailing stop (from peak)
            new_stop = position['peak_price'] * (1 - trailing_pct)
            position['trailing_stop_price'] = max(
                new_stop,
                position['cost_basis']  # Never trail below cost basis (breakeven)
            )
            
            # Check if we hit the trailing stop
            profit_pct = ((current_price - position['cost_basis']) / position['cost_basis']) * 100
            
            if current_price <= position['trailing_stop_price'] and profit_pct > 0.5:
                # Trailing stop triggered
                position['status'] = 'trailing_stop_hit'
                position['profit_locked'] = profit_pct
                
                signals.append({
                    'action': 'sell_trailing_stop',
                    'position_id': pos_id,
                    'reason': f"Trailing stop hit. Peak was {position['peak_price']}, now {current_price}",
                    'profit_pct': profit_pct,
                    'profit_locked_at': current_price
                })
        
        self.save_trailing_stops()
        return signals
    
    def get_active_position_status(self):
        """
        Get status of all active positions.
        
        Returns:
            list of active positions with their trailing stop info
        """
        active = []
        
        for pos_id, position in self.stops['positions'].items():
            if position['status'] == 'active':
                active.append({
                    'position_id': pos_id,
                    'cost_basis': position['cost_basis'],
                    'peak_price': position['peak_price'],
                    'trailing_stop_price': position['trailing_stop_price'],
                    'entry_time': position['entry_time']
                })
        
        return active
    
    def close_position(self, position_id, exit_price, profit_pct):
        """
        Mark a position as closed.
        
        Args:
            position_id: ID of position to close
            exit_price: Price at which position was exited
            profit_pct: Profit percentage achieved
        """
        if position_id in self.stops['positions']:
            self.stops['positions'][position_id]['status'] = 'closed'
            self.stops['positions'][position_id]['exit_price'] = exit_price
            self.stops['positions'][position_id]['profit_locked'] = profit_pct
            self.save_trailing_stops()
    
    def get_position_profit_potential(self, current_price):
        """
        Calculate profit potential if we hold vs if we sell now with trailing stop.
        
        Args:
            current_price: Current market price
        
        Returns:
            dict with analysis
        """
        if not self.stops['positions']:
            return {'positions': [], 'avg_profit_if_sell_now': 0, 'avg_profit_at_peak': 0}
        
        positions_analysis = []
        total_profit_now = 0
        total_profit_potential = 0
        count = 0
        
        for pos_id, position in self.stops['positions'].items():
            if position['status'] != 'active':
                continue
            
            profit_now = ((current_price - position['cost_basis']) / position['cost_basis']) * 100
            profit_potential = ((position['peak_price'] - position['cost_basis']) / position['cost_basis']) * 100
            
            positions_analysis.append({
                'position_id': pos_id,
                'cost_basis': position['cost_basis'],
                'current_price': current_price,
                'peak_price': position['peak_price'],
                'profit_if_sell_now': profit_now,
                'profit_at_peak': profit_potential,
                'distance_from_peak': current_price - position['peak_price']
            })
            
            total_profit_now += profit_now
            total_profit_potential += profit_potential
            count += 1
        
        return {
            'positions': positions_analysis,
            'avg_profit_if_sell_now': round(total_profit_now / count, 2) if count > 0 else 0,
            'avg_profit_at_peak': round(total_profit_potential / count, 2) if count > 0 else 0
        }


def calculate_atr_trailing_stop(prices, atr_multiplier=2.0, atr_period=14):
    """
    Calculate trailing stop using ATR (Average True Range) - pro trader method.
    
    Args:
        prices: List of [timestamp, price] pairs (need OHLC ideally, but using close)
        atr_multiplier: Multiplier for ATR (1.5-2.0 typical)
        atr_period: Period for ATR calculation (14 common)
    
    Returns:
        float: Trailing stop price
    """
    if not prices or len(prices) < atr_period:
        return None
    
    price_values = [p[1] for p in prices]
    
    # Simple ATR calculation (using range approximation)
    true_ranges = []
    
    for i in range(1, len(price_values)):
        high = max(price_values[i-1], price_values[i])
        low = min(price_values[i-1], price_values[i])
        tr = high - low
        true_ranges.append(tr)
    
    # Average True Range
    atr = sum(true_ranges[-atr_period:]) / atr_period if len(true_ranges) >= atr_period else sum(true_ranges) / len(true_ranges)
    
    # Trailing stop = highest high - (ATR × multiplier)
    highest_high = max(price_values[-atr_period:])
    trailing_stop = highest_high - (atr * atr_multiplier)
    
    return trailing_stop


if __name__ == "__main__":
    # Test the trailing stop manager
    print("Testing trailing stop manager...")
    
    manager = TrailingStopManager('test_state.txt')
    
    # Simulate a buy
    pos_id = manager.record_buy(cost_basis=21000, amount=0.5)
    print(f"Recorded buy: {pos_id}")
    
    # Simulate price movements
    prices = [21000, 21500, 22000, 22500, 23000, 22800, 22500, 22000, 21800]
    
    for price in prices:
        signals = manager.update_peak_and_stop(price, volatility_level='moderate')
        if signals:
            print(f"Signal at price {price}: {signals}")
    
    # Check status
    status = manager.get_position_profit_potential(21800)
    print(f"\nPosition status: {json.dumps(status, indent=2)}")
