#! /usr/bin/env python3

# Script to easily get branch name from docker_utils function
# Run by GitHub Actions (in ci/actions/run_tests/entrypoint.sh,
# ci/jobs/create_output_data_volumes.sh, and ci/jobs/docker_setup.sh)

from docker_utils import get_branch_name

print(get_branch_name())
