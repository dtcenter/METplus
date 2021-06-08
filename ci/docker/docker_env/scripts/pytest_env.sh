#! /bin/sh

################################################################################
# Environment: pytest
# Last Updated: 2021-06-08 (mccabe@ucar.edu)
# Notes: Adds pytest and pytest coverage packages to run unit tests
# Python Packages:
#   pytest==?
#   pytest-cov==?
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=pytest

# Conda environment to use as base for new environment
BASE_ENV=$1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge pytest
conda install -y --name ${ENV_NAME} -c conda-forge pytest-cov
