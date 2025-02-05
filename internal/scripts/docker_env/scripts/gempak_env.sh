#! /bin/sh

################################################################################
# Environment: gempak.v6.0
# Last Updated: 2023-09-12 (mccabe@ucar.edu)
# Notes: Installs Java and obtains GempakToCF.jar to convert GEMPAK
#   files to NetCDF format.
# Python Packages: None
#
# Other Content:
#   - Java OpenJDK 17
#   - GempakToCF.jar (downloaded from DTCenter web server)
################################################################################

apt update
apt -y upgrade
apt install -y openjdk-17-jdk

mkdir -p /data/input
curl -L -o /data/input/GempakToCF.jar https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar
