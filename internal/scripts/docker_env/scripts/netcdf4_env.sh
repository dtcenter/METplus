#! /bin/sh

################################################################################
# Environment: netcdf4.v5.1
# Last Updated: 2023-01-27 (mccabe@ucar.edu)
# Notes: Adds NetCDF4 Python package
# Python Packages:
#   netcdf4==1.6.2
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=netcdf4.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.6.2
