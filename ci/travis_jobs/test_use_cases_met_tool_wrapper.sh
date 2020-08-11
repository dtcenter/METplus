# Test Use Cases in MET Tool Wrapper
# Author: George McCabe 05/2020
# Usage: test_use_case_met_tool_wrapper.sh
# About: Called by the .travis.yml file to run use cases found in parm/use_cases/met_tool_wrapper
# Note: Sample data tarball values must be updated if a new version is added to a release

met_tool_wrapper_tarball=https://github.com/NCAR/METplus/releases/download/v3.1/sample_data-met_tool_wrapper-3.1.tgz

gempak_to_cf_location=https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar

mkdir -p ${OWNER_BUILD_DIR}/test-use-case-output
mkdir -p ${OWNER_BUILD_DIR}/test.metplus.data

cd ${OWNER_BUILD_DIR}/test.metplus.data

echo Downloading $met_tool_wrapper_tarball
curl -L -O $met_tool_wrapper_tarball

echo tar xfzp `basename $met_tool_wrapper_tarball`
tar xfzp `basename $met_tool_wrapper_tarball`

echo Downloading $gempak_to_cf_location
curl -L -O $gempak_to_cf_location

# set clone from travis env var to tell docker not to clone repository
# because travis is handling that step
export CLONE_FROM_TRAVIS=true

echo Get Docker image: ${DOCKERHUB_TAG}
docker build -t ${DOCKERHUB_TAG} --build-arg CLONE_FROM_TRAVIS internal_tests/docker/.
docker images
docker run --rm -e "PATH=/metplus/METplus/ush:$PATH" -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash -c 'echo $MY_CUSTOM_VAR;which master_metplus.py;ls -al /metplus;python3 -V'

echo Running tests...
docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --met_tool_wrapper
returncode=$?

echo Tests completed.

# Dump the output directories from running METplus
#ls -alR ${OWNER_BUILD_DIR}/test-use-case-output

# Dump and see how much space is left on Travis disk.
df -h

exit $returncode
