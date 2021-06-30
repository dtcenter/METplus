#! /bin/sh

################################################################################
# Environment: pytest
# Last Updated: 2021-06-08 (mccabe@ucar.edu)
# Notes: Adds pytest and pytest coverage packages to run unit tests
#   Added pandas because plot_util test needs it
#   Added netcdf4 because SeriesAnalysis test needs it
# Python Packages:
#   pytest==?
#   pytest-cov==?
#   pandas==?
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
conda install -y --name ${ENV_NAME} -c conda-forge pandas
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4
