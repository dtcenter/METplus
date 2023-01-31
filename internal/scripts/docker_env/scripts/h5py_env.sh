#! /bin/sh

################################################################################
# Environment: h5py.v5.1
# Last Updated: 2023-01-27 (mccabe@ucar.edu)
# Notes: Adds Python interface to the HDF5 binary format
# Python Packages:
#   h5py==3.6.0
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=h5py.v5.1

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.v5.1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge h5py==3.6.0
