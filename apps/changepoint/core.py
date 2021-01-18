import pandas as pd
import ruptures as rpt
import numpy as np


def get_changepoints(df, n_samples=50, sample_len=50):
    """
    """

    # remove low std cols
    s = df.diff().std()
    s = s.where(s >= 0.005).dropna()
    df = df[s.index]

    results = []

    for col in df.columns:

        x = df[col].dropna().values
        breakpoints = rpt.Window(width=100, model='l2').fit_predict(x, n_bkps=1)

        if len(breakpoints) > 1:

            changepoint = breakpoints[0]-1
            changepoint_idx = df.index[changepoint]
            x_post_breakpoints = x[breakpoints[0]:breakpoints[1]]
            x_pre_breakpoints = x[0:breakpoints[0]]

            x_sample_post = np.random.choice(x_post_breakpoints, (n_samples, sample_len))
            x_sample_pre = np.random.choice(x_pre_breakpoints, (n_samples, sample_len))
            dist = np.linalg.norm(x_sample_post - x_sample_pre)

            results.append([col, dist, changepoint_idx])

    df_results = pd.DataFrame(results, columns=['metric', 'qs', 'cp'])
    df_results['rank'] = df_results['qs'].rank(ascending=False, method='first')

    return df_results
