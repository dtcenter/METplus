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
import time

import get_use_case_commands
import get_data_volumes
from docker_utils import get_branch_name, VERSION_EXT

runner_workspace = os.environ.get('RUNNER_WORKSPACE')
github_workspace = os.environ.get('GITHUB_WORKSPACE')

repo_name =os.path.basename(runner_workspace)
ws_path = os.path.join(runner_workspace, repo_name)

docker_data_dir = '/data'
docker_output_dir = os.path.join(docker_data_dir, 'output')
gha_output_dir = os.path.join(runner_workspace, 'output')

RUN_TAG = 'metplus-run-env'

def main():
    categories, subset_list, _ = (
        get_use_case_commands.handle_command_line_args()
    )
    categories_list = categories.split(',')
    all_commands = (
        get_use_case_commands.main(categories_list,
                                   subset_list,
                                   work_dir=os.environ.get('GITHUB_WORKSPACE'),
                                   host_name='docker')
    )
    # get input data volumes
    volumes_from = get_data_volumes.main(categories_list)
    print(f"Input Volumes: {volumes_from}")

    # build Docker image with conda environment and METplus branch image
    branch_name = get_branch_name()
    if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request':
        branch_name = f"{branch_name}-pull_request"

    dockerfile_dir = os.path.join('.github', 'actions', 'run_tests')

    # use BuildKit to build image
    os.environ['DOCKER_BUILDKIT'] = '1'

    volume_mounts = [
        f"-v {runner_workspace}/output/mysql:/var/lib/mysql",
        f"-v {gha_output_dir}:{docker_output_dir}",
        f"-v {ws_path}:{github_workspace}",
    ]

    isOK = True
    for setup_commands, use_case_commands, requirements in all_commands:

        # get environment image tag
        use_env = [item for item in requirements if item.endswith('_env')]
        if use_env:
            env_tag = use_env[0].replace('_env', '')
        else:
            env_tag = 'metplus_base'

        env_tag = f'{env_tag}{VERSION_EXT}'

        # get Dockerfile to use
        dockerfile_name = 'Dockerfile.run'
        if 'gempak' in str(requirements).lower():
            dockerfile_name = f'{dockerfile_name}_gempak'
        elif 'gfdl' in str(requirements).lower():
            dockerfile_name = f'{dockerfile_name}_gfdl'
        elif 'cartopy' in str(requirements).lower():
            dockerfile_name = f'{dockerfile_name}_cartopy'

        docker_build_cmd = (
            f"docker build -t {RUN_TAG} "
            f"--build-arg METPLUS_IMG_TAG={branch_name} "
            f"--build-arg METPLUS_ENV_TAG={env_tag} "
            f"-f {dockerfile_dir}/{dockerfile_name} ."
        )

        print(f'Building Docker environment/branch image...')
        if not run_docker_commands([docker_build_cmd]):
            isOK = False
            continue

        all_commands = []
        all_commands.append('docker images')
        all_commands.append(
            f"docker run -d --rm -it -e GITHUB_WORKSPACE "
            f"--name {RUN_TAG} "
            f"{os.environ.get('NETWORK_ARG', '')} "
            f"{' '.join(volume_mounts)} "
            f"{volumes_from} --workdir {github_workspace} "
            f'{RUN_TAG} bash'
        )
        all_commands.append('docker ps -a')
        for use_case_command in [setup_commands] + use_case_commands:
            all_commands.append(
                f'docker exec -e GITHUB_WORKSPACE {RUN_TAG} '
                f'bash -cl "{use_case_command}"'
            )
        all_commands.append('cat /etc/bashrc')
        all_commands.append(f'docker rm -f {RUN_TAG}')
        if not run_docker_commands(all_commands):
            isOK = False

    if not isOK:
        print("ERROR: Some commands failed.")
        sys.exit(1)


def run_docker_commands(docker_commands):
    is_ok = True
    for docker_command in docker_commands:
        print(f"RUNNING: {docker_command}")
        start_time = time.time()
        try:
            process = subprocess.Popen(shlex.split(docker_command),
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
                raise subprocess.CalledProcessError(rc, docker_command)

        except subprocess.CalledProcessError as err:
            print(f"ERROR: Command failed -- {err}")
            is_ok = False

        end_time = time.time()
        print("TIMING: Command took "
              f"{time.strftime('%M:%S', time.gmtime(end_time - start_time))}"
              f" (MM:SS): '{docker_command}')")

    return is_ok


if __name__ == '__main__':
    main()
