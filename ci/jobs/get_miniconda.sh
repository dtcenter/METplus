#! /bin/bash

script_dir=$(dirname "$0")

python_version=`${script_dir}/print_python_version.py`
echo Python Version is $python_version
# these are used to obtain version of MiniConda3
# the version determines the default version of Python
# that is used, but earlier versions can be obtained
# there is no version of MiniConda available that
# matches the current Python version requirement of METplus
MINIC_PYTHON_VERS=38
MINIC_VERS=4.8.3

echo Checking if Miniconda is installed
# check if conda is already available and exit if it is
conda --version
if [ $? == 0 ]; then
    echo Miniconda is already installed
    exit 0
fi

echo Installing Miniconda
curl -sSL https://repo.continuum.io/miniconda/Miniconda3-py${MINIC_PYTHON_VERS}_${MINIC_VERS}-Linux-x86_64.sh -o /tmp/miniconda.sh

bash /tmp/miniconda.sh -bfp /usr/local/
rm -rf /tmp/miniconda.sh
conda install -y python=${python_version}
conda update conda
conda clean --all --yes
