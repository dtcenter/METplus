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

${TRAVIS_BUILD_DIR}/ci/travis_jobs/download_sample_data.sh $@

source ${OWNER_BUILD_DIR}/METplus/internal_tests/use_cases/metplus_test_env.docker.sh
export TRAVIS_OUTPUT_BASE=${METPLUS_TEST_OUTPUT_BASE/$DOCKER_WORK_DIR/$OWNER_BUILD_DIR}
export TRAVIS_PREV_OUTPUT_BASE=${METPLUS_TEST_PREV_OUTPUT_BASE/$DOCKER_WORK_DIR/$OWNER_BUILD_DIR}

echo mkdir -p ${TRAVIS_PREV_OUTPUT_BASE}
mkdir -p ${TRAVIS_PREV_OUTPUT_BASE}
echo mkdir -p ${TRAVIS_OUTPUT_BASE}
mkdir -p ${TRAVIS_OUTPUT_BASE}
echo mkdir -p ${TRAVIS_INPUT_BASE}
mkdir -p ${TRAVIS_INPUT_BASE}

${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_setup.sh

echo Run tests...
test_args=''
for i in "$@"
do
  if [ -z "$i" ]; then
    continue
  fi
  if [ $i == "medium_range3" ]; then
      

    echo medium_range3
    echo TRAVIS_BUILD_DIR ${TRAVIS_BUILD_DIR}
    echo DOCKER_WORK_DIR ${DOCKER_WORK_DIR}
    echo calling docker_run_metplus
  
  # use docker_run_metplus.sh
    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "${DOCKER_WORK_DIR}/METplus/ci/travis_jobs/get_pygrib.sh; /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --config model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf,user_env_vars.MET_PYTHON_EXE=python3" $returncode
    returncode=$?
  else
    test_args=${test_args}" --"${i}      
  fi

done

docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker ${test_args}
returncode=$?


echo Tests completed.
# Dump the output directories from running METplus
ls -alR ${OWNER_BUILD_DIR}/test-use-case-output

# Dump and see how much space is left on Travis disk.
df -h

exit $returncode
