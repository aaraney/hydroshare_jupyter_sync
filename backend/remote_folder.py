'''
This file sets up the remote folder class for getting the files stored within
the remote hydroshare folder.

Author: 2019-20 CUAHSI Olin SCOPE Team
Email: vickymmcd@gmail.com
'''
#!/usr/bin/python
# -*- coding: utf-8 -*-
import hs_restclient
import datetime
from dateutil.parser import parse
import os
import logging
import pathlib


# spiffy: move below "class RemoteFolder:". Also what's a remote folder? (maybe rename the file too)
''' Class that defines a Remote Folder so we can access attributes of it.
'''
class RemoteFolder:

    def __init__(self, hs, res_id):
        '''Authenticates Hydroshare & sets up class variables.
        '''
        self.res_id = res_id
        self.hs = hs

    def get_file_metadata(self, filepath, long_path, file_info, path_prefix):
        """Gets file definition formatting for returning HS files, given path
        & size. Returns false if the path is a folder & not a file.
        """
        if file_info.get("modified_time"):
            modified_time = str(parse(file_info.get("modified_time")))
        # spiffy: this could be done away with if line 33 was instead modified_time = file_info.get("modified_time")
        else:
            modified_time = None
        # spiffy: what's this doing?
        if filepath.rfind("/") == -1 and filepath.rfind(".") != -1:
            file_type = filepath[filepath.rfind(".")+1:]
            filename = filepath[:filepath.rfind(".")]
            return ({
                "name": filename,
                "path": path_prefix + '/' + long_path.strip('/'),
                "sizeBytes": file_info.get("size"),
                "modifiedTime": modified_time,
                "type": file_type,
            })
        #TODO (Charlie): This might be simpler with pathlib
        # spiffy: what's this doing?
        elif filepath.rfind("/") == -1:

            return ({
                "name": filepath,
                "path": path_prefix + '/' + long_path.strip('/'),
                "sizeBytes": file_info.get("size"),
                "modifiedTime": modified_time,
                "type": "file",
            })
        else:
            return False

    def get_contents_recursive(self, val, folders_dict, nested_files, path_prefix):
        """Recursively build up nested folder structure for HS files
        """
        contents = []
        folder_size = 0
        folder_time = datetime.datetime.min
        for v in val:
            # spiffy: maybe unpack v so the rest of the code is clearer (i.e. what each index is)
            if v in folders_dict:
                subfolder_time, subfolder_size, subfolder_contents = self.get_contents_recursive(folders_dict[v], folders_dict, nested_files, path_prefix)
                folder_size += subfolder_size
                if subfolder_time and folder_time and subfolder_time > folder_time:
                    folder_time = subfolder_time
                if subfolder_time:
                    subfolder_time = str(subfolder_time)
                contents.append({
                    # spiffy: remove whitespace before : (per PEP8)
                    "name" : v[1],
                    "path" : path_prefix + '/' + v[2].strip('/'),
                    "sizeBytes" : subfolder_size,
                    "modifiedTime" : subfolder_time,
                    "type" : "folder",
                    "contents" : subfolder_contents,
                })
            else:
                # spiffy: what's happening here?
                contents.append(self.get_file_metadata(v[1], v[2], nested_files[v[2]], path_prefix))
                folder_size += nested_files[v[2]]["size"]
                if nested_files[v[2]].get("modified_time"):
                    curr_time = parse(nested_files[v[2]].get("modified_time"))
                else:
                    curr_time = None
                if curr_time and folder_time and curr_time > folder_time:
                    folder_time = curr_time

        return folder_time, folder_size, contents

    def rename_or_move_file(self, old_filepath, new_filepath):
        '''Renames the hydroshare version of the file from old_filename to
        new_filename by using the HS API.
        '''

        options = {
                 "source_path": old_filepath,
                 "target_path": new_filepath
                          }
        self.hs.resource(self.res_id).functions.move_or_rename(options)


    def delete_file(self, filepath):
        """ deletes file in HS, if file is only item in directory, remove that parent directory"""
        # TODO: Charlie, send message to frontend
        try:
            resource_id = self.hs.deleteResourceFile(self.res_id, filepath)
        # spiffy: where does "exceptions" come from? My IDE isn't recognizing it. Doesn't it need to be imported?
        except exceptions.HydroShareNotAuthorized:
            # print("Not authorized")
            logging.info("Not authorized to delete file in "+self.res_id)
        except exceptions.HydroShareNotFound:
            logging.info("{} does not exist in {}".format(filepath, self.res_id))
        except:
            logging.info("Unknown error while deleting file from "+self.res_id)

    def delete_folder(self, filepath):
        """ deletes folder in HS, if folder is only item in directory, remove that parent directory"""
        # TODO: Charlie, send message to frontend
        try:
            response_json = self.hs.deleteResourceFolder(self.res_id, pathname=filepath)
        except IndexError:
            logging.info("Either {} does not exist in {}, or not authorized to delete folder".format(filepath, self.res_id))
        except:
            logging.info("Uknown error while trying to delete {} in {}".format(filepath, self.res_id))

    def download_file_to_JH(self, HS_filepath, JH_filepath):
        """ download HS file to JH"""
        self.hs.getResourceFile(self.res_id, HS_filepath, destination=JH_filepath)

    def upload_file_to_HS(self, JHfilepath, HSfilepath):
        """ upload JH file to HS """
        # make sure input files exist
        if not os.path.exists(JHfilepath):
            raise Exception(f'Could not find file: {JHfilepath}')

        try:
            self.hs.addResourceFile(self.res_id, str(JHfilepath), str(HSfilepath))
        except hs_restclient.HydroShareHTTPException as e:
            logging.error(e)

    def create_folder(self, filepath):
        """ Attempts to create a folder in the HydroShare resource """
        if isinstance(filepath, pathlib.PosixPath):
            filepath = str(filepath)
        # Remove the leading /, if one exists
        if filepath.startswith('/'):
            filepath = filepath[1:]
        self.hs.createResourceFolder(self.res_id, pathname=filepath)
