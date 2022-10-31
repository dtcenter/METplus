#! /bin/sh

################################################################################
# Environment: metplotpy
# Last Updated: 2022-06-14 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METplotpy and METcalcpy
# Python Packages:
#   matplotlib==3.5.2
#   scipy==1.8.1
#   plotly==5.9.0
#   xarray==2022.3.0
#   netcdf4==1.6.0
#   pyyaml==6.0
#   statsmodels==0.13.2
#   python-kaleido==0.2.1
#   imageio==2.19.3
#   imutils==0.5.4
#   scikit-image==0.19.3
#   pint==0.19.2
#   metpy=1.3.1
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=metplotpy.v5

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.v5


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.5.2
conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.8.1
conda install -y --name ${ENV_NAME} -c conda-forge plotly==5.9.0
conda install -y --name ${ENV_NAME} -c conda-forge xarray==2022.3.0
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.6.0
conda install -y --name ${ENV_NAME} -c conda-forge pyyaml==6.0
conda install -y --name ${ENV_NAME} -c conda-forge statsmodels==0.13.2
conda install -y --name ${ENV_NAME} -c conda-forge python-kaleido==0.2.1
conda install -y --name ${ENV_NAME} -c conda-forge imageio==2.19.3
conda install -y --name ${ENV_NAME} -c conda-forge imutils==0.5.4
conda install -y --name ${ENV_NAME} -c conda-forge scikit-image==0.19.3
conda install -y --name ${ENV_NAME} -c conda-forge pint==0.19.2
conda install -y --name ${ENV_NAME} -c conda-forge metpy=1.3.1

yum -y install wget
wget https://raw.githubusercontent.com/SciTools/cartopy/master/tools/cartopy_feature_download.py
/usr/local/envs/${ENV_NAME}/bin/python3 cartopy_feature_download.py cultural physical
