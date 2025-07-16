#!/bin/bash

# assumes SOURCE_BRANCH is set before calling script

source "${GITHUB_WORKSPACE}"/.github/jobs/bash_functions.sh

dockerhub_repo=dtcenter/metplus
dockerhub_repo_analysis=dtcenter/metplus-analysis

# remove v prefix
metplus_version=${SOURCE_BRANCH:1}

# if rc is in version number, get main_vX.Y, otherwise get X.Y-latest or develop
if [[ "${metplus_version}" =~ rc ]]; then
  tag_format="main_v{X}.{Y}"
else
  tag_format="{X}.{Y}-latest"
fi

# Get MET tag and adjust MET Docker repo if develop
met_tag=$("${GITHUB_WORKSPACE}"/develop/metplus/component_versions.py -v "${metplus_version}" -o MET -f ${tag_format} --no-get_dev_version)
echo "$met_tag"

MET_DOCKER_REPO=met
if [ "$met_tag" == "develop" ] || [[ "${met_tag}" =~ ^main_v[0-9]+\.[0-9]+ ]]; then
    MET_DOCKER_REPO=met-dev
fi

# get METplus Analysis tool versions
METDATAIO_VERSION=$("${GITHUB_WORKSPACE}"/develop/metplus/component_versions.py -v "${metplus_version}" -o METdataio)
METCALCPY_VERSION=$("${GITHUB_WORKSPACE}"/develop/metplus/component_versions.py -v "${metplus_version}" -o METcalcpy)
METPLOTPY_VERSION=$("${GITHUB_WORKSPACE}"/develop/metplus/component_versions.py -v "${metplus_version}" -o METplotpy)

# Build metplus image
METPLUS_IMAGE_NAME=${dockerhub_repo}:${metplus_version}
if ! time_command docker build -t "$METPLUS_IMAGE_NAME" \
       --build-arg SOURCE_VERSION="$SOURCE_BRANCH" \
       --build-arg MET_TAG="$met_tag" \
       --build-arg MET_DOCKER_REPO="$MET_DOCKER_REPO" \
       -f "${GITHUB_WORKSPACE}"/internal/scripts/docker/Dockerfile \
       "${GITHUB_WORKSPACE}"; then
    exit 1
fi

# Build metplus-analysis image
METPLUS_A_IMAGE_NAME=${dockerhub_repo_analysis}:${metplus_version}
if ! time_command docker build -t "$METPLUS_A_IMAGE_NAME" \
       --build-arg METPLUS_BASE_TAG="${metplus_version}" \
       --build-arg METDATAIO_VERSION="${METDATAIO_VERSION}" \
       --build-arg METCALCPY_VERSION="${METCALCPY_VERSION}" \
       --build-arg METPLOTPY_VERSION="${METPLOTPY_VERSION}" \
       -f "${GITHUB_WORKSPACE}"/internal/scripts/docker/Dockerfile.metplus-analysis \
       "${GITHUB_WORKSPACE}"; then
    exit 1
fi
