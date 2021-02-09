#! /usr/bin/env python3

import sys
import os

workspace = os.environ.get('GITHUB_WORKSPACE')

util_dir = os.path.join(workspace,
                        'ci',
                        'util')
sys.path.insert(0, util_dir)

import netcdf_util

data_dir = os.path.abspath(os.path.join(workspace,
                                        os.pardir))
dir_a = os.path.join(data_dir, 'truth')
dir_b = os.path.join(data_dir, 'output')

netcdf_util.compare_dir(dir_a, dir_b, debug=True)
