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

import os

from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from . import MODEWrapper
from . import CompareGriddedWrapper

class MTDWrapper(MODEWrapper):

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'mtd'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)
        self.fcst_file = None
        self.obs_file = None

    def create_c_dict(self):
        c_dict = CompareGriddedWrapper.create_c_dict(self)
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_MTD_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        # set to prevent find_obs from getting multiple files within
        #  a time window. Does not refer to time series of files
        c_dict['ALLOW_MULTIPLE_FILES'] = False

        c_dict['OUTPUT_DIR'] = self.config.getdir('MTD_OUTPUT_DIR',
                                           self.config.getdir('OUTPUT_BASE'))
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'MTD_OUTPUT_TEMPLATE')
        )
        c_dict['CONFIG_FILE'] = self.config.getraw('config', 'MTD_CONFIG_FILE', '')
        c_dict['MIN_VOLUME'] = self.config.getstr('config', 'MTD_MIN_VOLUME', '2000')
        c_dict['SINGLE_RUN'] = self.config.getbool('config', 'MTD_SINGLE_RUN', False)
        c_dict['SINGLE_DATA_SRC'] = self.config.getstr('config', 'MTD_SINGLE_DATA_SRC', 'FCST')

        # only read FCST conf if processing forecast data
        if not c_dict['SINGLE_RUN'] or c_dict['SINGLE_DATA_SRC'] == 'FCST':
            c_dict['FCST_IS_PROB'] = self.config.getbool('config', 'FCST_IS_PROB', False)
            c_dict['FCST_INPUT_DIR'] = \
              self.config.getdir('FCST_MTD_INPUT_DIR', '')
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
                self.log_error('[config] FCST_MTD_CONV_RADIUS not set in config')

            if self.config.has_option('config', 'FCST_MTD_CONV_THRESH'):
                c_dict['FCST_CONV_THRESH'] = self.config.getstr('config', 'FCST_MTD_CONV_THRESH')
            elif self.config.has_option('config', 'MTD_CONV_THRESH'):
                c_dict['FCST_CONV_THRESH'] = self.config.getstr('config', 'MTD_CONV_THRESH')
            else:
                self.log_error('[config] FCST_MTD_CONV_THRESH not set in config')

            # check that values are valid
            if not util.validate_thresholds(util.getlist(c_dict['FCST_CONV_THRESH'])):
                self.log_error('FCST_MTD_CONV_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')

        # only read OBS conf if processing observation data
        if not c_dict['SINGLE_RUN'] or c_dict['SINGLE_DATA_SRC'] == 'OBS':
            c_dict['OBS_IS_PROB'] = self.config.getbool('config', 'OBS_IS_PROB', False)
            c_dict['OBS_INPUT_DIR'] = \
            self.config.getdir('OBS_MTD_INPUT_DIR', '')
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
                self.log_error('[config] OBS_MTD_CONV_RADIUS not set in config')

            if self.config.has_option('config', 'OBS_MTD_CONV_THRESH'):
                c_dict['OBS_CONV_THRESH'] = self.config.getstr('config', 'OBS_MTD_CONV_THRESH')
            elif self.config.has_option('config', 'MTD_CONV_THRESH'):
                c_dict['OBS_CONV_THRESH'] = self.config.getstr('config', 'MTD_CONV_THRESH')
            else:
                self.log_error('[config] OBS_MTD_CONV_THRESH not set in config')

            # check that values are valid
            if not util.validate_thresholds(util.getlist(c_dict['OBS_CONV_THRESH'])):
                self.log_error('OBS_MTD_CONV_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')

        # handle window variables [FCST/OBS]_[FILE_]_WINDOW_[BEGIN/END]
        self.handle_window_variables(c_dict, 'mtd')

        c_dict['REGRID_TO_GRID'] = self.config.getstr('config', 'MTD_REGRID_TO_GRID', '')

        # used to override the file type for fcst/obs if using python embedding for input
        c_dict['FCST_FILE_TYPE'] = ''
        c_dict['OBS_FILE_TYPE'] = ''

        return c_dict

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function loops
              over the list of user-defined strings and runs the application for each.
              Overrides run_at_time in compare_gridded_wrapper.py
              Args:
                @param input_dict dictionary containing timing information
        """

        if util.skip_time(input_dict, self.c_dict.get('SKIP_TIMES', {})):
            self.logger.debug('Skipping run time')
            return

        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string
            self.run_at_time_loop_string(input_dict)

    def run_at_time_loop_string(self, input_dict):
        """! Runs the MET application for a given run time. This function loops
              over the list of forecast leads and runs the application for each.
              Overrides run_at_time in compare_gridded_wrapper.py
              Args:
                @param input_dict dictionary containing timing information
        """        
#        max_lookback = self.c_dict['MAX_LOOKBACK']
#        file_interval = self.c_dict['FILE_INTERVAL']
        lead_seq = util.get_lead_sequence(self.config, input_dict)

        # if only processing a single data set (FCST or OBS) then only read that var list and process
        if self.c_dict['SINGLE_RUN']:
            var_list = util.parse_var_list(self.config, input_dict, self.c_dict['SINGLE_DATA_SRC'],
                                           met_tool=self.app_name)
            for var_info in var_list:
                self.run_single_mode(input_dict, var_info)

            return

        # if comparing FCST and OBS data, get var list from FCST/OBS or BOTH variables
        var_list = util.parse_var_list(self.config, input_dict,
                                       met_tool=self.app_name)

        # report error and exit if field info is not set
        if not var_list:
            self.log_error('No input fields were specified to MTD. You must set '
                           '[FCST/OBS]_VAR<n>_[NAME/LEVELS].')
            return None

        for var_info in var_list:

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
                model_file = self.find_model(current_task, var_info,
                                             mandatory=False)
                obs_file = self.find_obs(current_task, var_info,
                                         mandatory=False)
                if model_file is None and obs_file is None:
                    continue

                if model_file is None:
                    continue

                if obs_file is None:
                    continue

                self.logger.debug("Adding forecast file: {}".format(model_file))
                self.logger.debug("Adding observation file: {}".format(obs_file))
                model_list.append(model_file)
                obs_list.append(obs_file)

            # only check model list because obs list should have same size
            if not model_list:
                self.log_error('Could not find any files to process')
                return

            # write ascii file with list of files to process
            input_dict['lead'] = lead_seq[0]
            time_info = time_util.ti_calculate(input_dict)

            # if var name is a python embedding script, check type of python input and name file list file accordingly
            fcst_file_ext = self.check_for_python_embedding('FCST', var_info)
            obs_file_ext = self.check_for_python_embedding('OBS', var_info)
            # if check_for_python_embedding returns None, an error occurred
            if not fcst_file_ext or not obs_file_ext:
                return

            model_outfile = time_info['valid_fmt'] + '_mtd_fcst_' + fcst_file_ext + '.txt'
            obs_outfile = time_info['valid_fmt'] + '_mtd_obs_' + obs_file_ext + '.txt'
            model_list_path = self.write_list_file(model_outfile, model_list)
            obs_list_path = self.write_list_file(obs_outfile, obs_list)

            arg_dict = {'obs_path' : obs_list_path,
                        'model_path' : model_list_path }

            self.process_fields_one_thresh(time_info, var_info, **arg_dict)


    def run_single_mode(self, input_dict, var_info):
        single_list = []

        data_src = self.c_dict['SINGLE_DATA_SRC']
        if data_src == 'OBS':
            find_method = self.find_obs
        else:
            find_method = self.find_model

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
        input_dict['lead'] = lead_seq[0]
        time_info = time_util.ti_calculate(input_dict)
        file_ext = self.check_for_python_embedding(data_src, var_info)
        if not file_ext:
            return

        single_outfile = time_info['valid_fmt'] + '_mtd_single_' + file_ext + '.txt'
        single_list_path = self.write_list_file(single_outfile, single_list)

        arg_dict = {}
        if data_src == 'OBS':
            arg_dict['obs_path'] = single_list_path
            arg_dict['model_path'] = None
        else:
            arg_dict['model_path'] = single_list_path
            arg_dict['obs_path'] = None

        self.process_fields_one_thresh(time_info, var_info, **arg_dict)


    def process_fields_one_thresh(self, time_info, var_info, model_path, obs_path):
        """! For each threshold, set up environment variables and run mode
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
                @param model_path forecast file list path
                @param obs_path observation file list path
        """
        fcst_field_list = []
        obs_field_list = []

        if not self.c_dict['SINGLE_RUN'] or self.c_dict['SINGLE_DATA_SRC'] == 'FCST':
            fcst_thresh_list = var_info['fcst_thresh']

            # if probabilistic forecast and no thresholds specified, error and skip
            if self.c_dict['FCST_IS_PROB'] and not fcst_thresh_list:
                self.logger.error("Must specify thresholds for probabilistic forecast data")
                return

            # if no thresholds are specified, run once
            if not fcst_thresh_list:
                fcst_thresh_list = [""]

           # loop over thresholds and build field list with one thresh per item
            for fcst_thresh in fcst_thresh_list:
                fcst_field = self.get_field_info(v_name=var_info['fcst_name'],
                                                 v_level=var_info['fcst_level'],
                                                 v_extra=var_info['fcst_extra'],
                                                 v_thresh=[fcst_thresh],
                                                 d_type='FCST')

                if fcst_field is None:
                    self.log_error("No forecast fields found")
                    return

                fcst_field_list.extend(fcst_field)


        if not self.c_dict['SINGLE_RUN'] or self.c_dict['SINGLE_DATA_SRC'] == 'OBS':
            obs_thresh_list = var_info['obs_thresh']

            if self.c_dict['OBS_IS_PROB'] and not obs_thresh_list:
                self.logger.error("Must specify thresholds for probabilistic obs data")
                return

            # if no thresholds are specified, run once
            if not obs_thresh_list:
                obs_thresh_list = [""]

            # loop over thresholds and build field list with one thresh per item
            for obs_thresh in obs_thresh_list:
                obs_field = self.get_field_info(v_name=var_info['obs_name'],
                                                v_level=var_info['obs_level'],
                                                v_extra=var_info['obs_extra'],
                                                v_thresh=[obs_thresh],
                                                d_type='OBS')

                if obs_field is None:
                    self.log_error("No observation fields found")
                    return

                obs_field_list.extend(obs_field)

            # if FCST is not set, set it to the OBS field list so the lists are the same length
            if not fcst_field_list:
                fcst_field_list = obs_field_list

        else:
            # if OBS is not set, set it to the FCST field list so the lists are the same length
            obs_field_list = fcst_field_list


        # loop through fields and call MTD
        for fcst_field, obs_field in zip(fcst_field_list, obs_field_list):
            self.param  = do_string_sub(self.c_dict['CONFIG_FILE'],
                                        **time_info)

            self.set_current_field_config(var_info)
            self.set_environment_variables(fcst_field, obs_field, time_info)

            if not self.find_and_check_output_file(time_info,
                                                   is_directory=True):
                return

            if self.c_dict['SINGLE_RUN']:
                if self.c_dict['SINGLE_DATA_SRC'] == 'OBS':
                    self.set_fcst_file(obs_path)
                else:
                    self.set_fcst_file(model_path)
            else:
                self.set_fcst_file(model_path)
                self.set_obs_file(obs_path)

            cmd = self.get_command()
            if cmd is None:
                self.log_error(self.app_name + " could not generate command")
                return
            self.build()
            self.clear()


    def set_fcst_file(self, fcst_file):
        self.fcst_file = fcst_file


    def set_obs_file(self, obs_file):
        self.obs_file = obs_file


    def clear(self):
        super().clear()
        self.fcst_file = None
        self.obs_file = None

    def set_environment_variables(self, fcst_field, obs_field, time_info):
        self.add_env_var("MIN_VOLUME", self.c_dict["MIN_VOLUME"])
        self.add_env_var("OBTYPE", self.c_dict['OBTYPE'])
        """
        # set config variables that can be referenced in output_prefix
        self.config.set('config', 'CURRENT_FCST_NAME',
                        var_info['fcst_name'] if 'fcst_name' in var_info else '')
        self.config.set('config', 'CURRENT_FCST_LEVEL',
                        var_info['fcst_level'] if 'fcst_level' in var_info else '')
        self.config.set('config', 'CURRENT_OBS_NAME',
                        var_info['obs_name'] if 'obs_name' in var_info else '')
        self.config.set('config', 'CURRENT_OBS_LEVEL',
                        var_info['obs_level'] if 'obs_level' in var_info else '')
        """

        # single mode - set fcst file, field, etc.
        if self.c_dict['SINGLE_RUN']:
            if self.c_dict['SINGLE_DATA_SRC'] == 'OBS':
                self.add_env_var("FCST_FIELD", obs_field)
                self.add_env_var("OBS_FIELD", obs_field)
                self.add_env_var("OBS_CONV_RADIUS", self.c_dict["OBS_CONV_RADIUS"])
                self.add_env_var("FCST_CONV_RADIUS", self.c_dict["OBS_CONV_RADIUS"])
                self.add_env_var("OBS_CONV_THRESH", self.c_dict["OBS_CONV_THRESH"])
                self.add_env_var("FCST_CONV_THRESH", self.c_dict["OBS_CONV_THRESH"])
            else:
                self.add_env_var("FCST_FIELD", fcst_field)
                self.add_env_var("OBS_FIELD", fcst_field)
                self.add_env_var("FCST_CONV_RADIUS", self.c_dict["FCST_CONV_RADIUS"])
                self.add_env_var("OBS_CONV_RADIUS", self.c_dict["FCST_CONV_RADIUS"])
                self.add_env_var("FCST_CONV_THRESH", self.c_dict["FCST_CONV_THRESH"])
                self.add_env_var("OBS_CONV_THRESH", self.c_dict["FCST_CONV_THRESH"])
        else:
            self.add_env_var("FCST_CONV_RADIUS", self.c_dict["FCST_CONV_RADIUS"])
            self.add_env_var("FCST_CONV_THRESH", self.c_dict["FCST_CONV_THRESH"])
            self.add_env_var("OBS_CONV_RADIUS", self.c_dict["OBS_CONV_RADIUS"])
            self.add_env_var("OBS_CONV_THRESH", self.c_dict["OBS_CONV_THRESH"])
            self.add_env_var("FCST_FIELD", fcst_field)
            self.add_env_var("OBS_FIELD", obs_field)

        self.add_env_var('OUTPUT_PREFIX', self.get_output_prefix(time_info))

        self.add_env_var("FCST_FILE_TYPE", self.c_dict['FCST_FILE_TYPE'])
        self.add_env_var("OBS_FILE_TYPE", self.c_dict['OBS_FILE_TYPE'])

        CompareGriddedWrapper.set_environment_variables(self, time_info)

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.log_error(self.app_name + ": No app path specified. \
                              You must use a subclass")
            return None

        cmd = '{} -v {} '.format(self.app_path, self.c_dict['VERBOSITY'])

        for a in self.args:
            cmd += a + " "

        if self.c_dict['SINGLE_RUN']:
            if self.fcst_file == None:
                self.log_error("No file path specified")
                return None
            cmd += '-single ' + self.fcst_file + ' '
        else:
            if self.fcst_file == None:
                self.log_error("No forecast file path specified")
                return None

            if self.obs_file == None:
                self.log_error("No observation file path specified")
                return None

            cmd += '-fcst ' + self.fcst_file + ' '
            cmd += '-obs ' + self.obs_file + ' '

        cmd += '-config ' + self.param + ' '

        if self.outdir != "":
            cmd += '-outdir {}'.format(self.outdir)

        return cmd
