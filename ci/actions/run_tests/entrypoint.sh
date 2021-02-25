#! /bin/sh

# The repo source code is cloned to $RUNNER_WORKSPACE/$REPO_NAME
# Setup the workspace path to that for easier access later
REPO_NAME=$(basename $RUNNER_WORKSPACE)
WS_PATH=$RUNNER_WORKSPACE/$REPO_NAME

DOCKER_DATA_DIR=/data
DOCKER_OUTPUT_DIR=${DOCKER_DATA_DIR}/output
GHA_OUTPUT_DIR=$RUNNER_WORKSPACE/output

branch_name=`${GITHUB_WORKSPACE}/ci/jobs/print_branch_name.py`
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  branch_name=${branch_name}-PR
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

CATEGORIES=`echo $INPUT_CATEGORIES | awk -F: '{print $1}'`
SUBSETLIST=`echo $INPUT_CATEGORIES | awk -F: '{print $2}'`
if [ -z "${SUBSETLIST}" ]; then
    SUBSETLIST="all"
fi

# install Pillow library needed for diff testing
# this will be replaced with better image diffing package used by METplotpy
pip_command="pip3 install Pillow"

# build command to run
command="./ci/jobs/run_use_cases_docker.py ${CATEGORIES} ${SUBSETLIST}"

# add input volumes to run command
echo "Get Docker data volumes for input data"
${GITHUB_WORKSPACE}/ci/jobs/get_data_volumes.py $CATEGORIES

# keep track of --volumes-from arguments to docker run command
VOLUMES_FROM=""

# split list of categories by comma
category_list=`echo $CATEGORIES | tr "," "\n"`

# add input category --volumes-from arguments for docker run command
for category in ${category_list}; do
  VOLUMES_FROM=${VOLUMES_FROM}`echo --volumes-from $category" "`
done

# get Docker data volumes for output data if running a pull request into
# develop or main_v* branches
if [ "$GITHUB_EVENT_NAME" == "pull_request" ] && ([ "${GITHUB_BASE_REF:0:7}" == "develop" ] || [ "${GITHUB_BASE_REF:0:6}" == "main_v" ]); then
  echo "Get Docker data volumes for output data"

  # get branch of pull request destination
  pr_destination=${GITHUB_BASE_REF}

  # strip off -ref if found
  if [ "${pr_destination: -4}" == "-ref" ]; then
    pr_destination=${pr_destination:0: -4}
  fi

  category=`${GITHUB_WORKSPACE}/ci/jobs/get_artifact_name.sh $INPUT_CATEGORIES`
  output_category=output-${pr_destination}-${category}

  ${GITHUB_WORKSPACE}/ci/jobs/get_data_volumes.py $output_category
  new_volume=output-${category#use_cases_}
  VOLUMES_FROM=${VOLUMES_FROM}`echo --volumes-from $new_volume" "`

  # add 3rd argument to command to trigger difference testing
  command=${command}" true"
fi

echo VOLUMES_FROM: $VOLUMES_FROM

echo "Run Docker container: $DOCKERHUBTAG"
echo docker run -e GITHUB_WORKSPACE -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "${pip_command};${command}"
docker run -e GITHUB_WORKSPACE -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "${pip_command};${command}"
