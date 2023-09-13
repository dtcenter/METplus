#! /bin/sh

################################################################################
# Environment: icecover.v6.0
# Last Updated: 2023-09-12 (mccabe@ucar.edu)
# Notes: Adds Python packages required for ice cover use case
# Python Packages:
#   xarray==2023.5.0
#   pyresample==1.27.1
#   scikit-learn==1.3.0
#   pyproj==3.6.0
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
conda install -y --name ${ENV_NAME} -c conda-forge xarray==2023.5.0
conda install -y --name ${ENV_NAME} -c conda-forge pyresample==1.27.1
conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn==1.3.0
conda install -y --name ${ENV_NAME} -c conda-forge pyproj==3.6.0
