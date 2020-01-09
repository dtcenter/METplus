#!/usr/bin/env python

import sys

supported_py_version = '3.6.3'
py_version = sys.version.split(' ')[0]
if py_version < supported_py_version:
    print("Must be using Python {} or higher.".format(supported_py_version))
    print("You are using {}.".format(py_version))
    exit(1)
