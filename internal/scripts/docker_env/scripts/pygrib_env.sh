#! /bin/sh

################################################################################
# Environment: pygrib.v5.1
# Last Updated: 2023-01-27 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to read GRIB data
# Python Packages:
#   pygrib==2.1.4
#   metpy==1.3.0
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=pygrib.v5.1

# Conda environment to use as base for new environment
BASE_ENV=py_embed_base.v5.1


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

conda install -y --name ${ENV_NAME} -c conda-forge pygrib==2.1.4
conda install -y --name ${ENV_NAME} -c conda-forge metpy==1.3.0
