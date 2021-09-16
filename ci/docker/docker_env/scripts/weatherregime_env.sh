#! /bin/sh

################################################################################
# Environment: weatherregime
# Last Updated: 2021-09-16 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run weather regime use case
#  METplotpy and METcalcpy
# Python Packages:
#   All packages from metplotpy_env
#   scikit-learn==0.24.2
#   eofs==1.4.0
#   netcdf4==1.5.7
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=weatherregime

# Conda environment to use as base for new environment
BASE_ENV=$1


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn==0.24.2
conda install -y --name ${ENV_NAME} -c conda-forge eofs==1.4.0
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.5.7
