#! /usr/bin/env python3

import sys
import os
import subprocess
import shlex

from docker_utils import docker_get_volumes_last_updated, get_branch_name

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                os.pardir,)))

from metplus import __version__

DOCKERHUB_METPLUS_DATA = 'dtcenter/metplus-data'
DOCKERHUB_METPLUS_DATA_DEV = 'dtcenter/metplus-data-dev'

# METPLUS_VERSION should be set to develop or a release version, i.e. vX.Y
# if version is set to X.Y without -betaZ or -dev, use that version
# otherwise use develop
if len(__version__.split('-')) == 1:
    # only get first 2 numbers from version, i.e. X.Y.Z will use vX.Y
    METPLUS_VERSION = f"v{'.'.join(__version__.split('.')[:2])}"

else:
    METPLUS_VERSION = 'develop'

def main(args):
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
    # if released version, i.e. vX.Y, use metplus-data
    if METPLUS_VERSION == 'develop':
        data_repo = DOCKERHUB_METPLUS_DATA_DEV
    else:
        data_repo = DOCKERHUB_METPLUS_DATA

    # get all docker data volumes associated with current branch
    available_volumes = docker_get_volumes_last_updated(branch_name).keys()

    # loop through arguments and get data volume for each category
    for model_app_name in args:
        # set another variable for DockerHub repo to use
        # this will be switched to the dev version if reading output data
        repo_to_use = data_repo

        # if getting all input data, set volume name to METplus version
        if model_app_name == 'all_metplus_data':
            volume_name = METPLUS_VERSION

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
        elif (METPLUS_VERSION == 'develop' and
              f'{branch_name}-{model_app_name}' in available_volumes):
                volume_name = f'{branch_name}-{model_app_name}'
        else:
            volume_name = f'{METPLUS_VERSION}-{model_app_name}'

        cmd = f'docker pull {repo_to_use}:{volume_name}'
        ret = subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)

        # if return code is non-zero, a failure occurred
        if ret.returncode:
            return f'Command failed: {cmd}'

        cmd = (f'docker create --name {model_app_name} '
               f'{repo_to_use}:{volume_name}')
        ret = subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)

        if ret.returncode:
            return f'Command failed: {cmd}'

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
