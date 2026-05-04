#! /bin/sh

################################################################################
# Environment: pandac.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds Python packages needed for PANDA-C use cases
# Python Packages:
#   All packages from metplotpy.v6.1
#   pygrib
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=pandac.${METPLUS_VERSION}

# Conda environment to use as base for new environment
#BASE_ENV=py_embed_base.${METPLUS_VERSION}
BASE_ENV=metplotpy.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge \
  pygrib~=2.1.8
