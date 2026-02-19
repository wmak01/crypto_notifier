"""
Signal state tracker - prevents spam by only alerting on meaningful changes.
Tracks previous signals and only sends Telegram when:
1. Signal type changes (HOLD → BUY, BUY → SELL, etc.)
2. Signal parameters change significantly (conviction, price level, etc.)
"""

import json
import os
from datetime import datetime
from confidence_levels import (
    get_confidence_level, 
    format_confidence_display,
    format_decision_table,
    format_confidence_explanation
)


class SignalStateTracker:
    """Tracks signal state to prevent message spam."""
    
    def __init__(self, state_file):
        """
        Initialize tracker.
        
        Args:
            state_file: Path to state file (e.g., 'state.txt' or 'state_btc.txt')
        """
        self.state_file = state_file
        self.tracker_file = state_file.replace('.txt', '_signal_state.json')
        self.load_state()
    
    def load_state(self):
        """Load previous signal state."""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r') as f:
                    self.state = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.state = self._init_state()
        else:
            self.state = self._init_state()
    
    def _init_state(self):
        """Initialize empty state."""
        return {
            'last_signal': None,  # 'BUY', 'SELL', 'HOLD'
            'last_signal_time': None,
            'last_conviction': 0,
            'last_price': None,
            'last_explanation': None,
            'consecutive_same_signals': 0,
            'signal_history': []  # Last 10 signals
        }
    
    def save_state(self):
        """Save current state."""
        with open(self.tracker_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def should_send_alert(self, new_signal, new_conviction=0, new_price=None, new_explanation=""):
        """
        Determine if we should send a Telegram alert.
        
        Args:
            new_signal: 'BUY', 'SELL', 'HOLD'
            new_conviction: Conviction score (0-100)
            new_price: Current price
            new_explanation: Reason for signal
        
        Returns:
            (should_send: bool, reason: str, is_state_change: bool)
        """
        last_signal = self.state['last_signal']
        last_conviction = self.state['last_conviction']
        
        # First signal ever
        if last_signal is None:
            return (False, "First signal - wait for confidence", False)
        
        # Signal type changed (BUY→SELL, HOLD→BUY, etc) - ALWAYS ALERT
        if new_signal != last_signal:
            return (True, f"Signal change: {last_signal} → {new_signal}", True)
        
        # Same signal but conviction changed significantly (±15 points)
        if abs(new_conviction - last_conviction) >= 15:
            return (True, f"Conviction shifted: {last_conviction} → {new_conviction}", False)
        
        # Same HOLD signal - don't spam (only alert on change away from HOLD)
        if new_signal == 'HOLD' and last_signal == 'HOLD':
            return (False, "Still HOLDing - no message needed", False)
        
        # Same BUY/SELL but price moved significantly (±3%)
        if new_price and self.state['last_price']:
            price_change_pct = abs((new_price - self.state['last_price']) / self.state['last_price']) * 100
            if price_change_pct >= 3:
                return (True, f"Price moved {price_change_pct:.1f}% - alert user", False)
        
        # Explanation changed significantly (new reasoning)
        if new_explanation != self.state['last_explanation']:
            return (False, "Explanation updated but same signal", False)
        
        # Same signal, similar conviction, similar price - don't spam
        return (False, f"No meaningful change (same {new_signal})", False)
    
    def update_state(self, signal, conviction=0, price=None, explanation=""):
        """
        Update signal state after sending alert.
        
        Args:
            signal: 'BUY', 'SELL', 'HOLD'
            conviction: Conviction score (0-100)
            price: Current price
            explanation: Reason for signal
        """
        # Check if this is the same signal as before
        if signal == self.state['last_signal']:
            self.state['consecutive_same_signals'] += 1
        else:
            self.state['consecutive_same_signals'] = 1
        
        # Update state
        self.state['last_signal'] = signal
        self.state['last_signal_time'] = datetime.now().isoformat()
        self.state['last_conviction'] = conviction
        self.state['last_price'] = price
        self.state['last_explanation'] = explanation
        
        # Add to history (keep last 10)
        self.state['signal_history'].append({
            'signal': signal,
            'conviction': conviction,
            'price': price,
            'time': self.state['last_signal_time'],
            'explanation': explanation
        })
        self.state['signal_history'] = self.state['signal_history'][-10:]
        
        self.save_state()
    
    def get_signal_summary(self):
        """Get summary of signal state."""
        return {
            'current_signal': self.state['last_signal'],
            'conviction': self.state['last_conviction'],
            'consecutive_same': self.state['consecutive_same_signals'],
            'last_time': self.state['last_signal_time'],
            'history_count': len(self.state['signal_history'])
        }


def format_detailed_explanation(signal_type, price, cost_basis, balance, cash, 
                               moving_avg, rsi, support, resistance, volatility,
                               trend, percentile, conviction=0, reason="", asset='ETH'):
    """
    Generate a detailed, human-readable explanation of a signal with confidence levels.
    Shows decision table with multiple conviction scenarios.
    
    Returns: Formatted explanation string
    """
    
    conf = get_confidence_level(conviction)
    
    if signal_type == 'HOLD':
        explanation = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 HOLD SIGNAL - Neutral Zone
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Current Price:</b> {price:,.0f} HKD
<b>Moving Average:</b> {moving_avg:,.0f} HKD

<b>WHY HOLD:</b>
Price is within ±5% of MA (neutral zone)
No clear directional signal yet.

If you're already holding:
→ Continue to hold, wait for clarity
→ Price needs to move significantly to trigger action

<b>Technical Context:</b>
• RSI: {rsi or 'N/A'} (not extreme)
• Volatility: {volatility} (stable)
• Trend: {trend}

NO ACTION NEEDED - Monitor for changes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    elif signal_type == 'BUY':
        loss_pct = ((price - cost_basis) / cost_basis * 100) if cost_basis else 0
        dist_to_support = ((price - support) / support * 100) if support else 0
        
        explanation = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 BUY SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>CONFIDENCE LEVEL:</b>
{format_confidence_display(conviction)}

<b>Current Price:</b> {price:,.0f} HKD
<b>Cost Basis:</b> {cost_basis:,.0f} HKD
<b>Current Loss:</b> {loss_pct:.1f}%

<b>WHY BUY NOW:</b>
✓ Price dropped significantly below MA
✓ Price near support level ({support:,.0f})
✓ RSI indicates oversold ({rsi})
✓ Volatility acceptable ({volatility})
✓ Trend shows stabilization ({trend})
✓ Price at {percentile}th percentile (cheap)

<b>This is a tactical AVERAGE DOWN opportunity.</b>

<b>Decision Table - Choose Your Risk Level:</b>

🔴 20% Conviction → Skip, too risky
🟠 40% Conviction → Micro position (gamble)
🟡 60% Conviction → Small position (conservative)
🟢 80% Conviction → Large position (confident)
🟢 100% Conviction → Maximum position (very sure)

<b>Your Current Conviction:</b> {conviction}% ({conf['level']})
{conf['recommendation']}

Action:
→ If you agree, proceed with BUY
→ If you want higher conviction (80%+), skip and wait
→ Monitor closely for next 1-2 hours

Risk Level: MODERATE (averaging down in downtrend)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    elif signal_type == 'SELL':
        profit_pct = ((price - cost_basis) / cost_basis * 100) if cost_basis else 0
        dist_to_resist = ((price - resistance) / resistance * 100) if resistance else 0
        
        explanation = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 SELL SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>CONFIDENCE LEVEL:</b>
{format_confidence_display(conviction)}

<b>Current Price:</b> {price:,.0f} HKD
<b>Cost Basis:</b> {cost_basis:,.0f} HKD
<b>Profit:</b> {profit_pct:+.2f}%

<b>WHY SELL NOW:</b>
✓ Price reached profit target
✓ Price near resistance ({resistance:,.0f})
✓ RSI in overbought zone ({rsi})
✓ Volume signal suggests consolidation
✓ Trend showing signs of reversal ({trend})

<b>This is profit-taking - locking in {profit_pct:.1f}%</b>

<b>Decision Table - Choose Your Risk Level:</b>

🔴 20% Conviction → Skip, hold longer
🟠 40% Conviction → Partial sell (cautious)
🟡 60% Conviction → Half position (balanced)
🟢 80% Conviction → Full sell (confident)
🟢 100% Conviction → Maximum sell (very sure)

<b>Your Current Conviction:</b> {conviction}% ({conf['level']})
{conf['recommendation']}

Expected Proceeds:
→ Sell {balance:.4f} tokens
→ Receive ~{(price * balance):,.0f} HKD
→ Profit: {(price * balance - cost_basis * balance):+,.0f} HKD

Action:
→ If you agree, proceed with SELL
→ If you want higher conviction (80%+), skip and wait
→ Re-deploy capital on next dip

Risk Level: LOW (taking profits)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    else:
        explanation = f"Signal: {signal_type}\nPrice: {price:,.0f} HKD"
    
    return explanation.strip()


if __name__ == "__main__":
    # Test the tracker
    print("Testing signal state tracker...")
    
    tracker = SignalStateTracker('test_state.txt')
    
    # Simulate signals
    should_send, reason, is_change = tracker.should_send_alert('BUY', 75, 21400)
    print(f"Signal 1 (BUY): Send={should_send}, Reason={reason}")
    
    tracker.update_state('BUY', 75, 21400)
    
    # Same signal, similar conviction - don't send
    should_send, reason, is_change = tracker.should_send_alert('BUY', 76, 21450)
    print(f"Signal 2 (BUY): Send={should_send}, Reason={reason}")
    
    # Signal changes to SELL - send!
    should_send, reason, is_change = tracker.should_send_alert('SELL', 65, 32000)
    print(f"Signal 3 (SELL): Send={should_send}, Reason={reason}")
    
    print("\nExplanation example:")
    print(format_detailed_explanation('BUY', 21400, 30743, 0.46669, 3500, 21680, 28, 20500, 23200, 'moderate', 'uptrend', 35, 78))
