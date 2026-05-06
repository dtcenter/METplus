#! /bin/sh

################################################################################
# Environment: diff.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds packages needed to run differences tests to compare output to
#   truth data.
# Python Packages:
#   pandas
#   pillow
#   pdf2image
#
# Other Content:
#   poppler-utils
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=diff.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=netcdf4.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge \
  pandas \
  pillow

apt-get update
apt-get install -y poppler-utils

mamba install -y --name ${ENV_NAME} -c conda-forge pdf2image
