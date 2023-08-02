#! /bin/bash

# The repo source code is cloned to $RUNNER_WORKSPACE/$REPO_NAME
# Setup the workspace path to that for easier access later
REPO_NAME=$(basename $RUNNER_WORKSPACE)
WS_PATH=$RUNNER_WORKSPACE/$REPO_NAME

# set CI jobs directory variable to easily move it
CI_JOBS_DIR=.github/jobs

source ${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/bash_functions.sh

# get branch name for push or pull request events
# add -pull_request if pull request event to keep separated
branch_name=`${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/print_branch_name.py`
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  branch_name=${branch_name}-pull_request
fi

# try to pull image from DockerHub
DOCKERHUBTAG=dtcenter/metplus-dev:${branch_name}
time_command docker pull $DOCKERHUBTAG

# if unsuccessful (i.e. pull request from a fork)
# then build image locally
docker inspect --type=image $DOCKERHUBTAG > /dev/null
if [ $? != 0 ]; then
   # if docker pull fails, build locally
   echo docker pull failed. Building Docker image locally...
   ${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/docker_setup.sh
fi

# running use case tests

# split apart use case category and subset list from input
CATEGORIES=`echo $INPUT_CATEGORIES | awk -F: '{print $1}'`
SUBSETLIST=`echo $INPUT_CATEGORIES | awk -F: '{print $2}'`

# run all cases if no subset list specified
if [ -z "${SUBSETLIST}" ]; then
    SUBSETLIST="all"
fi

# get METviewer if used in any use cases
all_requirements=`./${CI_JOBS_DIR}/get_requirements.py ${CATEGORIES} ${SUBSETLIST}`
echo All requirements: $all_requirements
NETWORK_ARG=""
if [[ "$all_requirements" =~ .*"metviewer".* ]]; then
  echo "Setting up METviewer"
  ${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/get_metviewer.sh
  NETWORK_ARG=--network="container:mysql_mv"
fi

# export network arg so it can be read by setup_and_run_use_cases.py
export NETWORK_ARG

# call script to loop over use case groups to
# get data volumes, set up run image, and run use cases
./${CI_JOBS_DIR}/setup_and_run_use_cases.py ${CATEGORIES} ${SUBSETLIST}
