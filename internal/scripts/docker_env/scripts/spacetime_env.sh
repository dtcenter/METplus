#! /bin/sh

################################################################################
# Environment: spacetime.v6.0
# Last Updated: 2023-09-12 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to generate coherence spectra (METplotpy)
# Python Packages:
#   netCDF4==1.6.4
#   xarray==2023.8.0
#   scipy==1.11.2
#   matplotlib==3.7.2
#   pyngl==1.6.1
#   pyyaml==6.0.1
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=spacetime.${METPLUS_VERSION}

conda create -y --name ${ENV_NAME} -c conda-forge python=3.10.4

conda install -y --name ${ENV_NAME} -c conda-forge netCDF4==1.6.4
conda install -y --name ${ENV_NAME} -c conda-forge xarray==2023.8.0
conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.11.2
conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.7.2
conda install -y --name ${ENV_NAME} -c conda-forge pyngl==1.6.1
conda install -y --name ${ENV_NAME} -c conda-forge pyyaml==6.0.1
