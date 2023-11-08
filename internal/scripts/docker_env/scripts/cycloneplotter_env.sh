#! /bin/sh

################################################################################
# Environment: cycloneplotter.v5.1
# Last Updated: 2023-01-30 (mccabe@ucar.edu)
# Notes: Adds packages needed to run CyclonePlotter wrapper
#   Added pandas because it is used by tc_and_extra_tc use case
# Python Packages:
#   cartopy==0.20.3
#   matplotlib==3.5.2
#   pandas==1.4.3
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=cycloneplotter.${METPLUS_VERSION}

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.${METPLUS_VERSION}

mamba create -y --clone ${BASE_ENV} --name ${ENV_NAME}
mamba install -y --name ${ENV_NAME} -c conda-forge cartopy==0.20.3
mamba install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.5.2
mamba install -y --name ${ENV_NAME} -c conda-forge pandas==1.4.3
