# set clone from travis env var to tell docker not to clone repository
# because travis is handling that step
export CLONE_FROM_TRAVIS=true

echo Get Docker image: ${DOCKERHUB_TAG}
docker build -t ${DOCKERHUB_TAG} --build-arg CLONE_FROM_TRAVIS internal_tests/docker
docker images
docker run --rm -e "PATH=/metplus/METplus/ush:$PATH" -v ${OWNER_BUILD_DIR}:/metplus ${DOCKERHUB_TAG} /bin/bash -c 'echo $MY_CUSTOM_VAR;which master_metplus.py;ls -al /metplus;python3 -V'

