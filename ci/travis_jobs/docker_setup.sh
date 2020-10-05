echo Get Docker image: ${DOCKERHUB_TAG}
echo 'doing docker build'
# Note: adding --build-arg <arg-name> without any value tells docker to
#  use value from local environment (export DO_GIT_CLONE)

echo Timing docker pull...
start_seconds=$SECONDS

docker pull ${DOCKERHUB_TAG} || true

duration=$(( SECONDS - start_seconds ))
echo "Docker pull took $(($duration / 60)) minutes and $(($duration % 60)) seconds."

echo CURRENT_BRANCH = ${CURRENT_BRANCH}


echo Timing docker build with --cache-from...
start_seconds=$SECONDS

docker build --pull --cache-from ${DOCKERHUB_TAG} -t ${DOCKERHUB_TAG} --build-arg SOURCE_BRANCH=${DOCKERHUB_DEFAULT_TAGNAME} --build-arg MET_BRANCH=${DOCKERHUB_MET_TAGNAME} --build-arg DO_GIT_CLONE ${TRAVIS_BUILD_DIR}/ci/docker

duration=$(( SECONDS - start_seconds ))
echo "Docker build took $(($duration / 60)) minutes and $(($duration % 60)) seconds."
echo

echo Timing docker push...
start_seconds=$SECONDS

echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
docker push ${DOCKERHUB_TAG}

duration=$(( SECONDS - start_seconds ))
echo "Docker push took $(($duration / 60)) minutes and $(($duration % 60)) seconds."
echo

echo DOCKER IMAGES after DOCKER_SETUP
docker images
echo

echo 'done'
