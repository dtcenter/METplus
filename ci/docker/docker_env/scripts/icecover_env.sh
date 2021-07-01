#! /bin/sh

################################################################################
# Environment: icecover
# Last Updated: 2021-06-29 (mccabe@ucar.edu)
# Notes: Adds Python packages required for ice cover use case
# Python Packages:
#   pyproj==3.0.1
#   pyresample==1.20.0
#   scikit-learn==0.24.2
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=icecover

# Conda environment to use as base for new environment
BASE_ENV=$1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge xarray==0.18.2
conda install -y --name ${ENV_NAME} -c conda-forge pyresample==1.16.0
conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn==0.23.2
#conda install -y --name ${ENV_NAME} -c conda-forge pyproj==3.0.1
conda install -y --name ${ENV_NAME} -c conda-forge pyproj
