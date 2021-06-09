# Docker Conda Environments

## Commands to create Docker images in dtcenter/metplus-envs

Run from this directory (ci/docker/docker_env)

### create metplus_base env (just dateutil)
```
docker build -t dtcenter/metplus-envs:metplus_base -f Dockerfile.metplus_base .
docker push dtcenter/metplus-envs:metplus_base
```

### create py_embed_base env (all python embedding requirements (xarray and netcdf)
```
docker build -t dtcenter/metplus-envs:py_embed_base -f Dockerfile.py_embed_base .
docker push dtcenter/metplus-envs:py_embed_base
```

### create h5py env from py_embed_base
```
docker build -t dtcenter/metplus-envs:h5py --build-arg BASE_ENV=py_embed_base --build-arg ENV_INSTALL_SCRIPT=h5py_env.sh .
docker push dtcenter/metplus-envs:h5py
```

### create metdatadb env from metplus_base
```
docker build -t dtcenter/metplus-envs:metdatadb --build-arg ENV_INSTALL_SCRIPT=metdatadb_env.sh .
docker push dtcenter/metplus-envs:metdatadb
```

### create pygrib env from py_embed_base
```
docker build -t dtcenter/metplus-envs:pygrib --build-arg BASE_ENV=py_embed_base --build-arg ENV_INSTALL_SCRIPT=pygrib_env.sh .
docker push dtcenter/metplus-envs:pygrib
```

### create netcdf4 env from metplus_base
```
docker build -t dtcenter/metplus-envs:netcdf4 --build-arg ENV_INSTALL_SCRIPT=netcdf4_env.sh .
docker push dtcenter/metplus-envs:netcdf4
```

### create xesmf env from metplus_base
```
docker build -t dtcenter/metplus-envs:xesmf --build-arg ENV_INSTALL_SCRIPT=xesmf_env.sh .
docker push dtcenter/metplus-envs:xesmf
```

### create spacetime env from metplus_base
```
docker build -t dtcenter/metplus-envs:spacetime --build-arg ENV_INSTALL_SCRIPT=spacetime_env.sh .
docker push dtcenter/metplus-envs:spacetime
```

### create metplotpy env from metplus_base
```
docker build -t dtcenter/metplus-envs:metplotpy --build-arg ENV_INSTALL_SCRIPT=metplotpy_env.sh .
docker push dtcenter/metplus-envs:metplotpy
```

### create pytest env from metplus_base
```
docker build -t dtcenter/metplus-envs:pytest --build-arg ENV_INSTALL_SCRIPT=pytest_env.sh .
docker push dtcenter/metplus-envs:pytest
```

### create diff env from netcdf4
```
docker build -t dtcenter/metplus-envs:diff --build-arg BASE_ENV=netcdf4 --build-arg ENV_INSTALL_SCRIPT=diff_env.sh .
docker push dtcenter/metplus-envs:diff
```

### create cycloneplotter env from metplus_base
```
docker build -t dtcenter/metplus-envs:cycloneplotter --build-arg ENV_INSTALL_SCRIPT=cycloneplotter_env.sh .
docker push dtcenter/metplus-envs:cycloneplotter
```
