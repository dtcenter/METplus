#! /bin/sh

################################################################################
# Environment: gempak.v5.1
# Last Updated: 2023-01-31 (mccabe@ucar.edu)
# Notes: Installs Java and obtains GempakToCF.jar to convert GEMPAK
#   files to NetCDF format.
# Python Packages: None
#
# Other Content:
#   - Java 1.8.0 OpenJDK
#   - GempakToCF.jar (downloaded from DTCenter web server
################################################################################

apt update
apt -y upgrade
apt install -y openjdk-8-jdk
apt install -y curl
mkdir -p /data/input
curl -L -o /data/input/GempakToCF.jar -O https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar
