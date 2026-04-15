#! /bin/sh

################################################################################
# Environment: swpc_metpy.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds MetPy version with support for geospatial_gradient
################################################################################

# version of METplus when the environment was updated, e.g. v13.0
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=swpc_metpy.${METPLUS_VERSION}

mamba create -y --name ${ENV_NAME} -c conda-forge \
  python=3.14.4
mamba install -y --name ${ENV_NAME} -c conda-forge \
  xarray \
  netcdf4 \
  pyyaml \
  scipy \
  metpy
