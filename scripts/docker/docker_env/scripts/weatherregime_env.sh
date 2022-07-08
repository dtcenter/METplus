#! /bin/sh

################################################################################
# Environment: weatherregime.v5
# Last Updated: 2022-06-16 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run weather regime use case
#  METplotpy and METcalcpy
# Python Packages:
# TODO: update versions
#   All packages from metplotpy_env
#   scikit-learn==0.24.2
#   eofs==1.4.0
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=weatherregime.v5

# Conda environment to use as base for new environment
BASE_ENV=metplotpy.v5


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn #==0.24.2
conda install -y --name ${ENV_NAME} -c conda-forge eofs #==1.4.0

rm cartopy_feature_download.py
yum -y install wget
wget https://raw.githubusercontent.com/SciTools/cartopy/master/tools/cartopy_feature_download.py
/usr/local/envs/${ENV_NAME}/bin/python3 cartopy_feature_download.py cultural physical cultural-extra
