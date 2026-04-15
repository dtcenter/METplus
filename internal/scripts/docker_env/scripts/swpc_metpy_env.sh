#! /bin/sh

################################################################################
# Environment: swpc_metpy.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds MetPy version with support for geospatial_gradient
################################################################################

# Conda environment to create
ENV_NAME=swpc_metpy.v6.1

mamba create -y --name ${ENV_NAME} -c conda-forge python=3.14.4
mamba install -y --name ${ENV_NAME} -c conda-forge \
  xarray \
  netcdf4 \
  pyyaml \
  scipy \
  metpy
