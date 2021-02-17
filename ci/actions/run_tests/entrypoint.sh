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

if [ "$INPUT_CATEGORIES" == "pytests" ]; then
  echo Running Pytests
  command="pip3 install pytest-cov netCDF4; export METPLUS_PYTEST_HOST=docker; cd internal_tests/pytests; pytest --cov=../../metplus"
  docker run -v $WS_PATH:$GITHUB_WORKSPACE --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "$command"
  exit $?
fi

CATEGORIES=`echo $INPUT_CATEGORIES | awk -F: '{print $1}'`
SUBSETLIST=`echo $INPUT_CATEGORIES | awk -F: '{print $2}'`

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

# get Docker data volumes for output data if running a pull request 
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  # echo "Get Docker data volumes for output data"
  pr_destination=${GITHUB_BASE_REF}
  category=`${GITHUB_WORKSPACE}/ci/jobs/get_artifact_name.sh $INPUT_CATEGORIES`
  output_category=output-${pr_destination}-${category}

  ${GITHUB_WORKSPACE}/ci/jobs/get_data_volumes.py $output_category
  VOLUMES_FROM=${VOLUMES_FROM}`echo --volumes-from $output_category" "`
fi
echo VOLUMES_FROM: $VOLUMES_FROM

echo "Run Docker container: $DOCKERHUBTAG"

# install netCDF4 library needed for diff testing
pip_command="pip3 install netCDF4"

# build command to run
command="./ci/jobs/run_use_cases_docker.py ${CATEGORIES} ${SUBSETLIST}"

# add 3rd argument to trigger comparison if pull request
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  command=$command True
fi

echo docker run -e GITHUB_WORKSPACE -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "${pip_command};${command}"
docker run -e GITHUB_WORKSPACE -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "${pip_command};${command}"
ret=$?
