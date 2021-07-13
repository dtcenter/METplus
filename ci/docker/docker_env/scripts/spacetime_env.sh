#! /bin/sh

################################################################################
# Environment: spacetime
# Last Updated: 2021-06-08 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to generate coherence spectra (METplotpy)
# Python Packages:
#   netCDF4==1.5.4
#   xarray==0.18.2
#   scipy==1.5.3
#   matplotlib==3.2.2
#   pyngl==1.6.1
#   pyyaml==5.3.1
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=spacetime

# Conda environment to use as base for new environment
# Not used in this script because Python version differs from base version
BASE_ENV=$1


conda create -y --name ${ENV_NAME} python=3.8

conda install -y --name ${ENV_NAME} -c conda-forge netCDF4==1.5.4
conda install -y --name ${ENV_NAME} -c conda-forge xarray==0.18.2
conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.5.3
conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.2.2
conda install -y --name ${ENV_NAME} -c conda-forge pyngl==1.6.1
conda install -y --name ${ENV_NAME} -c conda-forge pyyaml==5.3.1

# tested using anaconda channel but changed to using conda-forge
#conda install -y --name ${ENV_NAME} -c anaconda pyyaml
