#! /bin/sh

# The repo source code is cloned to $RUNNER_WORKSPACE/$REPO_NAME
# Setup the workspace path to that for easier access later
REPO_NAME=$(basename $RUNNER_WORKSPACE)
WS_PATH=$RUNNER_WORKSPACE/$REPO_NAME

cd /docker-action

echo "Creating a docker image with Dockerhub Tag: $INPUT_DOCKERHUBTAG"
docker build -t docker-action --build-arg dockerhub_tag="$INPUT_DOCKERHUBTAG" .

echo "Run Docker Action container"
docker run -e DOCKERHUB_TAG2 -e DOCKERHUB_TAG -e INPUT_DOCKERHUBTAG -v $WS_PATH:$GITHUB_WORKSPACE  --workdir $GITHUB_WORKSPACE docker-action
