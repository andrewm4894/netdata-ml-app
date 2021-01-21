import pandas as pd
import re


def process_opts(opts):
    if opts != '':
        try:
            opts = opts.split(',')
            opts = [opt.split('=') for opt in opts]
            opts = {opt[0]: opt[1] for opt in opts}
        except:
            opts = {}
    else:
        opts = {}
    return opts


def get_cols_like(df: pd.DataFrame, cols_like: list) -> list:
    df_columns = df.columns
    cols_like = [like.replace('%', '.*') for like in cols_like]
    cols = []
    for like in cols_like:
        pattern = re.compile(f'^{like}$')
        matched_cols = [col for col in df_columns if pattern.match(col)]
        cols.extend(matched_cols)
    cols = list(set(cols))
    return cols
