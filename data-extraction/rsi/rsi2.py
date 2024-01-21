def calc_rsi(data):
    # difference between two consecutive Adj Close
    dif = data['Adj Close'].diff(1)
    dif.dropna(inplace=True)  # Replace NAN values

    positive = dif.copy()
    positive[positive < 0] = 0  # Positive values only
    negative = dif.copy()
    negative[negative > 0] = 0  # Negative values only

    days = 14

    avg_profit = positive.rolling(days).mean()
    avg_loss = abs(negative.rolling(days).mean())

    relative_strength = avg_profit / avg_loss

    RSI = 100.0 - (100.0 / (1.0 + relative_strength))

    data['RSI'] = RSI

    # print(data)
