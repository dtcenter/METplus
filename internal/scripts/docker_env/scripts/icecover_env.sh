#! /bin/sh

################################################################################
# Environment: icecover.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds Python packages required for ice cover use case
# Python Packages:
#   xarray
#   pyresample
#   scikit-learn
#   pyproj
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
mamba install -y --name ${ENV_NAME} -c conda-forge \
  xarray~=2026.4.0 \
  pyresample~=1.35.0 \
  scikit-learn~=1.8.0 \
  pyproj~=3.7.2
