#! /bin/bash

source ${OWNER_BUILD_DIR}/METplus/internal_tests/pytests/minimum_pytest.docker.sh
export TRAVIS_INPUT_BASE=${METPLUS_TEST_INPUT_BASE/$DOCKER_DATA_DIR/$OWNER_BUILD_DIR}
export TRAVIS_OUTPUT_BASE=${METPLUS_TEST_OUTPUT_BASE/$DOCKER_DATA_DIR/$OWNER_BUILD_DIR}

echo mkdir -p ${TRAVIS_INPUT_BASE}
mkdir -p ${TRAVIS_INPUT_BASE}
echo mkdir -p ${TRAVIS_OUTPUT_BASE}
mkdir -p ${TRAVIS_OUTPUT_BASE}

${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_setup.sh

docker run --rm -v ${OWNER_BUILD_DIR}:${DOCKER_WORK_DIR} ${DOCKERHUB_TAG} /bin/bash -c "pip3 install pytest-cov; export METPLUS_PYTEST_HOST=docker; cd ${DOCKER_WORK_DIR}/METplus/internal_tests/pytests; pytest --cov=../../metplus"

ls -alR ${TRAVIS_OUTPUT_BASE}
