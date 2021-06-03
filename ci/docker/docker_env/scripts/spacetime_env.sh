#! /bin/sh

################################################################################
# Environment: spacetime
# Last Updated: 2021-06-03 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to generate coherence spectra (METplotpy)
# Python Packages:
#   netCDF4==?
#   xarray==?
#   scipy==?
#   matplotlib==?
#   pyngl==?
#   pyyaml==?
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=spacetime_env

# Conda environment to use as base for new environment
# Not used in this script because Python version differs from base version
BASE_ENV=$1


conda create -y --name ${ENV_NAME} python=3.8

conda install -y --name ${ENV_NAME} -c conda-forge netCDF4
conda install -y --name ${ENV_NAME} -c conda-forge xarray
conda install -y --name ${ENV_NAME} -c conda-forge scipy
conda install -y --name ${ENV_NAME} -c conda-forge matplotlib
conda install -y --name ${ENV_NAME} -c conda-forge pyngl
conda install -y --name ${ENV_NAME} -c conda-forge pyyaml
conda install -y --name ${ENV_NAME} -c conda-forge 
# tested using anaconda channel but changed to using conda-forge
#conda install -y --name ${ENV_NAME} -c anaconda pyyaml
