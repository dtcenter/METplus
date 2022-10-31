#! /bin/sh

################################################################################
# Environment: gempak.v5
# Last Updated: 2021-07-08 (mccabe@ucar.edu)
# Notes: Installs Java and obtains GempakToCF.jar to convert GEMPAK
#   files to NetCDF format.
# Python Packages: None
#
# Other Content:
#   - Java 1.8.0 OpenJDK
#   - GempakToCF.jar (downloaded from DTCenter web server
################################################################################

yum -y update
yum -y install java-1.8.0-openjdk
mkdir -p /data/input
curl -L -o /data/input/GempakToCF.jar -O https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar
