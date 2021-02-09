import yaml
import os

DEFAULT_APP_CONFIG = {
    'hosts': ['london.my-netdata.io', 'newyork.my-netdata.io', 'frankfurt.my-netdata.io']
}


def get_config(config_file='app_config.yml'):
    app_config_found = True
    if os.path.exists(config_file):
        with open(config_file) as file:
            app_config = yaml.load(file, Loader=yaml.FullLoader)
    else:
        app_config = DEFAULT_APP_CONFIG
        app_config_found = False
    return app_config_found, app_config

