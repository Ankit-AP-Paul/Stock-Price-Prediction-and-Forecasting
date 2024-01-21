import os
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None

# stock_data = pd.read_csv('data/ADANIGREEN.NS.csv')


def calc_val(df, column, index):
    prev_val = df.loc[index-1, column]
    curr_val = df.loc[index, column]
    return (curr_val, prev_val)


def calc_dm(df, index):
    curr_high, prev_high = calc_val(df, high, index)
    curr_low, prev_low = calc_val(df, low, index)
    dm_pos = curr_high - prev_high
    dm_neg = prev_low - curr_low

    if dm_pos > dm_neg:
        if dm_pos < 0:
            dm_pos = 0.00
        dm_neg = 0.00
        return (dm_pos, dm_neg)

    elif dm_pos < dm_neg:
        if dm_neg < 0:
            dm_neg = 0.00
        dm_pos = 0.00
        return (dm_pos, dm_neg)

    else:
        if dm_pos < 0:
            dm_pos = 0.00
        dm_neg = 0.00
        return (dm_pos, dm_neg)


def calc_tr(df, index):
    curr_high, prev_high = calc_val(df, high, index)
    curr_low, prev_low = calc_val(df, low, index)
    curr_close, prev_close = calc_val(df, close, index)

    ranges = [curr_high - curr_low,
              abs(curr_high - prev_close), abs(curr_low - prev_close)]
    tr = max(ranges)
    return tr


def calc_first_14(df, index, column):
    result = 0
    for i in range(index-13, index+1):
        result += df.loc[i, column]
    return (result)


def calc_sub_14(df, index, column):
    return (df.loc[index-1, column+'14'] - (df.loc[index-1, column+'14']/14) + df.loc[index, column])


def calc_first_adx(df, index):
    result = 0
    for i in range(index-13, index+1):
        result += df.loc[i, 'DX']
    return (result/14)


def calc_adx(df, index):
    return ((df.loc[index-1, 'ADX']*13) + df.loc[index, 'DX'])/14


# df = stock_data


def func(stock_data):
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
            stock_data.loc[i, '+DI'] = (stock_data.loc[i,
                                        '+DM14'] / stock_data.loc[i, 'TR14'])*100
            stock_data.loc[i, '-DI'] = (stock_data.loc[i,
                                        '-DM14'] / stock_data.loc[i, 'TR14'])*100

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


folder_path = 'data'
file_list = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

for file_name in file_list:
    sd = pd.read_csv(folder_path+'/'+file_name)
    high, low, close = 'High', 'Low', 'Close'
    columns = ['Date', high, low, close]
    stock_data = sd[columns]

    func(stock_data)

    if 'ADX' in stock_data.columns:
        sd['ADX'] = stock_data[['ADX']]
        sd.to_csv(f"data/{file_name}", index=False)
        print("Done")
    else:
        print("ADX does'nt exist")
    # if 'ADX' in stock_data.columns:
    #     stock_data = stock_data.dropna(subset=['ADX'])
    # else:
    #     print("Column 'adx' not found in the DataFrame.")
    # stock_data.reset_index(drop=True, inplace=True)
    # if 'ADX' in stock_data.columns:
    #     stock_data[['Date', 'ADX']].to_csv(f'adx\DATA_CALCULATED\{file_name}')
