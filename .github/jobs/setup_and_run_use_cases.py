#! /usr/bin/env python3

################################################################################
# Used in GitHub Actions (in .github/actions/run_tests/entrypoint.sh) to run cases
# For each use case group specified:
#  - create input Docker data volumes and get --volumes-from arguments
#  - build Docker image with conda environment and METplus branch image
#  - Run commands to run use cases


import os
import sys
import subprocess
import shlex

import get_use_case_commands
import get_data_volumes
from docker_utils import get_branch_name

runner_workspace = os.environ.get('RUNNER_WORKSPACE')
github_workspace = os.environ.get('GITHUB_WORKSPACE')

repo_name =os.path.basename(runner_workspace)
ws_path = os.path.join(runner_workspace, repo_name)

docker_data_dir = '/data'
docker_output_dir = os.path.join(docker_data_dir, 'output')
gha_output_dir = os.path.join(runner_workspace, 'output')

def main():
    categories, subset_list, _ = (
        get_use_case_commands.handle_command_line_args()
    )
    categories_list = categories.split(',')
    all_commands = (
        get_use_case_commands.main(categories_list,
                                   subset_list,
                                   work_dir=os.environ.get('GITHUB_WORKSPACE'))
    )
    # get input data volumes
    volumes_from = get_data_volumes.main(categories_list)
    print(f"Input Volumes: {volumes_from}")

    # build Docker image with conda environment and METplus branch image
    branch_name = get_branch_name()
    if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request':
        branch_name = f"{branch_name}-pull_request"

    run_tag = 'metplus-run-env'
    dockerfile_dir = os.path.join('.github', 'actions', 'run_tests')

    # use BuildKit to build image
    os.environ['DOCKER_BUILDKIT'] = '1'

    volume_mounts = [
        f"-v {runner_workspace}/output/mysql:/var/lib/mysql",
        f"-v {gha_output_dir}:{docker_output_dir}",
        f"-v {ws_path}:{github_workspace}",
    ]

    isOK = True
    for cmd, requirements in all_commands:

        # get environment image tag
        use_env = [item for item in requirements if item.endswith('_env')]
        if use_env:
            env_tag = use_env[0].replace('_env', '')
        else:
            env_tag = 'metplus_base'

        # get Dockerfile to use (gempak if using gempak)
        if 'gempak' in requirements:
            dockerfile_name = 'Dockerfile.gempak'
        else:
            dockerfile_name = 'Dockerfile.run'

        docker_build_cmd = (
            f"docker build -t {run_tag} "
            f"--build-arg METPLUS_IMG_TAG={branch_name} "
            f"--build-arg METPLUS_ENV_TAG={env_tag} "
            f"-f {dockerfile_dir}/{dockerfile_name} ."
        )
        print(f"Building Docker environment/branch image...\n"
              f"Running: {docker_build_cmd}")
        try:
            subprocess.run(shlex.split(docker_build_cmd), check=True)
        except subprocess.CalledProcessError as err:
            print(f"ERROR: Docker Build failed: {docker_build_cmd} -- {err}")
            isOK = False
            continue

        cmd_args = {'check': True,
                    'encoding': 'utf-8',
                    'capture_output': True,
                    }
        output = subprocess.run(shlex.split('docker ps -a'),
                                **cmd_args).stdout.strip()
        print(f"docker ps -a\n{output}")

        full_cmd = (
            f"docker run -e GITHUB_WORKSPACE "
            f"{os.environ.get('NETWORK_ARG', '')} "
            f"{' '.join(volume_mounts)} "
            f"{volumes_from} --workdir {github_workspace} "
            f'{run_tag} bash -c "{cmd}"')
        print(f"RUNNING: {full_cmd}")
        try:
            process = subprocess.Popen(shlex.split(full_cmd),
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
                raise subprocess.CalledProcessError(rc, full_cmd)

        except subprocess.CalledProcessError as err:
            print(f"ERROR: Command failed -- {err}")
            isOK = False

    if not isOK:
        print("ERROR: Some commands failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
