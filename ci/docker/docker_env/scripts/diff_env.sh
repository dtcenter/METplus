#! /bin/sh

################################################################################
# Environment: diff
# Last Updated: 2021-06-08 (mccabe@ucar.edu)
# Notes: Adds packages needed to run differences tests to compare output to
#   truth data.
# Python Packages:
#   pillow==?
#   pdf2image==?
#
# Other Content:
#   poppler-utils
################################################################################

# Conda environment to create
ENV_NAME=diff

# Conda environment to use as base for new environment
BASE_ENV=$1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge pillow

yum -y install poppler-utils

conda install -y --name ${ENV_NAME} -c conda-forge pdf2image
