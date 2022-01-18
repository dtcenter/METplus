#! /bin/bash

# Called by .github/workflows/testing.yml
# Runs Python script to perform difference testing on use case output
# to compare output to truth data.
# If any differences were reported, set GHA output var upload_diff
# to true, copy difference files to artifact directory, and return
# non-zero status. If no differences were found, set GHA output var
# upload_diff to false

matrix_categories=$1
artifact_name=$2

.github/jobs/setup_and_run_diff.py ${matrix_categories} $artifact_name

if [ "$( ls -A ${RUNNER_WORKSPACE}/diff)" ]; then
  echo ::set-output name=upload_diff::true
  mkdir -p artifact/diff-${artifact_name}
  cp -r ${RUNNER_WORKSPACE}/diff/* artifact/diff-${artifact_name}
  exit 1
fi

echo ::set-output name=upload_diff::false
