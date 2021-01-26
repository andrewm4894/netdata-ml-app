import math
import itertools

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from ..utils.utils import get_cols_like
from plotly.subplots import make_subplots


def plot_scatters(df: pd.DataFrame, cols: list = None, cols_like: list = None, title: str = None,
                  h: int = 400, w: int = 400, marker_size: int = 4, theme: str = 'simple_white', n_cols: int = 1,
                  show_axis: bool = False, show_titles: bool = False, normalize_method: str = None, colors: list = None, labels: list = None):
    """Plot scatters with plotly"""

    # get cols to plot
    if not cols:
        if cols_like:
            cols = get_cols_like(df, cols_like)
        else:
            cols = df._get_numeric_data().columns

    # normalize if specified
    if normalize_method == 'minmax':
        df = (df - df.min()) / (df.max() - df.min())

    num_plots = len(list(itertools.combinations(cols, 2)))
    n_rows = math.ceil(num_plots / n_cols)

    if show_titles:
        subplot_titles = tuple(f'{x[0]} vs {x[1]}' for x in itertools.combinations(cols, 2))
    else:
        subplot_titles = None

    p = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=subplot_titles)

    # figure out what to plot where on the subplot
    axes_dict = dict()
    i = 0

    for index, x in np.ndenumerate(np.zeros((n_cols, n_rows))):
        axes_dict[i] = index
        i += 1

    # make each plot
    for i, pair in enumerate(itertools.combinations(cols, 2)):
        x = pair[0]
        y = pair[1]
        i_row = axes_dict[i][1]+1
        i_col = axes_dict[i][0]+1
        p.add_trace(go.Scatter(
            x=df[x], y=df[y], name=f'{x} vs {y}', mode='markers',
            text=labels, textposition="top center",
            marker=dict(
                size=marker_size,
                color=colors
            )),
            row=i_row, col=i_col
        )
        p.update_xaxes(title_text=x, row=i_row, col=i_col, title_standoff=0,
                       showline=show_axis, linewidth=1, linecolor='grey', showticklabels=show_axis, ticks='')
        p.update_yaxes(title_text=y, row=i_row, col=i_col, title_standoff=0,
                       showline=show_axis, linewidth=1, linecolor='grey', showticklabels=show_axis, ticks='')

    p.update_layout(showlegend=False)
    if title:
        p.update_layout(title_text=title)
    if h:
        p.update_layout(height=h)
    if w:
        p.update_layout(width=w)
    p.update_layout(template=theme)

    return p
