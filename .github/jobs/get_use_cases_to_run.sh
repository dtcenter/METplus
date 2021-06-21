#! /bin/bash

# set matrix to string of an empty array in case no use cases will be run
matrix="[]"

# if running use cases, generate JQ filter to use
if [ "$run_use_cases" == "true" ]; then
  # start of jq filter to get all items from JSON file
  jq_filter=".[]"

  # if only running new use cases, add to filter criteria
  if [ "$run_all_use_cases" == "false" ]; then
    jq_filter=${jq_filter}" | select(has(\"new\"))"
  fi

  # add filter to pull out category values from object list
  jq_filter${jq_filter}" | .category"

  # add square brackets around filter to create array
  jq_filter="["${jq_filter}"]"

  # perform JQ query to get list of use case groups to run
  matrix=$(jq '[.[] | select(has("new")) | .category]' .github/jobs/use_case_groups_objects.json)
fi

# if unit tests will be run, add "pytests" to beginning of matrix list
if [ "$run_unit_tests" == "true" ]; then
  # if matrix is empty, set to a list that only includes pytests
  if [ "$matrix" == "[]" ]; then
    matrix="[\"pytests\"]"
  # otherwise prepend item to list
  else
    matrix="[\"pytests\", ${matrix:1}"
  fi
fi

# if matrix is still empty, exit 1 to fail step and skip rest of workflow
if [ "$matrix" == "[]" ]; then
  echo No tests to run!
  exit 1
fi

echo ::set-output name=matrix::{\"categories\":$(echo $matrix)}\"
echo $matrix
