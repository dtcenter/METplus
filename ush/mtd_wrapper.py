#!/usr/bin/env python

'''
Program Name: mtd_wrapper.py
Contact(s): George McCabe
Abstract: Runs mode time domain
History Log:  Initial version
Usage: 
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division)

import os
import met_util as util
import time_util
from mode_wrapper import ModeWrapper

class MTDWrapper(ModeWrapper):

    def __init__(self, config, logger):
        super(MTDWrapper, self).__init__(config, logger)
        self.app_name = 'mtd'
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)
        self.fcst_file = None
        self.obs_file = None

    def create_c_dict(self):
        c_dict = super(ModeWrapper, self).create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_MTD_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        # set to prevent find_obs from getting multiple files within
        #  a time window. Does not refer to time series of files
        c_dict['ALLOW_MULTIPLE_FILES'] = False

        c_dict['OUTPUT_DIR'] = self.config.getdir('MTD_OUTPUT_DIR',
                                           self.config.getdir('OUTPUT_BASE'))
        c_dict['CONFIG_FILE'] = self.config.getstr('config', 'MTD_CONFIG', '')
        c_dict['MIN_VOLUME'] = self.config.getstr('config', 'MTD_MIN_VOLUME', '2000')
        c_dict['SINGLE_RUN'] = self.config.getbool('config', 'MTD_SINGLE_RUN', False)
        c_dict['SINGLE_DATA_SRC'] = self.config.getstr('config', 'MTD_SINGLE_DATA_SRC', 'FCST')

        # only read FCST conf if processing forecast data
        if not c_dict['SINGLE_RUN'] or c_dict['SINGLE_DATA_SRC'] == 'FCST':
            c_dict['FCST_IS_PROB'] = self.config.getbool('config', 'FCST_IS_PROB', False)
            c_dict['FCST_INPUT_DIR'] = \
              self.config.getdir('FCST_MTD_INPUT_DIR', c_dict['INPUT_BASE'])
            c_dict['FCST_INPUT_TEMPLATE'] = \
              self.config.getraw('filename_templates',
                                 'FCST_MTD_INPUT_TEMPLATE')
            c_dict['FCST_INPUT_DATATYPE'] = \
                self.config.getstr('config', 'FCST_MTD_INPUT_DATATYPE', '')

            if self.config.has_option('config', 'FCST_MTD_CONV_RADIUS'):
                c_dict['FCST_CONV_RADIUS'] = self.config.getstr('config', 'FCST_MTD_CONV_RADIUS')
            elif self.config.has_option('config', 'MTD_CONV_RADIUS'):
                c_dict['FCST_CONV_RADIUS'] = self.config.getstr('config', 'MTD_CONV_RADIUS')
            else:
                self.logger.error('[config] FCST_MTD_CONV_RADIUS not set in config')
                exit(1)

            if self.config.has_option('config', 'FCST_MTD_CONV_THRESH'):
                c_dict['FCST_CONV_THRESH'] = self.config.getstr('config', 'FCST_MTD_CONV_THRESH')
            elif self.config.has_option('config', 'MTD_CONV_THRESH'):
                c_dict['FCST_CONV_THRESH'] = self.config.getstr('config', 'MTD_CONV_THRESH')
            else:
                self.logger.error('[config] FCST_MTD_CONV_THRESH not set in config')
                exit(1)

            # check that values are valid
            if not util.validate_thresholds(util.getlist(c_dict['FCST_CONV_THRESH'])):
                self.logger.error('FCST_MTD_CONV_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')
                exit(1)

        # only read OBS conf if processing observation data
        if not c_dict['SINGLE_RUN'] or c_dict['SINGLE_DATA_SRC'] == 'OBS':
            c_dict['OBS_IS_PROB'] = self.config.getbool('config', 'OBS_IS_PROB', False)
            c_dict['OBS_INPUT_DIR'] = \
            self.config.getdir('OBS_MTD_INPUT_DIR', c_dict['INPUT_BASE'])
            c_dict['OBS_INPUT_TEMPLATE'] = \
              self.config.getraw('filename_templates',
                                   'OBS_MTD_INPUT_TEMPLATE')
            c_dict['OBS_INPUT_DATATYPE'] = \
                self.config.getstr('config', 'OBS_MTD_INPUT_DATATYPE', '')

            if self.config.has_option('config', 'OBS_MTD_CONV_RADIUS'):
                c_dict['OBS_CONV_RADIUS'] = self.config.getstr('config', 'OBS_MTD_CONV_RADIUS')
            elif self.config.has_option('config', 'MTD_CONV_RADIUS'):
                c_dict['OBS_CONV_RADIUS'] = self.config.getstr('config', 'MTD_CONV_RADIUS')
            else:
                self.logger.error('[config] OBS_MTD_CONV_RADIUS not set in config')
                exit(1)

            if self.config.has_option('config', 'OBS_MTD_CONV_THRESH'):
                c_dict['OBS_CONV_THRESH'] = self.config.getstr('config', 'OBS_MTD_CONV_THRESH')
            elif self.config.has_option('config', 'MTD_CONV_THRESH'):
                c_dict['OBS_CONV_THRESH'] = self.config.getstr('config', 'MTD_CONV_THRESH')
            else:
                self.logger.error('[config] OBS_MTD_CONV_THRESH not set in config')
                exit(1)

            # check that values are valid
            if not util.validate_thresholds(util.getlist(c_dict['OBS_CONV_THRESH'])):
                self.logger.error('OBS_MTD_CONV_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')
                exit(1)

        # handle window variables [FCST/OBS]_[FILE_]_WINDOW_[BEGIN/END]
        self.handle_window_variables(c_dict, 'mtd')

        return c_dict


    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function loops
              over the list of forecast leads and runs the application for each.
              Overrides run_at_time in compare_gridded_wrapper.py
              Args:
                @param input_dict dictionary containing timing information
        """        
#        max_lookback = self.c_dict['MAX_LOOKBACK']
#        file_interval = self.c_dict['FILE_INTERVAL']

        lead_seq = util.get_lead_sequence(self.config, input_dict)
        var_list = util.parse_var_list(self.config, input_dict)

        for var_info in var_list:
            if self.c_dict['SINGLE_RUN']:
                self.run_single_mode(input_dict, var_info)
                continue

            model_list = []
            obs_list = []
            # find files for each forecast lead time
            tasks = []
            for lead in lead_seq:
                input_dict['lead'] = lead
                time_info = time_util.ti_calculate(input_dict)
                tasks.append(time_info)

            for current_task in tasks:
                # call find_model/obs as needed
                model_file = self.find_model(current_task, var_info, False)
                obs_file = self.find_obs(current_task, var_info, False)
                if model_file is None and obs_file is None:
                    continue

                if model_file is None:
                    continue

                if obs_file is None:
                    continue

                model_list.append(model_file)
                obs_list.append(obs_file)

            # only check model list because obs list should have same size
            if not model_list:
                self.logger.error('Could not find any files to process')
                return

            # write ascii file with list of files to process
            input_dict['lead'] = 0
            time_info = time_util.ti_calculate(input_dict)
            model_outfile = time_info['valid_fmt'] + '_mtd_fcst_' + var_info['fcst_name'] + '.txt'
            obs_outfile = time_info['valid_fmt'] + '_mtd_obs_' + var_info['obs_name'] + '.txt'
            model_list_path = self.write_list_file(model_outfile, model_list)
            obs_list_path = self.write_list_file(obs_outfile, obs_list)

            arg_dict = {'obs_path' : obs_list_path,
                        'model_path' : model_list_path }

            self.process_fields_one_thresh(current_task, var_info, **arg_dict)


    def run_single_mode(self, input_dict, var_info):
        single_list = []

        if self.c_dict['SINGLE_DATA_SRC'] == 'OBS':
            find_method = self.find_obs
            s_name = var_info['obs_name']
            s_level = var_info['obs_level']
        else:
            find_method = self.find_model
            s_name = var_info['fcst_name']
            s_level = var_info['fcst_level']

        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead
            current_task = time_util.ti_calculate(input_dict)

            single_file = find_method(current_task, var_info)
            if single_file is None:
                continue

            single_list.append(single_file)

        if len(single_list) == 0:
            return

        # write ascii file with list of files to process
        input_dict['lead'] = 0
        time_info = time_util.ti_calculate(input_dict)
        single_outfile = time_info['valid_fmt'] + '_mtd_single_' + s_name + '.txt'
        single_list_path = self.write_list_file(single_outfile, single_list)

        arg_dict = {}
        if self.c_dict['SINGLE_DATA_SRC'] == 'OBS':
            arg_dict['obs_path'] = single_list_path
            arg_dict['model_path'] = None
        else:
            arg_dict['model_path'] = single_list_path
            arg_dict['obs_path'] = None

        self.process_fields_one_thresh(current_task, var_info, **arg_dict)


    def process_fields_one_thresh(self, time_info, var_info, model_path, obs_path):
        """! For each threshold, set up environment variables and run mode
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
                @param model_path forecast file list path
                @param obs_path observation file list path
        """
        # if no thresholds are specified, run once
        fcst_thresh_list = []
        obs_thresh_list = []
        fcst_field_list = []
        obs_field_list = []

        # if probabilistic forecast and no thresholds specified, error and skip
        if self.c_dict['FCST_IS_PROB']:
            # set thresholds for fcst and obs if prob
            fcst_thresh_list = var_info['fcst_thresh']
            obs_thresh_list = var_info['obs_thresh']

        # loop over thresholds and build field list with one thresh per item
        for fcst_thresh, obs_thresh in zip(fcst_thresh_list, obs_thresh_list):
            fcst_field = self.get_field_info(v_name=var_info['fcst_name'],
                                             v_level=var_info['fcst_level'],
                                             v_extra=var_info['fcst_extra'],
                                             v_thresh=[fcst_thresh],
                                             d_type='FCST')

            obs_field = self.get_field_info(v_name=var_info['obs_name'],
                                            v_level=var_info['obs_level'],
                                            v_extra=var_info['obs_extra'],
                                            v_thresh=[obs_thresh],
                                            d_type='OBS')

            if fcst_field is None or obs_field is None:
                return

            fcst_field_list.extend(fcst_field)
            obs_field_list.extend(obs_field)

        # loop through fields and call MTD
        for fcst_field, obs_field in zip(fcst_field_list, obs_field_list):
            self.param = self.c_dict['CONFIG_FILE']
            self.create_and_set_output_dir(time_info)

            print_list = [ 'MIN_VOLUME', 'MODEL', 'FCST_VAR', 'OBTYPE',
                           'OBS_VAR', 'LEVEL', 'CONFIG_DIR',
                           'MET_VALID_HHMM', 'FCST_FIELD', 'OBS_FIELD',
                           'FCST_CONV_RADIUS', 'FCST_CONV_THRESH',
                           'OBS_CONV_RADIUS', 'OBS_CONV_THRESH' ]
            self.add_env_var("MIN_VOLUME", self.c_dict["MIN_VOLUME"] )
            self.add_env_var("MODEL", self.c_dict['MODEL'])
            self.add_env_var("FCST_VAR", var_info['fcst_name'])
            self.add_env_var("OBTYPE", self.c_dict['OBTYPE'])
            self.add_env_var("OBS_VAR", var_info['obs_name'])
            self.add_env_var("LEVEL", util.split_level(var_info['fcst_level'])[1])
            self.add_env_var("CONFIG_DIR", self.c_dict['CONFIG_DIR'])
            self.add_env_var("MET_VALID_HHMM", time_info['valid_fmt'][4:8])

            # single mode - set fcst file, field, etc.
            if self.c_dict['SINGLE_RUN']:
                if self.c_dict['SINGLE_DATA_SRC'] == 'OBS':
                    self.set_fcst_file(obs_path)

                    self.add_env_var("FCST_FIELD", obs_field)
                    self.add_env_var("OBS_FIELD", obs_field)
                    self.add_env_var("OBS_CONV_RADIUS", self.c_dict["OBS_CONV_RADIUS"] )
                    self.add_env_var("FCST_CONV_RADIUS", self.c_dict["OBS_CONV_RADIUS"] )
                    self.add_env_var("OBS_CONV_THRESH", self.c_dict["OBS_CONV_THRESH"] )
                    self.add_env_var("FCST_CONV_THRESH", self.c_dict["OBS_CONV_THRESH"] )
                else:
                    self.set_fcst_file(model_path)

                    self.add_env_var("FCST_FIELD", fcst_field)
                    self.add_env_var("OBS_FIELD", fcst_field)
                    self.add_env_var("FCST_CONV_RADIUS", self.c_dict["FCST_CONV_RADIUS"] )
                    self.add_env_var("OBS_CONV_RADIUS", self.c_dict["FCST_CONV_RADIUS"] )
                    self.add_env_var("FCST_CONV_THRESH", self.c_dict["FCST_CONV_THRESH"] )
                    self.add_env_var("OBS_CONV_THRESH", self.c_dict["FCST_CONV_THRESH"] )
            else:
                self.set_fcst_file(model_path)
                self.set_obs_file(obs_path)
                self.add_env_var("FCST_CONV_RADIUS", self.c_dict["FCST_CONV_RADIUS"] )
                self.add_env_var("FCST_CONV_THRESH", self.c_dict["FCST_CONV_THRESH"] )
                self.add_env_var("OBS_CONV_RADIUS", self.c_dict["OBS_CONV_RADIUS"] )
                self.add_env_var("OBS_CONV_THRESH", self.c_dict["OBS_CONV_THRESH"] )
                self.add_env_var("FCST_FIELD", fcst_field)
                self.add_env_var("OBS_FIELD", obs_field)

            # set user environment variables
            self.set_user_environment(time_info)

            self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
            self.print_user_env_items()
            for l in print_list:
                self.print_env_item(l)

            self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
            self.print_env_copy(print_list)

            cmd = self.get_command()
            if cmd is None:
                self.logger.error(self.app_name + " could not generate command")
                return
            self.build()
            self.clear()


    def set_fcst_file(self, fcst_file):
        self.fcst_file = fcst_file


    def set_obs_file(self, obs_file):
        self.obs_file = obs_file


    def clear(self):
        super(MTDWrapper, self).clear()
        self.fcst_file = None
        self.obs_file = None


    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.logger.error(self.app_name + ": No app path specified. \
                              You must use a subclass")
            return None

        cmd = '{} -v {} '.format(self.app_path, self.c_dict['VERBOSITY'])

        for a in self.args:
            cmd += a + " "

        if self.c_dict['SINGLE_RUN']:
            if self.fcst_file == None:
                self.logger.error("No file path specified")
                return None
            cmd += '-single ' + self.fcst_file + ' '
        else:
            if self.fcst_file == None:
                self.logger.error("No forecast file path specified")
                return None

            if self.obs_file == None:
                self.logger.error("No observation file path specified")
                return None

            cmd += '-fcst ' + self.fcst_file + ' '
            cmd += '-obs ' + self.obs_file + ' '

        cmd += '-config ' + self.param + ' '

        if self.outdir != "":
            cmd += '-outdir {}'.format(self.outdir)

        return cmd


if __name__ == "__main__":
    util.run_stand_alone("mtd_wrapper", "MTD")
