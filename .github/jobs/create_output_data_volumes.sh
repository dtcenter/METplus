#! /bin/bash

# Run by GitHub Actions (in .github/workflows/testing.yml) to create
# Docker data volumes from output data to create a "truth"
# data set to use in difference tests.

if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  echo This is a pull request, so skip this setp
  exit 0
fi

branch_name=`${GITHUB_WORKSPACE}/.github/jobs/print_branch_name.py`

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
  echo ERROR: No artifacts that start with use_cases_ were found
  exit 1
fi

docker_data_output_dir=scripts/docker/docker_data_output

success=1
for vol_name in use_cases_*; do
    echo vol name is $vol_name
    cp -r $vol_name ${docker_data_output_dir}/

    image_name=dtcenter/metplus-data-dev:output-${branch_name}-${vol_name#use_cases_}
    echo Creating Docker data volume: ${image_name}

    start_time=$SECONDS
    echo docker build -t ${image_name} --build-arg vol_name=${vol_name} ${docker_data_output_dir}
    docker build -t ${image_name} --build-arg vol_name=${vol_name} ${docker_data_output_dir}
    if [ $? != 0 ]; then
      echo ERROR: Could not build ${image_name}
      success=0
    fi
    echo Build took $(( SECONDS - start_time))

    start_time=$SECONDS
    echo docker push ${image_name}
    docker push ${image_name}
    if [ $? != 0 ]; then
      echo ERROR: Could not push ${image_name}
      success=0
    fi
    echo Push took $(( SECONDS - start_time))

    # remove data after it has been added to data volume
    rm -rf ${docker_data_output_dir}/$vol_name
done

if [ $success != 1 ]; then
  echo ERROR: Some data volumes failed to update
  exit 1
fi
