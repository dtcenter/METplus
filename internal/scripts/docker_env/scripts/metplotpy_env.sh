#! /bin/sh

################################################################################
# Environment: metplotpy.v6.1
# Updated: 2025-07-16 (johnhg@ucar.edu)
#   Increases plotly version from 6.0.0 to 6.1.1
#   Increases kaleido version from 0.2.1 to 1.0.0
# Updated: 2025-02-05 (mccabe@ucar.edu)
#   Adds Python packages needed to run METplotpy and METcalcpy
# Python Packages:
#   matplotlib==3.10.0
#   scipy==1.15.1
#   plotly==6.1.1
#   xarray==2025.1.2
#   netcdf4==1.7.2
#   pyyaml==6.0.2
#   python-kaleido==1.0.0
#   imageio==2.37.0
#   imutils==0.5.4
#   scikit-image==0.25.1
#   pint==0.24.4
#   metpy==1.6.3
#   cartopy==0.24.0
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
  matplotlib==3.10.0 \
  scipy==1.15.1 \
  plotly==6.1.1 \
  xarray==2025.1.2 \
  netcdf4==1.7.2 \
  pyyaml==6.0.2 \
  imageio==2.37.0 \
  imutils==0.5.4 \
  scikit-image==0.25.1 \
  pint==0.24.4 \
  metpy==1.6.3 \
  cartopy==0.24.0

# install kaleido via pip because (as of 2024/07/24) kaleido 1.0.0 from
# conda-forge is installed as 0.0.0 and the plotly_get_chrome script fails
# due to the version check
/usr/local/conda/envs/${ENV_NAME}/bin/pip install kaleido==1.0.0

# install chrome which is required by plotly/kaleido
/usr/local/conda/envs/${ENV_NAME}/bin/plotly_get_chrome -y
