#!/bin/bash

# assumes SOURCE_BRANCH is set before calling script

source "${GITHUB_WORKSPACE}"/.github/jobs/bash_functions.sh

# get names of images to push

dockerhub_repo=dtcenter/metplus
dockerhub_repo_analysis=dtcenter/metplus-analysis

# remove v prefix
metplus_version=${SOURCE_BRANCH:1}

METPLUS_IMAGE_NAME=${dockerhub_repo}:${metplus_version}
METPLUS_A_IMAGE_NAME=${dockerhub_repo_analysis}:${metplus_version}

# Scan the images
cve_scan_image ${METPLUS_IMAGE_NAME}
cve_scan_image ${METPLUS_A_IMAGE_NAME}

