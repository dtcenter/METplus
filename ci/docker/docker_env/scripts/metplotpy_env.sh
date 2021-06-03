#! /bin/sh

################################################################################
# Environment: metplotpy
# Last Updated: 2021-06-03 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run METplotpy and METcalcpy
#   Uses pip to install kaleido because
#   could not install via Conda (glibc conflict)
# Python Packages:
#   matplotlib==3.3.0
#   scipy==1.5.1
#   plotly==4.9.0
#   pingouin==0.3.8
#   cartopy==0.17.0
#   eofs==1.3.0
#   cmocean==1.0
#   python-kaleido==?
#
# Other Content: None
################################################################################

# Conda environment to create
ENV_NAME=metplotpy

# Conda environment to use as base for new environment
BASE_ENV=$1


conda create -y --clone ${BASE_ENV} --name ${ENV_NAME}

conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.3.0
conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.5.1
conda install -y --name ${ENV_NAME} -c conda-forge plotly==4.9.0
conda install -y --name ${ENV_NAME} -c conda-forge pingouin==0.3.8
conda install -y --name ${ENV_NAME} -c conda-forge cartopy==0.17.0
conda install -y --name ${ENV_NAME} -c conda-forge eofs==1.3.0
conda install -y --name ${ENV_NAME} -c conda-forge cmocean==1.0
/usr/local/envs/${ENV_NAME}/bin/pip3 install kaleido
