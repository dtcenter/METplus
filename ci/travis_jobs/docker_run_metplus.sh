#!/bin/bash

# set umask to 002 so that the travis user has (group) permission
# to move files that are created by docker

set VOLUMES = $1
echo 'In docker_run_metplus, $VOLUMES= ',$VOLUMES
echo 'docker images'
docker images

echo  In docker_run_metplus.sh, RUNNING: $2
docker run --rm --user root:$UID $VOLUMES -v ${OWNER_BUILD_DIR}:${DOCKER_WORK_DIR} -v ${OWNER_BUILD_DIR}/input:${DOCKER_DATA_INPUT} -v ${OWNER_BUILD_DIR}/output:/output ${DOCKERHUB_TAG} /bin/bash -c "umask 002; $2"
ret=$?

#check return codes
echo "In docker_run_metplus.sh previous return code: $3
echo "In docker_run_metplus.sh new return code: $ret

if [ $ret != 0 ]; then
  exit $ret
fi

exit $3
