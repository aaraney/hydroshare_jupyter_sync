'''
This file sets up the remote folder class for getting the files stored within
the remote hydroshare folder.

Author: 2019-20 CUAHSI Olin SCOPE Team
Email: vickymmcd@gmail.com
'''
#!/usr/bin/python
# -*- coding: utf-8 -*-
from hs_restclient import HydroShare, HydroShareAuthBasic
from login import username, password
import os



''' Class that defines a Remote Folder so we can access attributes of it.
'''
class RemoteFolder:

    def __init__(self, hs, res_id):
        '''Authenticates Hydroshare & sets up class variables.
        '''
        self.res_id = res_id
        self.hs = hs

    def get_file_metadata(self, filepath, size):
        """Gets file definition formatting for returning HS files, given path
        & size. Returns false if the path is a folder & not a file.
        """
        if filepath.rfind("/") == -1 and filepath.rfind(".") != -1:
            file_type = filepath[filepath.rfind(".")+1:]
            filename = filepath[:filepath.rfind(".")]
            return ({
                "name": filename,
                "sizeBytes": size,
                "type": file_type,
            })
        elif filepath.rfind("/") == -1:
            return ({
                "name": filepath,
                "sizeBytes": size,
                "type": "file",
            })
        else:
            return False

    def get_contents_recursive(self, val, folders_dict, nested_files):
        """Recursively build up nested folder structure for HS files
        """
        contents = []
        folder_size = 0
        for v in val:
            if v in folders_dict:
                subfolder_size, subfolder_contents = self.get_contents_recursive(folders_dict[v], folders_dict, nested_files)
                folder_size += subfolder_size
                contents.append({
                    "name" : v[1],
                    "sizeBytes" : subfolder_size,
                    "type" : "folder",
                    "contents" : subfolder_contents,
                })
            else:
                contents.append(self.get_file_metadata(v[1], nested_files[v[2]]["size"]))
                folder_size += nested_files[v[2]]["size"]

        return folder_size, contents

    def rename_file(self, filepath, old_filename, new_filename):
        '''Renames the hydroshare version of the file from old_filename to
        new_filename by using the HS API.
        '''

        options = {
                 "source_path": filepath + "/" + old_filename,
                 "target_path": filepath + "/" + new_filename
                          }
        self.hs.resource(self.res_id).functions.move_or_rename(options)

    def delete_file(self, filepath):
        """ deletes file in HS, if file is only item in directory, remove that parent directory"""
        resource_id = self.hs.deleteResourceFile(self.res_id, filepath)

    def delete_folder(self, filepath):
        """ deletes folder in HS, if folder is only item in directory, remove that parent directory"""
        response_json = self.hs.deleteResourceFolder(self.res_id, pathname=filepath)

    def download_file_to_JH(self, HS_filepath, JH_filepath):
        """ download HS file to JH"""
        print("destination: ")
        print(JH_filepath)
        print("source: ")
        print(HS_filepath)
        self.hs.getResourceFile(self.res_id, HS_filepath, destination=JH_filepath)

    def upload_file_to_HS(self, JHfilepath, HSfilepath):
        """ upload JH file to HS """
        # make sure input files exist
        if not os.path.exists(JHfilepath):
            raise Exception(f'Could not find file: {JHfilepath}')

        self.hs.addResourceFile(self.res_id, JHfilepath, HSfilepath)

    def create_folder(self, filepath):
        """ create folder in HS """
        self.hs.createResourceFolder(self.res_id, pathname=filepath)

