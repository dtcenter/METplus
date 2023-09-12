#! /bin/sh

################################################################################
# Environment: geovista.v5.1
# Last Updated: 2023-01-31 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run iris use case
#   Requires development version of geovista package that is obtained
#   from github.com/bjlittle/geovista
# Python Packages:
#   geovista==0.1a1.dev462
#   xarray==2022.11.0
#   iris==3.3.1
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
conda install -y --name ${ENV_NAME} -c conda-forge geovista
conda install -y --name ${ENV_NAME} -c conda-forge xarray
conda install -y --name ${ENV_NAME} -c conda-forge iris
