#! /bin/sh

################################################################################
# Environment: cfgrib.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to read GRIB data into Xarray and
#   so it can easily be processed with MetPy
# Python Packages:
#   metpy
#   netcdf4
#   cfgrib
#   pygrib
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=cfgrib.${METPLUS_VERSION}

BASE_ENV=metplus_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge \
  metpy~=1.7.1 \
  netcdf4~=1.7.4 \
  cfgrib~=0.9.15.1 \
  pygrib~=2.1.8
