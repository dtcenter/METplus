#! /bin/sh

################################################################################
# Environment: mp_analysis.v6.0
# Last Updated: 2024-02-06 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METplotpy and METdataio
# Python Packages:
#   All packages from metplotpy
#   lxml==4.9.1
#   pymysql==1.0.2
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v6.0
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=mp_analysis.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplotpy.${METPLUS_VERSION}

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge lxml==4.9.1 pymysql==1.0.2
