#! /bin/sh

################################################################################
# Environment: cfgrib.v5
# Last Updated: 2022-06-16 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to read GRIB data into Xarray and
#   so it can easily be processed with MetPy
# Python Packages:
#   metpy==1.3.0
#   netcdf4==1.5.8
#   cfgrib==0.9.10.1
#   pygrib==2.1.4
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=cfgrib.v5

conda create -y --name ${ENV_NAME} -c conda-forge python=3.8.6
conda install -y --name ${ENV_NAME} -c conda-forge metpy==1.3.0
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.5.8
conda install -y --name ${ENV_NAME} -c conda-forge cfgrib==0.9.10.1
conda install -y --name ${ENV_NAME} -c conda-forge pygrib==2.1.4
