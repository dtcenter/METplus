# Docker Conda Environments

Run the commands from this directory (scripts/docker/docker_env).
Instructions include how to create Docker images in dtcenter/metplus-envs so
environments are available for the automated tests. Instructions to create
these Conda environments on a local machine are also provided.

**IMPORTANT NOTE:** If all of the Docker Conda Environment images need to be
rebuilt again, consider adding logic to update the OS packages first to
prevent potential issues with wget commands used to download the cartopy
shapefiles. Without this, the wget commands may fail because the
certificate trust store is out of date.

## metplus_base.v5

This environment includes the minimum requirements to run the METplus wrappers.


### Docker

```
docker build -t dtcenter/metplus-envs:metplus_base.v5 -f Dockerfile.metplus_base .
docker push dtcenter/metplus-envs:metplus_base.v5
```

### Local

```
./scripts/metplus_base_env.sh
```


## py_embed_base.v5

This environment includes all python embedding requirements (xarray and netcdf).

### Docker

```
docker build -t dtcenter/metplus-envs:py_embed_base.v5 -f Dockerfile.py_embed_base .
docker push dtcenter/metplus-envs:py_embed_base.v5
```

### Local

```
./scripts/py_embed_base_env.sh
```


## h5py.v5 (from py_embed_base.v5)

### Docker

```
docker build -t dtcenter/metplus-envs:h5py.v5 --build-arg BASE_ENV=py_embed_base.v5 --build-arg ENV_NAME=h5py .
docker push dtcenter/metplus-envs:h5py.v5
```

### Local

```
./scripts/h5py_env.sh
```


## metdataio.v5 (from metplus_base.v5)

### Docker

```
docker build -t dtcenter/metplus-envs:metdataio.v5 --build-arg ENV_NAME=metdataio .
docker push dtcenter/metplus-envs:metdataio.v5
```

### Local

```
./scripts/metdatadb_env.sh
```


## pygrib.v5 (from py_embed_base.v5)

### Docker

```
docker build -t dtcenter/metplus-envs:pygrib.v5 --build-arg BASE_ENV=py_embed_base.v5 --build-arg ENV_NAME=pygrib .
docker push dtcenter/metplus-envs:pygrib.v5
```

### Local

```
./scripts/pygrib_env.sh
```


## cfgrib.v5 (from fresh Python 3.8.6 environment)

### Docker

```
docker build -t dtcenter/metplus-envs:cfgrib.v5 --build-arg ENV_NAME=cfgrib .
docker push dtcenter/metplus-envs:cfgrib.v5
```

### Local

```
./scripts/cfgrib_env.sh
```


## netcdf4.v5 (from metplus_base.v5)

### Docker

```
docker build -t dtcenter/metplus-envs:netcdf4.v5 --build-arg ENV_NAME=netcdf4 .
docker push dtcenter/metplus-envs:netcdf4.v5
```

### Local

```
./scripts/netcdf4_env.sh
```


## xesmf.v5 (from metplus_base.v5)

### Docker

```
docker build -t dtcenter/metplus-envs:xesmf.v5 --build-arg ENV_NAME=xesmf .
docker push dtcenter/metplus-envs:xesmf.v5
```

### Local

```
./scripts/xesmf_env.sh
```


## spacetime.v5

### Docker

```
docker build -t dtcenter/metplus-envs:spacetime.v5 --build-arg ENV_NAME=spacetime .
docker push dtcenter/metplus-envs:spacetime.v5
```

### Local

```
./scripts/spacetime_env.sh
```


## metplotpy.v5 (from metplus_base.v5)

### Docker

```
docker build -t dtcenter/metplus-envs:metplotpy.v5 --build-arg ENV_NAME=metplotpy .
docker push dtcenter/metplus-envs:metplotpy.v5
```

### Local

```
./scripts/metplotpy_env.sh
/home/met_test/.conda/envs/metplotpy.v5/bin/python3 cartopy_feature_download.py cultural physical
rm cartopy_feature_download.py
```

#### To install METplotpy and METcalcpy packages in environment

