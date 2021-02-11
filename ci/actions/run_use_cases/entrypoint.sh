#! /bin/sh

# The repo source code is cloned to $RUNNER_WORKSPACE/$REPO_NAME
# Setup the workspace path to that for easier access later
REPO_NAME=$(basename $RUNNER_WORKSPACE)
WS_PATH=$RUNNER_WORKSPACE/$REPO_NAME

DOCKER_DATA_DIR=/data
DOCKER_OUTPUT_DIR=${DOCKER_DATA_DIR}/output
GHA_OUTPUT_DIR=$RUNNER_WORKSPACE/output

cd /docker-action

echo "Creating a docker image with Dockerhub Tag: $INPUT_DOCKERHUBTAG"
docker build -t docker-action --build-arg dockerhub_tag="$INPUT_DOCKERHUBTAG" .

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

echo "Run Docker Action container: $INPUT_DOCKERHUBTAG"
docker run -e GITHUB_WORKSPACE -e INPUT_CATEGORIES -e INPUT_SUBSETLIST -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE docker-action
ret=$?

# if branch ends with -ref and not a pull request, create/update Docker
# data volume for output data
if [ "$GITHUB_EVENT_NAME" == "pull_request" ] || [ "${BRANCH_NAME: -4}" != "-ref" ]; then
  echo $BRANCH_NAME is not a reference branch.
  exit $ret
fi

echo Updating Docker data volume for output data from reference branch: ${BRANCH_NAME}
image_name=dtcenter/metplus-data-dev:output-${GITHUB_ACTION}
docker build -t ${image_name} --build-arg output_dir=${GHA_OUTPUT_DIR} output_data_volumes

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker push ${image_name}
