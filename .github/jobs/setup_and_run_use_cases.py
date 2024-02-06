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
    if volumes_from is None:
        print('ERROR: Could not get input data to run use cases')
        sys.exit(1)

    print(f"Input Volumes: {volumes_from}")

    # build Docker image with conda environment and METplus branch image
    branch_name = get_branch_name()
    if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request':
        branch_name = f"{branch_name}-pull_request"

    # use BuildKit to build image
    os.environ['DOCKER_BUILDKIT'] = '1'

    isOK = True
    failed_use_cases = []
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

        # print list of existing docker images
        commands.append('docker images')

        # remove docker image after creating run env or prune untagged images
        commands.append(f'docker image rm dtcenter/metplus-dev:{branch_name} -f || docker image prune -f')

        # list docker images again after removal
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

        # execute setup commands in running docker container
        commands.append(_format_docker_exec_command(setup_commands))

        # run docker commands and skip running cases if something went wrong
        if not run_commands(commands):
            isOK = False

            # force remove container if setup step fails
            run_commands(f'docker rm -f {RUN_TAG}')

            # add all use cases that couldn't run to list of failed cases
            failed_use_cases.extend(use_case_commands)

            continue

        # execute use cases in running docker container
        # save list of use cases that failed
        for use_case_command in use_case_commands:
            if not run_commands(_format_docker_exec_command(use_case_command)):
                failed_use_cases.append(use_case_command)
                isOK = False

        # print bashrc file to see what was added by setup commands
        # then force remove container to stop and remove it
        if not run_commands([
            _format_docker_exec_command('cat /root/.bashrc'),
            f'docker rm -f {RUN_TAG}',
        ]):
            isOK = False

    # print summary of use cases that failed
    for failed_use_case in failed_use_cases:
        print(f'ERROR: Use case failed: {failed_use_case}')

    if not isOK:
        print("ERROR: Some commands failed.")
        sys.exit(1)


def _format_docker_exec_command(command):
    """! Get docker exec command to call given command in a bash login shell

    @param command string of command to run in docker
    @returns string of docker exec command to run command
    """
    return f'docker exec -e GITHUB_WORKSPACE {RUN_TAG} bash -cl "{command}"'


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
    if 'geovista' in str(requirements).lower():
        return f'{dockerfile_name}_geovista'
    return dockerfile_name


if __name__ == '__main__':
    main()
