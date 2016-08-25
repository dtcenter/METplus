#!/usr/bin/python
from __future__ import print_function

import unittest
import ConfigMaster
import constants_pdef as P
import met_util as util
import extract_tiles as et
import os
import sys

class TestExtractTiles(unittest.TestCase):

    def setup(self):
        # Perform set up for each test
        pass

    def teardown(self):
        # Perform any cleanup after every test
        pass

    def test_extract_year_month(self):
        p = P.Params()
        p.init(__doc__)
        # Expect  201607 to be extracted from 20160704_12
        self.assertEqual(et.extract_year_month('20160704_12',p), '201607')

     
    def test_archive_date(self):
        p = P.Params()
        p.init(__doc__)
        # Expect  199907 to be extracted from 19990704_12
        self.assertEqual(et.extract_year_month('19990704_12',p), '199907')
    
    def test_incorrect_year(self):
        # Now provide something that doesn't have the expected format
        p = P.Params()
        p.init(__doc__)
        try:
            et.extract_year_month('39990704_12',p)
        except:
            self.assertTrue(True)


    def test_create_tile_grid_string(self):
        # Test that the tile grid string is what was
        # expected.
        p = P.Params()
        p.init(__doc__)
        logger = util.get_logger(p)
        lat = -14.1
        lon = 64.2
        expected_string= 'latlon 49.0:60:0.5 -29.0:60:0.5'
        actual_string = str(et.create_tile_grid_string(lat, lon, logger, p))
        self.assertEqual(actual_string, expected_string)

if __name__ == "__main__":
    unittest.main()

    



