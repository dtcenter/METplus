echo Get Docker image: ${DOCKERHUB_TAG}
echo 'doing docker build'
# Note: adding --build-arg <arg-name> without any value tells docker to
#  use value from local environment (export DO_GIT_CLONE)

#${TRAVIS_BUID_DIR}/ci/docker/get_data_volumes.py

docker build -t ${DOCKERHUB_TAG} --build-arg SOURCE_BRANCH=${DOCKERHUB_DEFAULT_TAGNAME} --build-arg MET_BRANCH=${DOCKERHUB_MET_TAGNAME} --build-arg DO_GIT_CLONE ${TRAVIS_BUILD_DIR}/internal_tests/docker

### GitHub 607
### eg change ${TRAVIS_BUILD_DIR}/internal_tests/docker to ${TRAVIS_BUILD_DIR}/ci/docker
### use "git mv" to move files to different directories
### use future_branch (METplus 4)
### mv docker_data directories to under ci/docker_data

echo 'done'
