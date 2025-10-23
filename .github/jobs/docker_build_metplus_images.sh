#!/bin/bash

# assumes SOURCE_BRANCH and METPLUS_VERSION are set before calling script
# SOURCE_BRANCH is METplus branch or tag used to clone METplus repo
# METPLUS_VERSION is branch or tag with v prefix removed used to get
#   component versions and set Docker tag names

source "${GITHUB_WORKSPACE}"/.github/jobs/bash_functions.sh

dockerhub_repo=${DOCKERHUB_BASE_REPO}
dockerhub_repo_analysis=${DOCKERHUB_ANALYSIS_REPO}

# if rc is in version number, get main_vX.Y, otherwise get X.Y-latest or develop
if [[ "${METPLUS_VERSION}" =~ rc ]]; then
  tag_format="main_v{X}.{Y}"
else
  tag_format="{X}.{Y}-latest"
fi

# Get MET tag and adjust MET Docker repo if develop
met_tag=$("${GITHUB_WORKSPACE}"/develop/metplus/component_versions.py -v "${METPLUS_VERSION}" -o MET -f ${tag_format} --no-get_dev_version)
echo "$met_tag"

MET_DOCKER_REPO=met
if [ "$met_tag" == "develop" ] || [[ "${met_tag}" =~ ^main_v[0-9]+\.[0-9]+ ]]; then
  MET_DOCKER_REPO=met-dev
fi

# get METplus Analysis tool versions
METDATAIO_VERSION=$("${GITHUB_WORKSPACE}"/develop/metplus/component_versions.py -v "${METPLUS_VERSION}" -o METdataio)
METCALCPY_VERSION=$("${GITHUB_WORKSPACE}"/develop/metplus/component_versions.py -v "${METPLUS_VERSION}" -o METcalcpy)
METPLOTPY_VERSION=$("${GITHUB_WORKSPACE}"/develop/metplus/component_versions.py -v "${METPLUS_VERSION}" -o METplotpy)

# Build metplus image
METPLUS_IMAGE_NAME=${dockerhub_repo}:${METPLUS_VERSION}
if ! time_command docker build -t "$METPLUS_IMAGE_NAME" \
       --build-arg SOURCE_VERSION="$SOURCE_BRANCH" \
       --build-arg MET_TAG="$met_tag" \
       --build-arg MET_DOCKER_REPO="$MET_DOCKER_REPO" \
       -f "${GITHUB_WORKSPACE}"/internal/scripts/docker/Dockerfile \
       "${GITHUB_WORKSPACE}"; then
    exit 1
fi

# Build metplus-analysis image
METPLUS_A_IMAGE_NAME=${dockerhub_repo_analysis}:${METPLUS_VERSION}
if ! time_command docker build -t "$METPLUS_A_IMAGE_NAME" \
       --build-arg METPLUS_BASE_TAG="${METPLUS_VERSION}" \
       --build-arg METDATAIO_VERSION="${METDATAIO_VERSION}" \
       --build-arg METCALCPY_VERSION="${METCALCPY_VERSION}" \
       --build-arg METPLOTPY_VERSION="${METPLOTPY_VERSION}" \
       -f "${GITHUB_WORKSPACE}"/internal/scripts/docker/Dockerfile.metplus-analysis \
       "${GITHUB_WORKSPACE}"; then
    exit 1
fi
