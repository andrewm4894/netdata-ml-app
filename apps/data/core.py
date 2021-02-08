

def normalize_df(df, method='minmax'):
    if method == 'minmax':
        df = (df - df.min()) / (df.max() - df.min())
    return df


def smooth_df(df, smooth_n, agg_func='mean'):
    if agg_func == 'mean':
        df = df.rolling(smooth_n).mean()
    return df

