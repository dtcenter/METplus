#! /usr/bin/env python3

import os
import sys
import subprocess
import shlex
import re

from docker_utils import VERSION_EXT, get_branch_name

ci_dir = os.path.join(os.environ.get('GITHUB_WORKSPACE'), '.github')
sys.path.insert(0, ci_dir)

from jobs import get_data_volumes
from jobs.docker_utils import run_command

CI_JOBS_DIR = '.github/jobs'

RUNNER_WORKSPACE = os.environ.get('RUNNER_WORKSPACE')
GITHUB_WORKSPACE = os.environ.get('GITHUB_WORKSPACE')
REPO_NAME = os.path.basename(GITHUB_WORKSPACE)
METPLUS_DEVELOP_PATH = os.path.join(GITHUB_WORKSPACE, f"{REPO_NAME}.develop")
print(f"METPLUS_DEVELOP_PATH is {METPLUS_DEVELOP_PATH}")
print(f"GITHUB_WORKSPACE is {GITHUB_WORKSPACE}")

INPUT_CATEGORIES = sys.argv[1]
artifact_name = sys.argv[2]

# get output data volumes
print("Get Docker data volumes for output data")

# use develop branch output data volumes if not a pull request (forced diff)
if os.environ.get('GITHUB_EVENT_NAME') == "pull_request":
    output_data_branch = os.environ.get('GITHUB_BASE_REF')
else:
    branch_name = get_branch_name()
    match = re.match(r'.*(main_v\d+\.\d+).*', branch_name)
    if match:
        output_data_branch = match.group(1)
    else:
        output_data_branch = 'develop'

output_category = f"output-{output_data_branch}-{artifact_name}"

VOLUMES_FROM = get_data_volumes.main([output_category])
if VOLUMES_FROM is None:
    print(f"::error:: Could not get truth data to run diff for {artifact_name}."
          " If this is a new use case, "
          "this is expected because the truth data has not been created yet.")
    sys.exit(2)

print(f"Output Volumes: {VOLUMES_FROM}")

VOLUME_MOUNTS = [
    f'-v {METPLUS_DEVELOP_PATH}:{GITHUB_WORKSPACE}',
    f'-v {RUNNER_WORKSPACE}/output:/data/output',
    f'-v {RUNNER_WORKSPACE}/diff:/data/diff',
]

MOUNT_ARGS = ' '.join(VOLUME_MOUNTS)

# command to run inside Docker
diff_command = (f'/usr/local/conda/envs/diff{VERSION_EXT}/bin/python3 '
                f'{GITHUB_WORKSPACE}/{CI_JOBS_DIR}/run_diff_docker.py')

# start detached interactive diff env container
# mount METplus code and output dir, volumes from output volumes
docker_cmd = (
    f'docker run -d --rm -it --name diff -e GITHUB_WORKSPACE {VOLUMES_FROM}'
    f' {MOUNT_ARGS} dtcenter/metplus-envs:diff{VERSION_EXT} bash'
)
if not run_command(docker_cmd):
    sys.exit(1)

# execute command to run difference tests in Docker container
# do not include GitHub Actions log grouping so full diff output can be put
# into one group so it is easier to view the diff summary
docker_cmd = f'docker exec -e GITHUB_WORKSPACE diff bash -cl "{diff_command}"'
if not run_command(docker_cmd, include_github_groups=False, include_timing=False):
    sys.exit(1)

# force remove container to stop and remove it
if not run_command('docker rm -f diff'):
    sys.exit(1)
