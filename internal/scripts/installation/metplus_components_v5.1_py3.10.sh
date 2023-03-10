#! /bin/sh

ENV_NAME=metplus_v5.1_py3.10

/miniconda/miniconda3/bin/conda create -y --name ${ENV_NAME} -c conda-forge python=3.10.4
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge python-dateutil==2.8.2
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge matplotlib==3.6.3
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge scipy==1.9.3
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge plotly==5.13.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge xarray==2023.1.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge netcdf4==1.6.2
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge pyyaml==6.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge statsmodels==0.13.2
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge python-kaleido==0.2.1
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge imageio==2.25.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge imutils==0.5.4
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge scikit-image==0.19.3
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge pint==0.20.1
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge metpy=1.4.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge pyngl==1.6.1
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge scikit-learn==1.2.1
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge eofs==1.4.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge cmocean==2.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge xesmf==0.3.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge lxml==4.9.1
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge pymysql==1.0.2
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge pandas==1.5.2
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge h5py==3.6.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge cartopy==0.20.3
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge psutil==5.7.2
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge pytest==7.2.1
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge pytest-cov
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge numpy==1.24.2
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge libstdcxx-ng==12.1.0
/miniconda/miniconda3/bin/conda install -y --name ${ENV_NAME} -c conda-forge opencv-python==4.7.0
