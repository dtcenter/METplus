#! /bin/bash

# Called from .github/workflows/testing.yml
# Call Python script to copy logs from any use case that contains "ERROR:"
# into directory to create GitHub Actions artifact.
# Sets output variable upload_error_logs to 'true' if errors occurred or
# 'false' if no errors occurred

.github/jobs/copy_error_logs.py ${RUNNER_WORKSPACE}/output artifact/error_logs
if [ -d "artifact/error_logs" ]; then
  echo "upload_error_logs=true" >> $GITHUB_OUTPUT
else
  echo "upload_error_logs=false" >> $GITHUB_OUTPUT
fi
