#! /bin/bash

if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  echo This is a pull request, so skip this setp
  exit 0
fi

if [ "${GITHUB_REF: -4}" != "-ref" ]; then
  echo Not a reference branch, so skip this step
  exit 0
fi

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

pwd
ls
ls use_cases*
if [ $? != 0 ]; then
  exit 0
fi

branch_name=`cat artifact/branch_name.txt`

for vol_name in use_cases*; do
    echo vol name is $vol_name
    cp -r $vol_name ci/actions/run_use_cases/docker-action/output_data_volumes/

    image_name=dtcenter/metplus-data-dev:output-${branch_name}-${vol_name}
    echo docker build -t ${image_name} --build-arg vol_name=${vol_name} ci/actions/run_use_cases/docker-action/output_data_volumes
    docker build -t ${image_name} --build-arg vol_name=${vol_name} ci/actions/run_use_cases/docker-action/output_data_volumes
    echo docker push ${image_name}
    docker push ${image_name}

    # remove data after it has been added to data volume
    rm -rf ci/actions/run_use_cases/docker-action/output_data_volumes/$vol_name
done
