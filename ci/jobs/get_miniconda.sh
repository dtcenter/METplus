#! /bin/bash

PYTHON_VERS=38
MINIC_VERS=4.8.3

echo Checking if Miniconda is installed
# check if conda is already available and exit if it is
conda --version
if [ $? == 0 ]; then
    echo Miniconda is already installed
    exit 0
fi

echo Installing Miniconda
curl -sSL https://repo.continuum.io/miniconda/Miniconda3-py${PYTHON_VERS}_${MINIC_VERS}-Linux-x86_64.sh -o /tmp/miniconda.sh

bash /tmp/miniconda.sh -bfp /usr/local/
rm -rf /tmp/miniconda.sh
conda install -y python=3
conda update conda
conda clean --all --yes
