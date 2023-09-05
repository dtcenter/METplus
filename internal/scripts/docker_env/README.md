# Docker Conda Environments

Run the commands from this directory (internal/scripts/docker_env).
Instructions include how to create Docker images in dtcenter/metplus-envs so
environments are available for the automated tests. Instructions to create
these Conda environments on a local machine are also provided.

**IMPORTANT NOTE:** If all of the Docker Conda Environment images need to be
rebuilt again, consider adding logic to update the OS packages first to
prevent potential issues with wget commands used to download the cartopy
shapefiles. Without this, the wget commands may fail because the
certificate trust store is out of date.

## conda.v5.1

This environment includes Conda which is needed to create all of the Conda environments. NOTE: The OS used as the base image in Dockerfile.conda must match the OS of the MET base image (dtcenter/METbaseimage). Changes to that OS warrant a rebuild of ALL of the Docker images that hold Conda environments.


### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:conda.${METPLUS_ENV_VERSION} \
    -f Dockerfile.conda .
docker push dtcenter/metplus-envs:conda.${METPLUS_ENV_VERSION}
```

### Local

This environment is not needed locally because it is assumed that `conda` is available on the machine running the local commands.

## metplus_base.v5.1

This environment includes the minimum requirements to run the METplus wrappers.


### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:metplus_base.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    -f Dockerfile.metplus_base .
docker push dtcenter/metplus-envs:metplus_base.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/metplus_base_env.sh ${METPLUS_ENV_VERSION}
```


## py_embed_base.v5.1

This environment includes all python embedding requirements (xarray and netcdf).

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:py_embed_base.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    -f Dockerfile.py_embed_base .
docker push dtcenter/metplus-envs:py_embed_base.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/py_embed_base_env.sh ${METPLUS_ENV_VERSION}
```


## h5py.v5.1 (from py_embed_base.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:h5py.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg BASE_ENV=py_embed_base \
    --build-arg ENV_NAME=h5py .
docker push dtcenter/metplus-envs:h5py.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/h5py_env.sh ${METPLUS_ENV_VERSION}
```


## metdataio.v5.1 (from metplus_base.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:metdataio.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=metdataio .
docker push dtcenter/metplus-envs:metdataio.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/metdataio_env.sh ${METPLUS_ENV_VERSION}
```


## pygrib.v5.1 (from py_embed_base.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:pygrib.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg BASE_ENV=py_embed_base \
    --build-arg ENV_NAME=pygrib .
docker push dtcenter/metplus-envs:pygrib.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/pygrib_env.sh ${METPLUS_ENV_VERSION}
```


## cfgrib.v5.1 (from fresh Python 3.10.4 environment)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:cfgrib.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=cfgrib .
docker push dtcenter/metplus-envs:cfgrib.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/cfgrib_env.sh ${METPLUS_ENV_VERSION}
```


## netcdf4.v5.1 (from metplus_base.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:netcdf4.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=netcdf4 .
docker push dtcenter/metplus-envs:netcdf4.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/netcdf4_env.sh ${METPLUS_ENV_VERSION}
```


## xesmf.v5.1 (from metplus_base.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:xesmf.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=xesmf .
docker push dtcenter/metplus-envs:xesmf.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/xesmf_env.sh ${METPLUS_ENV_VERSION}
```


## spacetime.v5.1

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:spacetime.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=spacetime .
docker push dtcenter/metplus-envs:spacetime.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/spacetime_env.sh ${METPLUS_ENV_VERSION}
```


## metplotpy.v5.1 (from metplus_base.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:metplotpy.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=metplotpy \
    -f Dockerfile.cartopy .
docker push dtcenter/metplus-envs:metplotpy.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/metplotpy_env.sh ${METPLUS_ENV_VERSION}
wget https://raw.githubusercontent.com/SciTools/cartopy/master/tools/cartopy_feature_download.py
/home/met_test/.conda/envs/metplotpy.${METPLUS_ENV_VERSION}/bin/python3 cartopy_feature_download.py cultural physical
rm cartopy_feature_download.py
```

#### To install METplotpy and METcalcpy packages in environment

```
runas met_test

export METPLUS_ENV_VERSION=v5.1

cd /home/met_test

# git clone not necessary if repo is already available
git clone https://github.com/dtcenter/METplotpy
git clone https://github.com/dtcenter/METcalcpy

cd /home/met_test/METplotpy
git checkout develop
/home/met_test/.conda/envs/metplotpy.${METPLUS_ENV_VERSION}/bin/pip3 install .

cd /home/met_test/METcalcpy
git checkout develop
/home/met_test/.conda/envs/metplotpy.${METPLUS_ENV_VERSION}/bin/pip3 install .

