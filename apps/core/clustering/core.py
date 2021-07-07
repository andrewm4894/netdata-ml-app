import numpy as np
import pandas as pd
import warnings
from datetime import datetime
from netdata_pandas.data import get_data
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from tslearn.clustering import TimeSeriesKMeans


class Clusterer:
    """
    """

    def __init__(self,
                 hosts: list, charts_regex: str, after: int, before: int, points: int, diff: bool = False, norm: bool = True,
                 smooth_n: int = 5, smooth_func: str = 'mean', n_clusters: int = 10, min_n: int = 3,
                 max_n: int = 100, min_qs: float = 0.5):
        self.hosts = hosts
        self.charts_regex = charts_regex
        self.after = after
        self.before = before
        self.diff = diff
        self.points = points
        self.norm = norm
        self.smooth_n = smooth_n
        self.smooth_func = smooth_func
        self.n_clusters = n_clusters
        self.min_n = min_n
        self.max_n = max_n
        self.min_qs = min_qs
        self.cluster_quality_dict = {}

    def get_data(self):
        """
        """
        self.df = get_data(self.hosts, charts_regex=self.charts_regex, after=self.after, before=self.before, user=None, pwd=None, points=self.points)
        # remove duplicate columns that we might get from get_data()
        self.df = self.df.loc[:, ~self.df.columns.duplicated()]
        # drop any empty columns
        self.df = self.df.dropna(axis=1, how='all')
        # forward fill and backward fill to try remove any N/A values
        self.df = self.df.ffill().bfill()

    def preprocess_data(self):
        """
        """
        if self.diff:
            self.df = self.df.diff()
        if self.smooth_n > 0:
            if self.smooth_func == 'mean':
                self.df = self.df.rolling(self.smooth_n).mean().dropna(how='all')
            elif self.smooth_func == 'max':
                self.df = self.df.rolling(self.smooth_n).max().dropna(how='all')
            elif self.smooth_func == 'min':
                self.df = self.df.rolling(self.smooth_n).min().dropna(how='all')
            elif self.smooth_func == 'sum':
                self.df = self.df.rolling(self.smooth_n).sum().dropna(how='all')
            elif self.smooth_func == 'median':
                self.df = self.df.rolling(self.smooth_n).median().dropna(how='all')
            else:
                self.df = self.df.rolling(self.smooth_n).mean().dropna(how='all')
        if self.norm:
            self.df = (self.df - self.df.min()) / (self.df.max() - self.df.min())
        self.df = self.df.dropna(axis=1, how='all')
        self.df = self.df.set_index(pd.to_datetime(self.df.index, unit='s'))

    def cluster_data(self):
        """
        """
        self.model = TimeSeriesKMeans(
            n_clusters=self.n_clusters, metric="euclidean", max_iter=10, n_init=2
        ).fit(self.df.transpose().values)
        self.df_cluster = pd.DataFrame(list(zip(self.df.columns, self.model.labels_)), columns=['metric', 'cluster'])
        self.cluster_metrics_dict = self.df_cluster.groupby(['cluster'])['metric'].apply(
            lambda x: [x for x in x]).to_dict()
        self.cluster_len_dict = self.df_cluster['cluster'].value_counts().to_dict()

    def generate_quality_scores(self):
        """
        """
        for cluster in self.model.labels_:
            self.x_corr = self.df[self.cluster_metrics_dict[cluster]].corr().abs().values
            self.x_corr_mean = round(self.x_corr[np.triu_indices(self.x_corr.shape[0], 1)].mean(), 2)
            self.cluster_quality_dict[cluster] = self.x_corr_mean

    def generate_df_cluster_meta(self):
        """
        """
        self.df_cluster_meta = pd.DataFrame.from_dict(self.cluster_len_dict, orient='index', columns=['n'])
        self.df_cluster_meta.index.names = ['cluster']
        self.df_cluster_meta['quality_score'] = self.df_cluster_meta.index.map(self.cluster_quality_dict).fillna(0)
        self.df_cluster_meta = self.df_cluster_meta.sort_values('quality_score', ascending=False)
        self.df_cluster_meta['valid'] = np.where(self.df_cluster_meta['n'] < self.min_n, 0, 1)
        self.df_cluster_meta['valid'] = np.where(self.df_cluster_meta['n'] > self.max_n, 0,
                                                 self.df_cluster_meta['valid'])
        self.df_cluster_meta['valid'] = np.where(self.df_cluster_meta['quality_score'] < self.min_qs, 0,
                                                 self.df_cluster_meta['valid'])

    def generate_df_cluster_centers(self):
        """
        """
        self.df_cluster_centers = pd.DataFrame(
            data=self.model.cluster_centers_.reshape(
                self.model.cluster_centers_.shape[0],
                self.model.cluster_centers_.shape[1]
            )
        ).transpose()
        self.df_cluster_centers.index = self.df.index

    def run_all(self):
        """
        """
        self.get_data()
        self.preprocess_data()
        self.cluster_data()
        self.generate_quality_scores()
        self.generate_df_cluster_meta()
        self.generate_df_cluster_centers()