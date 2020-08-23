#!/bin/bash

echo 'In docker_run_metplus.sh, DOCKERHUB_TAG =', ${DOCKERHUB_TAG}

docker run --rm --it -v ${OWNER_BUILD_DIR}:/metplus -v ${OWNER_BUILD_DIR}/test.metplus.data:/metplus/input -v ${OWNER_BUILD_DIR}/test-use-case-output:/metplus/output ${DOCKERHUB_TAG} /bin/bash
#docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash -c "$1"
docker run --rm -v ${OWNER_BUILD_DIR}:/metplus -v ${OWNER_BUILD_DIR}/test.metplus.data:/metplus/input -v ${OWNER_BUILD_DIR}/test-use-case-output:/metplus/output ${DOCKERHUB_TAG} /bin/bash -c "$2"
ret=$?

echo "In docker_run_metplus.sh 1:", $1
echo "In docker_run_metplus.sh 2:", $2
echo "In docker_run_metplus.sh ret:", $ret

if [ $ret != 0 ]; then
  exit $ret
else
  exit $2
fi

exit 999
