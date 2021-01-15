import pandas as pd
import ruptures as rpt
import numpy as np
from scipy.stats import ks_2samp, ttest_ind


def get_changepoints(df, n_samples, sample_len):
    """
    """

    results = []

    for col in df.columns:

        x = df[col].dropna().values
        algo = rpt.Window(width=100, model='l2').fit(x)
        breakpoints = algo.predict(n_bkps=1)
        num_breakpoints = len(breakpoints)

        # if breakpoint found
        if num_breakpoints > 1:

            changepoint = breakpoints[0]
            changepoint_t = df.index[changepoint]
            x_post_breakpoints = x[breakpoints[0]:breakpoints[1]]
            x_pre_breakpoints = x[0:breakpoints[0]]

            metrics = []

            mean_pre = round(np.mean(x_pre_breakpoints), 4)
            mean_post = round(np.mean(x_post_breakpoints), 4)
            abs_mean_pct_diff = abs(round((mean_post - mean_pre) / mean_pre, 2))

            # run some samples
            for _ in range(n_samples):

                try:
                    sample_start_pre = np.random.choice(range(len(x_pre_breakpoints) - sample_len))
                    x_sample_pre = x_pre_breakpoints[sample_start_pre:sample_start_pre + sample_len]

                    sample_start_post = np.random.choice(range(len(x_post_breakpoints) - sample_len))
                    x_sample_post = x_post_breakpoints[sample_start_post:sample_start_post + sample_len]

                    _, p = ks_2samp(x_sample_post, x_sample_pre)
                    _, t = ttest_ind(x_sample_post, x_sample_pre)

                    metrics.append(round(p, 4))
                    metrics.append(round(t, 4))

                except:
                    pass

            if len(metrics) >= 1:

                quality_score = round(np.mean(metrics), 4)
                results.append([col, quality_score, changepoint_t, abs_mean_pct_diff])

    df_results = pd.DataFrame(results, columns=['metric', 'quality_score', 'changepoint', 'abs_mean_pct_diff'])
    df_results['quality_rank'] = df_results['quality_score'].rank(ascending=True, method='first')
    df_results = df_results.sort_values('quality_rank', ascending=True)
    df_results = df_results.reset_index()

    return df_results