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
from resource2 import Resource, HS_PREFIX, LOCAL_PREFIX
from resource_handler import ResourceHandler

import tornado.ioloop
import tornado.web
import tornado.options

# Global resource handler variable
resource_handler = ResourceHandler()


# spiffy: my IDE is telling me this should implement data_received(...) (not sure if that's really necessary)
class BaseRequestHandler(tornado.web.RequestHandler):
    # SPIFFY (Emily) probably should add a header comment
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")  # TODO: change from * (any server) to our specific url
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
        # TODO: Do this on a per-handler basis (not all of them allow all of these requests)
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, GET, DELETE, OPTIONS')

    def options(self, _):
        # SPIFFY (Vicky) just curious - what is this?
        # spiffy: web browsers make an OPTIONS request to check what methods (line 31) are allowed at/for an endpoint.
        # We just need to respond with the header set on line 31.
        self.set_status(204)  # No content
        self.finish()


class WebAppHandler(BaseRequestHandler):
    """ Handles starting up the frontend for our web app """
    # SPIFFY (Vicky) is this ever used or is it left over from pre bundle.js?
    # spiffy: it's still used. This is the HTML that loads the bundle.js later.
    def get(self):
        self.render('index.html')


class BundleHandler(BaseRequestHandler):
    """ Serves the web app JavaScript file """
    def get(self):
        self.render('bundle.js')


class ResourcesHandler(BaseRequestHandler):
    """ Class that handles GETing a list of a user's resources (with metadata) & POSTing
     a new resource for that user """
     # SPIFFY (Emily) should probably add delete to this header comment

    def get(self):
        success = False
        resources, error = resource_handler.get_list_of_user_resources()
        # spiffy: this could also be written on line 67 as 'success': error is None
        if not error:
            success = True

        self.write({'resources': resources,
                    'success': success,
                    'error': error})

    def delete(self):
        success = False
        # spiffy: not needed in Python (error always set later)
        error = None

        body = json.loads(self.request.body.decode('utf-8'))
        res_id = body.get("res_id")
        if res_id is not None:
            error = resource_handler.delete_resource_JH(res_id)
            if not error:
                success = True
        else:
            error = {'type':'MissingResourceID',
                    'msg':'Please specify resource id to delete'}

        self.write({'success': success,
                    'error': error})

    def post(self):
        """
        Makes a new resource with the bare minimum amount of information--
        This is enough to create the resource, but not to make it public or private
        (that should happen on HydroShare)

        Expects body:
        {"resource title": string
        "creators": list of strings}
        """
        success = False
        # SPIFFY (Emily) should we make this error_message to differentiate from the error returned on likne 105?
        # spiffy: not needed in Python (error always set later)
        error = None
        resource_id = None

        body = json.loads(self.request.body.decode('utf-8'))
        resource_title = body.get("resource title") # string
        creators = body.get("creators") # list of names (strings)

        if resource_title is not None and creators is not None:
            resource_id, error = resource_handler.create_HS_resource(resource_title, creators)
            if not error:
                success = True
        else:
            error = {'type':'MissingInput',
                    'msg':'Please specify title and creators to make new resource'}

        self.write({'resource_id':resource_id,
                    'success':success,
                    'error': error})


class FileHandlerJH(BaseRequestHandler):
    """ Class that handles DELETEing file in JH """
    # SPIFFY (Emily) header comment should be updated

    def get(self, res_id):
        resource = Resource(res_id, resource_handler)
        jh_files = resource.get_files_JH()
        self.write({'rootDir': jh_files})

    def delete(self, res_id):
        body = json.loads(self.request.body.decode('utf-8'))
        filepaths = body.get("filepaths")
        if filepaths is not None:
            for filepath in filepaths:
                resource = Resource(res_id, resource_handler)
                resource.delete_file_or_folder_from_JH(filepath)
        else:
            # spiffy: the format of this should be updated (the response code should also be something other than 200)
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
            self.write("Please specify list of filepaths to delete")

    def put(self, res_id):
        body = json.loads(self.request.body.decode('utf-8'))
        resource = Resource(res_id, resource_handler)
        request_type = body.get("request_type")
        if request_type == "new_file":
            resource.create_file_JH(body.get("new_filename"))
        else:
            # spiffy: the format of this should be updated (the response code should also be something other than 200)
            self.write("Please specify valid request type for PUT")

    def post(self, res_id):
        resource = Resource(res_id, resource_handler)
        # spiffy: this is normally achieved using different response status codes
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        response_message = "OK"
        for field_name, files in self.request.files.items():
            for info in files:
                response = resource.upload_file_to_JH(info)
                if response != True:
                    response_message = response
        jh_files = resource.get_files_JH()
        self.write({'response_message': response_message,
                    'JH_files': jh_files})


