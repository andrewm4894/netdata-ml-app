import os

import pandas as pd
import plotly.graph_objects as go
import plotly.offline
from plotly.subplots import make_subplots
from ..utils.utils import get_cols_like


def normalize_col(col, normalize_method: str = 'minmax'):
    if normalize_method == 'minmax':
        col = (col - col.min()) / (col.max() - col.min())
    return col


def plot_lines(df: pd.DataFrame, cols: list = None, cols_like: list = None, x: str = None, title: str = None,
               slider: bool = True, out_path: str = None, show_p: bool = True, return_p: bool = False, h: int = None,
               w: int = None, theme: str = 'simple_white', lw: int = 1, renderer: str = 'browser',
               stacked: bool = False, filltozero: bool = False, shade_regions: list = None,
               shade_color: str = 'Yellow', shade_opacity: float = 0.2, shade_line_width: int = 0,
               marker_list: list = None, marker_mode: str = "markers", marker_position: str = "bottom center",
               marker_color: str = 'Red', marker_size: int = 5, marker_symbol: str = 'circle-open',
               normalize_method: str = None):
    """Plot lines with plotly"""

    # set stackedgroup if stacked flag set
    if stacked:
        stackgroup = 'one'
    else:
        stackgroup = None
    if filltozero:
        fill = 'tozeroy'
    else:
        fill = None

    # create figure object
    p = go.Figure()

    # get cols to plot
    if not cols:
        if cols_like:
            cols = get_cols_like(df, cols_like)
        else:
            cols = df._get_numeric_data().columns

    # normalize if specified
    if normalize_method == 'minmax':
        df = (df - df.min()) / (df.max() - df.min())

    # define x axis if needed
    if not x:
        # if looks like int6e then convert to datetime
        if str(df.index.dtype) == 'int64':
            x = pd.to_datetime(df.index, unit='s')
        else:
            x = df.index
    else:
        x = df[x]

    for i, col in enumerate(cols):
        p.add_trace(
            go.Scatter(
                x=x, y=df[col], name=col, line=dict(width=lw), fill=fill, stackgroup=stackgroup,
                hoverlabel=dict(namelength=-1)
            )
        )
    if title:
        p.update_layout(title_text=title)
    if slider:
        p.update_layout(xaxis_rangeslider_visible=slider)
    if h:
        p.update_layout(height=h)
    if w:
        p.update_layout(width=w)

    # add any shaded regions
    if shade_regions:
        shapes_to_add = []
        for x_from, x_to, shade_color in shade_regions:
            # check if region is in the data to be plotted and only plot if is
            if x_from >= x.min() and x_to <= x.max():
                shapes_to_add.append(
                    dict(type="rect", xref="x", yref="paper", x0=x_from, y0=0, x1=x_to, y1=1, fillcolor=shade_color,
                        opacity=shade_opacity, layer="below", line_width=shade_line_width)
                )
        # now add relevant shapes
        p.update_layout(shapes=shapes_to_add)

    # add any markers
    if marker_list:
        for x_at, marker_label in marker_list:
            # check if region is in the data to be plotted and only plot if is
            if x_at >= x.min() and x_at <= x.max():
                p.add_trace(go.Scatter(
                    x=[x_at], y=[0], mode=marker_mode, text=[str(marker_label)], textposition=marker_position,
                    marker=dict(symbol=marker_symbol, color=marker_color, size=marker_size), showlegend=False)
                )

    p.update_layout(template=theme)

    if out_path:
        out_dir = '/'.join(out_path.split('/')[0:-1])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        plotly.offline.plot(p, filename=out_path, auto_open=False)
    if show_p:
        p.show(renderer=renderer)
    if return_p:
        return p


