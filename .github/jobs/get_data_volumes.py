#! /usr/bin/env python3

# Run by GitHub Actions (in .github/actions/run_tests/entrypoint.sh)
# to obtain Docker data volumes for input and output data, create
# an alias name for the volumes, and generate --volumes-from arguments
# that are added to the Docker run command to make data available

import sys
import os
import subprocess
import shlex

from docker_utils import docker_get_volumes_last_updated, get_branch_name
from docker_utils import get_data_repo, DOCKERHUB_METPLUS_DATA_DEV
from docker_utils import run_commands


def main(args):
    # get METplus version
    version_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                os.pardir,
                                                'metplus',
                                                'VERSION'))
    with open(version_file, 'r') as file_handle:
        version = file_handle.read().strip()

    # version should be set to develop or a release version, i.e. X.Y
    # if version is set to X.Y without -betaZ or -dev, use that version
    # otherwise use develop
    if len(version.split('-')) == 1:
        # only get first 2 numbers from version, i.e. X.Y.Z will use X.Y
        metplus_version = '.'.join(version.split('.')[:2])
    else:
        metplus_version = 'develop'

    volume_list = []

    # get the name of the current branch
    branch_name = get_branch_name()
    if not branch_name:
        print("Could not get current branch. Exiting.")
        sys.exit(1)

    # remove -ref from end of branch name if found
    if branch_name.endswith('-ref'):
        branch_name = branch_name[0:-4]

    # if running development version, use metplus-data-dev
    # if released version, i.e. X.Y.Z, use metplus-data
    data_repo = get_data_repo(metplus_version)

    if branch_name.startswith('main_v'):
        branch_name = branch_name[5:]

    # get all docker data volumes associated with current branch
    available_volumes = docker_get_volumes_last_updated(branch_name).keys()

    # loop through arguments and get data volume for each category
    for model_app_name in args:
        # set another variable for DockerHub repo to use
        # this will be switched to the dev version if reading output data
        repo_to_use = data_repo

        # if getting all input data, set volume name to METplus version
        if model_app_name == 'all_metplus_data':
            volume_name = metplus_version

        # requested data volume is output data
        # should match output-{pr_dest_branch}-use_cases_{dataset_id}
        # where {pr_dest_branch} is the destination branch of the pull request
        # and {dataset_id} is the identifier of the dataset,
        # i.e. met_tool_wrapper_2_5-6
        elif model_app_name.startswith('output-'):
            # set model_app_name to the dataset ID
            # set volume name to the string without '-use_cases_'
            prefix, model_app_name = model_app_name.rsplit('-use_cases_', 1)
            volume_name = f'{prefix}-{model_app_name}'

            # add output- to model app name
            model_app_name=f'output-{model_app_name}'

            # set DockerHub repo to dev version because all output data
            # should be in dev repository
            repo_to_use = DOCKERHUB_METPLUS_DATA_DEV

        # if using development version and branch data volume is available
        # use it, otherwise use develop version of data volume
        elif (metplus_version == 'develop' and
              f'{branch_name}-{model_app_name}' in available_volumes):
                volume_name = f'{branch_name}-{model_app_name}'
        else:
            volume_name = f'{metplus_version}-{model_app_name}'

        full_volume_name = f'{repo_to_use}:{volume_name}'
        print(f"CREATING DATA VOLUME FROM: {full_volume_name}")
        cmd = (f'docker create --name {model_app_name} '
               f'{full_volume_name}')
        if not run_commands(cmd):
            continue

        # add name to volumes from list to pass to docker build
        volume_list.append(f'--volumes-from {model_app_name}')

    return ' '.join(volume_list)

if __name__ == "__main__":
    # split up command line args that have commas before passing into main
    args = []

    for arg in sys.argv[1:]:
        args.extend(arg.split(','))
    out = main(args)
    print(out)
