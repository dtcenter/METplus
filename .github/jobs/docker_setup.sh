#! /bin/bash

# Run by GitHub Actions (in .github/workflows/testing.yml) to build
# METplus Docker image and put it up to DockerHub so it can be
# used by the use case tests.
# If GitHub Actions run is triggered by a fork that does not have
# permissions to push Docker images to DockerHub, the script is
# is also called (in .github/actions/run_tests/entrypoint.sh) to
# build the Docker image to use for each use case test group

source ${GITHUB_WORKSPACE}/.github/jobs/bash_functions.sh

branch_name=`${GITHUB_WORKSPACE}/.github/jobs/print_branch_name.py`
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  branch_name=${branch_name}-pull_request
fi

DOCKERHUB_TAG=dtcenter/metplus-dev:${branch_name}

echo Get Docker image: ${DOCKERHUB_TAG}

# can't use time_command function for this command because it contains redirection
start_seconds=$SECONDS

# pipe result to true because it will fail if image has not yet been built
docker pull ${DOCKERHUB_TAG} &> /dev/null || true

duration=$(( SECONDS - start_seconds ))
echo "TIMING: docker pull ${DOCKERHUB_TAG} took `printf '%02d' $(($duration / 60))`:`printf '%02d' $(($duration % 60))` (MM:SS)"

# set DOCKERFILE_PATH that is used by docker hook script get_met_version
export DOCKERFILE_PATH=${GITHUB_WORKSPACE}/ci/docker/Dockerfile

MET_TAG=`${GITHUB_WORKSPACE}/ci/docker/hooks/get_met_version`

echo Setting DOCKER_BUILDKIT=1
export DOCKER_BUILDKIT=1

time_command docker build --pull --cache-from ${DOCKERHUB_TAG} \
-t ${DOCKERHUB_TAG} \
--build-arg OBTAIN_SOURCE_CODE=copy \
--build-arg MET_TAG=$MET_TAG \
-f ${DOCKERFILE_PATH} ${GITHUB_WORKSPACE}

# skip docker push if credentials are not set
if [ -z ${DOCKER_USERNAME+x} ] || [ -z ${DOCKER_PASSWORD+x} ]; then
    echo "DockerHub credentials not set. Skipping docker push"
    exit 0
fi

echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
time_command docker push ${DOCKERHUB_TAG}

echo Running docker images
docker images
