#! /bin/sh

################################################################################
# Environment: spacetime.v5.1
# Last Updated: 2023-01-27 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to generate coherence spectra (METplotpy)
# Python Packages:
#   netCDF4==1.5.8
#   xarray==2022.3.0
#   scipy==1.8.1
#   matplotlib==3.5.2
#   pyngl==1.6.1
#   pyyaml==6.0
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=spacetime.v5.1

conda create -y --name ${ENV_NAME} -c conda-forge python=3.10.4

conda install -y --name ${ENV_NAME} -c conda-forge netCDF4==1.5.8
conda install -y --name ${ENV_NAME} -c conda-forge xarray==2022.3.0
conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.8.1
conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.5.2
conda install -y --name ${ENV_NAME} -c conda-forge pyngl==1.6.1
conda install -y --name ${ENV_NAME} -c conda-forge pyyaml==6.0
