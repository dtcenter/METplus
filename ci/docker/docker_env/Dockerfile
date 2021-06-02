# Dockerfile to create conda environments used for use case tests

FROM conda/miniconda3-centos7

# create conda environments
RUN conda update -y \
 && conda create -y --name metplus_base python=3.6.3 \
 && conda install -y --name metplus_base -c conda-forge xarray==0.16.2 \
 && conda install -y --name metplus_base -c conda-forge netcdf4==1.5.6

RUN  conda create -y --clone metplus_base --name h5py_env \
 && conda install -y --name h5py_env h5py
