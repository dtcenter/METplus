#!/usr/bin/python
from __future__ import print_function

import unittest
import os
import config_metplus
import met_util as util
import produtil.setup
import sys

"""!This class can NOT be instantiated directly. It MUST be called from main.
    The main function operates outside of this class which sets up the METplus
    configuration object, $METPLUS_CONF. 
"""
class TestUtil(unittest.TestCase):

    def __init__(self,*args):
        super(TestUtil,self).__init__(*args)
        # These self. instance variables are effectively class level variables
        # since they are assigned to to class level variables defined in main.
        # We are doing this, as a way to make available, these values within
        # the unit test object.
        self.p = TestUtil.config_inst

    def setup(self):
        # Perform set up for each test
        pass
 
    def teardown(self):
        # Perform any cleanup after every test
        pass


    def test_round_0p5(self):

        print("\nRunning unittest: round_0p5")

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

        print("\nRunning unittest: negative_round")

        self.assertEquals(util.round_0p5(-14.1), -13.5)

    def test_mkdir_rmtree(self):

        print("\nRunning unittest: mkdir_rmtree")

        # Make sure the test directory doesn't exist
        # before starting, and remove it when testing is complete

        # Gather test parameters
        test_dir_base= self.p.getdir('TEST_DIR')

        # Don't do the this test if the TEST_DIR exists.
        # We do not want to remove a directory unless this test created it.

        # Make sure we have a clean directory
        # before trying to create the directory
        if os.path.exists(test_dir_base):
            print("Remove your TEST_DIR: %s" % test_dir_base)
            self.assertTrue(False)
        else:
            full_test_dir = os.path.join(test_dir_base, 'extract_tiles_test')
            util.mkdir_p(full_test_dir)
            self.assertTrue(os.path.exists(full_test_dir))
  
            # clean up
            util.rmtree(test_dir_base)
            self.assertFalse(os.path.exists(test_dir_base))


    def test_file_exists(self):
       
        print("\nRunning unittest: file_exists")

        # Start with a "clean" directory and non-existent file
        # expect the file_exists function to return False
        test_dir_base= self.p.getdir('TEST_DIR')
        test_file = self.p.getstr('config','TEST_FILENAME')
        full_test_file = os.path.join(test_dir_base,test_file)

        # Don't do the this test if the TEST_DIR exists.
        # We do not want to remove a directory unless this test created it.
        if os.path.exists(test_dir_base):
            print("Remove your TEST_DIR: %s" % test_dir_base)
            self.assertTrue(False)
        else:
            # Create a file, expect the file_exists function to
            # return True
            util.mkdir_p(test_dir_base)
            touch_cmd = ' '.join(["/usr/bin/touch",full_test_file])
            #print("full_test_file: %s" % full_test_file)
            os.system(touch_cmd)
            self.assertTrue(util.file_exists(full_test_file))

            # clean up
            util.rmtree(test_dir_base)
        

if __name__ == "__main__":
    # NOTE: We are using unittest in a non-conventional manner.
    #
    # main Assumes ALL arguments passed in are only for METplus configuration
    # file processing.
    # The unittest class also has its own set of command line arguments
    # but we will not use them and do not have logic in place to 
    # automatically handle using command arguments for both METplus
    # and the unittest framework.
    # 
    # So AFTER we use the conf file arguments we must pop the command 
    # lines args so the unittest class doesn't try to process the conf file
    # arguments as unittest arguments.

    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False,
                                 jobname='test_util_unittest',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='test_util_unittest')
        produtil.log.postmsg('test_util_unittest is starting')

        # Process command line args conf files, creates a conf object and final conf file.
        CONFIG_INST = config_metplus.setup()

        # This is specfic to this unit test class.
        # Set a class level variable, (a METPlus configuration object), that can be used
        # and referenced by a unit test object.
        TestUtil.config_inst = CONFIG_INST

        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG_INST.getdir('MET_BASE')

        # Remove all conf file command line arguments from sys.argv,
        # except sys.argv[0]. Removing conf args allows unittest.main() 
        # to run, else it will fail.
        for arg in range(1, len(sys.argv)):
            sys.argv.pop()

        # Workaround - to pass in command line args to unittest.main()
        # You must code them in here ....
        # For example, uncomment the next line and you will see available options.
        # sys.argv.append('-h')

        # Setting exit=False allows unittest to return and NOT sys.exit, which
        # allows commands after unittest.main() to execute.
        unittest.main(exit=False)

        # Caveate to exit=False
        # It seems if you pass in an argument  than unittest will sys.exit
        # and these line do not get executed, 
        # at least for '-h' argument .... ie. sys.argv.append('-h')

    except Exception as exc:
        produtil.log.jlogger.critical(
            'test_util_unittest failed: %s' % (str(exc),), exc_info=True)
        sys.exit(2)

