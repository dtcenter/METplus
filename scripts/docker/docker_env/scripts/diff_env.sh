#! /bin/sh

################################################################################
# Environment: diff.v5
# Last Updated: 2022-07-08 (mccabe@ucar.edu)
# Notes: Adds packages needed to run differences tests to compare output to
#   truth data.
# TODO: update version numbers
# Python Packages:
#   pillow==?
#   pdf2image==?
#
# Other Content:
#   poppler-utils
################################################################################

# Conda environment to create
ENV_NAME=diff.v5

# Conda environment to use as base for new environment
BASE_ENV=netcdf4.v5

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge pillow

yum -y install poppler-utils

conda install -y --name ${ENV_NAME} -c conda-forge pdf2image
