#! /bin/sh

################################################################################
# Environment: pygrib
# Last Updated: 2021-06-03 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to read GRIB data
# Python Packages:
#   pygrib==?
#   metpy==?
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=pygrib_env

# Conda environment to use as base for new environment
BASE_ENV=$1


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

conda install -y --name ${ENV_NAME} -c conda-forge pygrib
conda install -y --name ${ENV_NAME} -c conda-forge metpy
