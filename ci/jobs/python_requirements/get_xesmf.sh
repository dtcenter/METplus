#! /bin/bash

script_dir=$(dirname "$0")

${script_dir}/get_miniconda.sh

echo Installing xesmf with conda
conda install -c conda-forge xarray==0.18.2
conda install -c conda-forge dask netCDF4 xesmf
