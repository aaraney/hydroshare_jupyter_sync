# potato (vicky): in general, this file is extremely long, can we think about breaking it up at all
# maybe HS functions go in one file, JH in another?
# potato (kyle) Yeah, I agree it should definitely be split up. The file should also be renamed.
# potato (emily): +1
"""
potato (vicky): let's get this header updated - I think it is mostly outdated at this point
also instead of listing things like this here we can write the function definitions and just pass
them until we have them fully implemented & make tasks in asana to fill them in
# potato (emily): +1

TODO
- get hs resource
- get files
- get metadata
- get user info

Get Name, Author, last updated, resource (rename, delete, publish, locate)
NOTE: Need access to private resources

CURRENT:
- get hs resource (with files) with resource id
- get metadata with resource id

"""

### This works for public resources
from hs_restclient import HydroShare, HydroShareAuthBasic
from pprint import pprint
from login import username, password
import os
import glob
import json
from metadata_parser import MetadataParser
from collections import OrderedDict
import pandas as pd
# potato (vicky): can we make path stuff more relative instead of things like hard changing working directory
# os.chdir(os.path.expanduser('a path')) # will change working directory

# potato (vicky): do we really want all this code to live outside of any main function or anything? can we clean it a bit?
# auth - TODO: get user credentials from hydroshare
auth = HydroShareAuthBasic(username=username, password=password)
hs = HydroShare(auth=auth)

# potato (kyle) Once we get copying working, we should remove all the test resources from the repo
test_resource_id = 'c40d9567678740dab868f35440a69b30'

# potato (kyle) We might want to wrap this in a setup function/file
### Making directory for local hs resources
get_info_path = os.path.dirname(os.path.realpath(__file__)) # Get path to this file's location
# output_folder = 'backend/tests/hs_resources'
output_folder = get_info_path + "/local_hs_resources"
if not os.path.exists(output_folder): # Make directory if it doesn't exist
    os.makedirs(output_folder)
    # potato (kyle) We might want to remove these print statements and replace them with a logging system
    print("Made {} folder for new resources".format(output_folder))

# potato (Kyle) We might want to place all file transferring functionality in one file
def get_hs_resource(resource_id, output_folder, unzip=True):
    # potato (vicky): add docstring
    # Get actual resource
    if not os.path.exists('{}/{}'.format(output_folder, resource_id)):

        print("getting hs resource")
        hs.getResource(resource_id, destination=output_folder, unzip=unzip)
    else:
        print("Resource already exists!")

def get_files_JH(resource_id):
    # potato (vicky): add docstring

    get_hs_resource(resource_id, output_folder)
    # files = glob.glob('{}/{}/{}/data/contents/*'.format(output_folder, resource_id, resource_id))
    prefix = output_folder + "/" + resource_id + "/" + resource_id + "/data/contents"
    files2 = get_recursive_folder_contents(prefix)
    return files2

