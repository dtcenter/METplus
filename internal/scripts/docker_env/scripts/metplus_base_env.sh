#! /bin/sh

################################################################################
# Environment: metplus_base (v5.1)
# Last Updated: 2023-01-25 (mccabe@ucar.edu)
# Notes: Move logic to create METplus base env to script so it can be called
#   on a local machine to create the environment
# Python Packages:
#   python-dateutil==2.8.2
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=metplus_base.${METPLUS_VERSION}

mamba create -y --name ${ENV_NAME} -c conda-forge python=3.10.4
mamba install -y --name ${ENV_NAME} -c conda-forge python-dateutil==2.8.2
