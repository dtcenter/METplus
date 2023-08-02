#! /bin/bash

use_case_groups_filepath=.github/parm/use_case_groups.json

# set matrix to string of an empty array in case no use cases will be run
matrix="[]"

run_use_cases=$1
run_all_use_cases=$2

echo Run use cases: $run_use_cases
echo Run all use cases: $run_all_use_cases

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

echo Array of groups to run is: $matrix
# if matrix is still empty, exit 1 to fail step and skip rest of workflow
if [ "$matrix" == "[]" ]; then
  echo No tests to run!
  echo "run_some_tests=false" >> $GITHUB_OUTPUT
  exit 0
fi

echo "run_some_tests=true" >> $GITHUB_OUTPUT
echo "matrix={\"categories\":$(echo $matrix)}\"" >> $GITHUB_OUTPUT
