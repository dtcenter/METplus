# Test Use Cases in MET Tool Wrapper
# Author: George McCabe 05/2020
# Usage: test_use_case_met_tool_wrapper.sh
# About: Called by the .travis.yml file to run use cases found in parm/use_cases/met_tool_wrapper
# Note: Sample data tarball values must be updated if a new version is added to a release

met_tool_wrapper_tarball=https://github.com/DTCenter/METplus/releases/download/v3.1/sample_data-met_tool_wrapper-3.1.tgz

gempak_to_cf_location=https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar

echo 'Owner Build Dir:' ${OWNER_BUILD_DIR}
echo 'pwd:' `pwd`
echo "mkdir -p {OWNER_BUILD_DIR}/test-use-case-output"
mkdir -p ${OWNER_BUILD_DIR}/test-use-case-output
echo "mkdir -p {OWNER_BUILD_DIR}/test.metplus.data"
mkdir -p ${OWNER_BUILD_DIR}/test.metplus.data

cd ${OWNER_BUILD_DIR}/test.metplus.data

#tea changed this to look more like test_use_cases_model_applications.sh
echo Downloading $met_tool_wrapper_tarball
echo curl -L -O ${met_tool_wrapper_tarball}
curl -L -O ${met_tool_wrapper_tarball}

echo file `basename $met_tool_wrapper_tarball`
tarball_basename=`basename $met_tool_wrapper_tarball`
echo `file $tarball_basename`

echo tar xfzp `basename $met_tool_wrapper_tarball`
tar xfzp `basename $met_tool_wrapper_tarball`

echo Downloading $gempak_to_cf_location
curl -L -O $gempak_to_cf_location

echo Getting Docker image
docker pull ${DOCKERHUB_TAG}/test
docker images
docker run --rm -e "PATH=/metplus/METplus/ush:$PATH" -v ${OWNER_BUILD_DIR}:/metplus -v ${OWNER_BUILD_DIR}/test.metplus.data:/input -v ${OWNER_BUILD_DIR}/test-use-case-output:/output {DOCKERHUB_TAG} /bin/bash -c 'echo $MY_CUSTOM_VAR;which master_metplus.py;ls -al /metplus;python -V'

echo Running tests...

returncode=0
echo 'Calling docker_run_metplus, returncode=' $returncode 

${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "/metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --met_tool_wrapper" $returncode
returncode=$?

echo 'Intermediate return code=' $returncode 

${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "pip install h5py; /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --config met_tool_wrapper/PCPCombine_python_embedding.conf,user_env_vars.MET_PYTHON_EXE=python3" $returncode
returncode=$?

echo '2nd Intermediate return code=' $returncode 

${TRAVIS_BUILD_DIR}/ci/travis_jobs/docker_run_metplus.sh "pip install h5py; /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --config met_tool_wrapper/GridStat/GridStat.conf" $returncode
returncode=$?

echo 'Final return code=' $returncode 

echo Tests completed.

# Dump the output directories from running METplus
#ls -alR ${OWNER_BUILD_DIR}/test-use-case-output

# Dump and see how much space is left on Travis disk.
df -h

exit $returncod-
