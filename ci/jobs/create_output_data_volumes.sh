#! /bin/bash

if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  echo This is a pull request, so skip this setp
  exit 0
fi

branch_name=`${GITHUB_WORKSPACE}/ci/jobs/print_branch_name.py`

if [ "${branch_name: -4}" != "-ref" ]; then
  echo Branch ${branch_name} is not a reference branch, so skip this step
  exit 0
fi

# remove -ref from branch name
branch_name=${branch_name:0: -4}

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

# if no artifacts that start with use_cases_ are found, exit
ls use_cases_*
if [ $? != 0 ]; then
  exit 0
fi

docker_data_output_dir=ci/docker/docker_data_output

for vol_name in use_cases_*; do
    echo vol name is $vol_name
    cp -r $vol_name ${docker_data_output_dir}/

    image_name=dtcenter/metplus-data-dev:output-${branch_name}-${vol_name#use_cases_}
    echo Creating Docker data volume: ${image_name}
    echo docker build -t ${image_name} --build-arg vol_name=${vol_name} ${docker_data_output_dir}
    docker build -t ${image_name} --build-arg vol_name=${vol_name} ${docker_data_output_dir}
    echo docker push ${image_name}
    docker push ${image_name}

    # remove data after it has been added to data volume
    rm -rf ${docker_data_output_dir}/$vol_name
done
