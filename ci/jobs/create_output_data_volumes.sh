#! /bin/bash

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

pwd
ls
ls use_cases*
if [ $? != 0 ]; then
  exit 0
fi

branch_name=$((cat artifact/branch_name.txt))

for vol_name in use_cases*; do
    echo vol name is $vol_name
    cp -r $vol_name ci/actions/run_use_cases/docker-action/output_data_volumes/

    image_name=dtcenter/metplus-data-dev:output-${branch_name}-${vol_name}
    echo docker build -t ${image_name} --build-arg vol_name=${vol_name} ci/actions/run_use_cases/docker-action/output_data_volumes
    docker build -t ${image_name} --build-arg vol_name=${vol_name} ci/actions/run_use_cases/docker-action/output_data_volumes
    echo docker push ${image_name}
    docker push ${image_name}
done
