#!/bin/bash

# assumes SOURCE_BRANCH and METPLUS_VERSION are set before calling script
# SOURCE_BRANCH is METplus branch or tag used to clone METplus repo
# METPLUS_VERSION is branch or tag with v prefix removed used to get
#   component versions and set Docker tag names
# DOCKERFILE_DIR is the directory containing the Dockerfiles to use. Set it to
#   the release's own copy so each release is built with the Dockerfiles it
#   shipped with. Defaults to the Dockerfiles in the current checkout.

source "${GITHUB_WORKSPACE}"/.github/jobs/bash_functions.sh

dockerfile_dir=${DOCKERFILE_DIR:-${GITHUB_WORKSPACE}/internal/scripts/docker}

dockerhub_repo=${DOCKERHUB_BASE_REPO}
dockerhub_repo_analysis=${DOCKERHUB_ANALYSIS_REPO}

# Build every release image on a released MET image so that the content of
# the image is determined by the release alone:
#   official release X.Y.Z    -> dtcenter/met:X.Y-latest, so that a scheduled
#                                rebuild picks up MET bugfix releases
#   beta or rc X.Y.Z-betaN/rcN -> the matching MET release, e.g.
#                                dtcenter/met:13.0.0-rc1
if [[ "${METPLUS_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  tag_format="{X}.{Y}-latest"
elif [[ "${METPLUS_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+-(beta|rc)[0-9]+$ ]]; then
  tag_format="{X}.{Y}.{Z}{N}"
else
  echo "ERROR: METplus version ${METPLUS_VERSION} is not a release version"
  exit 1
fi

MET_DOCKER_REPO=met
met_tag=$("${GITHUB_WORKSPACE}"/develop/metplus/component_versions.py -v "${METPLUS_VERSION}" -o MET -f "${tag_format}")
if [ -z "${met_tag}" ]; then
  echo "ERROR: Could not get MET version for METplus version ${METPLUS_VERSION}"
  exit 1
fi

met_image=dtcenter/${MET_DOCKER_REPO}:${met_tag}
echo "Using MET image: ${met_image}"

# The MET release image may be pushed to DockerHub after the METplus release
# is published. Fail instead of building on a different image.
if ! docker manifest inspect "${met_image}" > /dev/null; then
  echo "ERROR: MET image ${met_image} could not be verified (not found or DockerHub unreachable)."
  echo "Check the error above. If the image has not been pushed yet, run this workflow manually for ${SOURCE_BRANCH} once it is available."
  exit 1
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
       -f "${dockerfile_dir}"/Dockerfile \
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
       -f "${dockerfile_dir}"/Dockerfile.metplus-analysis \
       "${GITHUB_WORKSPACE}"; then
    exit 1
fi
