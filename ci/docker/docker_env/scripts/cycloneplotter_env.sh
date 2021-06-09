#! /bin/sh

################################################################################
# Environment: cycloneplotter
# Last Updated: 2021-06-09 (mccabe@ucar.edu)
# Notes: Adds packages needed to run CyclonePlotter wrapper
# Python Packages:
#   cartopy==0.17.0
#   matplotlib==3.3.0
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=cycloneplotter

# Conda environment to use as base for new environment
BASE_ENV=$1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge cartopy==0.17.0
conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.3.0
