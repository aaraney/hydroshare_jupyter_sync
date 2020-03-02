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
import sys
import json
from resource2 import Resource
from resource_handler import ResourceHandler

import tornado.ioloop
import tornado.web
import tornado.options


# Global resource handler variable
resource_handler = ResourceHandler()

''' Function that configures cors for a handler to allow our server to access it
'''
def configure_cors(handler):
    handler.set_header("Access-Control-Allow-Origin", "*") # TODO: change from * (any server) to our specific url
    handler.set_header("Access-Control-Allow-Headers", "x-requested-with")
    handler.set_header('Access-Control-Allow-Methods', 'POST, PUT, GET, DELETE, OPTIONS')


''' Class that handles starting up the frontend for our web app
'''
class WebAppHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        configure_cors(self)

    def get(self):
        self.render('index.html')


'''
'''
class BundleHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        configure_cors(self)

    def get(self):
        self.render('bundle_link')


''' Class that handles GETing a list of a user's resources (with metadata) & POSTing
a new resource for that user
'''
class ResourcesHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        configure_cors(self)

    def get(self):
        # TODO: Probably do some request error handling here
        resources = resource_handler.get_list_of_user_resources()
        self.write({'resources': resources})

    def post(self):
        """
        Makes a new resource with the bare minimum amount of information--
        This is enough to create the resource, but not to make it public or private
        (that should happen on HydroShare)

        Expects body:
        {"resource title": string
        "creators": list of strings}
        """
        body = json.loads(self.request.body.decode('utf-8'))
        resource_title = body["resource title"] # string
        creators = body["creators"] # list of names (strings)

        resource_id = resource_handler.create_HS_resource(resource_title, creators)

        # TODO: Check this method of returning resource id
        self.write(resource_id)

''' Class that handles DELETEing file in JH
'''
class FileHandlerJH(tornado.web.RequestHandler):

    def set_default_headers(self):
        configure_cors(self)

    def get(self, res_id):
        resource = Resource(res_id, resource_handler)
        jh_files = resource.get_files_JH()
        self.write({'files': jh_files})

    def delete(self, res_id):
        body = json.loads(self.request.body.decode('utf-8'))
        resource = Resource(res_id, resource_handler)
        resource.delete_file_or_folder_from_JH(body["filepath"])

    def put(self,res_id):
        body = json.loads(self.request.body.decode('utf-8'))
        resource = Resource(res_id, resource_handler)
        if body["request_type"] == "new_file":
            resource.create_file_JH(body["new_filename"])
        elif body["request_type"] == "rename_or_move_file":
            resource.rename_or_move_file_JH(body["old_filepath"], body["new_filepath"])
        elif body["request_type"] == "overwrite_HS":
            resource.overwrite_HS_with_file_from_JH(body["filepath"])

    def post(self, res_id):
        resource = Resource(res_id, resource_handler)
        response_message = "OK"
        for field_name, files in self.request.files.items():
            for info in files:
                response = resource.upload_file_to_JH(info)
                if response != True:
                    response_message = response
        jh_files = resource.get_files_JH()
        self.write({'response_message': response_message,
                    'JH_files': jh_files})


''' Class that handles GETing list of a files that are in a user's
hydroshare instance of a resource
'''
class FileHandlerHS(tornado.web.RequestHandler):

    def set_default_headers(self):
        configure_cors(self)

    def get(self, res_id):
        # TODO: Get folder info
        resource = Resource(res_id, resource_handler)
        hs_files = resource.get_files_HS()
        self.write({'files': hs_files})

    def delete(self, res_id):
        body = json.loads(self.request.body.decode('utf-8'))
        resource = Resource(res_id, resource_handler)
        resource.delete_file_or_folder_from_HS(body["filepath"])
        resource.update_hs_files()
        self.write({"files": resource.hs_files})
    
    def put(self,res_id):
        body = json.loads(self.request.body.decode('utf-8'))
        resource = Resource(res_id, resource_handler)
        if body["request_type"] == "rename_or_move_file":
            resource.rename_file_HS(body["old_filepath"], body["new_filepath"])
        elif body["request_type"] == "overwrite_JH":
            resource.overwrite_JH_with_file_from_HS(body["filepath"])
        resource.update_hs_files()
        self.write({"HS_files": resource.hs_files})


''' Class that handles GETing user information on the currently logged
in user including name, email, username, etc.
'''
class UserInfoHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        configure_cors(self)

    def get(self):
        data = resource_handler.get_user_info()
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
        (r"/", WebAppHandler),
        (r"/bundle.js", BundleHandler),
        (r"/user", UserInfoHandler),
        (r"/resources", ResourcesHandler),
        (r"/resources/([^/]+)/hs-files", FileHandlerHS),
        (r"/resources/([^/]+)/local-files", FileHandlerJH)
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
    LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        level = LEVELS.get(level_name, logging.NOTSET)
        logging.basicConfig(level=level)

    application = make_app()
    start_server(application)
