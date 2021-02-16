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

# add input volumes to run command
echo "Get Docker data volumes for input data"
${GITHUB_WORKSPACE}/ci/jobs/get_data_volumes.py $INPUT_CATEGORIES

# keep track of --volumes-from arguments to docker run command
VOLUMES_FROM=""

# split list of categories by comma
category_list=`echo $INPUT_CATEGORIES | tr "," "\n"`

# add input category --volumes-from arguments for docker run command
for category in ${category_list}; do
  VOLUMES_FROM=${VOLUMES_FROM}`echo --volumes-from $category" "`
done

# get Docker data volumes for output data if running a pull request
#if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
#  echo "Get Docker data volumes for output data"
#  output_categories=""
#  for category in ${category_list}; do
#    output_category=output-${category}
#    output_categories=${output_categories} ${output_category}
#    VOLUMES_FROM=${VOLUMES_FROM}`echo --volumes-from $output_category" "`
#  done
#
#  ${GITHUB_WORKSPACE}/ci/jobs/get_data_volumes.py $output_categories
#fi

echo VOLUMES_FROM: $VOLUMES_FROM

echo "Run Docker Action container: $DOCKERHUBTAG"
command="./ci/jobs/run_use_cases_docker.py ${INPUT_CATEGORIES} ${INPUT_SUBSETLIST}"
echo docker run -e GITHUB_WORKSPACE -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "$command"
docker run -e GITHUB_WORKSPACE -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE $DOCKERHUBTAG bash -c "$command"
ret=$?
