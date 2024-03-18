#! /bin/sh

################################################################################
# Environment: cfgrib.v5.1
# Last Updated: 2023-01-27 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to read GRIB data into Xarray and
#   so it can easily be processed with MetPy
# Python Packages:
#   metpy==1.3.0
#   netcdf4==1.6.2
#   cfgrib==0.9.10.1
#   pygrib==2.1.4
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=cfgrib.${METPLUS_VERSION}

mamba create -y --name ${ENV_NAME} -c conda-forge python=3.10.4
mamba install -y --name ${ENV_NAME} -c conda-forge metpy==1.4.0 netcdf4==1.6.2 cfgrib==0.9.10.1 pygrib==2.1.4
