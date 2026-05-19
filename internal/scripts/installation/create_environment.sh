#!/bin/sh

ENV_NAME=${ENV_NAME:-metplus_v13.0_py3.14}
MINICONDA_PATH=${MINICONDA_PATH:-$HOME/miniconda3}
CONDA_BIN=${CONDA_BIN:-${MINICONDA_PATH}/bin/conda}

${CONDA_BIN} env create -f environment.yml -n ${ENV_NAME}
