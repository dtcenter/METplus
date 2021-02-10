#! /usr/bin/env python3

import os
import sys
import subprocess
import shlex

names = sys.argv[1].split(',')

DEVELOP_REF_RUN = 552853822

ARTIFACT_IDS_DEVELOP = {
    'air_quality_and_comp': 39369666,
    'climate': 39369667,
    'convection_allowing_models_a': 39369668,
    'convection_allowing_models_b': 39369669,
    'cryosphere': 39369670,
    'data_assimilation': 39369671,
    'medium_range_a': 39369672,
    'medium_range_b': 39369673,
    'medium_range_c': 39369674,
    'met_tool_wrapper': 39369675,
    'precipitation': 39369676,
}

for name in names:
    artifact_id = ARTIFACT_IDS_DEVELOP[name]
    my_secret_api_token = os.environ.get('MY_SECRET_API_TOKEN')
    artifact_url = f"https://{my_secret_api_token}@api.github.com/repos/dtcenter/metplus/actions/artifacts/{artifact_id}/zip"

    truth_dir = os.path.abspath(os.path.join(os.environ.get('GITHUB_WORKSPACE'),
                                             os.pardir,
                                             'truth'))

    output_file = os.path.join(truth_dir, f'{name}.zip')

    if not os.path.exists(truth_dir):
        print(f"Creating directory: {truth_dir}")
        os.makedirs(truth_dir)

    cmd = f'curl -L -o {output_file} {artifact_url}'
    print(cmd)
    ret = subprocess.run(shlex.split(cmd))

    cmd = f'unzip {output_file} -d {truth_dir}/'
    ret = subprocess.run(shlex.split(cmd))
