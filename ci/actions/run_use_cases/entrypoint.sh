#! /bin/sh

DOCKERUB_TAG=$1

# The repo source code is cloned to $RUNNER_WORKSPACE/$REPO_NAME
# Setup the workspace path to that for easier access later
REPO_NAME=$(basename $RUNNER_WORKSPACE)
WS_PATH=$RUNNER_WORKSPACE/$REPO_NAME

cd /docker-action

echo "Creating a docker image with Dockerhub Tag: $DOCKERHUB_TAG"
docker build -t docker-action --build-arg dockerhub_tag="$DOCKERHUB_TAG" .

echo "Run Docker Action container"
docker run -e DOCKERHUB_TAG2 -v $WS_PATH:$GITHUB_WORKSPACE  --workdir $GITHUB_WORKSPACE docker-action
