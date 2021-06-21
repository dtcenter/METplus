#! /bin/bash

use_case_groups_filepath=.github/jobs/use_case_groups_objects.json
# set matrix to string of an empty array in case no use cases will be run
matrix="[]"

run_use_cases=$1
run_all_use_cases=$2
run_unit_tests=$3

echo Run use cases: $run_use_cases
echo Run All use cases: $run_all_use_cases
echo Run unit tests: $run_unit_tests

# if running use cases, generate JQ filter to use
if [ "$run_use_cases" == "true" ]; then
  echo generate JQ filter to get use cases to run

  # start of jq filter to get all items from JSON file
#  jq_filter=".[]"

  # if only running new use cases, add to filter criteria
  if [ "$run_all_use_cases" == "false" ]; then
    echo Only run new use cases
    matrix=$(jq '.[] | select(has(\"new\")) | .category' $use_case_groups_filepath)
#    jq_filter=${jq_filter}" | select(has(\"new\"))"
  else
    matrix=$(jq '.[] | .category' $use_case_groups_filepath)
  fi

  # add filter to pull out category values from object list
#  jq_filter=${jq_filter}" | .category"

  # add square brackets around filter to create array
#  jq_filter="["${jq_filter}"]"

#  echo Filter is $jq_filter

  # perform JQ query to get list of use case groups to run
#  matrix=$(jq --arg jq_filter "$jq_filter" '"$jq_filter"' $use_case_groups_filepath)
fi

# if unit tests will be run, add "pytests" to beginning of matrix list
if [ "$run_unit_tests" == "true" ]; then
  echo Adding unit tests to list to run

  # if matrix is empty, set to a list that only includes pytests
  if [ "$matrix" == "[]" ]; then
    matrix="[\"pytests\"]"
  # otherwise prepend item to list
  else
    matrix="[\"pytests\", ${matrix:1}"
  fi
fi

echo Array of groups to run is: $matrix
# if matrix is still empty, exit 1 to fail step and skip rest of workflow
if [ "$matrix" == "[]" ]; then
  echo No tests to run!
  echo ::set-output name=run_some_tests::true
  exit 0
fi

echo ::set-output name=run_some_tests::false
echo ::set-output name=matrix::{\"categories\":$(echo $matrix)}\"