exit
```


## weatherregime.v5.1 (from metplotpy.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:weatherregime.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg BASE_ENV=metplotpy \
    --build-arg ENV_NAME=weatherregime \
    -f Dockerfile.cartopy .
docker push dtcenter/metplus-envs:weatherregime.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/weatherregime_env.sh ${METPLUS_ENV_VERSION}
wget https://raw.githubusercontent.com/SciTools/cartopy/master/tools/cartopy_feature_download.py
/home/met_test/.conda/envs/weatherregime.${METPLUS_ENV_VERSION}/bin/python3 cartopy_feature_download.py cultural physical
rm cartopy_feature_download.py
```

#### To install METplotpy and METcalcpy packages in environment

```
runas met_test

export METPLUS_ENV_VERSION=v5.1

cd /home/met_test

# git clone not necessary if repo is already available
git clone https://github.com/dtcenter/METplotpy
git clone https://github.com/dtcenter/METcalcpy

cd /home/met_test/METplotpy
git checkout develop
/home/met_test/.conda/envs/weatherregime.${METPLUS_ENV_VERSION}/bin/pip3 install .

cd /home/met_test/METcalcpy
git checkout develop
/home/met_test/.conda/envs/weatherregime.${METPLUS_ENV_VERSION}/bin/pip3 install .

exit
```


## cycloneplotter.v5.1 (from metplus_base.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:cycloneplotter.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=cycloneplotter \
    -f Dockerfile.cartopy .
docker push dtcenter/metplus-envs:cycloneplotter.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/cycloneplotter_env.sh ${METPLUS_ENV_VERSION}
wget https://raw.githubusercontent.com/SciTools/cartopy/master/tools/cartopy_feature_download.py
/home/met_test/.conda/envs/cycloneplotter.${METPLUS_ENV_VERSION}/bin/python3 cartopy_feature_download.py cultural physical
rm cartopy_feature_download.py
```


## icecover.v5.1 (from py_embed_base.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:icecover.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg BASE_ENV=py_embed_base \
    --build-arg ENV_NAME=icecover .
docker push dtcenter/metplus-envs:icecover.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/icecover_env.sh ${METPLUS_ENV_VERSION}
```


## gempak.v5.1 (from metplus_base.v5.1 using Dockerfile.gempak_env)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:gempak.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=gempak \
    -f ./Dockerfile.gempak_env .
docker push dtcenter/metplus-envs:gempak.${METPLUS_ENV_VERSION}
```

### Local

This environment is not a conda environment. The script installs Java and obtains the
GempakToCF.jar file that is required to run use cases that read GEMPAK data. If "installing"
this environment locally, Java should be available on the system you are running and the
JAR file should be downloaded from the DTC website.


## gfdl-tracker.v5.1 (using Dockerfile.gfdl-tracker)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:gfdl-tracker.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    -f ./Dockerfile.gfdl-tracker .
docker push dtcenter/metplus-envs:gfdl-tracker.${METPLUS_ENV_VERSION}
```

### Local

This environment is not a conda environment. The Dockerfile installs the GFDL
Tracker and specific versions of the NetCDF-C and NetCDF-Fortran libraries
needed to install the tools. It is not recommended to follow these instructions
to install the GFDL Tracker using these steps. Please consult the documentation
for the tool for installation instructions.

## geovista.v5.1

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:geovista.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=geovista .
docker push dtcenter/metplus-envs:geovista.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/geovista_env.sh ${METPLUS_ENV_VERSION}

cd /home/met_test/geovista
/home/met_test/.conda/envs/geovista.${METPLUS_ENV_VERSION}/bin/pip3 install --no-deps --editable .
```

## pandac.v5.1 (from metplotpy.v5.1)

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:pandac.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg BASE_ENV=metplotpy \
    --build-arg ENV_NAME=pandac .
docker push dtcenter/metplus-envs:pandac.${METPLUS_ENV_VERSION}
```

### Local

```
export METPLUS_ENV_VERSION=v5.1
./scripts/pandac_env.sh ${METPLUS_ENV_VERSION}
```




## test.v5.1 (from metplus_base.v5.1)

This environment is used in automation to run the pytests and diff tests. It requires all of the
packages needed to run all of the METplus wrappers, the pytest package and the pytest
code coverage package.

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:test.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg ENV_NAME=test .
docker push dtcenter/metplus-envs:test.${METPLUS_ENV_VERSION}
```


## diff.v5.1 (from netcdf4.v5.1)

This environment is used to run the difference tests to compare output data to output
generated in previous runs to ensure that changes to the code base do not break or change
the results.

### Docker

```
export METPLUS_ENV_VERSION=v5.1
docker build -t dtcenter/metplus-envs:diff.${METPLUS_ENV_VERSION} \
    --build-arg METPLUS_ENV_VERSION \
    --build-arg BASE_ENV=netcdf4 \
    --build-arg ENV_NAME=diff .
docker push dtcenter/metplus-envs:diff.${METPLUS_ENV_VERSION}
```
