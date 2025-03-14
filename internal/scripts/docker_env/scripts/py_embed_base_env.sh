#! /bin/sh

################################################################################
# Environment: py_embed_base.v6.1
# Last Updated: 2025-02-05 (mccabe@ucar.edu)
# Notes: Move logic to create METplus base env to script so it can be called
#   on a local machine to create the environment
# Python Packages:
#   xarray==2025.1.2
#   netcdf4==1.7.2
#   pyyaml==6.0.2
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v6.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=py_embed_base.${METPLUS_VERSION}

mamba create -y --name ${ENV_NAME} -c conda-forge python=3.12.0
mamba install -y --name ${ENV_NAME} -c conda-forge xarray==2025.1.2 netcdf4==1.7.2 pyyaml==6.0.2 scipy=1.15.1