def plot_lines_grid(df: pd.DataFrame, cols: list = None, cols_like: list = None, x: str = None, title: str = None,
                    slider: bool = False, out_path: str = None, show_p: bool = True, return_p: bool = False,
                    h: int = None, w: int = None, vertical_spacing: float = 0.002, theme: str = 'simple_white',
                    lw: int = 1, renderer: str = 'browser', shade_regions: list = None, shade_opacity: float = 0.5,
                    shade_line_width: int = 0, marker_list: list = None, marker_mode: str = "markers",
                    marker_position: str = "bottom center", marker_color: str = 'Red', marker_size: int = 5,
                    marker_symbol: str = 'circle-open', h_each: int = None, legend: bool = True,
                    yaxes_visible: bool = True, xaxes_visible: bool = True, subplot_titles: list = None,
                    subplot_titles_size: int = 12, subplot_titles_x: float = 0.2, subplot_titles_color: str = 'grey',
                    normalize_method: str = None):
    """Plot lines with plotly"""

    # get cols to plot
    if not cols:
        if cols_like:
            cols = get_cols_like(df, cols_like)
        else:
            cols = df._get_numeric_data().columns

    # define x axis if needed
    if not x:
        x = df.index
    else:
        x = df[x]

    # define subplot titles if needed
    if not subplot_titles:
        subplot_titles = cols

    # make subplots
    p = make_subplots(
        rows=len(cols), cols=1, shared_xaxes=True, vertical_spacing=vertical_spacing, subplot_titles=subplot_titles
    )

    # update subplot titles
    for annotation in p['layout']['annotations']:
        annotation['x'] = subplot_titles_x
        annotation['font'] = {'size': subplot_titles_size, 'color': subplot_titles_color}

    # add lines
    for i, col in enumerate(cols):
        if isinstance(col, list):
            for c in col:
                col_data = normalize_col(df[c], normalize_method)
                p.add_trace(
                    go.Scatter(
                        x=x, y=col_data, name=c, line=dict(width=lw), hoverlabel=dict(namelength=-1)
                    ),
                    row=(1 + i),
                    col=1
                )
        else:
            col_data = normalize_col(df[col], normalize_method)
            p.add_trace(
                go.Scatter(
                    x=x, y=col_data, name=col, line=dict(width=lw), hoverlabel=dict(namelength=-1)
                ),
                row=(1+i),
                col=1
            )

    #p.update_layout(hoverlabel=dict(namelength=-1))

    if title:
        p.update_layout(title_text=title)
    if slider:
        p.update_layout(xaxis_rangeslider_visible=slider)
    if h_each:
        h = len(cols)*h_each
    if h:
        p.update_layout(height=h)
    if w:
        p.update_layout(width=w)
    p.update_layout(template=theme)

    # add any shaded regions
    if shade_regions:
        shapes_to_add = []
        for x_from, x_to, shade_color in shade_regions:
            # check if region is in the data to be plotted and only plot if is
            if x_from >= x.min() and x_to <= x.max():
                shapes_to_add.append(
                    dict(type="rect", xref="x", x0=x_from, y0=0, x1=x_to, y1=1, fillcolor=shade_color,
                         opacity=shade_opacity, layer="below", line_width=shade_line_width, yref='paper')
                )
        # now add relevant shapes
        p.update_layout(shapes=shapes_to_add)

    # add any markers
    if marker_list:
        for x_at, marker_label in marker_list:
            # check if region is in the data to be plotted and only plot if is
            if x.min() <= x_at <= x.max():
                p.add_trace(go.Scatter(
                    x=[x_at], y=[0], mode=marker_mode, text=[str(marker_label)], textposition=marker_position,
                    marker=dict(symbol=marker_symbol, color=marker_color, size=marker_size), showlegend=False)
                )

    # some other options
    p.update_layout(showlegend=legend)
    p.update_yaxes(visible=yaxes_visible)
    p.update_xaxes(visible=xaxes_visible)

    # save file
    if out_path:
        out_dir = '/'.join(out_path.split('/')[0:-1])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        plotly.offline.plot(p, filename=out_path, auto_open=False)

    if show_p:
        p.show(renderer=renderer)

    if return_p:
        return p