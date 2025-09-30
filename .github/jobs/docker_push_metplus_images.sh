#!/bin/bash

# assumes METPLUS_VERSION is set before calling script

source "${GITHUB_WORKSPACE}"/.github/jobs/bash_functions.sh

# get names of images to push

dockerhub_repo=${DOCKERHUB_BASE_REPO}
dockerhub_repo_analysis=${DOCKERHUB_ANALYSIS_REPO}

METPLUS_IMAGE_NAME=${dockerhub_repo}:${METPLUS_VERSION}
METPLUS_A_IMAGE_NAME=${dockerhub_repo_analysis}:${METPLUS_VERSION}

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

# only push X.Y-latest tag if requested for official or bugfix releases
# shellcheck disable=SC2154
if [[ "${UPDATE_LATEST}" == "true" && "${METPLUS_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  latest_version=$(echo ${METPLUS_VERSION} | cut -f1,2 -d'.')-latest

  # tag and push the METplus image
  if ! time_command docker tag ${METPLUS_IMAGE_NAME} "${dockerhub_repo}:${latest_version}"; then
    exit 1
  fi
  if ! time_command docker push "${dockerhub_repo}:${latest_version}"; then
    exit 1
  fi

  # tag and push the METplus Analysis image
  if ! time_command docker tag ${METPLUS_A_IMAGE_NAME} "${dockerhub_repo_analysis}:${latest_version}"; then
    exit 1
  fi
  if ! time_command docker push "${dockerhub_repo_analysis}:${latest_version}"; then
    exit 1
  fi
fi
