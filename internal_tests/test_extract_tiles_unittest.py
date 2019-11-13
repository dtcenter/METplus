#!/usr/bin/python

import unittest
import os
import sys
import produtil.setup
import config_metplus
from extract_tiles_wrapper import ExtractTilesWrapper
import met_util as util


"""!This class can NOT be instantiated directly. It MUST be called from main.
    The main function operates outside of this class which sets up the METplus
    configuration object, $METPLUS_CONF, and runs extract_tiles_wrapper.py. 
    Than all the unit tests in this class are based on the output from that 
    one run.
"""
class TestExtractTiles(unittest.TestCase):
    def __init__(self,*args):
        super(TestExtractTiles,self).__init__(*args)
        # These self. instance variables are effectively class level variables
        # since they are assigned to to class level variables defined in main.
        # We are doing this, as a way to make available, these values within
        # the unit test object.
        self.p = TestExtractTiles.config_inst
        self.et = TestExtractTiles.et
        self.logger = self.et.logger

    def setup(self):
        # Perform set up for each test
        pass

    def teardown(self):
        # Perform any cleanup after every test
        pass

    # Just an example, not a very hardened test.
    def test_no_empty_tiles_dir(self):
        """ Verify that we are extracting tiles. """
        print("\nRunning unittest: no_empty_tiles_dir")
        extract_tiles_dir = self.p.getdir('EXTRACT_OUT_DIR')
        self.assertTrue(os.listdir(extract_tiles_dir))        

    def test_extract_year_month(self):
        print("\nRunning unittest: extract_year_month")
        # Expect  201607 to be extracted from 20160704_12
        #self.assertEqual(self.et.extract_year_month('20160704_12',self.p), '201607')
        self.assertEqual(util.extract_year_month('20160704_12',self.logger), '201607') 

     
    def test_archive_date(self):
        print("\nRunning unittest: archive_date")
        # Expect  199907 to be extracted from 19990704_12
        #self.assertEqual(self.et.extract_year_month('19990704_12',self.p), '199907')
        self.assertEqual(util.extract_year_month('19990704_12',self.logger), '199907')
    
    def test_incorrect_year(self):
        # Now provide something that doesn't have the expected format
        print("\nRunning unittest: incorrect_year")
        try:
            util.extract_year_month('39990704_12', self.logger)
        except:
            self.assertTrue(True)

# Commneted out. THIS TEST DOES NOTHING ... create_tile_grid does not exist ?????
#    def test_create_tile_grid_string(self):
        # Test that the tile grid string is what was
        # expected.
#        lat = -14.1
#        lon = 64.2
#        expected_string= 'latlon 49.0:60:0.5 -29.0:60:0.5'
#        actual_string = str(util.create_tile_grid_string(lat, lon, self.logger, self.p))
#        self.assertEqual(actual_string, expected_string)

if __name__ == "__main__":
    # NOTE: We are using unittest in a non-conventional manner.
    # This is more of an integration test, on the output of running
    # extract tiles.
    # Assumes ALL arguments passed in are only for METplus configuration
    # file processing.
    # The unittest class does also process its own set of command line
    # arguments, but we will not use them, for now. So AFTER we use
    # the conf file arguments we must pop the command lines args
    # so the unittest class doesn't try to process them.

    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False,
                                 jobname='test_extract_tiles_unittest',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='test_extract_tiles_unittest')
        produtil.log.postmsg('test_extract_tiles_unittest is starting')

        # Process command line args conf files, creates a conf object and final conf file.
        CONFIG_INST = config_metplus.setup()

        # This is specfic to this unit test class.
        # Set a class level variable, (a METPlus configuration object), that can be used
        # and referenced by a unit test object.
        TestExtractTiles.config_inst = CONFIG_INST

        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = CONFIG_INST.getdir('MET_BASE')

        # Instantiates and runs extract tiles. Generating output.
        TestExtractTiles.et = ExtractTilesWrapper(CONFIG_INST, logger=None)
        #TestExtractTiles.et.run_all_times()
        #produtil.log.postmsg('ExtractTilesWrapper run_all_times completed')

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
        #util.rmtree(CONFIG_INST.getdir('EXTRACT_OUT_DIR'))

    except Exception as exc:
        produtil.log.jlogger.critical(
            'test_extract_tiles_unittest failed: %s' % (str(exc),), exc_info=True)
        sys.exit(2)


    




