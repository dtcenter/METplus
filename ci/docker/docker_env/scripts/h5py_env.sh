#! /bin/sh

################################################################################
# Environment: h5py
# Last Updated: 2021-06-08 (mccabe@ucar.edu)
# Notes: Adds Python interface to the HDF5 binary format
# Python Packages:
#   h5py==2.10.0
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=h5py

# Conda environment to use as base for new environment
BASE_ENV=$1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge h5py==2.10.0
