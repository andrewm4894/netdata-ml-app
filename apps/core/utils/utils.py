import pandas as pd
import re
from datetime import timedelta, datetime


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


def get_reference_timedelta(ref):
    if 'h' in ref:
        ref_timedelta = timedelta(hours=int(ref.replace('h', '')))
    elif 'm' in ref:
        ref_timedelta = timedelta(minutes=int(ref.replace('m', '')))
    else:
        ref_timedelta = timedelta(hours=1)

    return ref_timedelta


def get_ref_windows(ref_timedelta, df):
    ref_before = int(df.index.min().timestamp())
    ref_after = int((df.index.min() - ref_timedelta).timestamp())
    return ref_before, ref_after


def log_inputs(app, host, after=None, before=None):
    app.logger.info(f'host={host}')
    if after:
        app.logger.info(f"after={after}, {datetime.utcfromtimestamp(after).strftime('%Y-%m-%d %H:%M:%S')}")
    if before:
        app.logger.info(f"before={before}, {datetime.utcfromtimestamp(before).strftime('%Y-%m-%d %H:%M:%S')}")
