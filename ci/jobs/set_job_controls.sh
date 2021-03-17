#! /bin/bash

# set default status for jobs
run_docs=true
run_get_image=true
run_get_input_data=true
run_unit_tests=true
run_use_cases=true
run_save_truth_data=false
run_new_use_cases_only=true
run_diff=false

# run all use cases and save truth data if -ref branch and not PR
# run all use cases and diff logic for pull request
if [ "${GITHUB_EVENT_NAME}" == "pull_request" ]; then
  # only run diff logic if pull request INTO develop or main_v*
  # branches, not branches ending with -ref
  if [ "${GITHUB_BASE_REF: -4}" != "-ref" ] && \
    ([ "${GITHUB_BASE_REF:0:7}" == "develop" ] || \
     [ "${GITHUB_BASE_REF:0:6}" == "main_v" ]); then
    run_use_cases=true
    run_new_use_cases_only=false
    run_diff=true
  fi
elif [ "${GITHUB_HEAD_REF: -4}" == -ref ]; then
  run_use_cases=true
  run_new_use_cases_only=false
  run_save_truth_data=true
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

if grep -q "ci-skip-get-image" <<< "$commit_msg"; then
  run_get_image=false
fi

if grep -q "ci-skip-use-cases" <<< "$commit_msg"; then
  run_use_cases=false
fi

if grep -q "ci-new-cases-only" <<< "$commit_msg"; then
  run_new_use_cases_only=true
fi

if grep -q "ci-force-diff" <<< "$commit_msg"; then
  run_diff=true
fi

if grep -q "ci-force-all-cases" <<< "$commit_msg"; then
  run_use_cases=true
  run_new_use_cases_only=false
fi

touch job_control_status
echo run_docs=${run_docs} >> job_control_status
echo run_get_image=${run_get_image} >> job_control_status
echo run_get_input_data=${run_get_input_data} >> job_control_status
echo run_unit_tests=${run_unit_tests} >> job_control_status
echo run_use_cases=${run_use_cases} >> job_control_status
echo run_save_truth_data=${run_save_truth_data} >> job_control_status
echo run_new_use_cases_only=${run_new_use_cases_only} >> job_control_status
echo run_diff=${run_diff} >> job_control_status
echo Job Control Settings:
cat job_control_status