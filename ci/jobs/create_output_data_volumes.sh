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

docker_data_output_dir=ci/docker/docker_data_output

for vol_name in use_cases*; do
    echo vol name is $vol_name
    cp -r $vol_name ${docker_data_output_dir}/

    image_name=dtcenter/metplus-data-dev:output-${branch_name}-${vol_name}
    echo docker build -t ${image_name} --build-arg vol_name=${vol_name} ${docker_data_output_dir}
    docker build -t ${image_name} --build-arg vol_name=${vol_name} ${docker_data_output_dir}
    echo docker push ${image_name}
    docker push ${image_name}

    # remove data after it has been added to data volume
    rm -rf ${docker_data_output_dir}/$vol_name
done
