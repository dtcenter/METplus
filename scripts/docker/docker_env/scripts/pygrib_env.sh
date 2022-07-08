#! /bin/sh

################################################################################
# Environment: pygrib.v5
# Last Updated: 2022-06-16 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to read GRIB data
# Python Packages:
# TODO: update version numbers!
#   pygrib==2.0.2
#   metpy==1.0.1
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=pygrib.v5

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.v5


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

conda install -y --name ${ENV_NAME} -c conda-forge pygrib #==2.0.2
conda install -y --name ${ENV_NAME} -c conda-forge metpy #==1.0.1
