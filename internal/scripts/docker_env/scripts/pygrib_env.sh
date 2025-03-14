#! /bin/sh

################################################################################
# Environment: pygrib.v6.1
# Last Updated: 2025-02-05 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to read GRIB data
# Python Packages:
#   pygrib==2.1.6
#   metpy==1.6.3
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=pygrib.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.${METPLUS_VERSION}


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

mamba install -y --name ${ENV_NAME} -c conda-forge \
  pygrib==2.1.6 \
  metpy==1.6.3
