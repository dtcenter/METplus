#! /bin/sh

################################################################################
# Environment: zarr.v13.0
# Last Updated: 2026-05-22 (mccabe@ucar.edu)
# Notes: Adds Zarr-Python
# Python Packages:
#   zarr
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v13.0
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=zarr.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge \
  zarr
