#! /bin/sh

################################################################################
# Environment: cycloneplotter
# Last Updated: 2022-07-08 (mccabe@ucar.edu)
# Notes: Adds packages needed to run CyclonePlotter wrapper
#   Added pandas because it is used by tc_and_extra_tc use case
# Python Packages:
#   cartopy==0.20.3
#   matplotlib==3.5.2
#   pandas==1.4.3
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=cycloneplotter.v5

# Conda environment to use as base for new environment
BASE_ENV=metplus_base.v5

conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}
conda install -y --name ${ENV_NAME} -c conda-forge cartopy==0.20.3
conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.5.2
conda install -y --name ${ENV_NAME} -c conda-forge pandas==1.4.3

yum -y install wget
wget https://raw.githubusercontent.com/SciTools/cartopy/master/tools/cartopy_feature_download.py
/usr/local/envs/${ENV_NAME}/bin/python3 cartopy_feature_download.py cultural physical
