#! /bin/sh

################################################################################
# Environment: xesmf
# Last Updated: 2022-06-16 (mccabe@ucar.edu)
# Notes: Adds Python package to read Tripolar grids
# Python Packages:
# TODO: update package versions and add others
#   xesmf==0.3.0
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=xesmf.v5

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.v5

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4
conda install -y --name ${ENV_NAME} -c conda-forge xarray
conda install -y --name ${ENV_NAME} -c conda-forge xesmf
