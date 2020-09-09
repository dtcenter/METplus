# Test Use Cases in Model Applications
# Author: George McCabe 05/2020
# Usage: test_use_case_model_applications.sh [ <use_case_dir> ]
#   Where use_case_dir is the name of a directory under parm/use_cases/model_applications
#   Multiple values can be specified separated by a space
# About: Called by the .travis.yml file to run use cases found in parm/use_cases/model_applications/<use_case_dir>
# Note: Sample data tarball values must be updated if a new version is added to a release
#   If a new subdirectory is added to the repository, add a new tarball variable (with a
#   name ending with _var) and add a new block to the if/elif/else statement to pick the
#   correct use case tarball.

source ${OWNER_BUILD_DIR}/METplus/internal_tests/use_cases/metplus_test_env.docker.sh
export TRAVIS_OUTPUT_BASE=${METPLUS_TEST_OUTPUT_BASE/$DOCKER_DATA_DIR/$OWNER_BUILD_DIR}
export TRAVIS_PREV_OUTPUT_BASE=${METPLUS_TEST_PREV_OUTPUT_BASE/$DOCKER_DATA_DIR/$OWNER_BUILD_DIR}

echo mkdir -p ${TRAVIS_PREV_OUTPUT_BASE}
mkdir -p ${TRAVIS_PREV_OUTPUT_BASE}
echo mkdir -p ${TRAVIS_OUTPUT_BASE}
mkdir -p ${TRAVIS_OUTPUT_BASE}

#${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_setup.sh

echo Run tests...
returncode=0

# set volumes to include met_tool_wrapper because some use cases mistakenly use
# data from that volume. Eventually this should be set to an empty string
VOLUMES="--volumes-from met_tool_wrapper"

# hold all command line arguments to pass to test_use_cases script
test_args=''

# loop over all command line arguments and add appropriate data volumes
for i in "$@"
do
  if [ -z "$i" ]; then
    continue
  fi

   # get sample data tarball name
  if [ $i == "convection_allowing_models" ]; then
      VOLUMES+=" --volumes-from $i"
  elif [ $i == "climate" ]; then
      VOLUMES+=" --volumes-from $i"
  elif [ $i == "cryosphere" ]; then
      VOLUMES+=" --volumes-from $i"
  elif [ ${i:0: -1} == "medium_range" ]; then
      VOLUMES+=" --volumes-from medium_range"
  elif [ $i == "precipitation" ]; then
      VOLUMES+=" --volumes-from $i"
  elif [ $i == "s2s" ]; then
      VOLUMES+=" --volumes-from $i"
  elif [ $i == "space_weather" ]; then
      VOLUMES+=" --volumes-from $i"
  elif [ $i == "tc_and_extra_tc" ]; then
      VOLUMES+=" --volumes-from $i"
  else
      echo Invalid model_applications directory specified: $i
      exit 1
  fi

  # run use case that requires additional packages
  # otherwise add to command line args for test script
  if [ $i == "medium_range3" ]; then
      

    echo medium_range3
    echo TRAVIS_BUILD_DIR ${TRAVIS_BUILD_DIR}
    echo DOCKER_WORK_DIR ${DOCKER_WORK_DIR}
    echo calling docker_run_metplus
  
  # use docker_run_metplus.sh
    # use docker_run_metplus.sh
    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "${DOCKER_WORK_DIR}/METplus/ci/travis_jobs/get_pygrib.sh; pip3 install metpy; /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --config model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf,user_env_vars.MET_PYTHON_EXE=python3" $returncode "$VOLUMES"
    returncode=$?

    # remove logs dir and move data to previous output base so next run will not prompt
    rm -rf ${TRAVIS_OUTPUT_BASE}/logs
    mv ${TRAVIS_OUTPUT_BASE}/* ${TRAVIS_PREV_OUTPUT_BASE}/
  else
    test_args=${test_args}" --"${i}      
  fi

done

if [ "$test_args" != "" ]; then
    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "/metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker ${test_args}" $returncode "$VOLUMES"
    returncode=$?

  # remove logs dir and move data to previous output base so next run will not prompt
  rm -rf ${TRAVIS_OUTPUT_BASE}/logs
  mv ${TRAVIS_OUTPUT_BASE}/* ${TRAVIS_PREV_OUTPUT_BASE}/
fi

echo Tests completed.

# Dump the output directories from running METplus
echo listing TRAVIS_OUTPUT_BASE
ls -alR ${TRAVIS_OUTPUT_BASE}

echo
echo listing TRAVIS_PREV_OUTPUT_BASE
ls -alR ${TRAVIS_PREV_OUTPUT_BASE}


# Dump and see how much space is left on Travis disk.
df -h

exit $returncode
