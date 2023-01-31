#! /bin/sh

################################################################################
# Environment: netcdf4.v5.1
# Last Updated: 2023-01-27 (mccabe@ucar.edu)
# Notes: Adds NetCDF4 Python package
# Python Packages:
#   netcdf4==1.5.8
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=netcdf4.v5.1

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.v5.1

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.5.8
