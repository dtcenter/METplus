#! /bin/bash

OWNER_BUILD_DIR=`dirname ${GITHUB_WORKSPACE}`
echo OWNER_BUILD_DIR is $OWNER_BUILD_DIR

source ${GITHUB_WORKSPACE}/internal_tests/pytests/minimum_pytest.docker.sh
#export TRAVIS_INPUT_BASE=${METPLUS_TEST_INPUT_BASE}
#export TRAVIS_OUTPUT_BASE=${METPLUS_TEST_OUTPUT_BASE}
export TRAVIS_INPUT_BASE=${METPLUS_TEST_INPUT_BASE/$DOCKER_DATA_DIR/$OWNER_BUILD_DIR}
export TRAVIS_OUTPUT_BASE=${METPLUS_TEST_OUTPUT_BASE/$DOCKER_DATA_DIR/$OWNER_BUILD_DIR}

echo mkdir -p ${TRAVIS_INPUT_BASE}
mkdir -p ${TRAVIS_INPUT_BASE}
echo mkdir -p ${TRAVIS_OUTPUT_BASE}
mkdir -p ${TRAVIS_OUTPUT_BASE}

returncode=0
${GITHUB_WORKSPACE}/ci/jobs/docker_run_metplus.sh "pip3 install pytest-cov; export METPLUS_PYTEST_HOST=docker; cd ${DOCKER_WORK_DIR}/METplus/internal_tests/pytests; pytest --cov=../../metplus"
returncode=$?

ls -alR ${TRAVIS_OUTPUT_BASE}

if [ $returncode != 0 ]; then
  ${GITHUB_WORKSPACE}/ci/jobs/print_log_errors.py ${TRAVIS_OUTPUT_BASE} ${METPLUS_TEST_OUTPUT_BASE}
fi

exit $returncode
