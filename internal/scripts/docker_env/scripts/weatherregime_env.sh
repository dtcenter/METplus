#! /bin/sh

################################################################################
# Environment: weatherregime.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run weather regime use case
#  METplotpy and METcalcpy
# Python Packages:
#   All packages from metplotpy.v6.1
#   scikit-learn
#   eofs
#   cmocean
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=weatherregime.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplotpy.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge \
  scikit-learn~=1.8.0 \
  eofs~=2.0.0 \
  cmocean~=4.0.3
