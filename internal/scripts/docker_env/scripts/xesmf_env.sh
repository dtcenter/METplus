#! /bin/sh

################################################################################
# Environment: xesmf.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds Python package to read Tripolar grids
# Python Packages:
#   netcdf4
#   xarray
#   xesmf
#   esmf
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=xesmf.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge \
  netcdf4~=1.7.4 \
  xarray~=2026.4.0 \
  xesmf~=0.9.2 \
  esmf~=8.9.1
