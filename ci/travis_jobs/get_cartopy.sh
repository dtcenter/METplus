#!/bin/bash

#Shell script for installing cartopy
#Called from a docker run command inside "test_use_cases_met_tool_wrappers.sh"

sudo mkdir /cartopy
cd /cartopy
wget https://download.osgeo.org/proj/proj-4.9.1.tar.gz
tar zxf proj-4.9.1.tar.gz
cd proj-4.9.1
./configure
make
make install
sudo yum -y install geos
sudo yum -y install geos-devel
sudo pip3 install --upgrade cython numpy pyshp six
sudo pip3 install shapely --no-binary shapely
sudo pip3 install cartopy

