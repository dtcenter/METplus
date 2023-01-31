#! /bin/sh

################################################################################
# Environment: xesmf.v5.1
# Last Updated: 2023-01-27 (mccabe@ucar.edu)
# Notes: Adds Python package to read Tripolar grids
# Python Packages:
#   netcdf4==1.5.8
#   xarray==2022.3.0
#   xesmf==0.3.0
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=xesmf.v5.1

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.v5.1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.5.8
conda install -y --name ${ENV_NAME} -c conda-forge xarray==2022.3.0
conda install -y --name ${ENV_NAME} -c conda-forge xesmf==0.3.0
