#! /bin/bash

gempak_to_cf_location=https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar

source ${OWNER_BUILD_DIR}/METplus/internal_tests/use_cases/metplus_test_env.docker.sh
export TRAVIS_INPUT_BASE=${METPLUS_TEST_INPUT_BASE/$DOCKER_DATA_DIR/$OWNER_BUILD_DIR}

cd ${TRAVIS_INPUT_BASE}
echo Downloading $gempak_to_cf_location into ${TRAVIS_INPUT_BASE}
curl -L -O $gempak_to_cf_location
