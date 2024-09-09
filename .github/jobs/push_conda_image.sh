echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin
cmd="docker push dtcenter/metplus-envs:${ENV_NAME}.${METPLUS_ENV_VERSION}"
echo $cmd
$cmd
