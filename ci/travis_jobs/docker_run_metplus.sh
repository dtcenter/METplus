#!/bin/bash

# set umask to 002 so that the travis user has (group) permission
# to move files that are created by docker

VOLUMES=$2

echo 'In docker_run_metplus, $VOLUMES= ',$VOLUMES
echo 'docker images'
docker images

echo  In docker_run_metplus.sh, RUNNING: $1
docker run --rm \
--user root:$UID \
$VOLUMES \
-v ${OWNER_BUILD_DIR}:${DOCKER_WORK_DIR} \
-v ${OWNER_BUILD_DIR}/output:${DOCKER_DATA_DIR}/output \
-v ${OWNER_BUILD_DIR}/input:${DOCKER_DATA_DIR}/input \
${DOCKERHUB_TAG} \
/bin/bash -c "umask 002; $1"
