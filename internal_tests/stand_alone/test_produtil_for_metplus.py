#!/usr/bin/env python

from __future__ import print_function
import sys
import logging
import produtil.setup
import config_metplus


class TestProdutilForMETplus:
    def __init__(self):
        # Setup
        produtil.setup.setup(send_dbn=False, jobname='TestProdutilForMETplus')
        self.config = config_metplus.setup()

        # Create Logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create Handler for logging the data to a file
        logger_handler = logging.FileHandler('/tmp/produtil_for_METplus.log')
        logger_handler.setLevel(logging.DEBUG)

        # Create a Formatter to the Handler and add it to the Handler, then add the Handler to the Logger
        logger_formatter = logging.Formatter('%(asctime)s|%(name)s: %(message)s')
        logger_handler.setFormatter(logger_formatter)
        self.logger.addHandler(logger_handler)
        log_level_name = logging.getLevelName(self.logger.getEffectiveLevel())
        self.logger.debug('Logger configured at level: ' + log_level_name)

    def run_all_tests(self):
        # Invokes all tests
        self.logger.info('Running all tests...')
        self.test_conf()
        self.test_get_expected_number_of_sections()
        self.test_get_all_sections()
        self.test_get_expected_num_items_for_dir()
        self.test_get_all_items_for_dir()
        self.test_get_option_value_for_dir()
        self.test_config_raw()

    def run_selected_tests(self):
        # Invoke only those tests that you wish to run...
        self.logger.info('Running subset of tests...')
        self.test_conf()
        self.test_get_expected_number_of_sections()
        self.test_get_all_sections()

    def test_conf(self):
        # Obvious test, since we won't get here if no config object is returned from the initialization of this test
        # class...
        self.logger.debug('Running test_conf...')

        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.
        cur_function = sys._getframe().f_code.co_name
        fail_msg = cur_function + ' |FAIL: produtil config object NOT created'
        pass_msg = cur_function + ' |PASS: Valid produtil config object created'
        try:
            assert self.config, fail_msg
        except AssertionError:
            # Fail, since we might run this in a workflow manager, do not
            # allow an exception to be raised
            self.logger.info(fail_msg)
            return
        else:
            # Success
            self.logger.info(pass_msg)

    def test_get_expected_number_of_sections(self):
        # Verify that all sections in our corresponding test configuration file were
        # retrieved by produtil code.
        self.logger.debug('Running test_get_expected_number_of_sections...')

        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.
        cur_function = sys._getframe().f_code.co_name
        fail_msg = cur_function + ' |FAIL: Mismatch in the number of expected and retrieved sections'\
                                  ' from the config file.'
        pass_msg = cur_function + ' |PASS: Matching number of expected and retrieved sections from the config file.'
        expected_sections = ['dir', 'config', 'exe', 'filename_templates']
        retrieved_sections_size = len(self.config.sections())
        expected_sections_size = len(expected_sections)
        try:
            assert expected_sections_size == retrieved_sections_size, fail_msg
        except AssertionError:
            # Log failure and ignore exception since we may be running this in a workflow manager.
            self.logger.info(fail_msg)
        else:
            # Check if subsequent expected_section is in the retrieved_sections list.
            self.logger.info(pass_msg)

    def test_get_all_sections(self):
        # Verify that all sections in our corresponding test configuration file were
        # retrieved by produtil code.
        self.logger.debug('Running test_get_all_sections...')

        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.
        cur_function = sys._getframe().f_code.co_name
        fail_msg = cur_function + ' |FAIL: Not all expected sections were retrieved from the config file.'
        pass_msg = cur_function + ' |PASS: All expected sections were retrieved from the config file.'
        expected_sections = ['dir', 'config', 'exe', 'filename_templates']
        retrieved_sections = self.config.sections()
        for expected_section in expected_sections:
            try:
                assert expected_section in retrieved_sections, fail_msg
            except AssertionError:
                # Don't allow this exception to be raised up the call stack, we might be running these tests via
                # a workflow manager.
                self.logger.info(fail_msg)
                return

        # If we get to this point, we retrieved all the expected sections.
        self.logger.info(pass_msg)

    def test_get_expected_num_items_for_dir(self):
        # Verify that the expected number of items are retrieved from the dir section of our test config file.
        self.logger.debug('Running test_get_expected_num_items_for_dir')

        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.
        cur_function = sys._getframe().f_code.co_name
        fail_msg = cur_function + ' |FAIL: Mismatch in number of retrieved vs expected items from the [dir]'\
                                  ' section of all config files.'
        pass_msg = cur_function + ' |PASS: Same number of expected and retrieved items were retrieved from the [dir]'\
                                  ' section of all config files.'
        section_of_interest = 'dir'
        retrieved_items = self.config.items(section_of_interest)

        # Expected items from the [dir] section of all MET+ config files.
        expected_items = ['PROJ_DIR', 'METPLUS_BASE', 'MET_BASE', 'MET_INSTALL_DIR', 'OUTPUT_BASE', 'TMP_DIR',
                          'MODEL_DATA_DIR', 'PARM_BASE', 'LOG_DIR', 'TEST_DIR']
        # expected_items = ['PROJ_DIR']
        try:
            assert len(retrieved_items) == len(expected_items), fail_msg
        except AssertionError:
            self.logger.info(fail_msg)
        else:
            self.logger.info(pass_msg)

    def test_get_all_items_for_dir(self):
        # Verify that all the items are correctly retrieved from the dir section of our test config file.
        self.logger.debug('Running test_get_expected_num_items_for_dir')

        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.
        cur_function = sys._getframe().f_code.co_name
        fail_msg = cur_function + ' |FAIL: Mismatch in retrieved vs expected items from the [dir] section'\
                                  ' of all config files.'
        pass_msg = cur_function + ' |PASS: The same expected and retrieved items were retrieved from the [dir]'\
                                  ' section of all config files.'
        section_of_interest = 'dir'
        retrieved_items = self.config.items(section_of_interest)

        # Expected items from the [dir] section of MET+ config files.
        expected_items = ['PROJ_DIR', 'METPLUS_BASE', 'MET_BASE', 'MET_INSTALL_DIR', 'OUTPUT_BASE', 'TMP_DIR',
                          'MODEL_DATA_DIR', 'PARM_BASE', 'LOG_DIR', 'TEST_DIR']
        for retrieved_item in retrieved_items:
            try:
                assert retrieved_item[0] in expected_items, fail_msg
            except AssertionError:
                self.logger.info(fail_msg)
                return

        # If we get here, all expected items were retrieved
        self.logger.info(pass_msg)

    def test_get_option_value_for_dir(self):
        # Verify that the option,value pair for certain items are correctly retrieved from the [dir] section of our
        # test config file.  Check the TEST_DIR and MODEL_DATA_DIR
        self.logger.debug('Running test_get_option_value_for_dir')

        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.
        cur_function = sys._getframe().f_code.co_name
        fail_msg = cur_function + ' |FAIL: No matching value for corresponding option from select item in [dir]'\
                                  ' section of all MET+ config files.'
        fail_msg2 = cur_function + ' |FAIL: Mismatch in number of expected and retrieved items in the [dir] section'\
                                   ' of all MET+ config files.'
        pass_msg = cur_function + ' |PASS: Matching values found for corresponding option from the [dir] section'\
                                  ' of all MET+ config files.'
        section_of_interest = 'dir'
        retrieved_items = self.config.items(section_of_interest)
        # Expected items from the [dir] section of all MET+ config files.
        expected_items = {'PROJ_DIR': '/tmp', 'METPLUS_BASE': '/home/some_user/METplus',
                          'MET_BASE': '/usr/local/met-6.1', 'MET_INSTALL_DIR': '/usr/local/met-6.1',
                          'OUTPUT_BASE': '/tmp/output_base', 'TMP_DIR': '/tmp',
                          'MODEL_DATA_DIR': '/tmp/model_data_dir', 'PARM_BASE': '/home/some_user/METplus/parm',
                          'LOG_DIR': '/log_dir', 'TEST_DIR': '/usr/local/met-6.1'}

        for retrieved_item in retrieved_items:
                if len(retrieved_items) == len(expected_items):
                    retrieved_option = retrieved_item[0]
                    # Retrieve the value for each option
                    try:
                        assert expected_items[retrieved_option] == retrieved_item[1], fail_msg
                    except AssertionError:
                        self.logger.info(fail_msg)
                        return

                else:
                    self.logger.info(fail_msg2)
        # If we get here, we found expected matches for values corresponding to the options in the [dir] section of all
        # MET+ config files.
        self.logger.info(pass_msg)

    def test_config_raw(self):
        # Verify that the raw value in the [config] section is correctly retrieved from produtil config.py
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.
        cur_function = sys._getframe().f_code.co_name
        fail_msg = cur_function + ' |FAIL:  Retrieved raw value is not what was expected.'
        pass_msg = cur_function + ' |PASS:  Correctly retrieved raw value.'
        section_of_interest = 'config'
        expected_raw = 'GRIB_lvl_val1 = 101'
        retrieved_raw = self.config.getraw(section_of_interest, 'TEST_CONFIG_RAW')
        try:
            assert retrieved_raw == expected_raw, fail_msg
        except AssertionError:
            self.logger.info(fail_msg)
            return
        else:
            self.logger.info(pass_msg)


if __name__ == "__main__":
    mpp = TestProdutilForMETplus()
    mpp.run_all_tests()
