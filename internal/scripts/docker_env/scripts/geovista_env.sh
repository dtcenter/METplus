#! /bin/sh

################################################################################
# Environment: geovista.v6.1
# Last Updated: 2025-02-05 (mccabe@ucar.edu)
# Notes: Adds Python packages needed to run iris use case
# Python Packages:
#   geovista==0.5.3
#   xarray==2025.1.2
#   iris==3.11.1
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

mamba create -y --name ${ENV_NAME} -c conda-forge python=3.12.0
mamba install -y --name ${ENV_NAME} -c conda-forge \
  geovista==0.5.3 \
  xarray==2025.1.2 \
  iris==3.11.1
