#! /bin/sh

################################################################################
# Environment: rioxarray.v6.1
# Last Updated: 2025-05-20 (mccabe@ucar.edu)
# Notes: Adds rioxarray package to read GeoTIFF files
# Python Packages:
#   rioxarray==
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v6.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=rioxarray.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge rioxarray
