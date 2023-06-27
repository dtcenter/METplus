#! /bin/sh

################################################################################
# Environment: diff.v5.1
# Last Updated: 2023-06-14 (mccabe@ucar.edu)
# Notes: Adds packages needed to run differences tests to compare output to
#   truth data.
# Python Packages:
#   pandas==2.0.2
#   pillow==9.2.0
#   pdf2image==1.16.0
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
conda install -y --name ${ENV_NAME} -c conda-forge pandas==2.0.2
conda install -y --name ${ENV_NAME} -c conda-forge pillow==9.2.0

apt-get update
apt-get install -y poppler-utils

conda install -y --name ${ENV_NAME} -c conda-forge pdf2image==1.16.0
