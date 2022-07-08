#! /bin/sh

################################################################################
# Environment: metdatadb.v5
# Last Updated: 2021-06-08 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METdbLoad from METdatadb
# Python Packages:
# TODO: update versions
#   lxml==3.8.0
#   pymysql==1.0.2
#   pandas==1.1.4
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=metdatadb.v5

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.v5

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

conda install -y --name ${ENV_NAME} -c conda-forge lxml #==3.8.0
conda install -y --name ${ENV_NAME} -c conda-forge pymysql #==1.0.2
conda install -y --name ${ENV_NAME} -c conda-forge pandas #==1.1.4
