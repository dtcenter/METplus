#! /bin/sh

################################################################################
# Environment: cfgrib
# Last Updated: 2021-07-20 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to read GRIB data
# Python Packages:
#   cfgrib==0.9.9.0
#   metpy==1.0.1
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=cfgrib

# Conda environment to use as base for new environment
BASE_ENV=$1


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

conda install -y --name ${ENV_NAME} -c conda-forge metpy==1.0.1
conda install -y --name ${ENV_NAME} -c conda-forge cfgrib==0.9.9.0
