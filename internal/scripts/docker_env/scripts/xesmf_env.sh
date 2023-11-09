#! /bin/sh

################################################################################
# Environment: xesmf.v5.1
# Last Updated: 2023-11-08 (mccabe@ucar.edu)
# Notes: Adds Python package to read Tripolar grids
#  Updated xesmf version from 0.3.0 because <0.7.1 does not work with mamba
# Python Packages:
#   netcdf4==1.6.2
#   xarray==2022.3.0
#   xesmf==0.8.2
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=xesmf.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.6.2
mamba install -y --name ${ENV_NAME} -c conda-forge xarray==2022.3.0
mamba install -y --name ${ENV_NAME} -c conda-forge xesmf==0.8.2
