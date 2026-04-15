#! /bin/sh

################################################################################
# Environment: py_embed_base.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Move logic to create METplus base env to script so it can be called
#   on a local machine to create the environment
# Python Packages:
#   xarray
#   netcdf4
#   pyyaml
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v6.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=py_embed_base.${METPLUS_VERSION}

mamba create -y --name ${ENV_NAME} -c conda-forge python=3.14.4
mamba install -y --name ${ENV_NAME} -c conda-forge \
  xarray~=2026.4.0 \
  netcdf4~=1.7.4 \
  pyyaml~=6.0.3 \
  scipy~=1.17.1
