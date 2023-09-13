DOCKER_ENV_DIR=${GITHUB_WORKSPACE}/internal/scripts/docker_env
cmd="docker build \
  -t dtcenter/metplus-envs:${ENV_NAME}.${METPLUS_ENV_VERSION} \
  --build-arg METPLUS_ENV_VERSION \
  --build-arg BASE_ENV \
  --build-arg ENV_NAME \
  -f ${DOCKER_ENV_DIR}/${DOCKERFILE} ${DOCKER_ENV_DIR}"
echo $cmd
$cmd
