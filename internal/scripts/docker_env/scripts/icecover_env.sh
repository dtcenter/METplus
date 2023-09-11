#! /bin/sh

################################################################################
# Environment: icecover.v5.1
# Last Updated: 2023-01-31 (mccabe@ucar.edu)
# Notes: Adds Python packages required for ice cover use case
# Python Packages:
#   xarray==
#   pyresample==
#   scikit-learn==
#   pyproj==
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=icecover.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge xarray
conda install -y --name ${ENV_NAME} -c conda-forge pyresample
conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn
conda install -y --name ${ENV_NAME} -c conda-forge pyproj
