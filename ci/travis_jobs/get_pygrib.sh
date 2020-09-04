#!/bin/bash

#shell script to install pygrib with dependencies
# todd arbetter: arbetter@ucar.edu

yum -y install eccodes-devel
pip3 install numpy
pip3 install pyproj
pip3 install eccodes-python
pip3 install pygrib
