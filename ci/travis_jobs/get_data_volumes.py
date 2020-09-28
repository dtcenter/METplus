#! /usr/bin/env python3

import sys
import subprocess
import shlex

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
                   'all_metplus_data',
                  )

def main():
    volume_list = []

    dockerhub_repo = 'metplus-data'
    if METPLUS_VERSION.startswith('v'):
        dockerhub_repo = f'{dockerhub_repo}-dev'

    for model_app_name in MODEL_APP_NAMES:

        # if model application name if found in any command line argument.
        # True if the name is found within any argument string
        # i.e. met_tool_wrapper or --met_tool_wrapper
        if any([model_app_name in item for item in sys.argv]):

            # if name is not all_metplus_data, use branch version, otherwise
            # add model application sub category to volume name
            if model_app_name == 'all_metplus_data':
                volume_name = METPLUS_VERSION
            else:
                volume_name = f'{METPLUS_VERSION}-{model_app_name}'

            cmd = f'docker pull dtcenter/{dockerhub_repo}:{volume_name}'
            ret = subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)

            # if return code is non-zero, a failure occurred
            if ret.returncode:
                return f'Command failed: {cmd}'

            cmd = (f'docker create --name {model_app_name} '
                   f'dtcenter/{dockerhub_repo}:{volume_name}')
            ret = subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)

            if ret.returncode:
                return f'Command failed: {cmd}'

            # add name to volumes from list to pass to docker build
            volume_list.append(f'--volumes-from {model_app_name}')

    return ' '.join(volume_list)

if __name__ == "__main__":
    out = main()
    print(out)
