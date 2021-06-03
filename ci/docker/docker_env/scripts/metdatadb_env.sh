#! /bin/sh

################################################################################
# Environment: metdatadb
# Last Updated: 2021-06-03 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METdbLoad from METdatadb
# Python Packages:
#   lxml==?
#   pymysql==?
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=metdatadb

# Conda environment to use as base for new environment
BASE_ENV=$1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

conda install -y --name ${ENV_NAME} -c conda-forge lxml pymysql
