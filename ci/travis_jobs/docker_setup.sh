echo Get Docker image: ${DOCKERHUB_TAG}
echo 'doing docker build'
# Note: adding --build-arg <arg-name> without any value tells docker to
#  use value from local environment (export DO_GIT_CLONE)

${TRAVIS_BUILD_DIR}/ci/travis_jobs/get_data_volumes.py


echo Timing docker pull...
start_seconds=$SECONDS

docker pull ${DOCKERHUB_TAG} || true

duration=$(( SECONDS - start_seconds ))
echo "Docker pull took $(($duration / 60)) minutes and $(($duration % 60)) seconds."


echo Timing docker build with --cache-from...
start_seconds=$SECONDS

docker build --pull --cache-from ${DOCKERHUB_TAG} -t ${DOCKERHUB_TAG} --build-arg SOURCE_BRANCH=${DOCKERHUB_DEFAULT_TAGNAME} --build-arg MET_BRANCH=${DOCKERHUB_MET_TAGNAME} --build-arg DO_GIT_CLONE ${TRAVIS_BUILD_DIR}/ci/docker

duration=$(( SECONDS - start_seconds ))
echo "Docker build took $(($duration / 60)) minutes and $(($duration % 60)) seconds."
echo

#${TRAVIS_BUILD_DIR}/ci/docker/docker_data/${TRAVIS_BUILD_DIR}/ci/docker/docker_data/build_docker_images.sh -pull ${DOCKERHUB_TAG} -push ${DOCKERHUB_TAB}

docker login
docker push ${DOCKERHUB_TAG}

echo DOCKER IMAGES after DOCKER_SETUP
docker images
echo

echo 'done'
