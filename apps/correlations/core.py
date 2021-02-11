# -*- coding: utf-8 -*-

import numpy as np
from netdata_pandas.data import get_data


def get_df_corr(hosts, charts_regex, after, before, index_as_datetime, freq):
    df = get_data(hosts=hosts, charts_regex=charts_regex, after=after, before=before, index_as_datetime=index_as_datetime)
    df = df.resample(freq).mean()
    df = df.corr().dropna(axis=0, how='all').dropna(axis=1, how='all')

    return df


def make_df_corr_long(df_corr):
    df_corr_long = df_corr.reset_index().melt('index')
    df_corr_long.columns = ['Dim A', 'Dim B', 'Correlation']
    df_corr_long['Dimension Pair'] = df_corr_long.apply(lambda x: str(set([x['Dim A'], x['Dim B']])), axis=1)
    df_corr_long['Correlation Abs'] = round(abs(df_corr_long['Correlation']), 2)
    df_corr_long['Pos or Neg'] = np.where(df_corr_long['Correlation'] > 0, '+', '-')
    df_corr_long = df_corr_long[df_corr_long['Correlation'].notna()].sort_values('Correlation Abs')
    df_corr_long = df_corr_long[df_corr_long['Dim A'] != df_corr_long['Dim B']]
    df_corr_long = df_corr_long[['Dimension Pair', 'Correlation', 'Correlation Abs', 'Pos or Neg']].drop_duplicates()

    return df_corr_long
