# Test Use Cases in MET Tool Wrapper
# Author: George McCabe 05/2020
# Usage: test_use_case_met_tool_wrapper.sh
# About: Called by the .travis.yml file to run use cases found in parm/use_cases/met_tool_wrapper
# Note: Sample data tarball values must be updated if a new version is added to a release

met_tool_wrapper_tarball=https://github.com/dtcenter/METplus/releases/download/v3.1/sample_data-met_tool_wrapper-3.1.tgz

gempak_to_cf_location=https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar

source ${OWNER_BUILD_DIR}/METplus/internal_tests/use_cases/metplus_test_env.docker.sh
export TRAVIS_OUTPUT_BASE=${METPLUS_TEST_OUTPUT_BASE/$DOCKER_WORK_DIR/$OWNER_BUILD_DIR}
export TRAVIS_INPUT_BASE=${METPLUS_TEST_INPUT_BASE/$DOCKER_WORK_DIR/$OWNER_BUILD_DIR}
export TRAVIS_PREV_OUTPUT_BASE=${METPLUS_TEST_PREV_OUTPUT_BASE/$DOCKER_WORK_DIR/$OWNER_BUILD_DIR}

echo 'Owner Build Dir:' ${OWNER_BUILD_DIR}
echo 'pwd:' `pwd`
echo mkdir -p ${TRAVIS_PREV_OUTPUT_BASE}
mkdir -p ${TRAVIS_PREV_OUTPUT_BASE}
echo mkdir -p ${TRAVIS_OUTPUT_BASE}
mkdir -p ${TRAVIS_OUTPUT_BASE}
echo mkdir -p ${TRAVIS_INPUT_BASE}
mkdir -p ${TRAVIS_INPUT_BASE}

cd ${OWNER_BUILD_DIR}/test.metplus.data

#echo Downloading $met_tool_wrapper_tarball
#echo curl -L -O ${met_tool_wrapper_tarball}
#curl -L -O ${met_tool_wrapper_tarball}

#echo file `basename $met_tool_wrapper_tarball`
#tarball_basename=`basename $met_tool_wrapper_tarball`
#echo `file $tarball_basename`

#echo tar xfzp `basename $met_tool_wrapper_tarball`
#tar xfzp `basename $met_tool_wrapper_tarball`

#echo Downloading $gempak_to_cf_location
#curl -L -O $gempak_to_cf_location

#${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_setup.sh

echo 'listing input directory'
ls -alR ${OWNER_BUILD_DIR}/input

echo Running tests...

returncode=0
echo 'Calling docker_run_metplus, returncode=' $returncode 

${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "${DOCKER_WORK_DIR}/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --met_tool_wrapper" $returncode
returncode=$?

echo 'Intermediate return code=' $returncode 

rm -rf ${TRAVIS_OUTPUT_BASE}/logs
mv ${TRAVIS_OUTPUT_BASE}/* ${TRAVIS_PREV_OUTPUT_BASE}/

${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "pip3 install h5py; ${DOCKER_WORK_DIR}/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --config met_tool_wrapper/PCPCombine/PCPCombine_python_embedding.conf,user_env_vars.MET_PYTHON_EXE=python3" $returncode
returncode=$?

echo '2nd Intermediate return code=' $returncode 

rm -rf ${TRAVIS_OUTPUT_BASE}/logs
mv ${TRAVIS_OUTPUT_BASE}/* ${TRAVIS_PREV_OUTPUT_BASE}/

### put cyclone plotter with cartopy and matplotlib
${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "${DOCKER_WORK_DIR}/METplus/ci/travis_jobs/get_cartopy.sh; pip3 install matplotlib; export DISPLAY=localhost:0.0; /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --config met_tool_wrapper/CyclonePlotter/CyclonePlotter.conf,user_env_vars.MET_PYTHON_EXE=python3" $returncode
returncode=$?

echo 'Final return code=' $returncode 

rm -rf ${TRAVIS_OUTPUT_BASE}/logs
mv ${TRAVIS_OUTPUT_BASE}/* ${TRAVIS_PREV_OUTPUT_BASE}/

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
