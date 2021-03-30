#! /bin/bash

# The repo source code is cloned to $RUNNER_WORKSPACE/$REPO_NAME
# Setup the workspace path to that for easier access later
REPO_NAME=$(basename $RUNNER_WORKSPACE)
WS_PATH=$RUNNER_WORKSPACE/$REPO_NAME

DOCKER_DATA_DIR=/data
DOCKER_OUTPUT_DIR=${DOCKER_DATA_DIR}/output
GHA_OUTPUT_DIR=$RUNNER_WORKSPACE/output

DOCKER_DIFF_DIR=${DOCKER_DATA_DIR}/diff
GHA_DIFF_DIR=$RUNNER_WORKSPACE/diff

DOCKER_ERROR_LOG_DIR=${DOCKER_DATA_DIR}/error_logs
GHA_ERROR_LOG_DIR=$RUNNER_WORKSPACE/error_logs

# get use case category, subset list, and optional NEW tag from input
CATEGORIES=`echo $INPUT_CATEGORIES | awk -F: '{print $1}'`
SUBSETLIST=`echo $INPUT_CATEGORIES | awk -F: '{print $2}'`

# run all cases if no subset list specified
if [ -z "${SUBSETLIST}" ]; then
    SUBSETLIST="all"
fi

branch_name=`${GITHUB_WORKSPACE}/ci/jobs/print_branch_name.py`
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  branch_name=${branch_name}-pull_request
fi
DOCKERHUBTAG=dtcenter/metplus-dev:${branch_name}

echo "Pulling docker image: $DOCKERHUBTAG"
docker pull $DOCKERHUBTAG
docker inspect --type=image $DOCKERHUBTAG > /dev/null
if [ $? != 0 ]; then
   # if docker pull fails, build locally
   echo docker pull failed. Building Docker image locally...
   ${GITHUB_WORKSPACE}/ci/jobs/docker_setup.sh
fi

if [ "$INPUT_CATEGORIES" == "pytests" ]; then
  echo Running Pytests
  command="pip3 install pytest-cov; export METPLUS_PYTEST_HOST=docker; cd internal_tests/pytests; pytest --cov=../../metplus"
  docker run -v $WS_PATH:$GITHUB_WORKSPACE --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "$command"
  exit $?
fi

# install Pillow library needed for diff testing
# this will be replaced with better image diffing package used by METplotpy
pip_command="pip3 install Pillow; yum install poppler-utils; pip3 install pdf2image"

# build command to run
command="./ci/jobs/run_use_cases.py ${CATEGORIES} ${SUBSETLIST}"

# add input volumes to run command
# keep track of --volumes-from arguments to docker run command
echo "Get Docker data volumes for input data"
VOLUMES_FROM=`${GITHUB_WORKSPACE}/ci/jobs/get_data_volumes.py $CATEGORIES`

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

  category=`${GITHUB_WORKSPACE}/ci/jobs/get_artifact_name.sh $INPUT_CATEGORIES`
  output_category=output-${output_data_branch}-${category}

  echo Get output data volume: ${output_category}
  OUT_VOLUMES_FROM=`${GITHUB_WORKSPACE}/ci/jobs/get_data_volumes.py $output_category`

  echo Output: ${OUT_VOLUMES_FROM}
  VOLUMES_FROM=${VOLUMES_FROM}" "$OUT_VOLUMES_FROM

  # add 3rd argument to command to trigger difference testing
  command=${command}" true"
fi

echo VOLUMES_FROM: $VOLUMES_FROM

echo "Run Docker container: $DOCKERHUBTAG"
echo docker run -e GITHUB_WORKSPACE -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $GHA_DIFF_DIR:$DOCKER_DIFF_DIR -v $GHA_ERROR_LOG_DIR:$DOCKER_ERROR_LOG_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "${pip_command};${command}"
docker run -e GITHUB_WORKSPACE -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $GHA_DIFF_DIR:$DOCKER_DIFF_DIR -v $GHA_ERROR_LOG_DIR:$DOCKER_ERROR_LOG_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "${pip_command};${command}"
