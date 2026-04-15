#! /bin/sh

################################################################################
# Environment: metdataio.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METdbLoad from METdataio
# Python Packages:
#   pymysql
#   pyyaml
#   xarray
#   lxml
#   netcdf4
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=metdataio.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

mamba install -y --name ${ENV_NAME} -c conda-forge \
  pymysql~=1.1.2 \
  pyyaml~=6.0.3 \
  xarray~=2026.4.0 \
  lxml~=6.0.4 \
  netcdf4~=1.7.4
