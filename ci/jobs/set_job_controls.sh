#! /bin/bash

# Run by GitHub Actions (in .github/workflows/testing.yml) to parse
# info from GitHub event and commit message from last commit before
# a push to determine which jobs to run and which to skip.

# set default status for jobs
run_docs=true
run_get_image=true
run_get_input_data=true
run_unit_tests=true
run_use_cases=true
run_save_truth_data=false
run_all_use_cases=false
run_diff=false

# run all use cases and diff logic for pull request
if [ "${GITHUB_EVENT_NAME}" == "pull_request" ]; then
  # only run diff logic if pull request INTO develop or main_v*
  # branches, not branches ending with -ref
  if [ "${GITHUB_BASE_REF: -4}" != "-ref" ] && \
    ([ "${GITHUB_BASE_REF:0:7}" == "develop" ] || \
     [ "${GITHUB_BASE_REF:0:6}" == "main_v" ]); then
    run_use_cases=true
    run_all_use_cases=true
    run_diff=true
  fi
# run all use cases and save truth data if -ref branch and not PR
elif [ "${GITHUB_REF: -4}" == -ref ]; then
  run_use_cases=true
  run_all_use_cases=true
  run_save_truth_data=true
# if not pull request or -ref branch, apply commit messages overrides
else

  # if develop or main branch, run all use cases
  branch_name=`cut -d "/" -f3 <<< "${GITHUB_REF}"`
  if [ "$branch_name" == "develop" ] || \
     [ "${branch_name:0:6}" == "main_v" ]; then
    run_all_use_cases=true
  fi

  # check commit messages for skip or force keywords
  if grep -q "ci-skip-all" <<< "$commit_msg"; then
    run_docs=false
    run_get_image=false
    run_get_input_data=false
    run_unit_tests=false
    run_use_cases=false
    run_save_truth_data=false
    run_diff=false
  fi

  if grep -q "ci-skip-use-cases" <<< "$commit_msg"; then
    run_use_cases=false
  fi

  if grep -q "ci-skip-unit-tests" <<< "$commit_msg"; then
    run_unit_tests=false
  fi

  if grep -q "ci-only-docs" <<< "$commit_msg"; then
    run_docs=true
    run_get_image=false
    run_get_input_data=false
    run_unit_tests=false
    run_use_cases=false
    run_save_truth_data=false
    run_diff=false
  fi

  if grep -q "ci-only-new-cases" <<< "$commit_msg"; then
    run_all_use_cases=false
  fi

  if grep -q "ci-run-diff" <<< "$commit_msg"; then
    run_all_use_cases=true
    run_diff=true
  fi

  if grep -q "ci-run-all-cases" <<< "$commit_msg"; then
    run_use_cases=true
    run_all_use_cases=true
  fi

fi

# output some job control variables so it can be read by another step
export run_use_cases
export run_all_use_cases
export run_unit_tests


touch job_control_status
echo run_docs=${run_docs} >> job_control_status
echo run_get_image=${run_get_image} >> job_control_status
echo run_get_input_data=${run_get_input_data} >> job_control_status
echo run_unit_tests=${run_unit_tests} >> job_control_status
echo run_use_cases=${run_use_cases} >> job_control_status
echo run_save_truth_data=${run_save_truth_data} >> job_control_status
echo run_all_use_cases=${run_all_use_cases} >> job_control_status
echo run_diff=${run_diff} >> job_control_status
echo Job Control Settings:
cat job_control_status

# get use cases to run
.github/jobs/get_use_cases_to_run.sh $run_use_cases $run_all_use_cases $run_run_unit_tests