class FileHandlerHS(BaseRequestHandler):
    """ Class that handles GETing list of a files that are in a user's HydroShare instance of a resource """
    # SPIFFY (Emily) Header comment should be updated

    # SPIFFY (Vicky) just confirming this in my own head but it is chill that this has many less things than the JH one?
    def get(self, res_id):
        # TODO: Get folder info
        resource = Resource(res_id, resource_handler)
        root_dir = resource.get_files_HS()
        self.write({'rootDir': root_dir})

    def delete(self, res_id):
        body = json.loads(self.request.body.decode('utf-8'))
        filepaths = body.get("filepaths")
        if filepaths is not None:
            for filepath in filepaths:
                # SPIFFY (Emily) should move this line outside of the for loop so we're not remaking this object over and over
                resource = Resource(res_id, resource_handler)
                resource.delete_file_or_folder_from_HS(filepath)
                resource.update_hs_files()
                self.write({"rootDir": resource.hs_files})
        else:
            self.write("Please specify list of filepaths to delete")


MOVE = 'move'
COPY = 'copy'


class MoveCopyFiles(BaseRequestHandler):
    """ Handles moving (or renaming) files within the local filesystem, on HydroShare, and between the two. """

    def set_default_headers(self):
        BaseRequestHandler.set_default_headers(self)
        self.set_header('Access-Control-Allow-Methods', 'PATCH, OPTIONS')

    def patch(self, res_id):
        body = json.loads(self.request.body.decode('utf-8'))
        resource = Resource(res_id, resource_handler)
        file_operations = body['operations']

        results = []
        success_count = 0
        failure_count = 0

        for operation in file_operations:
            method = operation['method']  # 'copy' or 'move'
            src_uri = operation['source']
            dest_uri = operation['destination']
            # SPIFFY (Emily) just curious what is this variable doing? it doesn't appear later in the function
            do_force = operation.get('force', False)

            # Split paths into filesystem prefix ('hs' or 'local') and path relative to the resource root on
            # that filesystem
            src_fs, src_path = src_uri.split(':')
            dest_fs, dest_path = dest_uri.split(':')

            # Remove the leading forward slashes
            src_path = src_path[1:]
            dest_path = dest_path[1:]

            # Exactly what operation we perform depends on where the source and destination files/folders are
            if src_fs == HS_PREFIX and dest_fs == HS_PREFIX:  # Move/copy within HydroShare
                if method == MOVE:  # Move or rename
                    # TODO: Test how well this works
                    resource.rename_or_move_file_HS(src_path, dest_path)
                    results.append({'success': True})
                    success_count += 1
                else:  # TODO: Copy
                    raise NotImplementedError('Copy within HydroShare not implemented')
            elif src_fs == LOCAL_PREFIX and dest_fs == LOCAL_PREFIX:  # Move/copy within the local filesystem
                # TODO: Move/rename/copy file on local filesystem
                if method == MOVE:  # Move or rename
                    resource.rename_or_move_file_JH(src_path, dest_path)
                    results.append({'success': True})
                    success_count += 1
                else:  # Copy
                    raise NotImplementedError('Copy within the local filesystem not implemented yet')
            elif src_fs == LOCAL_PREFIX and dest_fs == HS_PREFIX:  # Move/copy from the local filesystem to HydroShare
                # Transfer the file regardless of if we're moving or copying
                # SPIFFY (Vicky) will there be a prompt or something about whether you want to move or copy?
                # TODO: Support moving from one local folder to a different one on HS
                resource.overwrite_HS_with_file_from_JH(src_path)
                if method == MOVE:
                    # Delete the local copy of the file
                    resource.delete_file_or_folder_from_JH(src_path)
                results.append({'success': True})
                success_count += 1
            elif src_fs == HS_PREFIX and dest_fs == LOCAL_PREFIX:  # Move/copy from HydroShare to the local filesystem
                # Transfer the file regardless of if we're moving or copying
                # TODO: Support moving from one HS folder to a different one locally
                resource.overwrite_JH_with_file_from_HS(src_path)
                if method == MOVE:
                    # Delete the HS copy of the file
                    resource.delete_file_or_folder_from_HS(src_path)
                results.append({'success': True})
                success_count += 1
            else:
                msg = f'"source" prefix "{src_fs}" and/or destination prefix "{dest_fs} not recognized. Valid options' \
                      f' are "hs" and "local"'
                logging.warning(msg)
                results.append({
                    'success': False,
                    'error': 'UnrecognizedPathPrefix',
                    'message': msg,
                })
                failure_count += 1

        # CHARLIE: Example for error message
        self.write({
            'results': results,
            'successCount': success_count,
            'failureCount': failure_count,
        })


class UserInfoHandler(BaseRequestHandler):
    """ Class that handles GETing user information on the currently logged
    in user including name, email, username, etc. """

    def get(self):
        success = False
        data, error = resource_handler.get_user_info()
        if not error:
            success = True

        self.write({'data': data,
                    'success': success,
                    'error': error})


# spiffy: should rename this once we have our name
class HydroShareGUI(tornado.web.Application):
    """ Class for setting up the server & making sure it can exit cleanly """

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
        (r"/resources/([^/]+)/local-files", FileHandlerJH),
        (r"/resources/([^/]+)/move-copy-files", MoveCopyFiles),
    ])


def start_server(app):
    """ Starts running the server """
    tornado.options.parse_command_line()
    signal.signal(signal.SIGINT, app.signal_handler)
    app.listen(8080)
    tornado.ioloop.PeriodicCallback(app.try_exit, 100).start()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    # SPIFFY (Vicky): Is this a good place to put logging stuff? anyone have a better structure?
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
    print("Starting server at localhost:8080")
    start_server(application)
