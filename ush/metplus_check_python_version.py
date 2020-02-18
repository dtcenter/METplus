#!/usr/bin/env python

from sys import version, exit

supported_py_version = '3.6.3'.split('.')
py_version = version.split(' ')[0].split('.')

for user, supported in zip(py_version, supported_py_version):
    if user < supported:
        print("Must be using Python {} or higher.".format(supported_py_version))
        print("You are using {}.".format(py_version))
        exit(1)
