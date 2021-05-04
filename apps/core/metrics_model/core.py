import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def preprocess_data(df, target, std_threshold):

    target_chart = target.split('|')[0]

    # make y
    y = (df[target].shift(-1) + df[target].shift(-2) + df[target].shift(-3)) / 3
    df = df.drop([target], axis=1)

    # drop cols from same chart
    cols_to_drop = [col for col in df.columns if col.startswith(f'{target_chart}|')]
    df = df.drop(cols_to_drop, axis=1)

    # drop useless cols
    df = df.drop(df.std()[df.std() < std_threshold].index.values, axis=1)

    # work in diffs
    df = df.diff()

    # make x
    lags_n = 5
    colnames = [f'{col}_lag{n}' for n in [n for n in range(lags_n + 1)] for col in df.columns]
    df = pd.concat([df.shift(n) for n in range(lags_n + 1)], axis=1).dropna()
    df.columns = colnames
    df = df.join(y).dropna()
    y = df[target].values
    del df[target]
    X = df.values

    return df, X, y, colnames


def get_feature_importance(X, y, colnames, n_estimators, max_depth):
    # fit base model
    regr = RandomForestRegressor(max_depth=max_depth, n_estimators=n_estimators)
    regr.fit(X, y)

    # get feature importance
    df_feature_importance = pd.DataFrame.from_dict(
        {x[0]: x[1] for x in (zip(colnames, regr.feature_importances_))}, orient='index',
        columns=['importance']
    )
    df_feature_importance = df_feature_importance.sort_values('importance', ascending=False)

    return df_feature_importance


def get_topn_model_score(df, y, top_n_features, n_estimators, max_depth):
    regr = RandomForestRegressor(max_depth=max_depth, n_estimators=n_estimators)
    X = df[top_n_features].values
    regr.fit(X, y)
    score = round(regr.score(X, y), 2)
    return score
