#!/bin/bash

#clean up, delete this
#echo 'In docker_run_metplus.sh, DOCKERHUB_TAG =', ${DOCKERHUB_TAG}


echo  In docker_run_metplus.sh, RUNNING: $1
#docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash -c "$1"
docker run --rm -v ${OWNER_BUILD_DIR}:/metplus -v ${OWNER_BUILD_DIR}/test.metplus.data:/input -v ${OWNER_BUILD_DIR}/test-use-case-output:/output ${DOCKERHUB_TAG} /bin/bash -c "$1"
ret=$?

#check return codes
echo "In docker_run_metplus.sh previous return code: $2
echo "In docker_run_metplus.sh new return code: $ret

if [ $ret != 0 ]; then
  exit $ret
else
  exit $2
fi

exit 999
