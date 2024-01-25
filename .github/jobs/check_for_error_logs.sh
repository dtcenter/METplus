#! /bin/bash

json_data=$(curl -s -H "Authorization: Bearer ${GITHUB_TOKEN}" "https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}/jobs")
error_log_jobs=$(echo "$json_data" | jq -r '.jobs[] | select(.name | startswith("Use Case Tests")) | .steps[] | select(.name | startswith("Save error logs")) | select(.conclusion | startswith("success"))')
# save output variable to merge error logs if any error logs were created
if [ ! -z "${error_log_jobs}" ]; then
  echo "has_error_logs=true" >> $GITHUB_OUTPUT
else
  echo "has_error_logs=false" >> $GITHUB_OUTPUT
fi