# potato (kyle) Maybe this could go in a file that's got other resource metadata fetching functionality?
def get_folder_size(folderpath):
    """ Gets the size of the contents of a folder stored locally
    """
    total_size = 0
    for path, dirs, files in os.walk(folderpath):
        for f in files:
            fp = os.path.join(path, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_recursive_folder_contents(folderpath):
    """Uses recursion to get & properly nest contents of folders stored locally
    """
    # get all the files in the folder
    files = glob.glob('{}/*'.format(folderpath))
    # return empty list if the folder is empty
    if len(files) == 0:
        return []
    files2 = []
    for filepath in files:
        # +1 is to account for / after folderpath before file name
        # potato (kyle) We might want to use pathlib here instead of doing string manipulations ourselves
        file = filepath[len(folderpath)+1:]
        folder_contents = get_recursive_folder_contents(filepath)
        # potato (kyle) Can we please have some comments here explaining what these conditionals are checking?
        # potato (emily): +1
        if (len(folder_contents) == 0 and
                                                file.rfind(".") != -1):
            file_type = file[file.rfind(".")+1:]
            filename = file[:file.rfind(".")]
        elif os.path.isfile(filepath):
            file_type = "file"
            filename = file
        elif os.path.isdir(filepath):
            file_type = "folder"
            filename = file
        else:
            file_type = "unknown"
            filename = file
        if file_type == "folder":
            files2.append({
                "name": filename,
                "sizeBytes": get_folder_size(filepath),
                "type": file_type,
                "contents": folder_contents,
            })
        else:
            files2.append({
                "name": filename,
                "sizeBytes": os.path.getsize(filepath),
                "type": file_type,
            })
    return files2

# potato (kyle) Perhaps this could be called get_resource_files_from_HS
def get_files_HS(resource_id):
    # potato (vicky): add docstring

    # get the file information for all files in the HS resource in json
    # potato (kyle) We might want to call this something more descriptive than "array"...
    array = hs.resource(resource_id).files.all().json()
    # figure out what the url prefix to the filepath is
    # potato (kyle) We might want to declare the base URL as a constant at the top of the file, just so it's not buried
    # down here (on the off chance it changes or there's another instance someone wants to use). Also, can we use https?
    # potato (emily): +1
    url_prefix = 'http://www.hydroshare.org/resource/' + resource_id + '/data/contents'
    folders_dict = {}
    folders_final = []
    nested_files = {}
    # get the needed info for each file
    for file_info in array["results"]:
        # extract filepath from url
        # potato (kyle) This seems brittle. Is there another way we can do this? What if one url is http and the other
        # is https?
        filepath = file_info["url"][len(url_prefix)+1:]
        # get proper definition formatting of file if it is a file
        file_definition_hs = get_file_definition_hs(filepath, file_info["size"])
        # if it is a folder, build up contents
        if not file_definition_hs:
            nested_files[filepath + "/"] = file_info
            folders = filepath.split("/")
            currpath = ""
            for x in range(0, len(folders)-1):
                folder = folders[x]
                currpath = currpath + folder + "/"
                # build up dictionary of folder -> what is in it
                if (x, folder, currpath) not in folders_dict:
                    folders_dict[(x, folder, currpath)] = []
                folders_dict[(x, folder, currpath)].append((x+1, folders[x+1], currpath + folders[x+1] + "/"))
        # if it is just a file, add it to the final list
        else:
            folders_final.append(file_definition_hs)

    # go through folders dictionary & build up the nested structure
    i = 0
    for key, val in folders_dict.items():
        # potato (kyle) What is this checking? If it's a directory? (Comment?)
        if key[0] == 0:
            folder_size, folder_contents = populate_folders_hs(val, folders_dict, nested_files)
            folders_final.append({
                "name": key[1],
                "sizeBytes": folder_size,
                "type": "folder",
                "contents": folder_contents,
            })

    return folders_final

# potato (kyle) This should probably end is _HS, not _hs (like the other functions). Also, what's a file definition?
def get_file_definition_hs(filepath, size):
    """Gets file definition formatting for returning HS files, given path & size
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

# potato (kyle) _HS
def populate_folders_hs(val, folders_dict, nested_files):
    """Recursively build up nested folder structure for HS files
    """
    contents = []
    folder_size = 0
    for v in val:
        if v in folders_dict:
            subfolder_size, subfolder_contents = populate_folders_hs(folders_dict[v], folders_dict, nested_files)
            folder_size += subfolder_size
            contents.append({
                "name" : v[1],
                "sizeBytes" : subfolder_size,
                "type" : "folder",
                "contents" : subfolder_contents,
            })
        else:
            contents.append(get_file_definition_hs(v[1], nested_files[v[2]]["size"]))
            folder_size += nested_files[v[2]]["size"]

    return folder_size, contents

# potato (vicky): do we need/want this function?
# potato (kyle) If we do keep this function, can it not just call get_metadata_one_file repeatedly?
def get_metadata_of_all_files():
    #TODO scrape from xml file instead of API call

    # uses HS API to retrieve metadata -- different than existing app

    files = glob.glob('{}/*/*/data/resourcemetadata.xml'.format(output_folder))
    data = {}

    # TODO: Get ltime and size
    for f in files:
        # get ID and metadata
        resource_id = f.split('/')[1]

        # TODO: Modify this to extract data from xml files (work around for 'private' permissions with hs api)

        resource_metadata = hs.getSystemMetadata(resource_id)

        # generate absolute path to content for href
        content_dir = os.path.join(os.path.dirname(f), 'contents')
        cdir = '/hub/user-redirect/notebooks/notebooks/' + content_dir
        JH_resource_link = '<a href="{}" target="_blank">{}</a>'.format(cdir, resource_metadata['resource_title'])
        resource_metadata['JH_resource_link'] = JH_resource_link

        pprint(resource_metadata.keys())

        resource_name = resource_metadata['resource_title']
        data[resource_name] = resource_metadata

    if len(data) == 0:
        data = "There is no data"
    return data

# potato (vicky): same as above, what do we use metadata for?
def get_metadata_one_file(resource_id):
    """
    #TODO scrape from xml file instead of API call
    # potato (kyle) Check out the MetadataParser class I wrote a while ago
    Get metadata for one resource. Contains:
        - abstract
        - authors
        - bag_url
        - coverages
        - creator
        - date_created
        - date_last_updated
        - discoverable
        - doi
        - immutable
        - public
        - published
        - resource_id
        - resource_map_url
        - resource_title
        - resource_type
        - resource_url
        - science_metadata_url
        - shareable
    """
    print("getting hs resource metadata")
    resource_md = hs.getSystemMetadata(resource_id)
    print(resource_md['resource_title'])
    pprint(resource_md)
    return(resource_md)

def get_user_info():
    return hs.getUserInfo()

# potato (vicky): should this be in tests?
# potato (kyle) What is this for?
def test_socket():
    pass

"""IN HYDROSHARE"""
def create_resource_in_HS():
    # Creates a private resource for user
    """
    TODO:
    - Check if resource exists (API will just create a duplicate!)
    - Check if public
    """

    abstract = 'My abstract'
    title = 'Where does this go?'
    keywords = ('my keyword 1', 'my keyword 2')
    rtype = 'GenericResource'
    fpath = output_folder + '/{}/{}/readme.txt'.format(test_resource_id, test_resource_id)
    metadata = '[{"coverage":{"type":"period", "value":{"start":"01/01/2000", "end":"12/12/2010"}}}, {"creator":{"name":"John Smith"}}, {"creator":{"name":"Lisa Miller"}}]'
    extra_metadata = '{"key-1": "value-1", "key-2": "value-2"}'

    print("Creating resource")
    resource_id = hs.createResource(rtype, title, resource_file=fpath, keywords=keywords, abstract=abstract, metadata=metadata, extra_metadata=extra_metadata)
    print(resource_id)

    return

# potato (kyle) Could we just make this set_resource_public(resource_id, is_public) and handle both making it public
# and making it private?
# potato (emily): +1
def make_resource_public_in_HS(resource_id):
    hs.setAccessRules(resource_id, public=True)

def delete_resource_in_HS(resource_id):
    hs.deleteResource(resource_id)

def update_resource_in_HS(local_file_path, resource_folder_path, resource_id):
    options = {
                 "folder": resource_folder_path,
                 "files": local_file_path
              }
    result = hs.resource(resource_id).files(options)
    return result

# potato (vicky): why all commented out?
def rename_resource_in_HS():    # files2 = []
    # for filepath in files:
    #     file = filepath[len(prefix):]
    #     if file.rfind(".") != -1:
    #         type = file[file.rfind(".")+1:]
    #         filename = file[:file.rfind(".")]
    #     else:
    #         type = "folder"
    #         filename = file
    #     if type == "folder":
    #         files2.append({"file_name": filename, "type": type, "size": os.path.getsize(filepath), "contents": get_recursive_folder_contents(filepath)})
    #     else:
    #         files2.append({"file_name": filename, "type": type, "size": os.path.getsize(filepath)})
    pass

"""IN JUPYTERHUB"""
def create_resource_in_JH():
    pass

def rename_resource_in_JH():
    pass

def delete_resource_in_JH():
    pass

def locate_resource_in_JH():
    pass

# potato (emily): Just for readability, could we rename this to get_local_JH_resources so that when it's called later
# it's clear what exactly is local?
def get_local_resources():
    resource_folders = glob.glob(os.path.join(output_folder, '*'))
    # TODO: Use a filesystem-independent way of this
    mp_by_res_id = {}
    for folder_path in resource_folders:
        res_id = folder_path.split('/')[-1]
        metadata_file_Path = os.path.join(folder_path, res_id, 'data', 'resourcemetadata.xml')
        mp = MetadataParser(metadata_file_Path)
        mp_by_res_id[res_id] = mp

    return mp_by_res_id

"""Others"""
def get_list_of_user_resources():
    resources = {}

    # Get the user's resources from HydroShare
    user_hs_resources = hs.resources(owner=username)
    for res in user_hs_resources:
        res_id = res['resource_id']
        resources[res_id] = {
            'id': res_id,
            'title': res['resource_title'],
            'hydroShareResource': res,
        }

    # Get the resources copied to the local filesystem
    local_resources = get_local_resources()
    for res_id, res_metadata in local_resources.items():
        if res_id in resources:
            # TODO: Add local files
            resources[res_id]['localCopyExists'] = True
        else:
            resources[res_id] = {
                'id': res_id,
                'title': res_metadata.get_title(),
                'hydroShareResource': res_metadata.spoof_hs_api_response(),
                'localCopyExists': True,
            }

    return list(resources.values())


def get_folder_last_modified_time(id):
    # This is where we can get folder last modified time
    metadata = hs.getScienceMetadata(id)
    # TODO: extract modified time from metadata
    return

# potato (vicky): uhh, what?
def do_nothing():
    print("I'm doing nothing")
    return

# potato (kyle) Perhaps we just want to delete all this (and do_nothing())?
if __name__ == '__main__':
    # get_metadata(test_resource_id)
    # get_hs_resource(test_resource_id, output_folder, unzip=True)
    # # get_files_in_directory_with_metadata()
    # # create_resource_in_HS()
    # resources = get_list_of_user_resources()
    # for r in resources:
    #     print(r["resource_id"])
    #     get_hs_resource(r["resource_id"], output_folder, unzip=True)
    #
    # print(r["resource_id"])
    # local_file = 'backend/tests/hs_resources/' + r["resource_id"] + '/' + r["resource_id"] + '/data/contents/Introduction_to_Coding.ipynb'
    # update_path = 'data/contents'
    # print(update_resource_in_HS(local_file, update_path, r["resource_id"]))
    # for file in (get_files_HS("8b826c43f55043f583c85ae312a8894f")):
    #     print(file)
    # get_user_info()
    # test_socket()
    do_nothing()

#bbc2bcea4db14f6cbde009a43c8a97a1
