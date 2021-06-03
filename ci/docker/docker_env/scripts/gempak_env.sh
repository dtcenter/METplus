#! /bin/sh

################################################################################
# Environment: gempak
# Last Updated: 2021-06-03 (mccabe@ucar.edu)
# Notes: Installs Java OpenJDK and obtains JAR file used to
#   convert GEMPAK data to NetCDF file format
# Python Packages: None
#
# Other Content:
#   Java 1.8.0 OpenJDK
#   GempakToCF.jar
################################################################################

# The following environment variables are current unused in this script,
# but set in case the script is changed
# i.e. to use a Python package to convert GEMPAK

# Conda environment to create
ENV_NAME=gempak_env

# Conda environment to use as base for new environment
BASE_ENV=$1

yum -y update
yum -y install java-1.8.0-openjdk

curl -L -o /data/input/GempakToCF.jar -O https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar
