#! /bin/sh

################################################################################
# Environment: icecover
# Last Updated: 2022-07-08 (mccabe@ucar.edu)
# Notes: Adds Python packages required for ice cover use case
# Python Packages:
#   xarray==2022.3.0
#   pyresample==1.24.1
#   scikit-learn==1.1.1
#   pyproj==3.3.1
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=icecover.v5

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.v5

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge xarray==2022.3.0
conda install -y --name ${ENV_NAME} -c conda-forge pyresample==1.24.1
conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn==1.1.1
conda install -y --name ${ENV_NAME} -c conda-forge pyproj==3.3.1
