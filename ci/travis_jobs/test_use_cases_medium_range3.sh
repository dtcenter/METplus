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

echo Run tests...
returncode=0

echo CURRENT_BRANCH = ${CURRENT_BRANCH}

echo Timing get data volumes...
start_seconds=$SECONDS

VOLUMES=`${TRAVIS_BUILD_DIR}/ci/travis_jobs/get_data_volumes.py medium_range3`

duration=$(( SECONDS - start_seconds ))
echo "Get data volumes took $(($duration / 60)) minutes and $(($duration % 60)) seconds."

echo medium_range3

# use docker_run_metplus.sh
${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "${DOCKER_WORK_DIR}/METplus/ci/travis_jobs/get_pygrib.sh; pip3 install metpy; ${DOCKER_WORK_DIR}/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --config model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf,user_env_vars.MET_PYTHON_EXE=python3 --config model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.conf,user_env_vars.MET_PYTHON_EXE=python3" $returncode "$VOLUMES"
returncode=$?

# remove logs dir and move data to previous output base so next run will not prompt
rm -rf ${TRAVIS_OUTPUT_BASE}/logs
mv ${TRAVIS_OUTPUT_BASE}/* ${TRAVIS_PREV_OUTPUT_BASE}/

echo Tests completed.

# Dump the output directories from running METplus
#echo listing TRAVIS_OUTPUT_BASE
#ls -alR ${TRAVIS_OUTPUT_BASE}

#echo
#echo listing TRAVIS_PREV_OUTPUT_BASE
#ls -alR ${TRAVIS_PREV_OUTPUT_BASE}

# Dump and see how much space is left on Travis disk.
df -h

exit $returncode
