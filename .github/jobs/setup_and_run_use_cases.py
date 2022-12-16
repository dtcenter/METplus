#! /usr/bin/env python3

################################################################################
# Used in GitHub Actions (in .github/actions/run_tests/entrypoint.sh) to run cases
# For each use case group specified:
#  - create input Docker data volumes and get --volumes-from arguments
#  - build Docker image with conda environment and METplus branch image
#  - Run commands to run use cases


import os
import sys

import get_use_case_commands
import get_data_volumes
from docker_utils import get_branch_name, VERSION_EXT, run_commands

RUNNER_WORKSPACE = os.environ.get('RUNNER_WORKSPACE')
GITHUB_WORKSPACE = os.environ.get('GITHUB_WORKSPACE')

REPO_NAME = os.path.basename(RUNNER_WORKSPACE)
WS_PATH = os.path.join(RUNNER_WORKSPACE, REPO_NAME)

DOCKER_DATA_DIR = '/data'
DOCKER_OUTPUT_DIR = os.path.join(DOCKER_DATA_DIR, 'output')
GHA_OUTPUT_DIR = os.path.join(RUNNER_WORKSPACE, 'output')

RUN_TAG = 'metplus-run-env'

VOLUME_MOUNTS = [
    f"-v {RUNNER_WORKSPACE}/output/mysql:/var/lib/mysql",
    f"-v {GHA_OUTPUT_DIR}:{DOCKER_OUTPUT_DIR}",
    f"-v {WS_PATH}:{GITHUB_WORKSPACE}",
]

DOCKERFILE_DIR = os.path.join('.github', 'actions', 'run_tests')


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

    # use BuildKit to build image
    os.environ['DOCKER_BUILDKIT'] = '1'

    isOK = True
    for setup_commands, use_case_commands, requirements in all_commands:
        # get environment image tag
        env_tag = _get_metplus_env_tag(requirements)

        # get Dockerfile to use
        dockerfile_name = _get_dockerfile_name(requirements)

        docker_build_cmd = (
            f"docker build -t {RUN_TAG} "
            f"--build-arg METPLUS_IMG_TAG={branch_name} "
            f"--build-arg METPLUS_ENV_TAG={env_tag} "
            f"-f {DOCKERFILE_DIR}/{dockerfile_name} ."
        )

        print(f'Building Docker environment/branch image...')
        if not run_commands(docker_build_cmd):
            isOK = False
            continue

        commands = []
        commands.append('docker images')
        # start interactive container in the background
        commands.append(
            f"docker run -d --rm -it -e GITHUB_WORKSPACE "
            f"--name {RUN_TAG} "
            f"{os.environ.get('NETWORK_ARG', '')} "
            f"{' '.join(VOLUME_MOUNTS)} "
            f"{volumes_from} --workdir {GITHUB_WORKSPACE} "
            f'{RUN_TAG} bash'
        )
        # list running containers
        commands.append('docker ps -a')
        # execute commands in running docker container
        docker_commands = [setup_commands] + use_case_commands
        docker_commands.append('cat /etc/bashrc')
        for docker_command in docker_commands:
            commands.append(
                f'docker exec -e GITHUB_WORKSPACE {RUN_TAG} '
                f'bash -cl "{docker_command}"'
            )
        # force remove container to stop and remove it
        commands.append(f'docker rm -f {RUN_TAG}')
        if not run_commands(commands):
            isOK = False

    if not isOK:
        print("ERROR: Some commands failed.")
        sys.exit(1)


def _get_metplus_env_tag(requirements):
    """!Parse use case requirements to get Docker tag to obtain conda
     environment to use in tests. Append version extension e.g. .v5

    @param requirements list of use case requirements
    @returns string of Docker tag
    """
    use_env = [item for item in requirements if item.endswith('_env')]
    if use_env:
        env_tag = use_env[0].replace('_env', '')
    else:
        env_tag = 'metplus_base'

    return f'{env_tag}{VERSION_EXT}'


def _get_dockerfile_name(requirements):
    """!Parse use case requirements to get name of Dockerfile to use to build
     environment to use in tests. Dockerfile.run copies conda directories into
     test image. Other Dockerfiles copy additional files needed to run certain
     use cases. For example, cartopy uses shape files that occasionally cannot
     be downloaded on the fly, so they are downloaded in advance and copied
     into the test image. GEMPAK requires JavaRE. GFDL Tracker requires
     NetCDF libraries and tracker executable.

    @param requirements list of use case requirements
    @returns string of Dockerfile to use to create test environment
    """
    dockerfile_name = 'Dockerfile.run'
    if 'gempak' in str(requirements).lower():
        return f'{dockerfile_name}_gempak'
    if 'gfdl' in str(requirements).lower():
        return f'{dockerfile_name}_gfdl'
    if 'cartopy' in str(requirements).lower():
        return f'{dockerfile_name}_cartopy'
    return dockerfile_name


if __name__ == '__main__':
    main()
