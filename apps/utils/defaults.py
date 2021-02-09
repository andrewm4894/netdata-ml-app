
DEFAULT_STYLE = {"margin": "4px", "padding": "4px"}


def make_empty_fig(msg="Enter inputs and press 'Run'"):
    empty_fig = {
        "layout": {
            "xaxis": {
                "visible": False
            },
            "yaxis": {
                "visible": False
            },
            "annotations": [
                {
                    "text": msg,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }
    return empty_fig
