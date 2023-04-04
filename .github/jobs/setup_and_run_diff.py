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

CI_JOBS_DIR = '.github/jobs'

RUNNER_WORKSPACE = os.environ.get('RUNNER_WORKSPACE')
GITHUB_WORKSPACE = os.environ.get('GITHUB_WORKSPACE')
REPO_NAME = os.path.basename(RUNNER_WORKSPACE)
WS_PATH = os.path.join(RUNNER_WORKSPACE, REPO_NAME)
print(f"WS_PATH is {WS_PATH}")
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

print(f"Output Volumes: {VOLUMES_FROM}")

volume_mounts = [
    f'-v {WS_PATH}:{GITHUB_WORKSPACE}',
    f'-v {RUNNER_WORKSPACE}/output:/data/output',
    f'-v {RUNNER_WORKSPACE}/diff:/data/diff',
]

mount_args = ' '.join(volume_mounts)

# command to run inside Docker
cmd = (f'/usr/local/envs/diff{VERSION_EXT}/bin/python3 '
       f'{GITHUB_WORKSPACE}/{CI_JOBS_DIR}/run_diff_docker.py')

# run inside diff env: mount METplus code and output dir, volumes from output volumes
docker_cmd = (f'docker run -e GITHUB_WORKSPACE {VOLUMES_FROM} '
              f'{mount_args} dtcenter/metplus-envs:diff{VERSION_EXT} '
              f'bash -c "{cmd}"')
print(f'RUNNING: {docker_cmd}')
try:
    process = subprocess.Popen(shlex.split(docker_cmd),
                               shell=False,
                               encoding='utf-8',
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    # Poll process.stdout to show stdout live
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    if rc:
        raise subprocess.CalledProcessError(rc, docker_cmd)

except subprocess.CalledProcessError as err:
    print(f"ERROR: Command failed -- {err}")
    sys.exit(1)
