#! /bin/sh

################################################################################
# Environment: spacetime.v6.1
# Last Updated: 2025-02-05 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to generate coherence spectra (METplotpy)
# Python Packages:
#   netCDF4==1.7.2
#   xarray==2025.1.2
#   scipy==1.15.1
#   matplotlib==
#   pyngl==
#   pyyaml==6.0.2
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=spacetime.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge netCDF4==1.7.2 xarray==2025.1.2 scipy==1.15.1 matplotlib pyngl pyyaml==6.0.2
