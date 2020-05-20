#!/bin/bash

# NOTE:
# This script is meant to be called from withing a METplus docker container
# to run the METplus test use cases.
#
# /metplus is the container mountpoint to the local-disk host parent
# directory of the METplus directory.
# For example if METplus was located on local-disk here: /some/path/METplus
# docer run argument -v would be, /some/path:/metplus


# docker container note, using /bin/bash --login 
# equivalent to starting a login shell, so PATH,PYTHONPATH
# will be set by /etc/bashrc  ... OR
export PATH=/metplus/METplus/ush:${PATH}

# optional dir.TEST_OUTPUT_BASE

TEST_OUTPUT_BASE=/metplus/pytmp.docker
testdockerconf=/metplus/METplus/internal_tests/use_cases/metplus_test_docker.conf


#logging_stuff="config.LOG_LEVEL=DEBUG"
logging_stuff="config.LOG_METPLUS= config.LOG_LEVEL=DEBUG"

# If NOT cartopy and no plotting desired.
#export METPLUS_DISABLE_PLOT_WRAPPERS=True

# TEST ifferent python scenarios for MET and running embedded python
#MET_PYTHON_EXE= python
#MET_PYTHON_EXE = <met_intall_path>/MET/MET_releases/external_libs/python/Python-3.7.3/python
#metpyexe="user_env_vars.MET_PYTHON_EXE=<met_install_path>/MET/MET_releases/external_libs/python/Python-3.7.3/python"
#metpyexe="user_env_vars.MET_PYTHON_EXE=<conda_env_path>/bin/python"
#metpyexe="user_env_vars.MET_PYTHON_EXE=python"
#metpyexe=""


# ----- Plotting  -------------------------------

run_me=no
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/TCMPRPlotter/TCMPRPlotter.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.tcmprplotter \
                  ${logging_stuff}\
                  "$@"
fi


# ----- python embedding -------------------------------
run_me=no
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC_python_embedding_user_py.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.ascii2nc_pyembedusr \
                  ${logging_stuff} ${metpyexe}\
                  "$@"
fi

run_me=no
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/ASCII2NC/ASCII2NC_python_embedding.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.ascii2nc_pyembed \
                  ${logging_stuff} ${metpyexe}\
                  "$@"
fi

run_me=no
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/CustomIngest/CustomIngest.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.customingest \
                  ${logging_stuff} ${metpyexe}\
                  "$@"
fi



# ----- Stat Analysis -------------------------------
run_me=yes
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/StatAnalysis/StatAnalysis.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.statanalysis \
                  ${logging_stuff} \
                  "$@"
fi

# ----- Ensemble Stat -------------------------------
run_me=yes
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/EnsembleStat/EnsembleStat.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.ensemblestat \
                  ${logging_stuff} \
                  "$@"
fi


# ----- TC Pairs -------------------------------

run_me=no
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/TCPairs/TCPairs_ETC.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.tcpairs_ETC \
                  ${logging_stuff} \
                  "$@"
fi

run_me=no
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/TCPairs/TCPairs_HWRF.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.tcpairs_HWRF \
                  ${logging_stuff} \
                  "$@"
fi



# ----- Series By Init -------------------------------

# Early exit issue !!!!!!!!!!!!
run_me=no
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/SeriesByInit/SeriesByInit.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.seriesbyinit \
                  ${logging_stuff} \
                  "$@"
fi


# ----- Series By Lead - all forecast hours -------------------------------

# Uses ncdump, ncap2
run_me=no
if [ ${run_me} == 'yes' ]
then
master_metplus.py -c use_cases/met_tool_wrapper/SeriesByLead/SeriesByLead.conf \
                  -c ${testdockerconf} \
                  dir.OUTPUT_BASE=${TEST_OUTPUT_BASE}/pytmp.seriesbylead \
                  ${logging_stuff} \
                  "$@"
fi

exit 0

