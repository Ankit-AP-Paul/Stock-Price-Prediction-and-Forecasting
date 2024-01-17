import os
import pandas as pd
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
    for i in range(index - 13, index+1):
        result += df.loc[index, 'TR']
    return result


def calc_sub_14(df, index, column):
    return (df.loc[index-1, column+'14'] - (df.loc[index-1, column+'14']/14) + df.loc[index, column])


def calc_first_adx(df, index):
    result = 0
    for i in range(index - 13, index+1):
        result += df.loc[i, 'DX']
    return (result/14)


def calc_adx(df, index):
    return (((df.loc[index-1, 'ADX']*13) + df.loc[index, 'DX'])/14)


# df = stock_data


def func(df):
    for i in range(1, len(df)):
        dm_pos, dm_neg = calc_dm(df, i)
        tr = calc_tr(df, i)
        df.loc[i, '+DM'] = dm_pos
        df.loc[i, '-DM'] = dm_neg
        df.loc[i, 'TR'] = tr

        if df.TR.count() == 14:
            # Does'nt count NaN values
            df.loc[i, 'TR14'] = calc_first_14(df, i, 'TR')
            df.loc[i, '+DM14'] = calc_first_14(df, i, '+DM')
            df.loc[i, '-DM14'] = calc_first_14(df, i, '-DM')

        elif df.TR.count() >= 14:
            # Does'nt count NaN values
            df.loc[i, 'TR14'] = calc_sub_14(df, i, 'TR')
            df.loc[i, '+DM14'] = calc_sub_14(df, i, '+DM')
            df.loc[i, '-DM14'] = calc_sub_14(df, i, '-DM')

        if 'TR14' in df.columns:
            df.loc[i, '+DI'] = (df.loc[i,
                                       '+DM14']/df.loc[i, 'TR14'])*100
            df.loc[i, '-DI'] = (df.loc[i,
                                       '-DM14']/df.loc[i, 'TR14'])*100
            df.loc[i, 'DX'] = (
                abs(df.loc[i, '+DI']-df.loc[i, '-DI'])/abs(df.loc[i, '+DI']+df.loc[i, '-DI']))*100

        if 'DX' in df.columns:
            if df.DX.count() == 14:
                df.loc[i, 'ADX'] = calc_first_adx(df, i)

            elif df.DX.count() >= 14:
                df.loc[i, 'ADX'] = calc_adx(df, i)


folder_path = 'data'
file_list = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

for file_name in file_list:
    stock_data = pd.read_csv(folder_path+'/'+file_name)
    high, low, close = 'High', 'Low', 'Close'
    columns = ['Date', high, low, close]
    stock_data = stock_data[columns]

    func(stock_data)

    if 'ADX' in stock_data.columns:
        stock_data = stock_data.dropna(subset=['ADX'])
    else:
        print("Column 'adx' not found in the DataFrame.")
    stock_data.reset_index(drop=True, inplace=True)

    if stock_data.ADX.count() >= 1:
        stock_data[['Date', 'ADX']].to_csv(f'adx\DATA_CALCULATED\{file_name}')
