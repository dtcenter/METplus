# set DO_GIT_CLONE env var to false to tell docker not to
# clone repository because travis is handling that step
export DO_GIT_CLONE=false

echo Get Docker image: ${DOCKERHUB_TAG}
echo 'doing docker build'
# Note: adding --build-arg <arg-name> without any value tells docker to
#  use value from local environment (export DO_GIT_CLONE)

docker build -t ${DOCKERHUB_TAG} --build-arg SOURCE_BRANCH=${DOCKERHUB_DEFAULT_TAGNAME} --build-arg MET_BRANCH=${DOCKERHUB_MET_TAGNAME} --build-arg DO_GIT_CLONE ${TRAVIS_BUILD_DIR}/internal_tests/docker

export 'done'
export ' '
export VOLUMES=" "

echo 'pulling 3.1-met_tool_wrapper'
docker pull dtcenter/metplus-data:3.1-met_tool_wrapper
docker create --name met_tool_wrapper dtcenter/metplus-data:3.1-met_tool_wrapper
export VOLUMES="--volumes-from met_tool_wrapper"

echo 'pulling 3.1-s2s'
docker pull dtcenter/metplus-data:3.1-s2s
docker create --name s2s dtcenter/metplus-data:3.1-s2s
export VOLUMES="$VOLUMES --volumes-from s2s"

echo 'pulling space_weather'
docker pull dtcenter/metplus-data:3.1-space_weather
docker create --name space_weather dtcenter/metplus-data:3.1-space_weather
export VOLUMES="$VOLUMES --volumes-from space_weather"

echo 'pulling climate'
docker pull dtcenter/metplus-data:3.1-climate
docker create --name climate dtcenter/metplus-data:3.1-climate
export VOLUMES="$VOLUMES --volumes-from climate"

echo 'pulling tc_and_extra_tc'
docker pull dtcenter/metplus-data:3.1-tc_and_extra_tc
docker create --name tc_and_extra_tc dtcenter/metplus-data:3.1-tc_and_extra_tc
export VOLUMES="$VOLUMES --volumes-from tc_and_extra_tc"

echo 'pulling cryosphere'
docker pull dtcenter/metplus-data:3.1-cryosphere
docker create --name cryosphere dtcenter/metplus-data:3.1-cryosphere
export VOLUMES="$VOLUMES --volumes-from cryosphere"

echo 'pulling convection_allowing_models'
docker pull dtcenter/metplus-data:3.1-convection_allowing_models
docker create --name convection_allowing_models dtcenter/metplus-data:3.1-convection_allowing_models
export VOLUMES="$VOLUMES --volumes-from convection_allowing_models"

echo 'pulling precipitation'
docker pull dtcenter/metplus-data:3.1-precipitation
docker create --name precipitation dtcenter/metplus-data:3.1-precipitation
export VOLUMES="$VOLUMES --volumes-from precipitation"

echo 'pulling medium_range'
docker pull dtcenter/metplus-data:3.1-medium_range
docker create --name medium_range dtcenter/metplus-data:3.1-medium_range
export VOLUMES="$VOLUMES --volumes-from medium_range"

echo 'done'

echo 'Owner Builddir ',${OWNER_BUILD_DIR}
echo 'Docker Workdir ',${DOCKER_WORK_DIR}
echo 'Docker Inputdir ',${DOCKER_DATA_INPUT}
echo 'Docker Outputdir ',${DOCKER_DATA_OUTPUT}

echo 'doing docker run, mapping containers'
docker run --rm $VOLUMES  -v ${OWNER_BUILD_DIR}:${DOCKER_WORK_DIR} -v ${OWNER_BUILD_DIR}/input:${DOCKER_DATA_INPUT} -v ${OWNER_BUILD_DIR}/output:/output ${DOCKERHUB_TAG} "ls -al ${DOCKER_DATA_INPUT}"

echo 'checking TRAVIS input directory:'
ls -al ${OWNER_BUILD_DIR}/input

docker images

