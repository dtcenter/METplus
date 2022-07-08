#! /bin/sh

################################################################################
# Environment: cycloneplotter
# Last Updated: 2022-07-08 (mccabe@ucar.edu)
# Notes: Adds packages needed to run CyclonePlotter wrapper
#   Added pandas because it is used by tc_and_extra_tc use case
# Python Packages:
# TODO: update versions
#   cartopy==
#   matplotlib==
#   pandas==
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=cycloneplotter.v5

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.v5

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge cartopy
conda install -y --name ${ENV_NAME} -c conda-forge matplotlib
conda install -y --name ${ENV_NAME} -c conda-forge pandas

yum -y install wget
wget https://raw.githubusercontent.com/SciTools/cartopy/master/tools/cartopy_feature_download.py
/usr/local/envs/${ENV_NAME}/bin/python3 cartopy_feature_download.py cultural physical
