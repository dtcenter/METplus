#! /usr/bin/env python3

# Script to easily obtain minimum python version requirement
# Used in GitHub Actions (in ci/jobs/python_requirements/get_miniconda.sh)

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                os.pardir)))

from metplus import get_python_version

print(get_python_version())
