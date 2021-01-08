#! /bin/bash

DOCKERHUB_TAG=dtcenter/metplus-dev:${BRANCH_NAME}

echo Get Docker image: ${DOCKERHUB_TAG}
echo 'doing docker build'
# Note: adding --build-arg <arg-name> without any value tells docker to
#  use value from local environment (export DO_GIT_CLONE)

echo Timing docker pull...
start_seconds=$SECONDS

# pipe result to true because it will fail if image has not yet been built
docker pull ${DOCKERHUB_TAG} || true

duration=$(( SECONDS - start_seconds ))
echo TIMING docker_setup
echo "Docker pull took $(($duration / 60)) minutes and $(($duration % 60)) seconds."

echo Timing docker build with --cache-from...
start_seconds=$SECONDS

docker build --pull --cache-from ${DOCKERHUB_TAG} \
-t ${DOCKERHUB_TAG} \
--build-arg SOURCE_BRANCH=${BRANCH_NAME} \
--build-arg MET_BRANCH=develop \
--build-arg DO_GIT_CLONE ${GITHUB_WORKSPACE}/ci/docker

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
