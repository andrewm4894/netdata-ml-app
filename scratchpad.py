# used for playing with random dev code

#%%
from urllib.parse import urlparse as up


def parse_netdata_url(url):
    url_parsed = up(url)
    url_dict = {
        'host': url_parsed.hostname,
        'fragments': {frag.split('=')[0]: frag.split('=')[1] for frag in url_parsed.fragment.split(';') if '=' in frag}
    }
    return url_dict

url_dict = parse_netdata_url('http://london.my-netdata.io/#menu_system;after=1625674229000;before=1625674649000;theme=slate;help=true')


#%%

url_dict


#%%

#%%