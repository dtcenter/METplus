#!/usr/bin/env python

from sys import version, exit

supported_py_version = '3.6.3'
supported_list = supported_py_version.split('.')
py_version = version.split(' ')[0]
user_list = py_version.split('.')

for user, supported in zip(user_list, supported_list):
    if int(user) < int(supported):
        print("Must be using Python {} or higher.".format(supported_py_version))
        print("You are using {}.".format(py_version))
        exit(1)
