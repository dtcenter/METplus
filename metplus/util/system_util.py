"""
Program Name: system_manip.py
Contact(s): George McCabe
Description: METplus utility to handle OS/system calls
"""

import os
from pathlib import Path
import getpass


def mkdir_p(path):
    """!
       From stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
       Creates the entire directory path if it doesn't exist (including any
       required intermediate directories).
       Args:
           @param path : The full directory path to be created
       Returns
           None: Creates the full directory path if it doesn't exist,
                 does nothing otherwise.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_user_info():
    """! Get user information from OS. Note that some OS cannot obtain user ID
    and some cannot obtain username.
    @returns username(uid) if both username and user ID can be read,
     username if only username can be read, uid if only user ID can be read,
     or an empty string if neither can be read.
    """
    try:
        username = getpass.getuser()
    except OSError:
        username = None

    try:
        uid = os.getuid()
    except AttributeError:
        uid = None

    if username and uid:
        return f'{username}({uid})'

    if username:
        return username

    if uid:
        return uid

    return ''


def write_list_to_file(filename, output_list):
    with open(filename, 'w+') as f:
        for line in output_list:
            f.write(f"{line}\n")


def get_storms(filter_filename, id_only=False, sort_column='STORM_ID'):
    """! Get each storm as identified by a column in the input file.
         Create dictionary storm ID as the key and a list of lines for that
         storm as the value.

         @param filter_filename name of tcst file to read and extract storm id
         @param sort_column column to use to sort and group storms. Default
          value is STORM_ID
         @returns 2 item tuple - 1)dictionary where key is storm ID and value
          is list of relevant lines from tcst file, 2) header line from tcst
           file. Item with key 'header' contains the header of the tcst file
    """
    # Initialize a set because we want unique storm ids.
    storm_id_list = set()

    try:
        with open(filter_filename, "r") as file_handle:
            header, *lines = file_handle.readlines()

        storm_id_column = header.split().index(sort_column)
        for line in lines:
            storm_id_list.add(line.split()[storm_id_column])
    except (ValueError, FileNotFoundError):
        if id_only:
            return []
        return {}

    # sort the unique storm ids, copy the original
    # set by using sorted rather than sort.
    sorted_storms = sorted(storm_id_list)
    if id_only:
        return sorted_storms

    if not sorted_storms:
        return {}

    storm_dict = {'header': header}
    # for each storm, get all lines for that storm
    for storm in sorted_storms:
        storm_dict[storm] = [line for line in lines if storm in line]

    return storm_dict


def prune_empty(output_dir, logger):
    """! Start from the output_dir, and recursively check
        all directories and files.  If there are any empty
        files or directories, delete/remove them so they
        don't cause performance degradation or errors
        when performing subsequent tasks.

        @param output_dir The directory from which searching should begin.
        @param logger The logger to which all logging is directed.
    """

    # Check for empty files.
    for root, dirs, files in os.walk(output_dir):
        # Create a full file path by joining the path
        # and filename.
        for a_file in files:
            a_file = os.path.join(root, a_file)
            if os.stat(a_file).st_size == 0:
                logger.debug("Empty file: " + a_file +
                             "...removing")
                os.remove(a_file)

    # Now check for any empty directories, some
    # may have been created when removing
    # empty files.
    for root, dirs, files in os.walk(output_dir):
        for direc in dirs:
            full_dir = os.path.join(root, direc)
            if not os.listdir(full_dir):
                logger.debug("Empty directory: " + full_dir +
                             "...removing")
                os.rmdir(full_dir)
