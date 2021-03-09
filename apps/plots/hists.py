import numpy as np
import pandas as pd
import math

from ..utils.utils import get_cols_like
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px


def plot_hists(df: pd.DataFrame, cols: list = None, h: int = None, w: int = None, spacing: float = 0.05,
               theme: str = 'simple_white', n_cols: int = 3, shared_yaxes: bool = True, cols_like: list = None,
               cumulative: bool = False, show_axis: bool = True):
    """plot histogram"""

    # get cols to plot
    if not cols:
        if cols_like:
            cols = get_cols_like(df, cols_like)
        else:
            cols = df._get_numeric_data().columns

    n_rows = math.ceil(len(cols) / n_cols)

    p = make_subplots(
        rows=n_rows, cols=n_cols, shared_yaxes=shared_yaxes, vertical_spacing=spacing, horizontal_spacing=spacing
    )

    # figure out what to plot where on the subplot
    axes_dict = dict()
    i = 0
    for index, x in np.ndenumerate(np.zeros((n_cols, n_rows))):
        axes_dict[i] = index
        i += 1

    # make each plot
    for i, col in enumerate(cols):
        p.add_trace(
            go.Histogram(
                name=col, x=df[col], cumulative_enabled=cumulative
            ),
            row=axes_dict[i][1] + 1,
            col=axes_dict[i][0] + 1,
        )

    p.update_xaxes(showline=show_axis, linewidth=1, linecolor='lightgrey', showticklabels=show_axis, ticks='', tickfont=dict(color='lightgrey'))
    p.update_yaxes(showline=show_axis, linewidth=1, linecolor='lightgrey', showticklabels=show_axis, ticks='', tickfont=dict(color='lightgrey'))
    if h:
        p.update_layout(height=h)
    if w:
        p.update_layout(width=w)
    p.update_layout(showlegend=False, template=theme, hoverlabel=dict(namelength=-1))

    return p
