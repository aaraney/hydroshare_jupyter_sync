'''
This file sets up the jupyter server extension to launch our backend
server when jupyter is launched.

Author: 2019-20 CUAHSI Olin SCOPE Team
Email: vickymmcd@gmail.com
'''
#!/usr/bin/python
# -*- coding: utf-8

from hydroshare_jupyter_sync.index_html import set_backend_url, set_frontend_url
from .server import get_route_handlers
from notebook.utils import url_path_join


def _jupyter_server_extension_paths():
    return [{
        "module": "hydroshare_jupyter_sync"
    }]


def load_jupyter_server_extension(nb_server_app):
    nb_server_app.log.info("Successfully loaded hydroshare_jupyter_sync server extension.")

    web_app = nb_server_app.web_app

    frontend_base_url = url_path_join(web_app.settings['base_url'], 'sync')
    backend_base_url = url_path_join(web_app.settings['base_url'], 'syncApi')
    set_backend_url(backend_base_url)
    set_frontend_url(frontend_base_url)
    handlers = get_route_handlers(frontend_base_url, backend_base_url)
    web_app.add_handlers('.*$', handlers)
