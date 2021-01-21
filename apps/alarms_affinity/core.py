from datetime import timedelta, datetime
import dash_table
import pandas as pd
from netdata_pandas.data import get_alarm_log
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

itemsets_tooltips = {
    'support': 'explain what support is',
    'itemsets': 'explain what itemsets are'
}
rules_tooltips = {
    'antecedents': 'blah blah blah'
}


def make_baskets(host, hours_ago, last_n, window, max_n):
    df = get_alarm_log(host)
    df = df[df['status'].isin(['WARNING', 'CRITICAL'])]
    df = df.sort_values('when')

    if hours_ago:
        df = df[df['when'] >= (datetime.now() - timedelta(hours=hours_ago))]
    if last_n:
        df = df.tail(last_n).copy()

    # make transactions dataset
    td = pd.Timedelta(window)
    f_alarm = lambda x, y: df.loc[df['when'].between(y - td, y + td), 'name'].tolist()
    df['alarm_basket'] = [f_alarm(k, v) for k, v in df['when'].items()]
    f_chart = lambda x, y: df.loc[df['when'].between(y - td, y + td), 'chart'].tolist()
    df['chart_basket'] = [f_chart(k, v) for k, v in df['when'].items()]

    if max_n:
        if len(df) > max_n:
            df = df.sample(max_n)
            print(df.shape)

    alarm_dataset = df['alarm_basket'].values.tolist()
    chart_dataset = df['chart_basket'].values.tolist()

    when_min = df['when'].min()
    when_max = df['when'].max()

    return alarm_dataset, chart_dataset, when_min, when_max


def make_table(df, id, tooltip_header):
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


def process_basket(dataset, min_support, min_threshold):
    te = TransactionEncoder()
    te_ary = te.fit(dataset).transform(dataset)
    df_tx = pd.DataFrame(te_ary, columns=te.columns_)
    itemsets = fpgrowth(
        df_tx, min_support=min_support, use_colnames=True
    ).sort_values('support', ascending=False)
    rules = association_rules(
        itemsets, metric="confidence", min_threshold=min_threshold
    ).sort_values('support', ascending=False)
    itemsets['itemsets'] = itemsets['itemsets'].astype(str)
    itemsets['itemsets'] = itemsets['itemsets'].str.replace('frozenset', '')
    itemsets['itemsets'] = itemsets['itemsets'].str.replace('({', '(', regex=False)
    itemsets['itemsets'] = itemsets['itemsets'].str.replace('})', ')', regex=False)
    rules = rules.round(2)
    for col in ['antecedents', 'consequents']:
        rules[col] = rules[col].astype(str)
        rules[col] = rules[col].str.replace('frozenset', '')
        rules[col] = rules[col].str.replace('({', '(', regex=False)
        rules[col] = rules[col].str.replace('})', ')', regex=False)

    return itemsets, rules