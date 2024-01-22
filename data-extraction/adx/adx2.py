import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None

# stock_data = pd.read_csv('data/ADANIGREEN.NS.csv')
high, low, close = 'High', 'Low', 'Close'


def calc_val(df, column, index):
    """
    Calculate current and previous values for a specific column at the given index.

    Parameters:
    - df: DataFrame
    - column: str, the column for which values are calculated
    - index: int, the index for which values are calculated

    Returns:
    - Tuple of (current_value, previous_value)
    """
    prev_val = df.loc[index-1, column]
    curr_val = df.loc[index, column]
    return curr_val, prev_val


def calc_dm(df, index):
    """
    Calculate directional movement (dm_pos and dm_neg) at the given index.

    Parameters:
    - df: DataFrame
    - index: int, the index for which directional movement is calculated

    Returns:
    - Tuple of (dm_pos, dm_neg)
    """
    curr_high, prev_high = calc_val(df, high, index)
    curr_low, prev_low = calc_val(df, low, index)
    dm_pos = curr_high - prev_high
    dm_neg = prev_low - curr_low

    if dm_pos > dm_neg:
        if dm_pos < 0:
            dm_pos = 0.00
        dm_neg = 0.00
        return dm_pos, dm_neg
    elif dm_pos < dm_neg:
        if dm_neg < 0:
            dm_neg = 0.00
        dm_pos = 0.00
        return dm_pos, dm_neg
    else:
        if dm_pos < 0:
            dm_pos = 0.00
        dm_neg = 0.00
        return dm_pos, dm_neg


def calc_tr(df, index):
    """
    Calculate true range (TR) at the given index.

    Parameters:
    - df: DataFrame
    - index: int, the index for which true range is calculated

    Returns:
    - float, the calculated true range
    """
    curr_high, prev_high = calc_val(df, high, index)
    curr_low, prev_low = calc_val(df, low, index)
    curr_close, prev_close = calc_val(df, close, index)

    ranges = [curr_high - curr_low,
              abs(curr_high - prev_close), abs(curr_low - prev_close)]
    tr = max(ranges)
    return tr


def calc_first_14(df, index, column):
    """
    Calculate the sum of values in the specified column for the first 14 days.

    Parameters:
    - df: DataFrame
    - index: int, the current index
    - column: str, the column for which values are summed

    Returns:
    - float, the sum of values for the first 14 days
    """
    result = 0
    for i in range(index-13, index+1):
        result += df.loc[i, column]
    return result


def calc_sub_14(df, index, column):
    """
    Calculate the subtraction for the 14th day for a specific column.

    Parameters:
    - df: DataFrame
    - index: int, the current index
    - column: str, the column for which subtraction is calculated

    Returns:
    - float, the calculated subtraction for the 14th day
    """
    return df.loc[index-1, column+'14'] - (df.loc[index-1, column+'14']/14) + df.loc[index, column]


def calc_first_adx(df, index):
    """
    Calculate the first ADX value for a specific index.

    Parameters:
    - df: DataFrame
    - index: int, the current index

    Returns:
    - float, the first ADX value
    """
    result = 0
    for i in range(index-13, index+1):
        result += df.loc[i, 'DX']
    return result/14


def calc_adx(df, index):
    """
    Calculate the ADX value for a specific index.

    Parameters:
    - df: DataFrame
    - index: int, the current index

    Returns:
    - float, the calculated ADX value
    """
    return ((df.loc[index-1, 'ADX']*13) + df.loc[index, 'DX'])/14


def func(stock_data):
    """
    Main function to calculate directional movement, true range, and ADX values.

    Parameters:
    - stock_data: DataFrame, input stock data

    Returns:
    - DataFrame, stock data with additional calculated columns
    """
    for i in range(1, len(stock_data)):
        dm_pos, dm_neg = calc_dm(stock_data, i)
        TR = calc_tr(stock_data, i)
        stock_data.loc[i, '+DM'] = dm_pos
        stock_data.loc[i, '-DM'] = dm_neg
        stock_data.loc[i, 'TR'] = TR

        if stock_data.TR.count() == 14:
            stock_data.loc[i, 'TR14'] = calc_first_14(stock_data, i, 'TR')
            stock_data.loc[i, '+DM14'] = calc_first_14(stock_data, i, '+DM')
            stock_data.loc[i, '-DM14'] = calc_first_14(stock_data, i, '-DM')

        elif stock_data.TR.count() >= 14:
            stock_data.loc[i, 'TR14'] = round(
                calc_sub_14(stock_data, i, 'TR'), 2)
            stock_data.loc[i,
                           '+DM14'] = calc_sub_14(stock_data, i, '+DM')
            stock_data.loc[i,
                           '-DM14'] = calc_sub_14(stock_data, i, '-DM')

        if 'TR14' in stock_data.columns:
            stock_data.loc[i, '+DI'] = (
                stock_data.loc[i, '+DM14'] / stock_data.loc[i, 'TR14'])*100
            stock_data.loc[i, '-DI'] = (
                stock_data.loc[i, '-DM14'] / stock_data.loc[i, 'TR14'])*100

            den = abs(
                stock_data.loc[i, '+DI'] + stock_data.loc[i, '-DI'])
            num = abs(stock_data.loc[i, '+DI'] -
                      stock_data.loc[i, '-DI'])
            if den != 0 and not np.isnan(den):
                stock_data.loc[i, 'DX'] = (num/den)*100

        if 'DX' in stock_data.columns:
            if stock_data.DX.count() == 14:
                stock_data.loc[i, 'ADX'] = calc_first_adx(stock_data, i)

            elif stock_data.DX.count() >= 14:
                stock_data.loc[i, 'ADX'] = calc_adx(stock_data, i)
    return stock_data


def extract_adx(data):
    """
    Extract ADX-related data from the input DataFrame.

    Parameters:
    - data: DataFrame, input stock data

    Returns:
    - DataFrame, extracted ADX-related data
    """
    data = data[[high, low, close]]
    data['Date'] = data.index  # Store DateTimeIndex in a new column
    data.reset_index(drop=True, inplace=True)
    ADX = func(data)
    ADX.set_index('Date', inplace=True)
    ADX_DATA = ADX[['DX', 'ADX']]
    return ADX_DATA
