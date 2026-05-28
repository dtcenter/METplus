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

# only push X.Y and X.Y-latest tags if requested for official or bugfix releases
# NOTE: eventually remove X.Y-latest tags in favor of just X.Y
#       keep -latest until all references to it have been replaced with X.Y
if [[ "${UPDATE_LATEST}" == "true" && "${METPLUS_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  xy_version=$(echo ${METPLUS_VERSION} | cut -f1,2 -d'.')

  for tag in "${xy_version}" "${xy_version}-latest"; do
    # tag and push the METplus image
    if ! time_command docker tag ${METPLUS_IMAGE_NAME} "${dockerhub_repo}:${tag}"; then
      exit 1
    fi
    if ! time_command docker push "${dockerhub_repo}:${tag}"; then
      exit 1
    fi

    # tag and push the METplus Analysis image
    if ! time_command docker tag ${METPLUS_A_IMAGE_NAME} "${dockerhub_repo_analysis}:${tag}"; then
      exit 1
    fi
    if ! time_command docker push "${dockerhub_repo_analysis}:${tag}"; then
      exit 1
    fi
  done
fi
