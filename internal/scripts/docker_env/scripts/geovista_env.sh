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

# install libGL to prevent ImportError of libGL dynamic library in geovista
apt install -y libgl1-mesa-glx

# install git to clone geovista repo to get dev version of package
apt install -y git
git clone --depth=1 https://github.com/bjlittle/geovista.git
cd geovista
conda create -y -n ${ENV_NAME} --file requirements/locks/py310-lock-linux-64.txt

# note: this command will not work on a local machine
# it is specific to docker
/usr/local/conda/envs/${ENV_NAME}/bin/pip3 install --no-deps .
cd -

conda install -y --name ${ENV_NAME} -c conda-forge xarray==2022.11.0
conda install -y --name ${ENV_NAME} -c conda-forge iris==3.3.1

