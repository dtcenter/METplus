#! /bin/sh

################################################################################
# Environment: spacetime.v5.1
# Last Updated: 2023-01-27 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to generate coherence spectra (METplotpy)
# Python Packages:
#   netCDF4==
#   xarray==
#   scipy==
#   matplotlib==
#   pyngl==
#   pyyaml==
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=spacetime.${METPLUS_VERSION}

conda create -y --name ${ENV_NAME} -c conda-forge python=3.10.4

conda install -y --name ${ENV_NAME} -c conda-forge netCDF4
conda install -y --name ${ENV_NAME} -c conda-forge xarray
conda install -y --name ${ENV_NAME} -c conda-forge scipy
conda install -y --name ${ENV_NAME} -c conda-forge matplotlib
conda install -y --name ${ENV_NAME} -c conda-forge pyngl
conda install -y --name ${ENV_NAME} -c conda-forge pyyaml
