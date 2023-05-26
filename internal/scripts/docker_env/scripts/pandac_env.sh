#! /bin/sh

################################################################################
# Environment: pandac.v5.1
# Last Updated: 2023-05-25 (mccabe@ucar.edu)
# Notes: Adds Python packages needed for PANDA-C use cases
# Python Packages:
#   scipy==1.10.1
#   matplotlib==3.6.3
#   pygrib==2.1.4
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=pandac.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.${METPLUS_VERSION}


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.10.1
conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.6.3
conda install -y --name ${ENV_NAME} -c conda-forge pygrib==2.1.4
