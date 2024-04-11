"""!
Program Name: TCStatWrapper.py
Contact(s):  Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Stratify tropical cyclone data by any combination of time, column,
          statistics
History log: Initial version
Usage: TCStatWrapper.py
Parameters: None
Input Files: tc_pairs data
Output Files: subset of tc_pairs data
Condition codes: 0 for success, 1 for failure

"""

import os
import sys
from datetime import datetime

from ..util import getlist, mkdir_p, do_string_sub, ti_calculate
from . import RuntimeFreqWrapper

## @namespace TCStatWrapper
#  @brief Wrapper to the MET tool tc_stat, which is used for filtering tropical
#  cyclone pair data.

# pylint:disable=too-few-public-methods
# This class is just a wrapper to the MET tool tc_stat.  The attribute data
# is used to create the tc_stat commands and not necessarily operate on that
# attribute data.


class TCStatWrapper(RuntimeFreqWrapper):
    """! Wrapper for the MET tool, tc_stat, which is used to filter tropical
         cyclone pair data.
    """
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_PER_INIT_OR_VALID'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_PER_INIT_OR_VALID']

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_AMODEL',
        'METPLUS_BMODEL',
        'METPLUS_DESC',
        'METPLUS_STORM_ID',
        'METPLUS_BASIN',
        'METPLUS_CYCLONE',
        'METPLUS_STORM_NAME',
        'METPLUS_INIT_BEG',
        'METPLUS_INIT_END',
        'METPLUS_INIT_INC',
        'METPLUS_INIT_EXC',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_VALID_INC',
        'METPLUS_VALID_EXC',
        'METPLUS_INIT_HOUR',
        'METPLUS_VALID_HOUR',
        'METPLUS_LEAD',
        'METPLUS_LEAD_REQ',
        'METPLUS_INIT_MASK',
        'METPLUS_VALID_MASK',
        'METPLUS_LINE_TYPE',
        'METPLUS_TRACK_WATCH_WARN',
        'METPLUS_COLUMN_THRESH_NAME',
        'METPLUS_COLUMN_THRESH_VAL',
        'METPLUS_COLUMN_STR_NAME',
        'METPLUS_COLUMN_STR_VAL',
        'METPLUS_INIT_THRESH_NAME',
        'METPLUS_INIT_THRESH_VAL',
        'METPLUS_INIT_STR_NAME',
        'METPLUS_INIT_STR_VAL',
        'METPLUS_WATER_ONLY',
        'METPLUS_LANDFALL',
        'METPLUS_LANDFALL_BEG',
        'METPLUS_LANDFALL_END',
        'METPLUS_MATCH_POINTS',
        'METPLUS_JOBS',
        'METPLUS_COLUMN_STR_EXC_NAME',
        'METPLUS_COLUMN_STR_EXC_VAL',
        'METPLUS_INIT_STR_EXC_NAME',
        'METPLUS_INIT_STR_EXC_VAL',
        'METPLUS_DIAG_THRESH_NAME',
        'METPLUS_DIAG_THRESH_VAL',
        'METPLUS_INIT_DIAG_THRESH_NAME',
        'METPLUS_INIT_DIAG_THRESH_VAL',
        'METPLUS_EVENT_EQUAL',
        'METPLUS_EVENT_EQUAL_LEAD',
        'METPLUS_OUT_INIT_MASK',
        'METPLUS_OUT_VALID_MASK',
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'AMODEL',
        'BMODEL',
        'DESC',
        'STORM_ID',
        'BASIN',
        'CYCLONE',
        'STORM_NAME',
        'INIT_INCLUDE',
        'INIT_EXCLUDE',
        'VALID_INCLUDE',
        'VALID_EXCLUDE',
        'INIT_HOUR',
        'VALID_HOUR',
        'LEAD',
        'LEAD_REQ',
        'INIT_MASK',
        'VALID_MASK',
        'TRACK_WATCH_WARN',
        'COLUMN_THRESH_NAME',
        'COLUMN_THRESH_VAL',
        'COLUMN_STR_NAME',
        'COLUMN_STR_VAL',
        'INIT_THRESH_NAME',
        'INIT_THRESH_VAL',
        'INIT_STR_NAME',
        'INIT_STR_VAL',
        'JOBS',
        'INIT_BEG',
        'INIT_END',
        'VALID_BEG',
        'VALID_END',
        'LANDFALL_BEG',
        'LANDFALL_END',
        'WATER_ONLY',
        'LANDFALL',
        'MATCH_POINTS',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'tc_stat'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)

        super().__init__(config, instance=instance)

    def create_c_dict(self):
        """!  Read in and store all the values from the config file.  This
              will make it easier to reassign values while unit testing and
              make it easier when retrieving these values, especially when
              they are needed multiple times by different methods.

              @returns a dictionary of the key-value representation of options
               set in the config file.
        """
        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_TC_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        c_dict['LOOKIN_DIR'] = self.config.getdir('TC_STAT_LOOKIN_DIR', '')

        # support LOOKIN_DIR and INPUT_DIR
        if not c_dict['LOOKIN_DIR']:
            c_dict['LOOKIN_DIR'] = self.config.getdir('TC_STAT_INPUT_DIR', '')

        if not c_dict['LOOKIN_DIR']:
            self.log_error("TC_STAT_LOOKIN_DIR must be set")

        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_STAT_OUTPUT_DIR', '')
        if not c_dict['OUTPUT_DIR']:
            self.log_error("TC_STAT_OUTPUT_DIR must be set")

        # read optional output template to use for -out command line argument
        # set JOB_OUTPUT_TEMPLATE instead of OUTPUT_TEMPLATE because
        # OUTPUT_TEMPLATE is set in wrapper to handle -dump_row output
        c_dict['JOB_OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'TC_STAT_OUTPUT_TEMPLATE', '')
        )

        c_dict['JOBS'] = getlist(self.config.getraw('config',
                                                    'TC_STAT_JOB_ARGS',
                                                    ''))
        if not c_dict.get('JOBS'):
            self.log_error('No job arguments defined. '
                           'Please set TC_STAT_JOB_ARGS')

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('TCStatConfig_wrapped')

        self.set_met_config_for_environment_variables()
        # skip RuntimeFreq input file logic
        c_dict['FIND_FILES'] = False
        # force error if inputs are missing
        c_dict['ALLOW_MISSING_INPUTS'] = False
        return c_dict

    def set_met_config_for_environment_variables(self):
        """! Set c_dict dictionary entries that will be set as environment
        variables to be read by the MET config file.
            @param c_dict dictionary to add key/value pairs
        """
        self.handle_description(is_list=True)

        for config_list in [
            'amodel',
            'bmodel',
            'storm_id',
            'basin',
            'cyclone',
            'storm_name',
            'init_hour',
            'lead_req',
            'init_mask',
            'valid_mask',
            'line_type',
            'valid_hour',
            'lead',
            'track_watch_warn',
            'column_thresh_name',
            'column_thresh_val',
            'column_str_name',
            'column_str_val',
            'init_thresh_name',
            'init_thresh_val',
            'init_str_name',
            'init_str_val',
            'diag_thresh_name',
            'diag_thresh_val',
            'init_diag_thresh_name',
            'init_diag_thresh_val',
            'event_equal_lead',
        ]:
            extra_args = {}
            # remove quotation marks from *_thresh_val lists
            if 'thresh_val' in config_list:
                extra_args['remove_quotes'] = True
            self.add_met_config(name=config_list, data_type='list',
                                extra_args=extra_args)

        for iv_list in ['INIT', 'VALID']:
            self.add_met_config(name=f'{iv_list.lower()}_inc',
                                data_type='list',
                                metplus_configs=[f'TC_STAT_{iv_list}_INC',
                                                 f'TC_STAT_{iv_list}_INCLUDE'])
            self.add_met_config(name=f'{iv_list.lower()}_exc',
                                data_type='list',
                                metplus_configs=[f'TC_STAT_{iv_list}_EXC',
                                                 f'TC_STAT_{iv_list}_EXCLUDE'])

        for config_str in [
            'INIT_BEG',
            'INIT_END',
            'VALID_BEG',
            'VALID_END',
            'LANDFALL_BEG',
            'LANDFALL_END',
            'OUT_INIT_MASK',
            'OUT_VALID_MASK',
        ]:
            self.add_met_config(name=config_str.lower(), data_type='string',
                                metplus_configs=[f'TC_STAT_{config_str}',
                                                 config_str])

        for config_bool in [
            'water_only',
            'landfall',
            'match_points',
            'event_equal',
        ]:

            self.add_met_config(name=config_bool, data_type='bool')

        self.add_met_config(name='column_str_exc_name', data_type='list',
                            metplus_configs=['TC_STAT_COLUMN_STR_EXC_NAME',
                                             'TC_STAT_COLUMN_STR_EXCLUDE_NAME',
                                             ])
        self.add_met_config(name='column_str_exc_val', data_type='list',
                            metplus_configs=['TC_STAT_COLUMN_STR_EXC_VAL',
                                             'TC_STAT_COLUMN_STR_EXCLUDE_VAL',
                                             ])
        self.add_met_config(name='init_str_exc_name', data_type='list',
                            metplus_configs=['TC_STAT_INIT_STR_EXC_NAME',
                                             'TC_STAT_INIT_STR_EXCLUDE_NAME',
                                             ])
        self.add_met_config(name='init_str_exc_val', data_type='list',
                            metplus_configs=['TC_STAT_INIT_STR_EXC_VAL',
                                             'TC_STAT_INIT_STR_EXCLUDE_VAL',
                                             ])

    def run_at_time_once(self, input_dict=None):
        """! Builds the call to the MET tool TC-STAT for all requested
             initialization times (init or valid).  Called from run_metplus
        """
        self.logger.info('Starting tc_stat_wrapper...')

        time_info = None
        if input_dict:
            time_info = ti_calculate(input_dict)

        if not self.handle_jobs(time_info):
            return None

        # handle -out file if set
        if not self.handle_out_file(time_info):
            return None

        self.set_environment_variables(time_info)

        return self.build()

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """

        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']}"

        cmd += f" -lookin {self.c_dict['LOOKIN_DIR']}"

        cmd += f" -config {self.c_dict.get('CONFIG_FILE')}"

        # add output path if requested
        if self.c_dict['OUTPUT_TEMPLATE']:
            cmd += f' -out {self.get_output_path()}'

        return cmd

    def handle_jobs(self, time_info):
        """! Loop through job list found in c_dict key JOBS,
         create parent directory for -dump_row path if it is set,
         and format jobs string to pass to MET config file
         @param time_info time dictionary used to fill in filename
          template tags if used
         @returns formatted jobs string as jobs = ["job1", "job2"]; or None if
          command should be skipped
        """
        formatted_jobs = []
        for job in self.c_dict.get('JOBS'):
            # if time info is available, fill in filename template tags
            subbed_job = do_string_sub(job, **time_info) if time_info else job
            formatted_jobs.append(subbed_job.strip())

            # create parent directory of output file
            if not self._create_job_out_dirs(subbed_job, time_info):
                return None

        job_list_string = '","'.join(formatted_jobs)
        job_list_string = f'jobs = ["{job_list_string}"];'

        # set environment variable for MET config file
        self.env_var_dict['METPLUS_JOBS'] = job_list_string

        return job_list_string

    def _create_job_out_dirs(self, job_args, time_info):
        """!Create output directories for output files specified by job args
        like -dump_row and -out_stat to prevent the command from failing.

        @param job_args list of job arguments to parse
        @param time_info time dictionary used to fill in filename
          template tags if used
        @returns False if something went wrong trying to create directories or
        True if everything went smoothly.
        """
        split_job = job_args.split(' ')
        for out_type in ('-dump_row', '-out_stat'):
            # continue if job arg that writes a file is not found in job args
            if out_type not in split_job:
                continue

            # if job arg is found, create parent directory of output file
            index = split_job.index(out_type) + 1
            filepath = split_job[index]
            self.c_dict['OUTPUT_TEMPLATE'] = filepath
            if not self.find_and_check_output_file(time_info):
                return False

        return True

    def handle_out_file(self, time_info):
        """! If output template is set,
        """
        # clear output template that may have been set for -dump_row
        self.c_dict['OUTPUT_TEMPLATE'] = None

        if not self.c_dict['JOB_OUTPUT_TEMPLATE']:
            return True

        self.c_dict['OUTPUT_TEMPLATE'] = self.c_dict['JOB_OUTPUT_TEMPLATE']

        if not self.find_and_check_output_file(time_info):
            return False

        return True
