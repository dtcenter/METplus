#!/bin/bash
### Grab the compenents source code from git using manage_externals
### Externals.cfg specifies what to checkout and where to put it
../manage_externals/checkout_externals

## Grab the compile script
wget https://dtcenter.org/sites/default/files/community-code/met/compile_scripts/compile_MET_all.sh.tgz
tar -xzvf compile_MET_all.sh.tgz

## Grab the external library tar file
wget https://dtcenter.org/sites/default/files/community-code/met/compile_scripts/tar_files.tgz

## Stuff the contents into tar_files directory
tar -xzvf tar_files.tgz

## link the git hub source code directory to the current directory - serious hack for now
ln -s ../MET/met met

## Create a tarball which is what the compile script wants right now - hopefully change this later
tar -cvzhf tar_files/met.tar.gz met

### Source environment variables and run the compile_all script
source env_vars.bash
bash compile_MET_all.sh

