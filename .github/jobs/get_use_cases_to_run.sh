#! /bin/bash

use_case_groups_filepath=.github/parm/use_case_groups.json
pytests_groups_filepath=.github/parm/pytest_groups.txt
# set matrix to string of an empty array in case no use cases will be run
matrix="[]"

run_use_cases=$1
run_all_use_cases=$2
run_unit_tests=$3

echo Run use cases: $run_use_cases
echo Run all use cases: $run_all_use_cases
echo Run unit tests: $run_unit_tests

# if running use cases, generate JQ filter to use
if [ "$run_use_cases" == "true" ]; then
  echo generate JQ filter to get use cases to run

  # if only running new use cases, add to filter criteria
  if [ "$run_all_use_cases" == "false" ]; then
    echo "Only run use cases that are marked to run every time (run = true)"
    matrix=$(jq '[.[] | select(.run == true) | (.category + ":" + .index_list)]' $use_case_groups_filepath)
  else
    echo Add all available use cases
    matrix=$(jq '[.[] | (.category + ":" + .index_list)]' $use_case_groups_filepath)
  fi

fi

# if unit tests will be run, add "pytests" to beginning of matrix list
if [ "$run_unit_tests" == "true" ]; then
  echo Adding unit tests to list to run

  pytests=""
  for x in `cat $pytests_groups_filepath`; do
    pytests=$pytests"\"pytests_$x\","
  done

  # if matrix is empty, set to an array that only includes pytests
  if [ "$matrix" == "[]" ]; then
    matrix="[${pytests:0: -1}]"
  # otherwise prepend item to list
  else
    matrix="[${pytests}${matrix:1}"
  fi
fi

echo Array of groups to run is: $matrix
# if matrix is still empty, exit 1 to fail step and skip rest of workflow
if [ "$matrix" == "[]" ]; then
  echo No tests to run!
  echo ::set-output name=run_some_tests::false
  exit 0
fi

echo ::set-output name=run_some_tests::true
echo ::set-output name=matrix::{\"categories\":$(echo $matrix)}\"
