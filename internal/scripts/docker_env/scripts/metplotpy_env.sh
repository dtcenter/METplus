#! /bin/sh

################################################################################
# Environment: metplotpy.v13.0
# Updated: 2026-04-17 (mccabe@ucar.edu)
#   Update versions and remove plotly/kaleido/chrome dependency
# Updated: 2025-07-16 (johnhg@ucar.edu)
#   Increases plotly version from 6.0.0 to 6.1.1
#   Increases kaleido version from 0.2.1 to 1.0.0
# Updated: 2025-02-05 (mccabe@ucar.edu)
#   Adds Python packages needed to run METplotpy and METcalcpy
# Python Packages:
#   matplotlib
#   scipy
#   xarray
#   netcdf4
#   pyyaml
#   imageio
#   imutils
#   scikit-image
#   pint
#   metpy
#   cartopy
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=metplotpy.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

mamba install -y --name ${ENV_NAME} -c conda-forge \
  matplotlib~=3.10.8 \
  scipy~=1.17.1 \
  xarray~=2026.4.0 \
  netcdf4~=1.7.4 \
  pyyaml~=6.0.3 \
  imageio~=2.37.0 \
  imutils~=0.5.4 \
  scikit-image~=0.26.0 \
  pint~=0.25.3 \
  metpy~=1.7.1 \
  cartopy~=0.25.0
