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

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=h5py.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.${METPLUS_VERSION}

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge h5py==3.6.0
