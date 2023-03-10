#! /bin/sh

ENV_NAME=metplus_v5.0_py3.8
MINICONDA_PATH=/path/to/miniconda3

${MINICONDA_PATH}/bin/conda create -y --name ${ENV_NAME} -c conda-forge python=3.8.6
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge python-dateutil==2.8.2
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.5.2
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.8.1
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge plotly==5.9.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge xarray==2022.3.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.6.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pyyaml==6.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge statsmodels==0.13.2
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge python-kaleido==0.2.1
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge imageio==2.19.3
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge imutils==0.5.4
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge scikit-image==0.19.3
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pint==0.19.2
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge metpy=1.3.1
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pyngl==1.6.1
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn==1.1.1
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge eofs==1.4.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge cmocean==2.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge xesmf==0.3.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge lxml==4.9.1
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pymysql==1.0.2
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pandas==1.2.3
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge h5py==3.6.0
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge cartopy==0.20.3
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge psutil==5.7.2
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pytest
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge pytest-cov
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge numpy==1.20.1
${MINICONDA_PATH}/bin/conda install -y --name ${ENV_NAME} -c conda-forge libstdcxx-ng==12.1.0
