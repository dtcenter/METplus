#! /bin/bash

script_dir=$(dirname "$0")

${script_dir}/get_miniconda.sh

echo Installing xesmf with conda
conda install -c conda-forge dask netCDF4 xesmf
