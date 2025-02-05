#! /bin/sh

################################################################################
# Environment: metplotpy.v6.1
# Last Updated: 2025-02-05 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METplotpy and METcalcpy
# Python Packages:
#   matplotlib==
#   scipy==1.15.1
#   plotly==
#   xarray==2025.1.2
#   netcdf4==1.7.2
#   pyyaml==6.0.2
#   statsmodels==
#   python-kaleido==
#   imageio==
#   imutils==
#   scikit-image==
#   pint==
#   metpy=
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

mamba install -y --name ${ENV_NAME} -c conda-forge \
  matplotlib \
  scipy==1.15.1 \
  plotly \
  xarray==2025.1.2 \
  netcdf4==1.7.2 \
  pyyaml==6.0.2 \
  python-kaleido \
  imageio \
  imutils \
  scikit-image \
  pint \
  metpy \
  cartopy
