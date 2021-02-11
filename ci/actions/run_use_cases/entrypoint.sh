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

echo "Get Docker data volumes for input data"
${GITHUB_WORKSPACE}/ci/jobs/get_data_volumes.py $INPUT_CATEGORIES

# build --volumes-from arguments for docker run command
category_list=`echo $INPUT_CATEGORIES | tr "," "\n"`
VOLUMES_FROM=""
for n in ${category_list}; do
  VOLUMES_FROM=${VOLUMES_FROM}`echo --volumes-from $n" "`
done
echo VOLUMES_FROM: $VOLUMES_FROM

echo "Run Docker Action container: $INPUT_DOCKERHUBTAG"
docker run -e GITHUB_WORKSPACE -e INPUT_CATEGORIES -e INPUT_SUBSETLIST -v $GHA_OUTPUT_DIR:$DOCKER_OUTPUT_DIR -v $WS_PATH:$GITHUB_WORKSPACE ${VOLUMES_FROM} --workdir $GITHUB_WORKSPACE docker-action
