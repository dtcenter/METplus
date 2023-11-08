#! /bin/sh

################################################################################
# Environment: swpc_metpy.v5
# Last Updated: 2022-12-28 (mccabe@ucar.edu)
# Notes: Adds MetPy version with support for geospatial_gradient
# Python Packages:
#   metpy==1.4
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=swpc_metpy.v5

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.v5

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge metpy==1.4
