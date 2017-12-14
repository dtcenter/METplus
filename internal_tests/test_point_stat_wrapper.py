#!/usr/bin/env python

from __future__ import print_function

import unittest
import os
import config_metplus
from tc_pairs_wrapper import TcPairsWrapper
import csv
import re
import shutil
import met_util as util
import produtil.setup
import sys

#
# These are tests (not necessarily unit tests) for test-driven design for the
# MET Point-Stat Wrapper, PointStatWrapper.py
#


class TestPointStatWrapper(unittest.TestCase):
    def __init__(self, *args):
        pass

    def setUp(self):
        pass

    def test_read_use_case_config(self):
        self.assertFalse()


if __name__ == "__main__":
    #unittest.main(exit=False)
    unittest.main()
