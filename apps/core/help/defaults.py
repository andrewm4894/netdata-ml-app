
DEFAULT_HELP_INPUTS_HOST = "**`host`** - the host you want to pull data from."
DEFAULT_HELP_INPUTS_METRICS = """**`metrics`**: a string list of the specific metrics you want to focus on in the format "chart.name|metric,chart.name|metric", for example "system.cpu|user,system.load|load1"."""
DEFAULT_HELP_INPUTS_CHARTS_REGEX = """**`charts regex`** - a regex string of the charts you would like to include, for example "system.cpu*|apps.*" would include all system.cpu* charts and apps.* charts."""
DEFAULT_HELP_INPUTS_AFTER = "**`after`** - as per the [netdata REST API](https://registry.my-netdata.io/swagger/#/default/get_data)."
DEFAULT_HELP_INPUTS_BEFORE = "**`before`** - as per the [netdata REST API](https://registry.my-netdata.io/swagger/#/default/get_data)."
DEFAULT_HELP_INPUTS_OPTIONS = """**`options`** - a string representing specific `key=val` pairs you can pass to the app, for example "foo=bar,msg=hello" would pass the params `foo=bar` and `msg=hello` to the underlying app."""
DEFAULT_HELP_INPUTS_NETDATA_URL = """**`netdata url`** - copy and paste a netdata url of interest and relevant params will be read from the url and take precedence."""

DEFAULT_HELP_IMAGE_URL_HEATMAP = "https://raw.githubusercontent.com/andrewm4894/netdata-ml-app/develop/apps/help/assets/help-heatmap.png"
DEFAULT_HELP_IMAGE_URL_PERCENTILES = "https://raw.githubusercontent.com/andrewm4894/netdata-ml-app/develop/apps/help/assets/help-percentiles.png"