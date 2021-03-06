# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os
import requests

from app import app

load_dotenv()

DEFAULT_APP_CONFIG = {
    'hosts': [],
    'scrape_children': 'no'
}


def get_config():
    app_config = DEFAULT_APP_CONFIG
    app_config_found = False

    if os.getenv("NETDATAMLAPP_HOSTS"):
        env_hosts = os.getenv("NETDATAMLAPP_HOSTS").split(',')
        for host in env_hosts:
            if host not in app_config.get('hosts', []):
                app_config['hosts'].append(host)
                app_config_found = True

    if os.getenv("NETDATAMLAPP_SCRAPE_CHILDREN"):
        app_config['scrape_children'] = os.getenv("NETDATAMLAPP_SCRAPE_CHILDREN")
        app_config_found = True

    if app_config['scrape_children'] == 'yes':
        host_children = []
        for host in app_config.get('hosts', []):
            url = f'http://{host}/api/v1/info'
            children = requests.get(url).json().get('mirrored_hosts', [])
            for child in children:
                host_children.append(f'{host}/host/{child}')
        app_config['hosts'].extend(host_children)

    app.logger.debug(f'app_config: {app_config}')

    return app_config_found, app_config

