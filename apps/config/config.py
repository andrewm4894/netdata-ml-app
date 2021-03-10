from dotenv import load_dotenv
import yaml
import os
import requests

load_dotenv()

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

    if os.getenv("NETDATAMLAPP_HOSTS"):
        env_hosts = os.getenv("NETDATAMLAPP_HOSTS").split(',')
        for host in env_hosts:
            if host not in app_config.get('hosts', []):
                app_config['hosts'].append(host)

    host_children = []
    for host in app_config.get('hosts', []):
        url = f'http://{host}/api/v1/info'
        children = requests.get(url).json().get('mirrored_hosts', [])
        for child in children:
            host_children.append(f'{host}/host/{child}')
    app_config['hosts'].extend(host_children)

    return app_config_found, app_config

