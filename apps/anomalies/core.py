import numpy as np


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
