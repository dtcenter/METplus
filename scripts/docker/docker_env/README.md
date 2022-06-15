# Docker Conda Environments

Run the commands from this directory (scripts/docker/docker_env).
Instructions include how to create Docker images in dtcenter/metplus-envs so
environments are available for the automated tests. Instructions to create
these Conda environments on a local machine are also provided.

## metplus_base

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

## py_embed_base

This environment includes all python embedding requirements (xarray and netcdf).

### Docker

```
docker build -t dtcenter/metplus-envs:py_embed_base -f Dockerfile.py_embed_base .
docker push dtcenter/metplus-envs:py_embed_base
```

### Local

```
./scripts/py_embed_base_env.sh
```

## h5py (from py_embed_base)

### Docker

```
docker build -t dtcenter/metplus-envs:h5py --build-arg BASE_ENV=py_embed_base --build-arg ENV_NAME=h5py .
docker push dtcenter/metplus-envs:h5py
```

### Local

```
./scripts/h5py_env.sh py_embed_base
```

## metdatadb (from metplus_base)

### Docker

```
docker build -t dtcenter/metplus-envs:metdatadb --build-arg ENV_NAME=metdatadb .
docker push dtcenter/metplus-envs:metdatadb
```

### Local

```
./scripts/metdatadb_env.sh metplus_base
```

## pygrib (from py_embed_base)

### Docker

```
docker build -t dtcenter/metplus-envs:pygrib --build-arg BASE_ENV=py_embed_base --build-arg ENV_NAME=pygrib .
docker push dtcenter/metplus-envs:pygrib
```

### Local

```
./scripts/pygrib_env.sh  py_embed_base
```

## cfgrib (from fresh Python 3.6.8 environment)

### Docker

```
docker build -t dtcenter/metplus-envs:cfgrib --build-arg ENV_NAME=cfgrib .
docker push dtcenter/metplus-envs:cfgrib
```

### Local

```
./scripts/cfgrib_env.sh
```

## netcdf4 (from metplus_base)

### Docker

```
docker build -t dtcenter/metplus-envs:netcdf4 --build-arg ENV_NAME=netcdf4 .
docker push dtcenter/metplus-envs:netcdf4
```

### Local

```
./scripts/netcdf4_env.sh  metplus_base
```

## xesmf (from metplus_base)

### Docker

```
docker build -t dtcenter/metplus-envs:xesmf --build-arg ENV_NAME=xesmf .
docker push dtcenter/metplus-envs:xesmf
```

### Local

```
./scripts/xesmf_env.sh metplus_base
```

## spacetime (from metplus_base)

### Docker

```
docker build -t dtcenter/metplus-envs:spacetime --build-arg ENV_NAME=spacetime .
docker push dtcenter/metplus-envs:spacetime
```

### Local

```
./scripts/spacetime_env.sh metplus_base
```

## metplotpy (from metplus_base)

### Docker

```
docker build -t dtcenter/metplus-envs:metplotpy.v5 --build-arg ENV_NAME=metplotpy .
docker push dtcenter/metplus-envs:metplotpy.v5
```

### Local

NOTE: Environment cannot be created fully using conda commands because there is a conflict
with the python-kaleido package and the version of glibc. The kaleido package installation
will fail through the script, but it should be installed using pip3 afterwards.

```
./scripts/metplotpy_env.sh metplus_base
/home/met_test/.conda/envs/metplotpy/bin/pip3 install kaleido==0.2.1
/home/met_test/.conda/envs/metplotpy/bin/python3 cartopy_feature_download.py cultural physical
rm cartopy_feature_download.py
```

#### To install METplotpy and METcalcpy packages in environment

```
cd /home/met_test

# git clone not necessary if repo is already available
git clone https://github.com/dtcenter/METplotpy
git clone https://github.com/dtcenter/METcalcpy

cd /home/met_test/METplotpy
git checkout develop
/home/met_test/.conda/envs/metplotpy/bin/pip3 install .

cd /home/met_test/METcalcpy
git checkout develop
/home/met_test/.conda/envs/metplotpy/bin/pip3 install .
```

## weatherregime (from metplotpy_env)

### Docker

```
docker build -t dtcenter/metplus-envs:weatherregime --build-arg BASE_ENV=metplotpy --build-arg ENV_NAME=weatherregime .
docker push dtcenter/metplus-envs:weatherregime
```

### Local

```
./scripts/weatherregime_env.sh metplotpy
/home/met_test/.conda/envs/weatherregime/bin/python3 cartopy_feature_download.py cultural physical
rm cartopy_feature_download.py
```

#### To install METplotpy and METcalcpy packages in environment

```
cd /home/met_test

# git clone not necessary if repo is already available
git clone https://github.com/dtcenter/METplotpy
git clone https://github.com/dtcenter/METcalcpy

cd /home/met_test/METplotpy
git checkout develop
/home/met_test/.conda/envs/weatherregime/bin/pip3 install .

cd /home/met_test/METcalcpy
git checkout develop
/home/met_test/.conda/envs/weatherregime/bin/pip3 install .
```

## cycloneplotter (from metplus_base)

### Docker

```
docker build -t dtcenter/metplus-envs:cycloneplotter --build-arg ENV_NAME=cycloneplotter .
docker push dtcenter/metplus-envs:cycloneplotter
```

### Local

```
./scripts/cycloneplotter_env.sh metplus_base
```

## icecover (from py_embed_base)

### Docker

```
docker build -t dtcenter/metplus-envs:icecover --build-arg BASE_ENV=py_embed_base --build-arg ENV_NAME=icecover .
docker push dtcenter/metplus-envs:icecover
```

### Local

```
./scripts/icecover_env.sh  py_embed_base
```

## gempak (from metplus_base using Dockerfile.gempak_env)

### Docker

```
docker build -t dtcenter/metplus-envs:gempak --build-arg ENV_NAME=gempak -f ./Dockerfile.gempak_env .
docker push dtcenter/metplus-envs:gempak
```

### Local

This environment is not a conda environment. The script installs Java and obtains the
GempakToCF.jar file that is required to run use cases that read GEMPAK data. If "installing"
this environment locally, Java should be available on the system you are running and the
JAR file should be downloaded from the DTC website.

## gfdl-tracker (using Dockerfile.gfdl-tracker)

### Docker

```
docker build -t dtcenter/metplus-envs:gfdl-tracker -f ./Dockerfile.gfdl-tracker .
docker push dtcenter/metplus-envs:gfdl-tracker
```

### Local

This environment is not a conda environment. The Dockerfile installs the GFDL
Tracker and specific versions of the NetCDF-C and NetCDF-Fortran libraries
needed to install the tools. It is not recommended to follow these instructions
to install the GFDL Tracker using these steps. Please consult the documentation
for the tool for installation instructions.


## pytest (from metplus_base)

This environment is used in automation to run the pytests. It requires all of the
packages needed to run all of the METplus wrappers, the pytest package and the pytest
code coverage package.

### Docker

```
docker build -t dtcenter/metplus-envs:pytest --build-arg ENV_NAME=pytest .
docker push dtcenter/metplus-envs:pytest
```

## diff (from netcdf4)

This environment is used to run the difference tests to compare output data to output
generated in previous runs to ensure that changes to the code base do not break or change
the results.

### Docker

```
docker build -t dtcenter/metplus-envs:diff --build-arg BASE_ENV=netcdf4 --build-arg ENV_NAME=diff .
docker push dtcenter/metplus-envs:diff
```
