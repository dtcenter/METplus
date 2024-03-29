#! /bin/sh

################################################################################
# Environment: weatherregime.v5.1
# Last Updated: 2023-01-30 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run weather regime use case
#  METplotpy and METcalcpy
# Python Packages:
#   All packages from metplotpy.v5
#   scikit-learn==1.1.1
#   eofs==1.4.0
#   cmocean==2.0
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
conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn==1.1.1
conda install -y --name ${ENV_NAME} -c conda-forge eofs==1.4.0
conda install -y --name ${ENV_NAME} -c conda-forge cmocean==2.0
