'''
This file sets up the hydroshare server for communicating with the
hydroshare gui frontend.

Author: 2019-20 CUAHSI Olin SCOPE Team
Email: vickymmcd@gmail.com
'''
#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import logging
from resource import Resource
from resource_handler import ResourceHandler
from get_info import (get_files_HS,
                      get_files_JH,
                      get_user_info,
                      get_list_of_user_resources)

import tornado.ioloop
import tornado.web
import tornado.options


class HydroshareServer:

    '''Sets up the resource handler to be used in the server'''
    def __init__(self):
        self.resource_handler = ResourceHandler()

    ''' Class that handles GETing a list of a user's resources & POSTing
    a new resource for that user
    '''
    class ResourcesHandler(tornado.web.RequestHandler):

        # TODO: Remove this (security hazard), needed for frontend, make specific to our site
        def set_default_headers(self):
            # TODO (vicky) move into a function called configure_cors(handler) and that could be
            # called in each handler (with configure_cors(self)).
            self.set_header("Access-Control-Allow-Origin", "*") # change from * (any server) to our specific url
            self.set_header("Access-Control-Allow-Headers", "x-requested-with")
            self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        def get(self):
            # TODO: Probably do some request error handling here
            resources = get_list_of_user_resources()
            self.write({'resources': resources})

        def post(self):
            pass


    ''' Class that handles GETing list of a files that are in a user's
    hydroshare instance of a resource
    '''
    class ResourcesFileHandlerHS(tornado.web.RequestHandler):

        # TODO: Remove this (security hazard)
        def set_default_headers(self):
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Access-Control-Allow-Headers", "x-requested-with")
            self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        def get(self, res_id):
            # TODO: Get folder info
            resource = Resource(res_id)
            hs_files = resource.get_files_HS()
            self.write({'files': hs_files})


    ''' Class that handles GETing list of a files that are in a user's
    jupyterhub instance of a resource
    '''
    class ResourcesFileHandlerJH(tornado.web.RequestHandler):

        # TODO: Remove this (security hazard)
        def set_default_headers(self):
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Access-Control-Allow-Headers", "x-requested-with")
            self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        def get(self, res_id):
            resource = Resource(res_id)
            jh_files = resource.get_files_JH()
            self.write({'files': jh_files})


    ''' Class that handles GETing user information on the currently logged
    in user including name, email, username, etc.
    '''
    class UserInfoHandler(tornado.web.RequestHandler):

        # TODO: Remove this (security hazard)
        def set_default_headers(self):
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Access-Control-Allow-Headers", "x-requested-with")
            self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

        def get(self):
            data = get_user_info()
            self.write(data)


    ''' Class for setting up the server & making sure it can exit cleanly
    '''
    class HydroShareGUI(tornado.web.Application):
        is_closing = False

        def signal_handler(self, signum, frame):
            logging.info('exiting...')
            self.is_closing = True

        def try_exit(self):
            if self.is_closing:
                tornado.ioloop.IOLoop.instance().stop()
                logging.info('exit success')


    def make_app():
        """Returns an instance of the server with the appropriate endpoints"""
        return HydroShareGUI([
            (r"/user", UserInfoHandler),
            (r"/resources", ResourcesHandler),
            (r"/resources/([^/]+)/hs-files", ResourcesFileHandlerHS),
            (r"/resources/([^/]+)/local-files", ResourcesFileHandlerJH)
        ])

    ''' Starts running the server
    '''
    def start_server(application):
        tornado.options.parse_command_line()
        signal.signal(signal.SIGINT, application.signal_handler)
        application.listen(8080)
        tornado.ioloop.PeriodicCallback(application.try_exit, 100).start()
        tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    application = make_app()
    start_server(application)
