def calculate_vwap(data):
    required_columns = ['Volume', 'High', 'Low', 'Close']
    if not set(required_columns).issubset(set(data.columns)):
        raise ValueError(
            "Input DataFrame must contain 'Volume', 'High', 'Low', and 'Close' columns.")

    relevant_data = data[['Volume', 'High', 'Low', 'Close']]

    relevant_data['Typical Price'] = (
        relevant_data['High'] + relevant_data['Low'] + relevant_data['Close']) / 3

    relevant_data['Volume * Typical Price'] = relevant_data['Volume'] * \
        relevant_data['Typical Price']

    relevant_data['Cumulative Volume * Typical Price'] = relevant_data['Volume * Typical Price'].cumsum()
    relevant_data['Cumulative Volume'] = relevant_data['Volume'].cumsum()

    # Calculate VWAP
    relevant_data['VWAP'] = relevant_data['Cumulative Volume * Typical Price'] / \
        relevant_data['Cumulative Volume']

    return relevant_data[['VWAP']]
