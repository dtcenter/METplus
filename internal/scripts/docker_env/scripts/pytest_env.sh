#! /bin/sh

################################################################################
# Environment: pytest.v5.1
# Last Updated: 2023-01-31 (mccabe@ucar.edu)
# Notes: Adds pytest and pytest coverage packages to run unit tests
#   Added pandas because plot_util test needs it
#   Added netcdf4 because SeriesAnalysis test needs it
# Python Packages:
# TODO: update version numbers
#   pytest==?
#   pytest-cov==?
#   pandas==?
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=pytest.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge pytest
conda install -y --name ${ENV_NAME} -c conda-forge pytest-cov
conda install -y --name ${ENV_NAME} -c conda-forge pandas
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4
