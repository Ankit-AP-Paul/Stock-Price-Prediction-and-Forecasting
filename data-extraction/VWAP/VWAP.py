def calculate_vwap(data):
    
    total_price_volume = 0  # Sum of (price * volume)
    total_volume = 0  # Total trading volume

    for price, volume in data:
        total_price_volume += price * volume
        total_volume += volume

    if total_volume == 0:
        return None  # Avoid division by zero

    vwap = total_price_volume / total_volume
    return vwap
