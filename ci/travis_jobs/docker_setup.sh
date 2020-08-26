# set umask to 002 so that the travis user has (group) permission
# to move files that are created by docker
umask 002

# set DO_GIT_CLONE env var to false to tell docker not to
# clone repository because travis is handling that step
export DO_GIT_CLONE=false

#echo "creating i/o directories"
#mkdir -p ${OWNER_BUILD_DIR}/test-use-case-output
#mkdir -p ${OWNER_BUILD_DIR}/test.metplus.data

echo Get Docker image: ${DOCKERHUB_TAG}

# Note: adding --build-arg <arg-name> without any value tells docker to
#  use value from local environment (export DO_GIT_CLONE)
docker build -t ${DOCKERHUB_TAG} --build-arg SOURCE_BRANCH=${DOCKERHUB_DEFAULT_TAGNAME} --build-arg MET_BRANCH=${DOCKERHUB_MET_TAGNAME} --build-arg DO_GIT_CLONE ${TRAVIS_BUILD_DIR}/internal_tests/docker
docker images
docker run --rm -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash -c 'which master_metplus.py;ls -al /metplus;python3 -V'

