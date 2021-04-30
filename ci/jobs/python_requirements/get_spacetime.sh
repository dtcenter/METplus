#! /bin/bash

script_dir=$(dirname "$0")

work_dir=$script_dir/../../..

echo Installing environment for UserScript_obsPrecip_obsOnly_CrossSpectraPlot with conda

# create a MiniConda environemtn using Python 3.8
${script_dir}/get_miniconda.sh 3.8

conda install -y pip

# run manage externals to obtain METcalcpy
${work_dir}/manage_externals/checkout_externals -e ${work_dir}/ci/parm/Externals_metplotpy.cfg
python3 -m pip install ${work_dir}/../METplotpy

# run manage externals to obtain METcalcpy
${work_dir}/manage_externals/checkout_externals -e ${work_dir}/ci/parm/Externals_metcalcpy.cfg

python3 -m pip install ${work_dir}/../METcalcpy

# install required packages for use case
conda install -y -c conda-forge python-dateutil netCDF4 xarray scipy matplotlib pyngl 
conda install -c anaconda pyyaml
