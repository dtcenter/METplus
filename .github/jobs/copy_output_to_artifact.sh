#! /bin/bash

# Called from .github/workflows/testing.yml
# Creates directory for output data artifact and
# copies output data into directory

artifact_name=${{ steps.get-artifact-name.outputs.artifact_name }}
mkdir -p artifact/${artifact_name}
cp -r ${RUNNER_WORKSPACE}/output/* artifact/${artifact_name}/
