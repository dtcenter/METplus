#! /bin/sh

################################################################################
# Environment: metplus_dev.v6.1
# Last Updated: 2025-03-14 (mccabe@ucar.edu)
# Notes: Adds Python packages used to build documentation and run unit tests
# Python Packages:
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=metplus_dev.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=diff.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

mamba install -y --name ${ENV_NAME} -c conda-forge pytest-cov
