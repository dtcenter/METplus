#! /bin/sh

################################################################################
# Environment: geovista.v6.0
# Last Updated: 2023-09-12 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run iris use case
#   Requires development version of geovista package that is obtained
#   from github.com/bjlittle/geovista
# Python Packages:
#   geovista==0.3.0
#   xarray==2023.8.0
#   iris==3.7.0
#
# Other Content: None
################################################################################

# version of METplus when the environment was updated, e.g. v5.1
METPLUS_VERSION=$1

# Conda environment to create
ENV_NAME=geovista.${METPLUS_VERSION}

# install libGL and libEGL to prevent ImportError of libGL and libEGL dynamic library in geovista
apt install -y libgl1-mesa-glx
apt install -y libegl1

conda create -y --name ${ENV_NAME} -c conda-forge python=3.10.4
conda install -y --name ${ENV_NAME} -c conda-forge geovista==0.3.0
conda install -y --name ${ENV_NAME} -c conda-forge xarray==2023.8.0
conda install -y --name ${ENV_NAME} -c conda-forge iris==3.7.0