```
runas met_test
cd /home/met_test

# git clone not necessary if repo is already available
git clone https://github.com/dtcenter/METplotpy
git clone https://github.com/dtcenter/METcalcpy

cd /home/met_test/METplotpy
git checkout develop
/home/met_test/.conda/envs/metplotpy.v5/bin/pip3 install .

cd /home/met_test/METcalcpy
git checkout develop
/home/met_test/.conda/envs/metplotpy.v5/bin/pip3 install .

exit
```


## weatherregime.v5 (from metplotpy.v5)

### Docker

```
docker build -t dtcenter/metplus-envs:weatherregime.v5 --build-arg BASE_ENV=metplotpy.v5 --build-arg ENV_NAME=weatherregime .
docker push dtcenter/metplus-envs:weatherregime.v5
```

### Local

```
./scripts/weatherregime_env.sh
/home/met_test/.conda/envs/weatherregime.v5/bin/python3 cartopy_feature_download.py cultural physical
rm cartopy_feature_download.py
```

#### To install METplotpy and METcalcpy packages in environment

```
runas met_test
cd /home/met_test

# git clone not necessary if repo is already available
git clone https://github.com/dtcenter/METplotpy
git clone https://github.com/dtcenter/METcalcpy

cd /home/met_test/METplotpy
git checkout develop
/home/met_test/.conda/envs/weatherregime.v5/bin/pip3 install .

cd /home/met_test/METcalcpy
git checkout develop
/home/met_test/.conda/envs/weatherregime.v5/bin/pip3 install .

exit
```


## cycloneplotter.v5 (from metplus_base.v5)

### Docker

```
docker build -t dtcenter/metplus-envs:cycloneplotter.v5 --build-arg ENV_NAME=cycloneplotter .
docker push dtcenter/metplus-envs:cycloneplotter.v5
```

### Local

```
./scripts/cycloneplotter_env.sh
/home/met_test/.conda/envs/cycloneplotter.v5/bin/python3 cartopy_feature_download.py cultural physical
rm cartopy_feature_download.py
```


## icecover.v5 (from py_embed_base.v5)

### Docker

```
docker build -t dtcenter/metplus-envs:icecover.v5 --build-arg BASE_ENV=py_embed_base.v5 --build-arg ENV_NAME=icecover .
docker push dtcenter/metplus-envs:icecover.v5
```

### Local

```
./scripts/icecover_env.sh
```


## gempak.v5 (from metplus_base.v5 using Dockerfile.gempak_env)

### Docker

```
docker build -t dtcenter/metplus-envs:gempak.v5 --build-arg ENV_NAME=gempak -f ./Dockerfile.gempak_env .
docker push dtcenter/metplus-envs:gempak.v5
```

### Local

This environment is not a conda environment. The script installs Java and obtains the
GempakToCF.jar file that is required to run use cases that read GEMPAK data. If "installing"
this environment locally, Java should be available on the system you are running and the
JAR file should be downloaded from the DTC website.


## gfdl-tracker.v5 (using Dockerfile.gfdl-tracker)

### Docker

```
docker build -t dtcenter/metplus-envs:gfdl-tracker.v5 -f ./Dockerfile.gfdl-tracker .
docker push dtcenter/metplus-envs:gfdl-tracker.v5
```

### Local

This environment is not a conda environment. The Dockerfile installs the GFDL
Tracker and specific versions of the NetCDF-C and NetCDF-Fortran libraries
needed to install the tools. It is not recommended to follow these instructions
to install the GFDL Tracker using these steps. Please consult the documentation
for the tool for installation instructions.


## pytest.v5 (from metplus_base.v5)

This environment is used in automation to run the pytests. It requires all of the
packages needed to run all of the METplus wrappers, the pytest package and the pytest
code coverage package.

### Docker

```
docker build -t dtcenter/metplus-envs:pytest.v5 --build-arg ENV_NAME=pytest .
docker push dtcenter/metplus-envs:pytest.v5
```


## diff.v5 (from netcdf4.v5)

This environment is used to run the difference tests to compare output data to output
generated in previous runs to ensure that changes to the code base do not break or change
the results.

### Docker

```
docker build -t dtcenter/metplus-envs:diff.v5 --build-arg BASE_ENV=netcdf4.v5 --build-arg ENV_NAME=diff .
docker push dtcenter/metplus-envs:diff.v5
```
