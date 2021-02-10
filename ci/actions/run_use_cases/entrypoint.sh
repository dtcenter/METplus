#! /bin/bash

# The repo source code is cloned to $RUNNER_WORKSPACE/$REPO_NAME
# Setup the workspace path to that for easier access later
REPO_NAME=$(basename $RUNNER_WORKSPACE)
WS_PATH=$RUNNER_WORKSPACE/$REPO_NAME

cd /docker-action

echo "Creating a docker image with Dockerhub Tag: $INPUT_DOCKERHUBTAG"
docker build -t docker-action --build-arg dockerhub_tag="$INPUT_DOCKERHUBTAG" .

echo "Get Docker data volumes for input data"
${GITHUB_WORKSPACE}/ci/jobs/get_data_volumes.py $INPUT_CATEGORIES

readarray -d : -t category_list <<< "$INPUT_CATEGORIES"
VOLUMES_FROM=""
for (( n=0; n < ${#category_list[*]}; n++)); do
  VOLUMES_FROM+=`echo --volumes-from "${category_list[n]} "`
done

echo VOLUMES_FROM: $VOLUMES_FROM

echo "Run Docker Action container"
docker run ${VOLUMES_FROM} -e GITHUB_WORKSPACE -e BRANCH_NAME -e INPUT_DOCKERHUBTAG -e INPUT_CATEGORIES -e DOCKER_WORK_DIR -e DOCKER_DATA_DIR -e DOCKER_USERNAME -e DOCKER_PASSWORD -v $WS_PATH:$GITHUB_WORKSPACE  --workdir $GITHUB_WORKSPACE docker-action
