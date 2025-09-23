#! /bin/sh

################################################################################
# Environment: requests.v6.1
# Last Updated: 2025-09-23 (mccabe@ucar.edu)
# Notes: Adds requests Python package
# Python Packages:
#   requests==
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=requests.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge requests
