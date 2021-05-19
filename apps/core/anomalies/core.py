import numpy as np
from pyod.models.hbos import HBOS
from pyod.models.pca import PCA
import pandas as pd
from sklearn.cluster import AgglomerativeClustering


def make_features(arr, colnames, lags_n, diffs_n, smooth_n):
    def lag(arr, n):
        res = np.empty_like(arr)
        res[:n] = np.nan
        res[n:] = arr[:-n]
        return res

    if diffs_n > 0:
        arr = np.diff(arr, diffs_n, axis=0)
        arr = arr[~np.isnan(arr).any(axis=1)]

    if smooth_n > 1:
        arr = np.cumsum(arr, axis=0, dtype=float)
        arr[smooth_n:] = arr[smooth_n:] - arr[:-smooth_n]
        arr = arr[smooth_n - 1:] / smooth_n

    if lags_n > 0:
        colnames = colnames + [f'{col}_lag{lag}' for lag in range(1, lags_n + 1) for col in colnames]
        arr_orig = np.copy(arr)
        for lag_n in range(1, lags_n + 1):
            arr = np.concatenate((arr, lag(arr_orig, lag_n)), axis=1)
        arr = arr[~np.isnan(arr).any(axis=1)]

    return colnames, arr


def build_models(df, df_features, df_features_train, contamination):
    charts = list(set([col.split('|')[0] for col in df.columns]))

    preds, probs = {}, {}

    for chart in charts:

        chart_cols = [col for col in df_features.columns if col.startswith(f'{chart}|')]
        model = PCA(contamination=contamination)
        X_train = df_features_train[chart_cols].values
        X = df_features[chart_cols].values
        try:
            model.fit(X_train)
            preds[chart] = model.predict(X)
            probs[chart] = model.predict_proba(X)[:, 1].tolist()
        except:
            model = HBOS(contamination=contamination)
            model.fit(X_train)
            preds[chart] = model.predict(X)
            probs[chart] = model.predict_proba(X)[:, 1].tolist()

    df_preds = pd.DataFrame.from_dict(preds, orient='columns')
    df_probs = pd.DataFrame.from_dict(probs, orient='columns')

    len_preds = len(df_preds)
    df_preds['time'] = df.tail(len_preds).index
    df_preds = df_preds.set_index('time')
    df_probs['time'] = df.tail(len_preds).index
    df_probs = df_probs.set_index('time')

    df_probs['average_probability'] = df_probs.mean(axis=1)
    df_preds['anomaly_count'] = df_preds.sum(axis=1)

    return df_preds, df_probs


def cluster_sort(df, n_clusters):
    columns = ['chart', 'cluster']
    clustering = AgglomerativeClustering(n_clusters=n_clusters).fit(df.fillna(0).transpose().values)
    cols_labels = zip(df.columns, clustering.labels_)
    cols_sorted = pd.DataFrame(cols_labels, columns=columns).sort_values('cluster')['chart'].values.tolist()
    df = df[cols_sorted]
    plot_cols = [col for col in cols_sorted if col != 'anomaly_count']
    return df, plot_cols
