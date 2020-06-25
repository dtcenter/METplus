

# These are the paths from within the docker container, docker-space.
# /metplus is the mount point within docker to the external machine. 
export METPLUS_TEST_INPUT_BASE=/metplus/test.metplus.data
#export METPLUS_TEST_OUTPUT_BASE=/d1/${USER}/pytest
export METPLUS_TEST_OUTPUT_BASE=/metplus/pytmp.docker
export METPLUS_TEST_MET_INSTALL_DIR=/usr/local
export METPLUS_TEST_TMP_DIR=${METPLUS_TEST_OUTPUT_BASE}/tmp

# I don't think these are used anymore ...
#export METPLUS_TEST_EXE_WGRIB2=/usr/local/bin/wgrib2
#export METPLUS_TEST_EXE_CUT=/usr/bin/cut
#export METPLUS_TEST_EXE_TR=/usr/bin/tr
#export METPLUS_TEST_EXE_RM=/bin/rm
#export METPLUS_TEST_EXE_NCAP2=/usr/local/nco/bin/ncap2
#export METPLUS_TEST_EXE_CONVERT=/usr/bin/convert
#export METPLUS_TEST_EXE_NCDUMP=/usr/local/bin/ncdump
#export METPLUS_TEST_EXE_EGREP=/bin/egrep

