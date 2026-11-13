#! /usr/bin/env python3

# Script to easily get the dtcenter/metplus-dev image tag from docker_utils
# function. Run by GitHub Actions (in .github/actions/run_tests/entrypoint.sh
# and .github/jobs/docker_setup.sh)

from docker_utils import get_metplus_image_tag

print(get_metplus_image_tag())
