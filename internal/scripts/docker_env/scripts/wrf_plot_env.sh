#! /bin/sh

################################################################################
# Environment: wrf_plot.v6.1
# Last Updated: 2025-06-04 (mccabe@ucar.edu)
# Notes: Adds wrf package to read WRF files to METplus Analysis packages
# Python Packages:
#   wrf==
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v6.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=wrf_plot.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=mp_analysis.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge wrf-python
