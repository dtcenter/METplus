#! /bin/bash

$DOCKER_WORK_DIR/METplus/ci/job/get_miniconda.sh

echo Installing xesmf with conda
conda install -c conda-forge xesmf
