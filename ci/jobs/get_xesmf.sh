#! /bin/bash

$DOCKER_WORK_DIR/METplus/ci/jobs/get_miniconda.sh

echo Installing xesmf with conda
conda install -c conda-forge netCDF4 xesmf
