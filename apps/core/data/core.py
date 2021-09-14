import time

import dash_table
from netdata_pandas.data import get_data


def normalize_df(df, method='minmax'):
    if method == 'minmax':
        df = (df - df.min()) / (df.max() - df.min())
    return df


def smooth_df(df, smooth_n, agg_func='mean'):
    if agg_func == 'mean':
        df = df.rolling(smooth_n).mean()
    return df


def make_table(df, id, tooltip_header=None):
    table = dash_table.DataTable(
        id=id,
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_as_list_view=True,
        style_header={
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        tooltip_header=tooltip_header,
    )
    return table


def app_get_data(app, host, after, before, charts=None, charts_regex=None, points=None, options=None):
    time_get_data = time.time()
    if charts_regex:
        df = get_data(hosts=[host], charts_regex=charts_regex, after=after, before=before, index_as_datetime=True,
                      points=points, options=options)
    if charts:
        df = get_data(hosts=[host], charts=charts, after=after, before=before, index_as_datetime=True,
                      points=points, options=options)
    app.logger.debug(f'df.shape = {df.shape}')
    time_got_data = time.time()
    app.logger.debug(f'time took to get data = {time_got_data - time_get_data}')
    return df

