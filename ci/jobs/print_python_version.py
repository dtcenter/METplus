#! /usr/bin/env python3
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.pardir,
                                                os.pardir)))

from metplus import get_python_version

print(get_python_version())
