#! /bin/bash

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

for vol_name in artifacts/*; do
    echo $vol_name
    image_name=dtcenter/metplus-data-dev:output-${vol_name}
    echo docker build -t ${image_name} --build-arg vol_name=${vol_name} ci/actions/run_use_cases/docker-action/output_data_volumes
    docker build -t ${image_name} --build-arg vol_name=${vol_name} ci/actions/run_use_cases/docker-action/output_data_volumes
    echo docker push ${image_name}
    docker push ${image_name}
done
