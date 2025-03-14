#! /bin/sh

################################################################################
# Environment: icecover.v6.1
# Last Updated: 2025-02-05 (mccabe@ucar.edu)
# Notes: Adds Python packages required for ice cover use case
# Python Packages:
#   xarray==2025.1.2
#   pyresample==1.32.0
#   scikit-learn==1.6.1
#   pyproj==3.7.0
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=icecover.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.${METPLUS_VERSION}

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge \
  xarray==2025.1.2 \
  pyresample==1.32.0 \
  scikit-learn==1.6.1 \
  pyproj==3.7.0
