#! /bin/bash

# Run by GitHub Actions (in .github/workflows/testing.yml) to build
# METplus Docker image and put it up to DockerHub so it can be
# used by the use case tests.
# If GitHub Actions run is triggered by a fork that does not have
# permissions to push Docker images to DockerHub, the script is
# is also called (in ci/actions/run_tests/entrypoint.sh) to
# build the Docker image to use for each use case test group

branch_name=`${GITHUB_WORKSPACE}/ci/jobs/print_branch_name.py`
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  branch_name=${branch_name}-pull_request
fi

#DOCKERHUB_TAG=dtcenter/metplus-dev:${DOCKER_IMAGE}
DOCKERHUB_TAG=dtcenter/metplus-dev:${branch_name}

echo Get Docker image: ${DOCKERHUB_TAG}
echo 'doing docker build'
# Note: adding --build-arg <arg-name> without any value tells docker to
#  use value from local environment (export DO_GIT_CLONE)

echo Timing docker pull...
start_seconds=$SECONDS

# pipe result to true because it will fail if image has not yet been built
docker pull ${DOCKERHUB_TAG} &> /dev/null || true

duration=$(( SECONDS - start_seconds ))
echo TIMING docker_setup
echo "Docker pull took $(($duration / 60)) minutes and $(($duration % 60)) seconds."

echo Timing docker build with --cache-from...
start_seconds=$SECONDS

# set DOCKERFILE_PATH that is used by docker hook script get_met_version
export DOCKERFILE_PATH=${GITHUB_WORKSPACE}/ci/docker/Dockerfile

MET_TAG=`${GITHUB_WORKSPACE}/ci/docker/hooks/get_met_version`
echo Running docker build with MET_TAG=$MET_TAG

docker build --pull --cache-from ${DOCKERHUB_TAG} \
-t ${DOCKERHUB_TAG} \
--build-arg OBTAIN_SOURCE_CODE='copy' \
--build-arg MET_TAG=$MET_TAG \
-f ${DOCKERFILE_PATH} ${GITHUB_WORKSPACE}

duration=$(( SECONDS - start_seconds ))
echo TIMING docker_setup
echo "Docker build took $(($duration / 60)) minutes and $(($duration % 60)) seconds."
echo

# skip docker push if credentials are not set
if [ -z ${DOCKER_USERNAME+x} ] || [ -z ${DOCKER_PASSWORD+x} ]; then
    echo "DockerHub credentials not set. Skipping docker push"
    exit 0
fi

echo Timing docker push...
start_seconds=$SECONDS

echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
docker push ${DOCKERHUB_TAG}

duration=$(( SECONDS - start_seconds ))
echo TIMING docker_setup
echo "Docker push took $(($duration / 60)) minutes and $(($duration % 60)) seconds."
echo

echo DOCKER IMAGES after DOCKER_SETUP
docker images
echo

echo 'done'
