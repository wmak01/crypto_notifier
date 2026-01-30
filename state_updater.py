"""Helper functions to update state file"""

def update_state_field(state_file, field, value):
    """Update a single field in state file"""
    lines = []
    updated = False
    
    with open(state_file, 'r') as f:
        lines = f.readlines()
    
    # Update or add the field
    for i, line in enumerate(lines):
        if line.startswith(f"{field}="):
            lines[i] = f"{field}={value}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"{field}={value}\n")
    
    with open(state_file, 'w') as f:
        f.writelines(lines)

def update_cost_basis_after_buy(state_file, current_balance, current_cost_basis, buy_amount_hkd, buy_price):
    """
    Calculate new weighted average cost basis after a buy
    
    Args:
        state_file: Path to state file
        current_balance: Current crypto balance (before buy)
        current_cost_basis: Current average cost basis
        buy_amount_hkd: HKD amount spent on buy
        buy_price: Price per unit at which bought
    
    Returns:
        New cost basis
    """
    # Calculate how much crypto was bought
    buy_amount_crypto = buy_amount_hkd / buy_price
    
    # Calculate new weighted average
    old_value = current_balance * current_cost_basis
    new_value = buy_amount_hkd
    total_value = old_value + new_value
    
    new_balance = current_balance + buy_amount_crypto
    new_cost_basis = total_value / new_balance if new_balance > 0 else current_cost_basis
    
    # Update state file
    update_state_field(state_file, "COST_BASIS", round(new_cost_basis, 2))
    update_state_field(state_file, "CURRENT_BALANCE", round(new_balance, 8))
    
    return new_cost_basis, new_balance

def update_balance_after_sell(state_file, current_balance, sell_amount_crypto):
    """
    Update balance after a sell (cost basis stays same for remaining holdings)
    
    Args:
        state_file: Path to state file
        current_balance: Current crypto balance
        sell_amount_crypto: Amount of crypto sold
    
    Returns:
        New balance
    """
    new_balance = current_balance - sell_amount_crypto
    update_state_field(state_file, "CURRENT_BALANCE", round(new_balance, 8))
    
    return new_balance

def calculate_days_to_breakeven(current_price, cost_basis, avg_daily_change_pct):
    """
    Estimate days until breakeven based on average daily price change
    
    Args:
        current_price: Current price
        cost_basis: Cost basis (0.5% profit target = cost_basis * 1.005)
        avg_daily_change_pct: Average daily % change (can be from MA trend)
    
    Returns:
        Estimated days (None if already profitable or moving wrong direction)
    """
    target_price = cost_basis * 1.005  # Need 0.5% profit
    
    if current_price >= target_price:
        return 0  # Already at target
    
    if avg_daily_change_pct <= 0:
        return None  # Price declining, no breakeven
    
    pct_needed = ((target_price - current_price) / current_price) * 100
    days = pct_needed / avg_daily_change_pct
    
    return max(0, round(days))
