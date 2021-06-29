#! /bin/sh

################################################################################
# Environment: metplotpy
# Last Updated: 2021-06-08 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METplotpy and METcalcpy
#   Uses pip to install kaleido because
#   could not install via Conda (glibc conflict)
# Python Packages:
#   matplotlib==3.3.0
#   scipy==1.5.1
#   plotly==4.9.0
#   pingouin==0.3.8
#   cartopy==0.18.0
#   eofs==1.3.0
#   cmocean==2.0
#   xarray==0.17
#   netcdf4==1.5.6
#   pyyaml==?
#   python-kaleido==0.2.1
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=weatherregime

# Conda environment to use as base for new environment
BASE_ENV=$1


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn==0.24.2
conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.5.4
conda install -y --name ${ENV_NAME} -c conda-forge eofs==1.4.0
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.5.7
conda install -y --name ${ENV_NAME} -c conda-forge numpy==1.19.5
