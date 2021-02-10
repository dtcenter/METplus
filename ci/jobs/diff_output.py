#! /usr/bin/env python3

import sys
import os

workspace = os.environ.get('GITHUB_WORKSPACE')

util_dir = os.path.join(workspace,
                        'ci',
                        'util')
print(f"UTIL DIR is {util_dir}")
sys.path.insert(0, util_dir)

import diff_util

data_dir = os.path.abspath(os.path.join(workspace,
                                        os.pardir))
dir_a = os.path.join(data_dir, 'truth')
dir_b = os.path.join(data_dir, 'output')

if not diff_util.compare_dir(dir_a, dir_b, debug=True):
    sys.exit(1)
