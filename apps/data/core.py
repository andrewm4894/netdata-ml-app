import dash_table


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

