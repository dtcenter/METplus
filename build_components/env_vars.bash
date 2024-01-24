###### Environment examples for a non-module based system #####
export TEST_BASE=./
export COMPILER=gnu
export MET_SUBDIR=${TEST_BASE}
export MET_TARBALL=met.tar.gz
export MET_PYTHON_CC=CC_FLAGS
export MET_PYTHON_LD=LD_FLAGS
#### Python version on your system
export PYTHON_MODULE=python_3.6.3
### Local system ${PYTHON_MODULE} install location for python libraries
export MET_PYTHON=/usr/local/python3.6
export PYTHON_MODULE_USE=1


###### Environment examples for a module based system #####
#module load ips/18.0.5.274
#module load python/3.6.3
#export COMPILER=ips_18.0.5.274
#export MET_SUBDIR=${TEST_BASE}/
#export MET_TARBALL=met-9.0_beta3.20200207.tar.gz
#export PYTHON_MODULE=python_3.6.3
#export MET_PYTHON=/usrx/local/prod/packages/python/3.6.3/
#export MET_PYTHON_CC=-I/usrx/local/prod/packages/python/3.6.3/include/python3.6m\ 
#-I/usrx/local/prod/packages/python/3.6.3/include/python3.6m
#export MET_PYTHON_LD=-L/usrx/local/prod/packages/python/3.6.3/lib/\ 
#-lpython3.6m\ -lpthread\ -ldl\ -lutil\ -lm\ -Xlinker\ -export-dynamic
#export PYTHON_MODULE_USE=/usrx/local/prod/modulefiles/core_third/python


