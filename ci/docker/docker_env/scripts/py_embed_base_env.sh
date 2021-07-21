#! /bin/sh

################################################################################
# Environment: metplus_base
# Last Updated: 2021-07-06 (mccabe@ucar.edu)
# Notes: Move logic to create METplus base env to script so it can be called
#   on a local machine to create the environment
# Python Packages:
#   python-dateutil==2.8.1
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=py_embed_base

conda create -y --name ${ENV_NAME} python=3.6.8
conda install -y --name ${ENV_NAME} -c conda-forge xarray==0.16.2
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.5.6
