#! /bin/sh

################################################################################
# Environment: cfgrib
# Last Updated: 2021-07-20 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to read GRIB data into Xarray and
#   so it can easily be processed with MetPy
# Python Packages:
#   metpy==1.0.1
#   netcdf4==1.5.6
#   cfgrib==0.9.9.0
#   pygrib==2.1.3
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=cfgrib

conda create -y --name ${ENV_NAME} python=3.8.8
conda install -y --name ${ENV_NAME} -c conda-forge metpy==1.0.1
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.5.6
conda install -y --name ${ENV_NAME} -c conda-forge cfgrib==0.9.9.0
conda install -y --name ${ENV_NAME} -c conda-forge pygrib==2.1.3
