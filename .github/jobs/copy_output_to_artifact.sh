#! /bin/bash

# Called from .github/workflows/testing.yml
# Creates directory for output data artifact and
# copies output data into directory

artifact_name=$1
mkdir -p artifact/${artifact_name}
cp -r ${RUNNER_WORKSPACE}/output/* artifact/${artifact_name}/
