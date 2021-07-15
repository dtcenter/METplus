#! /bin/sh

################################################################################
# Environment: xesmf
# Last Updated: 2021-06-08 (mccabe@ucar.edu)
# Notes: Adds Python package to read Tripolar grids
# Python Packages:
#   xesmf==0.3.0
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=xesmf

# Conda environment to use as base for new environment
BASE_ENV=$1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4
conda install -y --name ${ENV_NAME} -c conda-forge xarray
conda install -y --name ${ENV_NAME} -c conda-forge xesmf
