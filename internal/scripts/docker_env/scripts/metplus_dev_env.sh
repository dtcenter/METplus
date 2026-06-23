#! /bin/sh

################################################################################
# Environment: metplus_dev.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds Python packages used to build documentation and run unit tests
# Python Packages:
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=metplus_dev.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

mamba install -y --name ${ENV_NAME} -c conda-forge \
  pytest-cov

# install documentation requirements using requirements.txt file from docs directory
curl https://raw.githubusercontent.com/dtcenter/METplus/refs/heads/develop/docs/requirements.txt --output docs_requirements.txt
conda install --force-reinstall -y --name ${ENV_NAME} -c conda-forge --file docs_requirements.txt
rm docs_requirements.txt
