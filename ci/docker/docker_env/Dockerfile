# Dockerfile to create conda environments used for use case tests

FROM conda/miniconda3-centos7

# create conda environments
RUN conda create -y --name metplus_base python=3.6.3 xarray netCDF4 \
 && conda create -y --clone metplus_base --name h5py_env \
 && conda install -y --name h5py_env h5py \
 && conda create -y --clone metplus_base --name xesmf_env \
 && conda install -y --name xesmf_env -c conda-forge xesmf \
 && conda create -y --clone metplus_base --name pygrib_env \
 && conda install -y --name pygrib_env -c conda-forge pygrib metpy \
 && conda create -y --clone metplus_base --name metdatadb_env \
 && conda install -y --name metdatadb_env -c conda-forge lxml pymysql \
 && conda create -y --clone metplus_base --name metplotcalcpy_env \
 && conda install -y --name metplotcalcpy_env -c conda-forge matplotlib scipy cmocean plotly==4.9.0 pyt\
hon-kaleido matplotlib pingouin \
 && conda create -y --name spacetime_env python=3.8 \
 && conda install -y --name spacetime_env -c conda-forge python-dateutil netCDF4 xarray scipy matplotli\
b pyngl \
 && conda install -y --name spacetime_env -c anaconda pyyaml
