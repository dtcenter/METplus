#! /usr/bin/env python3

import sys
import subprocess
import shlex

METPLUS_VERSION = '3.1'

MODEL_APP_NAMES = ('met_tool_wrapper',
                   'convection_allowing_models',
                   'climate',
                   'cryosphere',
                   'medium_range',
                   'precipitation',
                   's2s',
                   'space_weather',
                   'tc_and_extra_tc'
                  )

def main():
    volume_list = []

    for model_app_name in MODEL_APP_NAMES:
        if any([model_app_name in item for item in sys.argv]):
            volume_name = f'{METPLUS_VERSION}-{model_app_name}'

            cmd = f'docker pull dtcenter/metplus-data:{volume_name}'
            subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)

            cmd = (f'docker create --name {model_app_name} '
                   f'dtcenter/metplus-data:{volume_name}')
            subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL)

            # add name to volumes from list to pass to docker build
            volume_list.append(f'--volumes-from {model_app_name}')

    return ' '.join(volume_list)

if __name__ == "__main__":
    out = main()
    print(out)
