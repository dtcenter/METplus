#! /bin/sh

################################################################################
# Environment: metplus_base (v5)
# Last Updated: 2022-05-12 (mccabe@ucar.edu)
# Notes: Move logic to create METplus base env to script so it can be called
#   on a local machine to create the environment
# Python Packages:
#   python-dateutil==2.8.2
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=metplus_base.v5

conda create -y --name ${ENV_NAME} -c conda-forge python=3.8.6
conda install -y --name ${ENV_NAME} -c conda-forge python-dateutil==2.8.2
