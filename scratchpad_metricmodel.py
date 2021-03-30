#%%

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold
from netdata_pandas.data import get_data

# inputs
hosts = ['frankfurt.my-netdata.io']
#hosts = ['35.193.228.190:19999']
charts_regex = '.*'
#charts_regex = 'system.*'
#charts_regex = 'system.load|system.cpu'
before = 0
after = -60*15
top_n = 10
n_estimators = 250
max_depth = 3
std_threshold = 0.01

# get the data
df = get_data(hosts=hosts, charts_regex=charts_regex, after=after, before=before, index_as_datetime=True)
print(df.shape)
df.head()

# pick a target
#target = 'system.cpu|user'
target = np.random.choice(df.columns, 1)[0]
print(target)
target_chart = target.split('|')[0]

# make y
y = (df[target].shift(-1) + df[target].shift(-2) + df[target].shift(-3)) / 3
df = df.drop([target], axis=1)

# drop cols from same chart
cols_to_drop = [col for col in df.columns if col.startswith(f'{target_chart}|')]
df = df.drop(cols_to_drop, axis=1)

# drop useless cols
print(df.shape)
df = df.drop(df.std()[df.std() < std_threshold].index.values, axis=1)
print(df.shape)

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

regr = RandomForestRegressor(max_depth=max_depth, n_estimators=n_estimators)
regr.fit(X, y)

# print r-square
score = round(regr.score(X, y), 2)
print(f'score={score}')

df_feature_imp = pd.DataFrame.from_dict(
    {x[0]: x[1] for x in (zip(colnames, regr.feature_importances_))}, orient='index',
    columns=['importance']
)
df_feature_imp = df_feature_imp.sort_values('importance', ascending=False)
print(df_feature_imp.head(10))

# refit using top n features
regr = RandomForestRegressor(max_depth=2, random_state=0, n_estimators=100)
X = df[list(df_feature_imp.head(top_n).index)].values
regr.fit(X, y)
score = round(regr.score(X, y), 2)
print(f'score={score}')

#%%



#%%

#%%

#%%

#%%

#%%

#%%

#%%

#%%