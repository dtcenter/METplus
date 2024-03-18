#! /bin/sh

################################################################################
# Environment: metplotpy.v5.1
# Last Updated: 2023-01-30 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METplotpy and METcalcpy
# Python Packages:
#   matplotlib==3.5.2
#   scipy==1.8.1
#   plotly==5.9.0
#   xarray==2022.3.0
#   netcdf4==1.6.2
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

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=metplotpy.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}

mamba install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.6.3 scipy==1.9.3 plotly==5.13.0 xarray==2023.1.0 netcdf4==1.6.2 pyyaml==6.0 python-kaleido==0.2.1 imageio==2.25.0 imutils==0.5.4 scikit-image pint==0.20.1 metpy cartopy==0.21.1
