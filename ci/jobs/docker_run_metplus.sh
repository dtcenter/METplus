#!/bin/bash

DOCKERHUB_TAG=dtcenter/metplus-dev:${BRANCH_NAME}

# set umask to 002 so that the travis user has (group) permission
# to move files that are created by docker
export OWNER_BUILD_DIR=`dirname ${GITHUB_WORKSPACE}`
echo OWNER_BUILD_DIR is $OWNER_BUILD_DIR

VOLUMES=$2
echo --Timing docker pull in docker_run_metplus...
start_seconds=$SECONDS

echo Pulling image ${DOCKERHUB_TAG} from DockerHub
docker pull ${DOCKERHUB_TAG}
if [ $? != 0 ]; then
    echo Docker pull failed. Building image locally
    ${GITHUB_WORKSPACE}/ci/jobs/docker_setup.sh
fi

duration=$(( SECONDS - start_seconds ))
echo --TIMING docker_run_metplus
echo "--Docker pull took $(($duration / 60)) minutes and $(($duration % 60)) seconds."

echo 'In docker_run_metplus, $VOLUMES= ',$VOLUMES
echo 'DOCKER IMAGES in docker_run_metplus'
docker images

echo --Timing docker run in docker_run_metplus...
start_seconds=$SECONDS

echo  In docker_run_metplus.sh, RUNNING: $1

docker run --rm \
--user root:$UID \
$VOLUMES \
-v ${OWNER_BUILD_DIR}:${DOCKER_WORK_DIR} \
-v ${OWNER_BUILD_DIR}/output:${DOCKER_DATA_DIR}/output \
-v ${OWNER_BUILD_DIR}/input:${DOCKER_DATA_DIR}/input \
${DOCKERHUB_TAG} \
/bin/bash -c "umask 002; $1"
ret=$?

duration=$(( SECONDS - start_seconds ))
echo --TIMING docker_run_metplus
echo "--Docker run took $(($duration / 60)) minutes and $(($duration % 60)) seconds."

exit $ret
