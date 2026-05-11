#! /bin/sh

ENV_NAME=metplus_v13.0_py3.14
MINICONDA_PATH=/path/to/miniconda3

${MINICONDA_PATH}/bin/conda create -y --name ${ENV_NAME} -c conda-forge python=3.14.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge python-dateutil==2.9.0.post0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.10.8
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.17.1
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge plotly==6.1.1
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge xarray==2026.4.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.7.4
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pyyaml==6.0.3
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge statsmodels
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge python-kaleido==1.0.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge imageio==2.37.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge imutils==0.5.4
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pint==0.25.3
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge metpy=1.7.1  
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pyngl
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge eofs==2.0.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge cmocean==4.0.3
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge xesmf
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge lxml==6.0.4
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pymysql==1.1.2
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pandas==3.0.2
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge h5py
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge cartopy==0.25.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge psutil
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pytest==9.0.3
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pytest-cov
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge numpy==2.4.3
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge opencv-python>=4.13.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge libstdcxx-ng
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge libssh

