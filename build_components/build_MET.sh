#!/bin/bash
### Grab the compenents source code from git using manage_externals
### Externals.cfg specifies what to checkout and where to put it
../manage_externals/checkout_externals

## Grab the external library tar file
## Use wget if available, curl if not
if hash wget 2>/dev/null; then
        wget https://dtcenter.org/sites/default/files/community-code/met/compile_scripts/tar_files.tgz
    else
        curl https://dtcenter.org/sites/default/files/community-code/met/compile_scripts/tar_files.tgz -o tar_files.tgz
    fi

## Grab GFDL tracker tar file
if hash wget 2>/dev/null; then
        wget http://dtcenter.org/sites/default/files/community-code/gfdl/standalone_gfdl-vortextracker_v3.9a.tar.gz
    else
        curl http://dtcenter.org/sites/default/files/community-code/gfdl/standalone_gfdl-vortextracker_v3.9a.tar.gz -o gfdl_vortextracker_v3.9a.tar.gz 
    fi

## Extract the build script
echo "Extracting File"
tar -xzvf compile_MET_all.sh.tgz
## Copy the current MET build all script and sample configurations from the cloned git repo
cp ../MET/scripts/installation/compile_MET_all.sh . 
cp -r ../MET/scripts/installation/config .

## Extract the supporting library contents into tar_files directory
tar -xzvf tar_files.tgz

## link the git hub source code directory to the current directory
ln -s ../MET/met met

## Create a tarball which is what the compile script wants right now 
tar -cvzhf tar_files/met.tar.gz met

### Source environment variables and run the compile_all script
source env_vars.bash
cd met
./bootstrap
cd ../

bash compile_MET_all.sh config/install_met_env.generic


