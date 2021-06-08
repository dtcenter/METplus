#! /bin/bash

# The repo source code is cloned to $RUNNER_WORKSPACE/$REPO_NAME
# Setup the workspace path to that for easier access later
REPO_NAME=$(basename $RUNNER_WORKSPACE)
WS_PATH=$RUNNER_WORKSPACE/$REPO_NAME
echo WS_PATH is $WS_PATH
echo GITHUB_WORKSPACE is $GITHUB_WORKSPACE
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

# if running pytests not use cases
if [ "$INPUT_CATEGORIES" == "pytests" ]; then
  export  METPLUS_ENV_TAG="pytest"
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
  command="export METPLUS_PYTEST_HOST=docker; cd internal_tests/pytests; /usr/local/envs/pytest/bin/pytest --cov=../../metplus"
  docker run -v $WS_PATH:$GITHUB_WORKSPACE --workdir $GITHUB_WORKSPACE $RUN_TAG bash -c "$command"
  exit $?
fi

#
# running use case tests
#

# set up paths for mounting directories in Docker to
# make output available in GitHub Actions
# NOTE: we could adjust directories so we only need to mount the
# data directory instead of all subdirs
DOCKER_DATA_DIR=/data
DOCKER_OUTPUT_DIR=${DOCKER_DATA_DIR}/output
GHA_OUTPUT_DIR=$RUNNER_WORKSPACE/output

DOCKER_DIFF_DIR=${DOCKER_DATA_DIR}/diff
GHA_DIFF_DIR=$RUNNER_WORKSPACE/diff

DOCKER_ERROR_LOG_DIR=${DOCKER_DATA_DIR}/error_logs
GHA_ERROR_LOG_DIR=$RUNNER_WORKSPACE/error_logs


# get use case category and subset list
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
  ${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/python_requirements/get_metviewer.sh
  NETWORK_ARG=--network="container:mysql_mv"
fi

# call script to loop over use case groups to
# get data volumes, set up run image, and run use cases
./${CI_JOBS_DIR}/setup_and_run_use_cases.py ${CATEGORIES} ${SUBSETLIST}
exit $?

# determine which tag to use for dtcenter/metplus-environments
METPLUS_ENV_TAG="metplus_base"
if [[ ! -z "${all_requirements// }" ]]; then
    if [[ "$all_requirements" =~ .*"metplotpy".* ]]; then
	METPLUS_ENV_TAG=metplotpy
    else
	METPLUS_ENV_TAG=xesmf
    fi
fi

export METPLUS_ENV_TAG
export METPLUS_IMG_TAG=${branch_name}

echo METPLUS_ENV_TAG=${METPLUS_ENV_TAG}
echo METPLUS_IMG_TAG=${METPLUS_IMG_TAG}

export RUN_TAG=metplus-run-env

# use BuildKit to build image
export DOCKER_BUILDKIT=1

docker build -t $RUN_TAG --build-arg METPLUS_IMG_TAG --build-arg METPLUS_ENV_TAG -f ./ci/actions/run_tests/Dockerfile.run .

# install Pillow library needed for diff testing
# this will be replaced with better image diffing package used by METplotpy
pip_command="pip3 install Pillow; yum -y install poppler-utils; pip3 install pdf2image"

# build command to run
command="./${CI_JOBS_DIR}/run_use_cases.py ${CATEGORIES} ${SUBSETLIST}"

# add input volumes to run command
# keep track of --volumes-from arguments to docker run command
echo "Get Docker data volumes for input data"
VOLUMES_FROM=`${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/get_data_volumes.py $CATEGORIES`

echo Input: ${VOLUMES_FROM}
# get Docker data volumes for output data and run diffing logic
# if running a pull request into develop or main_v* branches, not -ref branches
if [ "${INPUT_RUN_DIFF}" == "true" ]; then
  echo "Get Docker data volumes for output data"

  # use develop branch output data volumes if not a pull request (forced diff)
  if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
    output_data_branch=${GITHUB_BASE_REF}
  else
    output_data_branch=develop
  fi

  category=`${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/get_artifact_name.sh $INPUT_CATEGORIES`
  output_category=output-${output_data_branch}-${category}

  echo Get output data volume: ${output_category}
  OUT_VOLUMES_FROM=`${GITHUB_WORKSPACE}/${CI_JOBS_DIR}/get_data_volumes.py $output_category`

  echo Output: ${OUT_VOLUMES_FROM}
  VOLUMES_FROM=${VOLUMES_FROM}" "$OUT_VOLUMES_FROM

  # add 3rd argument to command to trigger difference testing
  command=${command}" true"
fi

echo VOLUMES_FROM: $VOLUMES_FROM

echo docker ps:
docker ps -a

echo "Run Docker container: $RUN_TAG"
#echo docker run -e GITHUB_WORKSPACE $NETWORK_ARG -v $RUNNER_WORKSPACE/output/mysql:/var/lib/mysql -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $GHA_DIFF_DIR:$DOCKER_DIFF_DIR -v $GHA_ERROR_LOG_DIR:$DOCKER_ERROR_LOG_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "${pip_command};${command}"
#docker run -e GITHUB_WORKSPACE $NETWORK_ARG -v $RUNNER_WORKSPACE/output/mysql:/var/lib/mysql -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $GHA_DIFF_DIR:$DOCKER_DIFF_DIR -v $GHA_ERROR_LOG_DIR:$DOCKER_ERROR_LOG_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "${pip_command};${command}"
echo docker run -e GITHUB_WORKSPACE $NETWORK_ARG -v $RUNNER_WORKSPACE/output/mysql:/var/lib/mysql -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $GHA_DIFF_DIR:$DOCKER_DIFF_DIR -v $GHA_ERROR_LOG_DIR:$DOCKER_ERROR_LOG_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $RUN_TAG bash -c "${pip_command};${command}"
docker run -e GITHUB_WORKSPACE $NETWORK_ARG -v $RUNNER_WORKSPACE/output/mysql:/var/lib/mysql -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $GHA_DIFF_DIR:$DOCKER_DIFF_DIR -v $GHA_ERROR_LOG_DIR:$DOCKER_ERROR_LOG_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $RUN_TAG bash -c "${pip_command};${command}"
