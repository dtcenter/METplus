################################################################################
# Environment: mp_analysis.v13.0
# Last Updated: 2026-04-15 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METplotpy and METdataio
# Python Packages:
#   All packages from metplotpy
#   lxml
#   pymysql
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v6.0
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=mp_analysis.${METPLUS_VERSION}

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
  pint~=0.25.3 \
  metpy~=1.7.1 \
  cartopy~=0.25.0 \
  lxml~=6.0.4 \
  pymysql~=1.1.2
