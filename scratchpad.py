#%%

import pandas as pd
import plotly.express as px
from netdata_pandas.data import get_data
from am4894plots.plots import plot_lines, plot_lines_grid

#%%

df = get_data(['london.my-netdata.io'], ['system.cpu', 'system.load'], after=-60, before=0)
fig = plot_lines_grid(df, return_p=True, show_p=False)

fig.show()

#%%