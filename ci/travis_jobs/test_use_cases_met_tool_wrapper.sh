mkdir -p ${OWNER_BUILD_DIR}/test-use-case-output
mkdir -p ${OWNER_BUILD_DIR}/test.metplus.data

cd ${OWNER_BUILD_DIR}/test.metplus.data

curl -L -O https://github.com/NCAR/METplus/releases/download/v3.0/sample_data-met_test-9.0.tgz
tar xfzp sample_data-met_test-9.0.tgz

curl -L -O https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar

docker pull ${DOCKERHUB_TAG}
docker images
docker run --rm -e "PATH=/metplus/METplus/ush:$PATH" -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash -c 'echo $MY_CUSTOM_VAR;which master_metplus.py;ls -al /metplus;python -V'
docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash /metplus/METplus/internal_tests/use_cases/run_test_use_cases.sh docker --met_tool_wrapper
returncode=$?

# Dump the output directories from running METplus
#ls -alR ${OWNER_BUILD_DIR}/test-use-case-output

# Dump and see how much space is left on Travis disk.
df -h

exit $returncode
