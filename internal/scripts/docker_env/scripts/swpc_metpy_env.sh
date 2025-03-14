#! /bin/sh

################################################################################
# Environment: swpc_metpy.v6.1
# Last Updated: 2025-02-07 (mccabe@ucar.edu)
# Notes: Adds MetPy version with support for geospatial_gradient
################################################################################

# Conda environment to create
ENV_NAME=swpc_metpy.v6.1

mamba create -y --name ${ENV_NAME} -c conda-forge python=3.12.0
mamba install -y --name ${ENV_NAME} -c conda-forge \
  xarray==2025.1.2 \
  netcdf4==1.7.2 \
  pyyaml==6.0.2 \
  scipy=1.15.1 \
  metpy==1.6.3
