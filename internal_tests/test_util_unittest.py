#!/usr/bin/python
from __future__ import print_function

import unittest
import ConfigMaster
import constants_pdef as P
#import minna_extract_tiles_params as P
import met_util as util
import os
import sys

class TestUtil(unittest.TestCase):

    def setup(self):
        # Perform set up for each test
        pass
 
    def teardown(self):
        # Perform any cleanup after every test
        pass


    def test_round_0p5(self):
        # Verify that floats are getting correctly rounded to the
        # nearest n.5 or n.0 or (n+1).0  decimal place.
        # Test values:      3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0
        # Expected results: 3.0,3.0,3.0,3.5,3.5,3.5,3.5,3.5,4.0,4.0,4.0

        self.assertEquals(util.round_0p5(3.0) ,3.0)
        self.assertEquals(util.round_0p5(3.1) ,3.0)
        self.assertEquals(util.round_0p5(3.2) ,3.0)
        self.assertEquals(util.round_0p5(3.3) ,3.5)
        self.assertEquals(util.round_0p5(3.4) ,3.5)
        self.assertEquals(util.round_0p5(3.5) ,3.5)
        self.assertEquals(util.round_0p5(3.6) ,3.5)
        self.assertEquals(util.round_0p5(3.7) ,3.5)
        self.assertEquals(util.round_0p5(3.8) ,4.0)
        self.assertEquals(util.round_0p5(3.9) ,4.0)
        self.assertEquals(util.round_0p5(4.0) ,4.0)
      
    def test_negative_round(self):
        self.assertEquals(util.round_0p5(-14.1), -13.5)

    def test_mkdir(self):

        # Make sure the test directory doesn't exist
        # before starting, and remove it when testing is complete

        # Gather test parameters from the extract_tiles_params.py file
        p = P.Params()
        p.init(__doc__)
        rm_exe = p.opt["RM_EXE"]
        test_dir_base= p.opt["TEST_DIR"]
        rm_file = [rm_exe," ", test_dir_base]
        rm_file_cmd = ''.join(rm_file)
        

        # Make sure we have a clean directory
        # before trying to create the directory
        os.system(rm_file_cmd)
        full_test = (test_dir_base,"/","extract_tiles_test")
        full_test_dir = "".join(full_test)
        util.mkdir_p(full_test_dir)
        self.assertTrue(os.path.exists)
  
        # clean up
        clean_up = [rm_exe, " ", test_dir_base]
        clean_up_cmd = "".join(clean_up) 
        print("clean up cmd: %s", clean_up_cmd)
        os.system(clean_up_cmd)
    


    def test_file_exists(self):
        p = P.Params()
        p.init(__doc__)
        
        # Start with a "clean" directory and non-existent file
        # expect the file_exists function to return False
        rm_exe = p.opt["RM_EXE"]
        test_dir_base= p.opt["TEST_DIR"]
        rm_file = [rm_exe," ", test_dir_base]
        rm_file_cmd = ''.join(rm_file)
        test_file = p.opt["TEST_FILENAME"]
        full_test_file = test_dir_base + "/" + test_file
        self.assertFalse(util.file_exists(full_test_file))

        # Create a file, expect the file_exists function to
        # return True
        util.mkdir_p(test_dir_base)
        touch_cmd = "/usr/bin/touch full_test_file"
        print("full_test_file: %s", full_test_file)
        os.system(touch_cmd)
#        self.assertTrue(util.file_exists(full_test_file))

 
        

if __name__ == "__main__":
    unittest.main()

