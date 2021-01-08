#! /usr/bin/env python3

import sys
import os
import subprocess
import shlex

from docker_utils import docker_get_volumes_last_updated

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                os.pardir,)))

from metplus import __version__

# METPLUS_VERSION should be set to develop or a release version, i.e. vX.Y
# if version is set to X.Y without -betaZ or -dev, use that version
# otherwise use develop
if len(__version__.split('-')) == 1:
    # only get first 2 numbers from version, i.e. X.Y.Z will use vX.Y
    METPLUS_VERSION = f"v{'.'.join(__version__.split('.')[:2])}"

else:
    METPLUS_VERSION = 'develop'

MODEL_APP_NAMES = ('met_tool_wrapper',
                   'convection_allowing_models',
                   'climate',
                   'cryosphere',
                   'medium_range',
                   'precipitation',
                   's2s',
                   'space_weather',
                   'tc_and_extra_tc',
                   'data_assimilation',
                   'all_metplus_data',
                  )

def main(args):
    volume_list = []
    current_branch = os.environ.get('BRANCH_NAME')
    if not current_branch:
        print("Could not get current branch. Exiting.")
        sys.exit(1)

    # if running development version, use metplus-data-dev
    # if released version, i.e. vX.Y, use metplus-data
    if METPLUS_VERSION == 'develop':
        data_repo = 'dtcenter/metplus-data-dev'
    else:
        data_repo = 'dtcenter/metplus-data'

    # get all docker data volumes associated with current branch
    available_volumes = docker_get_volumes_last_updated(current_branch).keys()

    for model_app_name in MODEL_APP_NAMES:

        # if model application name if found in any command line argument.
        # True if the name is found within any argument string
        # i.e. met_tool_wrapper or --met_tool_wrapper
        if any([model_app_name in item for item in args]):

            # if name is not all_metplus_data, use branch version, otherwise
            # add model application sub category to volume name
            if model_app_name == 'all_metplus_data':
                volume_name = METPLUS_VERSION
            else:
                # if using development version and branch data volume is available
                # use it, otherwise use develop version of data volume
                if (METPLUS_VERSION == 'develop' and
                        f'{current_branch}-{model_app_name}' in available_volumes):
                    version = current_branch
                else:
                    version = METPLUS_VERSION

                volume_name = f'{version}-{model_app_name}'

            cmd = f'docker pull {data_repo}:{volume_name}'
            ret = subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)

            # if return code is non-zero, a failure occurred
            if ret.returncode:
                return f'Command failed: {cmd}'

            cmd = (f'docker create --name {model_app_name} '
                   f'{data_repo}:{volume_name}')
            ret = subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)

            if ret.returncode:
                return f'Command failed: {cmd}'

            # add name to volumes from list to pass to docker build
            volume_list.append(f'--volumes-from {model_app_name}')

    return ' '.join(volume_list)

if __name__ == "__main__":
    out = main(sys.argv)
    print(out)
