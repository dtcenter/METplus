#! /bin/sh

################################################################################
# Environment: metdataio.v5.1
# Last Updated: 2023-01-27 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METdbLoad from METdataio
# Python Packages:
#   lxml==4.9.1
#   pymysql==1.0.2
#   pandas==1.2.3
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=metdataio.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}

mamba install -y --name ${ENV_NAME} -c conda-forge lxml==4.9.1
mamba install -y --name ${ENV_NAME} -c conda-forge pymysql==1.0.2
mamba install -y --name ${ENV_NAME} -c conda-forge pandas==1.5.1
