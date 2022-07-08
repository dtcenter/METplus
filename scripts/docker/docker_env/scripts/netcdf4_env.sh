#! /bin/sh

################################################################################
# Environment: netcdf4
# Last Updated: 2022-06-16 (mccabe@ucar.edu)
# Notes: Adds NetCDF4 Python package
# Python Packages:
# TODO: update version numbers
#   netcdf4==1.5.6
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=netcdf4.v5

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.v5

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4 #==1.5.6
