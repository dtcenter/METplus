#!/usr/bin/env python

"""
Program Name: compare_gridded_wrapper.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os
import util.met_util as util
from command_builder import CommandBuilder
import util.time_util
import string_template_substitution as sts

'''!@namespace CompareGriddedWrapper
@brief Common functionality to wrap similar MET applications
that compare gridded data
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
'''

class CompareGriddedWrapper(CommandBuilder):
    """!Common functionality to wrap similar MET applications
that reformat gridded data
    """

    def __init__(self, config, logger):
        super().__init__(config, logger)

    def create_c_dict(self):
        """!Create dictionary from config items to be used in the wrapper
            Allows developer to reference config items without having to know
            the type and consolidates config get calls so it is easier to see
            which config variables are used in the wrapper"""
        c_dict = super().create_c_dict()
        c_dict['MODEL'] = self.config.getstr('config', 'MODEL', 'FCST')
        c_dict['OBTYPE'] = self.config.getstr('config', 'OBTYPE', 'OBS')
        c_dict['CONFIG_DIR'] = self.config.getdir('CONFIG_DIR', '')
        # INPUT_BASE is not required unless it is referenced in a config file
        # it is used in the use case config files. Don't error if it is not set
        # to a value that contains /path/to
        c_dict['INPUT_BASE'] = self.config.getdir_nocheck('INPUT_BASE', '')
        c_dict['FCST_IS_PROB'] = self.config.getbool('config', 'FCST_IS_PROB', False)
        c_dict['OBS_IS_PROB'] = self.config.getbool('config', 'OBS_IS_PROB', False)

        c_dict['FCST_PROB_THRESH'] = None
        c_dict['OBS_PROB_THRESH'] = None

        c_dict['ALLOW_MULTIPLE_FILES'] = False
        c_dict['NEIGHBORHOOD_WIDTH'] = ''
        c_dict['NEIGHBORHOOD_SHAPE'] = ''
        c_dict['VERIFICATION_MASK_TEMPLATE'] = ''
        c_dict['VERIFICATION_MASK'] = ''
        c_dict['CLIMO_INPUT_DIR'] = ''
        c_dict['CLIMO_INPUT_TEMPLATE'] = ''
        c_dict['CLIMO_FILE'] = None

        return c_dict

    def handle_climo(self, time_info):
        if self.c_dict['CLIMO_INPUT_TEMPLATE'] != '':
            template = self.c_dict['CLIMO_INPUT_TEMPLATE']
            climo_file = sts.StringSub(self.logger,
                                       template,
                                       **time_info).do_string_sub()
            climo_path = os.path.join(self.c_dict['CLIMO_INPUT_DIR'], climo_file)
            self.logger.debug(f"Looking for climatology file {climo_path}")
            self.c_dict['CLIMO_FILE'] = util.preprocess_file(climo_path,
                                                             '',
                                                             self.config)

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function loops
              over the list of forecast leads and runs the application for each.
              Args:
                @param input_dict dictionary containing time information
        """

        # loop of forecast leads and process each
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            # set current lead time config and environment variables
            self.config.set('config', 'CURRENT_LEAD_TIME', lead)
            os.environ['METPLUS_CURRENT_LEAD_TIME'] = str(lead)
            time_info = time_util.ti_calculate(input_dict)

            self.logger.info("Processing forecast lead {}".format(time_info['lead_string']))

            if util.skip_time(time_info, self.config):
                self.logger.debug('Skipping run time')
                continue

            # Run for given init/valid time and forecast lead combination
            self.run_at_time_once(time_info)

    def run_at_time_once(self, time_info):
        """! Build MET command for a given init/valid time and forecast lead combination
              Args:
                @param time_info dictionary containing timing information
        """

        # get verification mask if available
        self.get_verification_mask(time_info)

        self.c_dict['VAR_LIST'] = util.parse_var_list(self.config, time_info)

        self.handle_climo(time_info)

        if self.c_dict['ONCE_PER_FIELD']:
            # loop over all fields and levels (and probability thresholds) and
            # call the app once for each
            for var_info in self.c_dict['VAR_LIST']:
                self.clear()
                self.c_dict['CURRENT_VAR_INFO'] = var_info
                self.run_at_time_one_field(time_info, var_info)
        else:
            # loop over all variables and all them to the field list, then call the app once
            self.clear()
            self.run_at_time_all_fields(time_info)

    def run_at_time_one_field(self, time_info, var_info):
        """! Build MET command for a single field for a given
             init/valid time and forecast lead combination
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
        """
        # get model to compare, return None if not found
        model_path = self.find_model(time_info, var_info)
        if model_path is None:
            return

        self.infiles.append(model_path)

        # get observation to compare, return None if not found
        obs_path = self.find_obs(time_info, var_info)
        if obs_path is None:
            return

        self.infiles.append(obs_path)

        # get field info field a single field to pass to the MET config file
        fcst_field_list = self.get_field_info(v_level=var_info['fcst_level'],
                                              v_thresh=var_info['fcst_thresh'],
                                              v_name=var_info['fcst_name'],
                                              v_extra=var_info['fcst_extra'],
                                              d_type='FCST')

        obs_field_list = self.get_field_info(v_level=var_info['obs_level'],
                                             v_thresh=var_info['obs_thresh'],
                                             v_name=var_info['obs_name'],
                                             v_extra=var_info['obs_extra'],
                                             d_type='OBS')

        if fcst_field_list is None or obs_field_list is None:
            return

        fcst_fields = ','.join(fcst_field_list)
        obs_fields = ','.join(obs_field_list)

        self.process_fields(time_info, fcst_fields, obs_fields)

    def run_at_time_all_fields(self, time_info):
        """! Build MET command for all of the field/level combinations for a given
             init/valid time and forecast lead combination
              Args:
                @param time_info dictionary containing timing information
        """
        # get model from first var to compare
        model_path = self.find_model(time_info, self.c_dict['VAR_LIST'][0])
        if model_path is None:
            return

        self.infiles.append(model_path)

        # get observation to from first var compare
        obs_path = self.find_obs(time_info, self.c_dict['VAR_LIST'][0])
        if obs_path is None:
            return

        self.infiles.append(obs_path)

        fcst_field_list = []
        obs_field_list = []
        for var_info in self.c_dict['VAR_LIST']:
            next_fcst = self.get_field_info(v_level=var_info['fcst_level'],
                                            v_thresh=var_info['fcst_thresh'],
                                            v_name=var_info['fcst_name'],
                                            v_extra=var_info['fcst_extra'],
                                            d_type='FCST')
            next_obs = self.get_field_info(v_level=var_info['obs_level'],
                                           v_thresh=var_info['obs_thresh'],
                                           v_name=var_info['obs_name'],
                                           v_extra=var_info['obs_extra'],
                                           d_type='OBS')

            if next_fcst is None or next_obs is None:
                return

            fcst_field_list.extend(next_fcst)
            obs_field_list.extend(next_obs)

        fcst_field = ','.join(fcst_field_list)
        obs_field = ','.join(obs_field_list)

        self.process_fields(time_info, fcst_field, obs_field)

    def get_field_info(self, v_name, v_level, v_thresh, v_extra, d_type):
        """! Format field information into format expected by MET config file
              Args:
                @param v_level level of data to extract
                @param v_thresh threshold value to use in comparison
                @param v_name name of field to process
                @param v_extra additional field information to add if available
                @param d_type type of data to find (FCST or OBS)
                @rtype string
                @return Returns formatted field information
        """
        # separate character from beginning of numeric level value if applicable
        _, level = util.split_level(v_level)

        # list to hold field information
        fields = []

        # get cat thresholds if available
        cat_thresh = ""
        threshs = [None]
        if len(v_thresh) != 0:
            threshs = v_thresh
            cat_thresh = "cat_thresh=[ " + ','.join(threshs) + " ];"

        # if neither input is probabilistic, add all cat thresholds to same field info item
        if not self.c_dict['FCST_IS_PROB'] and not self.c_dict['OBS_IS_PROB']:

            # if pcp_combine was run, use name_level, (*,*) format
            # if not, use user defined name/level combination
            if self.config.getbool('config', d_type + '_PCP_COMBINE_RUN', False):
                field = "{ name=\"" + v_name + "_" + level + \
                        "\"; level=\"(*,*)\";"
            else:
                field = "{ name=\"" + v_name + "\";"

                # add level if it is set
                if v_level:
                    field += " level=\"" +  v_level + "\";"

            # add threshold if it is set
            if cat_thresh:
                field += ' ' + cat_thresh

            # add extra info if it is set
            if v_extra:
                field += ' ' + v_extra

            field += ' }'
            fields.append(field)

        # if either input is probabilistic, create separate item for each threshold
        else:

            # if input currently being processed if probabilistic, format accordingly
            if self.c_dict[d_type + '_IS_PROB']:
                # if probabilistic data for either fcst or obs, thresholds are required
                # to be specified or no field items will be created. Create a field dict
                # item for each threshold value
                for thresh in threshs:
                    # if utilizing python embedding for prob input, just set the
                    # field name to the call to the script
                    if util.is_python_script(v_name):
                        field = "{ name=\"" + v_name + "\"; prob=TRUE;"
                    elif self.c_dict[d_type + '_INPUT_DATATYPE'] == 'NETCDF':
                        field = "{ name=\"" + v_name + "\";"
                        if v_level:
                            field += " level=\"" +  v_level + "\";"
                        field += " prob=TRUE;"
                    else:
                        # a threshold value is required for GRIB prob DICT data
                        if thresh is None:
                            self.logger.error('No threshold was specified for probabilistic '
                                              'forecast GRIB data')
                            return None

                        thresh_str = ""
                        comparison = util.get_comparison_from_threshold(thresh)
                        number = util.get_number_from_threshold(thresh)
                        if comparison in ["gt", "ge", ">", ">=", "==", "eq"]:
                            thresh_str += "thresh_lo=" + str(number) + "; "
                        if comparison in ["lt", "le", "<", "<=", "==", "eq"]:
                            thresh_str += "thresh_hi=" + str(number) + "; "

                        field = "{ name=\"PROB\"; level=\"" + v_level + \
                                "\"; prob={ name=\"" + v_name + \
                                "\"; " + thresh_str + "}"

                    # add probabilistic cat thresh if different from default ==0.1
                    prob_cat_thresh = self.c_dict[d_type + '_PROB_THRESH']
                    if prob_cat_thresh is not None:
                        field += " cat_thresh=[" + prob_cat_thresh + "];"

                    if v_extra:
                        field += ' ' + v_extra

                    field += ' }'
                    fields.append(field)
            else:
                # if input being processed is not probabilistic but the other input is
                for thresh in threshs:
                    # if pcp_combine was run, use name_level, (*,*) format
                    # if not, use user defined name/level combination
                    if self.config.getbool('config', d_type + '_PCP_COMBINE_RUN', False):
                        field = "{ name=\"" + v_name + "_" + level + \
                                "\"; level=\"(*,*)\";"
                    else:
                        field = "{ name=\"" + v_name + "\";"
                        if v_level:
                            field += " level=\"" + v_level + "\";"

                    if thresh is not None:
                        field += " cat_thresh=[ " + str(thresh) + " ];"

                    if v_extra:
                        field += ' ' + v_extra

                    field += ' }'
                    fields.append(field)

        # return list of field dictionary items
        return fields

    def set_environment_variables(self, fcst_field, obs_field, time_info):
        """!Set environment variables that are referenced by the MET config file"""
        # list of fields to print to log
        print_list = ["MODEL", "FCST_VAR", "OBS_VAR",
                      "LEVEL", "OBTYPE", "CONFIG_DIR",
                      "FCST_FIELD", "OBS_FIELD",
                      "INPUT_BASE", "MET_VALID_HHMM",
                      "CLIMO_FILE", "FCST_TIME"]

        var_info = self.c_dict['VAR_LIST'][0]
        if 'CURRENT_VAR_INFO' in self.c_dict.keys():
            var_info = self.c_dict['CURRENT_VAR_INFO']

        # set environment variables needed for MET application
        self.add_env_var("MODEL", self.c_dict['MODEL'])
        self.add_env_var("OBTYPE", self.c_dict['OBTYPE'])
        self.add_env_var("FCST_VAR", var_info['fcst_name'])
        self.add_env_var("OBS_VAR", var_info['obs_name'])
        self.add_env_var("LEVEL", var_info['fcst_level'])
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)
        self.add_env_var("CONFIG_DIR", self.c_dict['CONFIG_DIR'])
        if self.c_dict['CLIMO_FILE']:
             self.add_env_var("CLIMO_FILE", self.c_dict['CLIMO_FILE'])
        else:
            self.add_env_var("CLIMO_FILE", '')
        # MET_VALID_HHMM should no longer be used and should be replaced with
        # CLIMO_FILE in the GridStat config file. Leaving the variable in
        # the environment so that people using older config files will still
        # be able to run. The value is actually month/day, not HHMM
        self.add_env_var("MET_VALID_HHMM", time_info['valid_fmt'][4:8])
        self.add_env_var("FCST_TIME", str(time_info['lead_hours']).zfill(3))
        self.add_env_var("INPUT_BASE", self.c_dict["INPUT_BASE"])

        # add additional env vars if they are specified
        if self.c_dict['NEIGHBORHOOD_WIDTH'] != '':
            self.add_env_var('NEIGHBORHOOD_WIDTH',
                             self.c_dict['NEIGHBORHOOD_WIDTH'])
            print_list.append('NEIGHBORHOOD_WIDTH')

        if self.c_dict['NEIGHBORHOOD_SHAPE'] != '':
            self.add_env_var('NEIGHBORHOOD_SHAPE',
                             self.c_dict['NEIGHBORHOOD_SHAPE'])
            print_list.append('NEIGHBORHOOD_SHAPE')

        if self.c_dict['VERIFICATION_MASK'] != '':
            self.add_env_var('VERIF_MASK',
                             self.c_dict['VERIFICATION_MASK'])
            print_list.append('VERIF_MASK')

        # set user environment variables
        self.set_user_environment(time_info)

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for item in print_list:
            self.print_env_item(item)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)

    def process_fields(self, time_info, fcst_field, obs_field, ens_field=None):
        """! Set and print environment variables, then build/run MET command
              Args:
                @param time_info dictionary with time information
                @param fcst_field field information formatted for MET config file
                @param obs_field field information formatted for MET config file
                @param ens_field field information formatted for MET config file
                only used for ensemble_stat
        """
        # set config file since command is reset after each run
        self.param = self.c_dict['CONFIG_FILE']

        # set up output dir with time info
        self.create_and_set_output_dir(time_info)

        # set environment variables needed by MET config file
        self.set_environment_variables(fcst_field, obs_field, time_info)

        # check if METplus can generate the command successfully
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return

        # run the MET command
        self.build()

    def create_and_set_output_dir(self, time_info):
        """! Builds the full output dir path with valid or init time
              Creates output directory if it doesn't already exist
              Args:
                @param time_info dictionary with time information
        """
        out_dir = self.c_dict['OUTPUT_DIR']

        # use output template if it is set
        # if output template is not set, do not add any extra directories to path
        out_template_name = '{}_OUTPUT_TEMPLATE'.format(self.app_name.upper())
        if self.config.has_option('filename_templates',
                                  out_template_name):
            template = self.config.getraw('filename_templates',
                                          out_template_name)
            # perform string substitution to get full path
            string_sub = sts.StringSub(self.logger,
                                       template,
                                       **time_info)
            extra_path = string_sub.do_string_sub()
            out_dir = os.path.join(out_dir, extra_path)

        # create full output dir if it doesn't already exist
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # set output dir for wrapper
        self.outdir = out_dir

    def get_verification_mask(self, time_info):
        """!If verification mask template is set in the config file,
            use it to find the verification mask filename"""
        self.c_dict['VERIFICATION_MASK'] = ''
        if self.c_dict['VERIFICATION_MASK_TEMPLATE'] != '':
            template = self.c_dict['VERIFICATION_MASK_TEMPLATE']
            string_sub = sts.StringSub(self.logger,
                                       template,
                                       **time_info)
            filename = string_sub.do_string_sub()
            self.c_dict['VERIFICATION_MASK'] = filename
        return

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.logger.error('No app path specified. '
                              'You must use a subclass')
            return None

        cmd = '{} -v {} '.format(self.app_path, self.c_dict['VERBOSITY'])
        for arg in self.args:
            cmd += arg + " "

        if len(self.infiles) == 0:
            self.logger.error("No input filenames specified")
            return None

        # add forecast file
        cmd += self.infiles[0] + ' '

        # add observation file
        cmd += self.infiles[1] + ' '

        if self.param == '':
            self.logger.error('Must specify config file to run MET tool')
            return None

        cmd += self.param + ' '

        if self.outdir == "":
            self.logger.error("No output directory specified")
            return None

        cmd += '-outdir {}'.format(self.outdir)
        return cmd
