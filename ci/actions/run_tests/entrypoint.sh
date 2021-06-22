#! /bin/bash

# The repo source code is cloned to $RUNNER_WORKSPACE/$REPO_NAME
# Setup the workspace path to that for easier access later
REPO_NAME=$(basename $RUNNER_WORKSPACE)
WS_PATH=$RUNNER_WORKSPACE/$REPO_NAME

# set CI jobs directory variable to easily move it
CI_JOBS_DIR=ci/jobs

# get branch name for push or pull request events
# add -pull_request if pull request event to keep separated
branch_name=`${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/print_branch_name.py`
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  branch_name=${branch_name}-pull_request
fi

# try to pull image from DockerHub
DOCKERHUBTAG=dtcenter/metplus-dev:${branch_name}
echo "Pulling docker image: $DOCKERHUBTAG"
docker pull $DOCKERHUBTAG

# if unsuccessful (i.e. pull request from a fork)
# then build image locally
docker inspect --type=image $DOCKERHUBTAG > /dev/null
if [ $? != 0 ]; then
   # if docker pull fails, build locally
   echo docker pull failed. Building Docker image locally...
   ${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/docker_setup.sh
fi

#
# running unit tests (pytests)
#
if [ "$INPUT_CATEGORIES" == "pytests" ]; then
  export METPLUS_ENV_TAG="pytest"
  export METPLUS_IMG_TAG=${branch_name}
  echo METPLUS_ENV_TAG=${METPLUS_ENV_TAG}
  echo METPLUS_IMG_TAG=${METPLUS_IMG_TAG}

  export RUN_TAG=metplus-run-env

  # use BuildKit to build image
  export DOCKER_BUILDKIT=1

  # build an image with the pytest conda env and the METplus branch image
  docker build -t $RUN_TAG \
	 --build-arg METPLUS_IMG_TAG \
	 --build-arg METPLUS_ENV_TAG \
	 -f ./ci/actions/run_tests/Dockerfile.run \
	 .

  echo Running Pytests
  command="mkdir /data/output; export METPLUS_PYTEST_HOST=docker; cd internal_tests/pytests; /usr/local/envs/pytest/bin/pytest -vv --cov=../../metplus"
  docker run -v $WS_PATH:$GITHUB_WORKSPACE --workdir $GITHUB_WORKSPACE $RUN_TAG bash -c "$command"
  exit $?
fi

#
# running use case tests
#

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
