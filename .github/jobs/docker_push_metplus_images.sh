#!/bin/bash

# assumes SOURCE_BRANCH is set before calling script
# assumes latest_tag will be set if pushing an official or bugfix release

source "${GITHUB_WORKSPACE}"/.github/jobs/bash_functions.sh

# get names of images to push

dockerhub_repo=dtcenter/metplus
dockerhub_repo_analysis=dtcenter/metplus-analysis

# remove v prefix
metplus_version=${SOURCE_BRANCH:1}

METPLUS_IMAGE_NAME=${dockerhub_repo}:${metplus_version}
METPLUS_A_IMAGE_NAME=${dockerhub_repo_analysis}:${metplus_version}

# skip docker push if credentials are not set
if [ -z ${DOCKER_USERNAME+x} ] || [ -z ${DOCKER_PASSWORD+x} ]; then
    echo "DockerHub credentials not set. Skipping docker push"
    exit 0
fi

echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin

# push images

if ! time_command docker push "${METPLUS_IMAGE_NAME}"; then
  exit 1
fi

if ! time_command docker push "${METPLUS_A_IMAGE_NAME}"; then
  exit 1
fi

# only push X.Y-latest tag if official or bugfix release
# shellcheck disable=SC2154
if [ "${latest_tag}" != "" ]; then
    if ! time_command docker push "${dockerhub_repo}:${latest_tag}"; then
      exit 1
    fi
    if ! time_command docker push "${dockerhub_repo_analysis}:${latest_tag}"; then
      exit 1
    fi
fi
