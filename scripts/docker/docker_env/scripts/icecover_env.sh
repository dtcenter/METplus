#! /bin/sh

################################################################################
# Environment: icecover
# Last Updated: 2022-07-08 (mccabe@ucar.edu)
# Notes: Adds Python packages required for ice cover use case
# Python Packages:
# TODO: update package versions
#   pyproj==
#   pyresample==
#   scikit-learn==
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=icecover.v5

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.v5

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge xarray
conda install -y --name ${ENV_NAME} -c conda-forge pyresample
conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn
conda install -y --name ${ENV_NAME} -c conda-forge pyproj
