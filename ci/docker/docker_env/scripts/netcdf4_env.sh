#! /bin/sh

################################################################################
# Environment: netcdf4
# Last Updated: 2021-06-08 (mccabe@ucar.edu)
# Notes: Adds NetCDF4 Python package
# Python Packages:
#   netcdf4==1.5.6
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=netcdf4

# Conda environment to use as base for new environment
BASE_ENV=$1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.5.6
