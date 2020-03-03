#!/usr/bin/env python

# Check that user's version of python is at equal or higher than the
# currently supported version

from sys import version, exit

supported_py_version = '3.6.3'

def check_metplus_python_version(user_py, supported_py):
    """!Test that the user's version of python is equal of higher than the
        the supported version of python. Imported in each wrapper and master_metplus
        to avoid confusing failures if the user's version is not current. Note:
        SyntaxError from using f-strings (available in 3.6+) in earlier versions of
        Python are output before the output from this function can be displayed.
        Calling a wrapper directly instead of using master_metplus.py may result in
        this behavior if the wrapper uses f-strings.
        A potential "hack" work-around in wrappers that use f-strings could be to 
        add an f-string at the top of the file that mentions the incorrect version
        issue so that user's see that message.
        Args:
          @param user_py user's python version number, i.e. 3.8.1
          @param supported_py currently supported python version number, i.e. 3.6.3
          @returns True if version is at least supported, False if not"""
    supported_list = supported_py.split('.')
    user_list = user_py.split('.')

    for user, supported in zip(user_list, supported_list):
        # if the same version is used, continue
        if int(user) == int(supported):
            continue

        # if a higher version is used, break out of the loop
        if int(user) > int(supported):
            break

        # a lower version is used - report and exit
        print("ERROR: Must be using Python {} or higher ".format(supported_py)+
              "with the required packages installed.")
        print("You are using {}.".format(user_py))
        print("See the METplus documentation for more information.")
        return False

    return True

# get user's python version and check that it is equal or
# higher than the supported version
user_py_version = version.split(' ')[0]
if not check_metplus_python_version(user_py_version, supported_py_version):
    exit(1)
