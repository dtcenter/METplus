'''
Program Name: pcp_combine_wrapper.py
Contact(s): George McCabe
Abstract: Runs pcp_combine to merge multiple forecast files
History Log:  Initial version
Usage:
Parameters: None
Input Files: grib2 files
Output Files: pcp_combine files
Condition codes: 0 for success, 1 for failure
'''

import os
import datetime

from ..util import met_util as util
from ..util import time_util
from ..util import do_string_sub
from . import ReformatGriddedWrapper

'''!@namespace PCPCombineWrapper
@brief Wraps the MET tool pcp_combine to combine or divide
precipitation accumulations
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
@todo add main function to be able to run alone via command line
'''
class PCPCombineWrapper(ReformatGriddedWrapper):
    """!Wraps the MET tool pcp_combine to combine or divide
    precipitation accumulations"""

    # valid values for [FCST/OBS]_PCP_COMBINE_METHOD
    valid_run_methods = ['ADD', 'SUM', 'SUBTRACT', 'DERIVE', 'USER_DEFINED']

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'pcp_combine'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)
        self.inaddons = []
        self.method = ""
        self.pcp_dir = ""
        self.pcp_regex = ""
        self.init_time = -1
        self.valid_time = -1
        self.in_accum = -1
        self.out_accum = -1
        self.field_name = None
        self.field_level = ""
        self.output_name = ""
        self.name = ""
        self.compress = -1
        self.user_command = ''

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_PCP_COMBINE_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        fcst_run = self.config.getbool('config', 'FCST_PCP_COMBINE_RUN', False)
        obs_run = self.config.getbool('config', 'OBS_PCP_COMBINE_RUN', False)

        if not fcst_run and not obs_run:
            self.log_error("Must set either FCST_PCP_COMBINE_RUN or OBS_PCP_COMBINE_RUN")
            self.isOK = False
        else:
            if fcst_run:
                c_dict = self.set_fcst_or_obs_dict_items('FCST', c_dict)

            if obs_run:
                c_dict = self.set_fcst_or_obs_dict_items('OBS', c_dict)

        return c_dict

    def set_fcst_or_obs_dict_items(self, d_type, c_dict):
        c_dict[d_type+'_MIN_FORECAST'] = self.config.getstr('config', d_type+'_PCP_COMBINE_MIN_FORECAST', '0')
        c_dict[d_type+'_MAX_FORECAST'] = self.config.getstr('config', d_type+'_PCP_COMBINE_MAX_FORECAST', '256H')
        c_dict[d_type+'_INPUT_DATATYPE'] = self.config.getstr('config',
                                              d_type+'_PCP_COMBINE_INPUT_DATATYPE', '')
        c_dict[d_type+'_DATA_INTERVAL'] = self.config.getint('config', d_type+'_PCP_COMBINE_DATA_INTERVAL', 1)
        c_dict[d_type+'_TIMES_PER_FILE'] = self.config.getint('config', d_type+'_PCP_COMBINE_TIMES_PER_FILE', -1)
        c_dict[d_type+'_IS_DAILY_FILE'] = self.config.getbool('config', d_type+'_PCP_COMBINE_IS_DAILY_FILE', False)
        c_dict[d_type+'_ACCUMS'] = util.getlist(self.config.getraw('config', d_type+'_PCP_COMBINE_INPUT_ACCUMS', ''))
        c_dict[d_type+'_NAMES'] = util.getlist(self.config.getraw('config', d_type+'_PCP_COMBINE_INPUT_NAMES', ''))
        c_dict[d_type+'_LEVELS'] = util.getlist(self.config.getraw('config', d_type+'_PCP_COMBINE_INPUT_LEVELS', ''))
        c_dict[d_type+'_OPTIONS'] = util.getlist(self.config.getraw('config', d_type+'_PCP_COMBINE_INPUT_OPTIONS', ''))
        c_dict[d_type+'_OUTPUT_ACCUM'] = self.config.getstr('config', d_type+'_PCP_COMBINE_OUTPUT_ACCUM', '')
        c_dict[d_type+'_OUTPUT_NAME'] = self.config.getstr('config', d_type+'_PCP_COMBINE_OUTPUT_NAME', '')
        c_dict[d_type+'_INPUT_DIR'] = self.config.getdir(d_type+'_PCP_COMBINE_INPUT_DIR', '')
        c_dict[d_type+'_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                              d_type+'_PCP_COMBINE_INPUT_TEMPLATE', '')
        if not c_dict[d_type+'_INPUT_TEMPLATE']:
            self.log_error(d_type + "_PCP_COMBINE_INPUT_TEMPLATE required to run")
        c_dict[d_type+'_OUTPUT_DIR'] = self.config.getdir(d_type+'_PCP_COMBINE_OUTPUT_DIR', '')
        c_dict[d_type+'_OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                     d_type+'_PCP_COMBINE_OUTPUT_TEMPLATE')

        c_dict[d_type+'_STAT_LIST'] = \
            util.getlist(self.config.getstr('config',
                                       d_type+'_PCP_COMBINE_STAT_LIST', ''))

        run_method = \
            self.config.getstr('config', d_type+'_PCP_COMBINE_METHOD', '').upper()

        # support run method of CUSTOM, but warn and change it to USER_DEFINED
        if run_method == 'CUSTOM':
            self.logger.warning(f'{d_type}_PCP_COMBINE_RUN_METHOD should be set to USER_DEFINED. CUSTOM method is deprecated')
            run_method = 'USER_DEFINED'

        c_dict[d_type+'_RUN_METHOD'] = run_method

        c_dict[d_type+'_DERIVE_LOOKBACK'] = \
          self.config.getstr('config', d_type+'_PCP_COMBINE_DERIVE_LOOKBACK', '0')

        c_dict[d_type+'_BUCKET_INTERVAL'] = self.config.getseconds('config',
                                                                   d_type+'_PCP_COMBINE_BUCKET_INTERVAL',
                                                                   0)

        c_dict[d_type + '_CONSTANT_INIT'] = self.config.getbool('config',
                                                                d_type+'_PCP_COMBINE_CONSTANT_INIT',
                                                                False)

        # initialize custom string for tests
        c_dict['CUSTOM_STRING'] = ''

        if run_method not in self.valid_run_methods:
            self.log_error(f"Invalid value for {d_type}_PCP_COMBINE_METHOD: "
                           f"{run_method}. Valid options are "
                           f"{','.join(self.valid_run_methods)}.")
            self.isOK = False

        if run_method == 'DERIVE' and not c_dict[d_type+'_STAT_LIST']:
            self.log_error('Statistic list is empty. ' + \
              'Must set ' + d_type + '_PCP_COMBINE_STAT_LIST if running ' +\
                              'derive mode')
            self.isOK = False

        if not c_dict[d_type+'_INPUT_TEMPLATE'] and c_dict[d_type+'_RUN_METHOD'] != 'SUM':
            self.log_error(f"Must set {d_type}_PCP_COMBINE_INPUT_TEMPLATE unless using SUM method")
            self.isOK = False

        if not c_dict[d_type+'_OUTPUT_TEMPLATE']:
            self.log_error(f"Must set {d_type}_PCP_COMBINE_OUTPUT_TEMPLATE")
            self.isOK = False

        if run_method == 'DERIVE' or run_method == 'ADD':
            if not c_dict[d_type+'_ACCUMS']:
                self.log_error(f'{d_type}_PCP_COMBINE_INPUT_ACCUMS must be specified.')
                self.isOK = False

            # name list should either be empty or the same length as accum list
            if c_dict[d_type+'_NAMES'] and \
              len(c_dict[d_type+'_ACCUMS']) != len(c_dict[d_type+'_NAMES']):
                msg = f'{d_type}_PCP_COMBINE_INPUT_ACCUM_NAMES list should be ' +\
                      'either empty or the same length as ' +\
                      f'{d_type}_PCP_COMBINE_INPUT_ACCUMS list.'
                self.log_error(msg)
                self.isOK = False

            if c_dict[d_type+'_LEVELS'] and \
              len(c_dict[d_type+'_ACCUMS']) != len(c_dict[d_type+'_LEVELS']):
                msg = f'{d_type}_PCP_COMBINE_INPUT_LEVELS list should be ' +\
                      'either empty or the same length as ' +\
                      f'{d_type}_PCP_COMBINE_INPUT_ACCUMS list.'
                self.log_error(msg)
                self.isOK = False

        return c_dict

    def clear(self):
        super().clear()
        self.inaddons = []
        self.method = ""
        self.pcp_dir = ""
        self.pcp_regex = ""
        self.init_time = -1
        self.valid_time = -1
        self.in_accum = -1
        self.out_accum = -1
        self.field_name = None
        self.field_level = ""
        self.field_extra = ""
        self.output_name = ""
        self.name = ""
        self.compress = -1
        self.user_command = ''

    def add_input_file(self, filename, addon):
        self.infiles.append(filename)
        self.inaddons.append(str(addon))

    def get_dir_and_template(self, data_type, in_or_out):
        dirr = self.c_dict[data_type+'_'+in_or_out+'_DIR']
        template = self.c_dict[data_type+'_'+in_or_out+'_TEMPLATE']

        return (dirr, template)

    def getLowestForecastFile(self, valid_time, dtype, template):
        """!Find the lowest forecast hour that corresponds to the
        valid time
        Args:
          @param valid_time valid time to search
          @param dtype data type (FCST or OBS) to get filename template
          @rtype string
          @return Path to file with the lowest forecast hour"""
        out_file = None

        # search for file with lowest forecast, then loop up into you find a valid one
        min_forecast = time_util.get_seconds_from_string(self.c_dict[dtype+'_MIN_FORECAST'], 'H')
        max_forecast = time_util.get_seconds_from_string(self.c_dict[dtype+'_MAX_FORECAST'], 'H')
        smallest_input_accum = min([lev['amount'] for lev in self.c_dict['ACCUM_DICT_LIST']])

        # if smallest input accumulation is greater than an hour, search hourly
        if smallest_input_accum > 3600:
            smallest_input_accum = 3600

        min_forecast_string = time_util.ti_get_lead_string(min_forecast)
        max_forecast_string = time_util.ti_get_lead_string(max_forecast)
        smallest_input_accum_string = time_util.ti_get_lead_string(smallest_input_accum, plural=False)
        self.logger.debug(f"Looking for file with lowest forecast lead valid at {valid_time}"
                          f" between {min_forecast_string} and {max_forecast_string} using "
                          f"{smallest_input_accum_string} intervals")

        forecast_lead = min_forecast
        while forecast_lead <= max_forecast:
            input_dict = {}
            input_dict['valid'] = valid_time
            input_dict['lead_seconds'] = forecast_lead
            time_info = time_util.ti_calculate(input_dict)
            time_info['custom'] = self.c_dict['CUSTOM_STRING']
            fSts = do_string_sub(template,
                                 **time_info)
            search_file = os.path.join(self.input_dir,
                                       fSts)

            self.logger.debug(f"Looking for {search_file}")

            search_file = util.preprocess_file(search_file,
                                self.c_dict[dtype+'_INPUT_DATATYPE'],
                                               self.config)

            if search_file is not None:
                return search_file, forecast_lead
            forecast_lead += smallest_input_accum

        return None, 0

    def get_daily_file(self, time_info, accum, data_src, file_template):
        """!Pull accumulation out of file that contains a full day of data
        Args:
          @param time_info dictionary containing timing information
          @param accum accumulation to extract from file
          @param data_src type of data (FCST or OBS)
          @param file_template filename template to search
          @rtype bool
          @return True if file was added to output list, False if not"""

        data_interval = self.c_dict[data_src + '_DATA_INTERVAL']
        times_per_file = self.c_dict[data_src + '_TIMES_PER_FILE']
        search_file = None
        # loop from valid_time back to data interval * times per file
        for i in range(0, times_per_file+1):
            search_time = time_info['valid'] - datetime.timedelta(hours=(i * data_interval))
            # check if file exists
            dSts = do_string_sub(file_template,
                                 valid=search_time,
                                 custom=self.c_dict['CUSTOM_STRING'])
            search_file = os.path.join(self.input_dir,
                                       dSts)
            search_file = util.preprocess_file(search_file,
                                            self.c_dict[data_src+\
                                              '_INPUT_DATATYPE'],
                                               self.config)
            if search_file is not None:
                break

        if search_file is None:
            return False

        diff = time_info['valid'] - search_time

        # Specifying integer division // Python 3,
        # assuming that was the intent in Python 2.
        lead = int((diff.days * 24) // (data_interval))
        lead += int((diff).seconds // (data_interval*3600)) - 1
        search_time_info = { 'valid' : search_time,
                             'custom': self.c_dict['CUSTOM_STRING']}

        # get name of input level item that matches the accumulation to extract from daily file
        accum_seconds = time_util.get_seconds_from_string(accum, 'H')
        accum_dict_list = self.c_dict['ACCUM_DICT_LIST']
        fname = next((item['name'] for item in accum_dict_list if item['amount'] == accum_seconds), '-1')
        # if accumulation was not found in levels dictionary list, error and return
        if fname == '-1':
            self.log_error(f'Accumulation {accum} was not specified in the {data_src}'
                              '_PCP_COMBINE_INPUT_ACCUMS list')
            return False

        # if name was not set in the input levels list, use accumulation time in MET time format
        if fname is None:
            addon = time_util.time_string_to_met_time(accum, default_unit='S')
        else:
            fname = do_string_sub(fname, **search_time_info)
            addon = "'name=\"" + fname + "\";"

            # if name is a python script, don't set level
            if not util.is_python_script(fname):
                addon += " level=\"(" + str(lead) + ",*,*)\";"

            addon += "'"

        self.add_input_file(search_file, addon)
        return True

    def get_addon(self, accum_dict, search_accum, search_time):
        field_name = accum_dict['name']
        field_level = accum_dict['level']
        field_extra = accum_dict['extra']
        if field_name is None:
            return search_accum

        # perform string substitution on name in case it uses filename templates
        field_name = do_string_sub(field_name,
                                   valid=search_time,
                                   custom=self.c_dict['CUSTOM_STRING'])
        addon = "'name=\"" + field_name + "\";"

        if not util.is_python_script(field_name) and field_level is not None:
            addon += f" level=\"{field_level}\";"

        if field_extra:
            search_time_info = {'valid': search_time,
                                'custom': self.c_dict['CUSTOM_STRING']}

            field_extra = do_string_sub(field_extra,
                                        **search_time_info)

            field_extra = field_extra.replace('"', '\"')
            addon += f" {field_extra}"

        addon += "'"
        return addon

    def find_input_file(self, in_template, init_time, valid_time, search_accum, data_src):
        lead = 0

        if '{lead?' in in_template or ('{init?' in in_template and '{valid?' in in_template):
            if not self.c_dict[f'{data_src}_CONSTANT_INIT']:
                return self.getLowestForecastFile(valid_time, data_src, in_template)

            # set init time and lead in time dictionary if init time should be constant
            # time_util.ti_calculate cannot currently handle supplying both init and valid
            lead = (valid_time - init_time).total_seconds()
            input_dict = {'init': init_time,
                          'lead': lead}
        else:
            if self.c_dict[f'{data_src}_CONSTANT_INIT']:
                input_dict = { 'init': init_time }
            else:
                input_dict = { 'valid': valid_time }


        time_info = time_util.ti_calculate(input_dict)
        time_info['custom'] = self.c_dict['CUSTOM_STRING']
        input_file = do_string_sub(in_template,
                                   level=int(search_accum),
                                   **time_info)
        input_path = os.path.join(self.input_dir, input_file)

        return util.preprocess_file(input_path,
                                    self.c_dict[data_src+'_INPUT_DATATYPE'],
                                    self.config), lead

    def get_template_accum(self, accum_dict, search_time, lead, data_src):
        # apply string substitution to accum amount
        search_time_dict = {'valid': search_time, 'lead_seconds': lead}
        search_time_info = time_util.ti_calculate(search_time_dict)
        search_time_info['custom'] = self.c_dict['CUSTOM_STRING']
        amount = do_string_sub(accum_dict['template'],
                               **search_time_info)
        amount = time_util.get_seconds_from_string(amount, default_unit='S', valid_time=search_time)

        # if bucket interval is provided, adjust the accumulation amount
        # if adjustment sets amount to 0, set it to the bucket interval
        bucket_interval = self.c_dict[f"{data_src}_BUCKET_INTERVAL"]
        if bucket_interval != 0:
            self.logger.debug(f"Applying bucket interval {time_util.ti_get_lead_string(bucket_interval)}"
                              f" to {time_util.ti_get_lead_string(amount)}")
            amount = amount % bucket_interval
            if amount == 0:
                amount = bucket_interval

            self.logger.debug(f"New accumulation amount is {time_util.ti_get_lead_string(amount)}")

        return amount

    def get_accumulation(self, time_info, accum, data_src):
        """!Find files to combine to build the desired accumulation
        Args:
          @param time_info dictionary containing time information
          @param accum desired accumulation to build
          @param data_src type of data (FCST or OBS)
          @rtype bool
          @return True if full set of files to build accumulation is found
        """
        in_template = self.c_dict[data_src+'_INPUT_TEMPLATE']

        if self.c_dict[data_src + '_IS_DAILY_FILE'] is True:
            return self.get_daily_file(time_info, accum, data_src, in_template)

        search_time = time_info['valid']
        # last time to search is the output accumulation subtracted from the
        # valid time, then add back the smallest accumulation that is available
        # in the input. This is done because data contains an accumulation from
        # the file/field time backwards in time
        # If building 6 hour accumulation from 1 hour accumulation files,
        # last time to process is valid - 6 + 1
        accum_relative = time_util.get_relativedelta(accum, 'H')
        # using 1 hour for now
        smallest_input_accum = min([lev['amount'] for lev in self.c_dict['ACCUM_DICT_LIST']])
        if smallest_input_accum == 9999999:
            smallest_input_accum = 3600

        last_time = time_info['valid'] -\
            accum_relative +\
            datetime.timedelta(seconds=smallest_input_accum)

        total_accum = time_util.ti_get_seconds_from_relativedelta(accum_relative,
                                                                  time_info['valid'])

        # log the input and output accumulation information
        search_accum_list = []
        for lev in self.c_dict['ACCUM_DICT_LIST']:
            if lev['template'] is not None:
                search_accum_list.append(lev['template'])
            else:
                search_accum_list.append(time_util.ti_get_lead_string(lev['amount'], plural=False))

        search_accum_string = ' or '.join(search_accum_list)
        self.logger.debug(f"Trying to build a {time_util.ti_get_lead_string(total_accum, plural=False)} accumulation using {search_accum_string} input data")

        # loop backwards in time until you have a full set of accum
        while last_time <= search_time:
            found = False

            if total_accum == 0:
                break

            # look for biggest accum that fits search
            for accum_dict in self.c_dict['ACCUM_DICT_LIST']:
                if accum_dict['amount'] > total_accum and accum_dict['template'] is None:
                    continue

                search_file, lead = self.find_input_file(in_template, time_info['init'], search_time,
                                                         accum_dict['amount'], data_src)

                # if found a file, add it to input list with info
                if search_file is not None:
                    # if template is used in accum, find value and apply bucket interval is set
                    if accum_dict['template'] is not None:
                        accum_amount = self.get_template_accum(accum_dict,
                                                               search_time,
                                                               lead,
                                                               data_src)
                        if accum_amount > total_accum:
                            self.logger.debug("Accumulation amount is bigger than remaining accumulation.")
                            continue
                    else:
                        accum_amount = accum_dict['amount']

                    accum_met_time = time_util.time_string_to_met_time(accum_amount)
                    addon = self.get_addon(accum_dict, accum_met_time, search_time)
                    # add file to input list and step back in time to find more data
                    self.add_input_file(search_file, addon)
                    self.logger.debug(f"Adding input file: {search_file} with {addon}")
                    search_time = search_time - datetime.timedelta(seconds=accum_amount)
                    total_accum -= accum_amount
                    found = True
                    break

            # if we don't need any more accumulation, break out of loop and run
            if not total_accum:
                break

            # if we still need to find more accum but we couldn't find it, fail
            if not found:
                return False

        # fail if no files were found or if we didn't find
        #  the entire accumulation needed
        if not self.infiles or total_accum:
            return False

        return True
        
    def get_command(self):

        cmd = '{} -v {} '.format(self.app_path, self.c_dict['VERBOSITY'])

        for a in self.args:
            cmd += a + " "

        if self.method == "USER_DEFINED":
            cmd += self.user_command
            return cmd
        elif self.method == "SUM":
            if self.init_time == -1:
                self.log_error("No init time specified")
                return None

            if self.valid_time == -1:
                self.log_error("No valid time specified")
                return None

            if self.in_accum == -1:
                self.log_error("No input accumulation specified")
                return None

            if self.out_accum == -1:
                self.log_error("No output accumulation specified")
                return None

            cmd += "-sum " + self.init_time + " " + str(self.in_accum) + " " +\
                   self.valid_time + " " + str(self.out_accum) + " "

        else:
            if self.method == "ADD":
                cmd += "-add "
            elif self.method == "SUBTRACT":
                cmd += "-subtract "
            elif self.method == 'DERIVE':
                cmd += '-derive '
                cmd += ','.join(self.c_dict['STAT_LIST']) + ' '

            if len(self.infiles) == 0:
                self.log_error("No input filenames specified")
                return None

            for idx, f in enumerate(self.infiles):
                cmd += f + " "
                if self.method != 'DERIVE':
                    cmd += self.inaddons[idx] + " "


        # set -field options if set
        if self.field_name:
            cmd += "-field 'name=\""+self.field_name+"\";"

            if self.field_level:
                cmd += " level=\""+self.field_level+"\";"

            if self.field_extra:
                cmd += f' {self.field_extra}'

            cmd += "' "

        if self.output_name:
            cmd += f'-name "{self.output_name}" '

        if not self.outfile:
            self.log_error("No output filename specified")
            return None

        out_path = self.get_output_path()

        # create outdir (including subdir in outfile) if it doesn't exist
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        cmd += f"{out_path} "

        if self.pcp_dir:
            cmd += f"-pcpdir {self.pcp_dir} "

        if self.pcp_regex:
            cmd += f"-pcprx {self.pcp_regex} "

        if self.name:
            cmd += f"-name {self.name} "

        if self.compress != -1:
            cmd += f"-compress {str(self.compress)} "

        # remove whitespace at beginning/end and return command
        return cmd.strip()

    def run_at_time_once(self, time_info, var_list, data_src):
        if not var_list:
            var_list = [None]

        for var_info in var_list:
            self.run_at_time_one_field(time_info, var_info, data_src)

    def run_at_time_one_field(self, time_info, var_info, data_src):

        self.clear()
        cmd = None
        self.method = self.c_dict[data_src+'_RUN_METHOD']

        # if method is not USER_DEFINED or DERIVE, check that field information is set
        if self.method == "USER_DEFINED":
            cmd = self.setup_user_method(time_info, data_src)
        elif self.method == "DERIVE":
            cmd = self.setup_derive_method(time_info, var_info, data_src)
        elif not var_info and not self.c_dict[f"{data_src}_OUTPUT_ACCUM"]:
            self.log_error('Cannot run PCPCombine without specifying fields to process '
                           'unless running in USER_DEFINED mode. You must set '
                           f'{data_src}_VAR<n>_[NAME/LEVELS] or {data_src}_OUTPUT_[NAME/LEVEL]')
            return False

        if self.method == "ADD":
            cmd = self.setup_add_method(time_info, var_info, data_src)
        elif self.method == "SUM":
            cmd = self.setup_sum_method(time_info, var_info, data_src)
        elif self.method == "SUBTRACT":
            cmd = self.setup_subtract_method(time_info, var_info, data_src)

        # invalid method should never happen because value is checked on init

        if cmd is None:
            self.log_error("pcp_combine could not generate command")
            return False

        # if output file exists and we want to skip it, warn and continue
        outfile = self.get_output_path()
        if os.path.exists(outfile) and self.c_dict['SKIP_IF_OUTPUT_EXISTS'] is True:
            self.logger.debug('Skip writing output file {} because it already '
                              'exists. Remove file or change '
                              'PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS to True to process'
                              .format(outfile))
            return True

        # set user environment variables if needed and print all envs
        self.set_environment_variables(time_info)

        return self.build()

    def setup_subtract_method(self, time_info, var_info, data_src):
        """!Setup pcp_combine to subtract two files to build desired accumulation
        Args:
          @param time_info object containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # if [FCST/OBS]_OUTPUT_[NAME/ACCUM] are set, use them instead of
        # [FCST/OBS]_VAR<n>_[NAME/LEVELS]
        if self.c_dict[f"{data_src}_OUTPUT_NAME"]:
            field_name = self.c_dict[f"{data_src}_OUTPUT_NAME"]
        else:
            field_name = var_info[f"{data_src.lower()}_name"]
            self.logger.warning(f'{data_src}_PCP_COMBINE_OUTPUT_NAME is not set. Using '
                                f'{field_name} from {data_src}_VAR{var_info.get("index")}_NAME. ')

        if self.c_dict[f"{data_src}_OUTPUT_ACCUM"]:
            accum = self.c_dict[f"{data_src}_OUTPUT_ACCUM"]
            level_type = 'A'
        else:
            level = var_info[f'{data_src.lower()}_level']
            level_type, accum = util.split_level(level)
            self.logger.warning(f'{data_src}_PCP_COMBINE_OUTPUT_ACCUM is not set. Using '
                                f'{accum} from {data_src}_VAR{var_info.get("index")}_LEVELS. '
                                'It is recommended that you explicitly set the '
                                'output accumulation.')

        accum = time_util.get_seconds_from_string(accum,
                                                  default_unit='H',
                                                  valid_time=time_info['valid'])
        if accum is None:
            self.log_error("Could not get accumulation from {data_src}_VAR{var_info.get('index')}_LEVEL or "
                           f"{data_src}_PCP_COMBINE_OUTPUT_ACCUM")
            return None

        lead = time_info['lead_seconds']
        lead2 = lead - accum

        self.logger.debug(f"Attempting to build {time_util.ti_get_lead_string(accum, False)} "
                          f"accumulation by subtracting {time_util.ti_get_lead_string(lead2, False)} "
                          f"from {time_util.ti_get_lead_string(lead, False)}.")

        # set output file information
        out_file = do_string_sub(out_template,
                                 level=accum,
                                 **time_info)
        self.outfile = out_file
        self.outdir = out_dir

        # get first file
        pcpSts1 = do_string_sub(in_template,
                                level=accum,
                                **time_info)
        file1_expected = os.path.join(in_dir, pcpSts1)
        file1 = util.preprocess_file(file1_expected,
                                     self.c_dict[data_src+'_INPUT_DATATYPE'],
                                     self.config)

        if file1 is None:
            self.log_error(f'Could not find {data_src} file {file1_expected} using template {in_template}')
            return None

        # if level type is A (accum) and second lead is 0, then
        # run PCPCombine in -add mode with just the first file
        if lead2 == 0 and level_type == 'A':
            self.logger.debug("Subtracted accumulation is 0, so running ADD mode on one file")
            self.method = 'ADD'
            lead = time_util.seconds_to_met_time(lead)
            self.add_input_file(file1, lead)
            return self.get_command()

        # else continue building -subtract command

        # set time info for second lead
        input_dict2 = { 'init' : time_info['init'],
                       'lead' : lead2 }
        time_info2 = time_util.ti_calculate(input_dict2)
        if hasattr(time_info, 'custom'):
            time_info2['custom'] = time_info['custom']

        pcpSts2 = do_string_sub(in_template,
                                level=accum,
                                **time_info2)
        file2_expected = os.path.join(in_dir, pcpSts2)
        file2 = util.preprocess_file(file2_expected,
                                     self.c_dict[data_src+'_INPUT_DATATYPE'],
                                     self.config)

        if file2 is None:
            self.log_error(f'Could not find {data_src} file {file2_expected} using template {in_template}')
            return None

        if self.c_dict[data_src+'_INPUT_DATATYPE'] != 'GRIB':
            field_name_1 = do_string_sub(field_name, **time_info)
            lead = "'name=\"" + field_name_1 + "\";'"
            field_name_2 = do_string_sub(field_name, **time_info2)
            lead2 = "'name=\"" + field_name_2 + "\";'"
            # TODO: need to add level if NetCDF input - how to specify levels for each
        else:
            lead = time_util.seconds_to_met_time(lead)
            lead2 = time_util.seconds_to_met_time(lead2)

        self.add_input_file(file1,
                            lead)
        self.add_input_file(file2,
                            lead2)

        return self.get_command()


    def setup_sum_method(self, time_info, var_info, data_src):
        """!Setup pcp_combine to build desired accumulation based on
        init/valid times and accumulations
        Args:
          @param time_info object containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        if self.c_dict[f"{data_src}_ACCUMS"]:
            in_accum = self.c_dict[data_src+'_ACCUMS'][0]
        else:
            in_accum = 0

        in_accum = time_util.time_string_to_met_time(in_accum, 'H')

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # if OUTPUT_ACCUM is set, use that instead of obs_level
        # and use obs_level as field level
        if self.c_dict[data_src+'_OUTPUT_ACCUM']:
            out_accum = self.c_dict[data_src+'_OUTPUT_ACCUM']
        else:
            out_accum = var_info[data_src.lower()+'_level']
            if out_accum[0].isalpha():
                out_accum = out_accum[1:]

            self.logger.warning(f'{data_src}_PCP_COMBINE_OUTPUT_ACCUM is not set. Using '
                                f'{out_accum} from {data_src}_VAR{var_info.get("index")}_LEVELS. '
                                'It is recommended that you explicitly set the '
                                'output accumulation.')

        if self.c_dict[data_src+'_OUTPUT_NAME']:
            self.output_name = self.c_dict[data_src+'_OUTPUT_NAME']
        else:
            self.output_name = var_info[f"{data_src.lower()}_name"]
            self.logger.warning(f'{data_src}_PCP_COMBINE_OUTPUT_NAME is not set. Using '
                                f'{self.output_name} from {data_src}_VAR{var_info.get("index")}_NAME.')

        # set field name and level if set in config
        if self.c_dict[f'{data_src}_NAMES']:
            self.field_name = self.c_dict[f'{data_src}_NAMES'][0]

        if self.c_dict[f'{data_src}_LEVELS']:
            self.field_level = self.c_dict[f'{data_src}_LEVELS'][0]

        if self.c_dict[f'{data_src}_OPTIONS']:
            self.field_extra = do_string_sub(self.c_dict[f'{data_src}_OPTIONS'][0],
                                             **time_info)

        init_time = time_info['init'].strftime('%Y%m%d_%H%M%S')
        valid_time = time_info['valid'].strftime('%Y%m%d_%H%M%S')

        time_info['level'] = time_util.get_seconds_from_string(out_accum,
                                                               'H',
                                                               time_info['valid'])

        out_accum = time_util.time_string_to_met_time(out_accum,
                                                      'H')

        in_regex = util.template_to_regex(in_template, time_info,
                                          self.logger)
        in_regex_split = in_regex.split('/')
        in_dir = os.path.join(in_dir, *in_regex_split[0:-1])
        in_regex = in_regex_split[-1]

        self.init_time = init_time
        self.valid_time = valid_time
        self.in_accum = in_accum
        self.out_accum = out_accum
        self.pcp_dir = in_dir
        self.pcp_regex = in_regex
        self.outdir = out_dir

        pcp_out = do_string_sub(out_template,
                               **time_info)
        self.outfile = pcp_out

        return self.get_command()


    def setup_add_method(self, time_info, var_info, data_src):
        """!Setup pcp_combine to add files to build desired accumulation
        Args:
          @param time_info dictionary containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""

        # if [FCST/OBS]_OUTPUT_[NAME/ACCUM] are set, use them instead of
        # [FCST/OBS]_VAR<n>_[NAME/LEVELS]
        if self.c_dict[f"{data_src}_OUTPUT_ACCUM"]:
            accum_string = self.c_dict[f"{data_src}_OUTPUT_ACCUM"]
        else:
            level = var_info[f'{data_src.lower()}_level']
            _, accum_string = util.split_level(level)

            self.logger.warning(f'{data_src}_PCP_COMBINE_OUTPUT_ACCUM is not set. Using '
                                f'{accum_string} from {data_src}_VAR{var_info.get("index")}_LEVELS. '
                                'It is recommended that you explicitly set the '
                                'output accumulation.')

        if self.c_dict[f"{data_src}_OUTPUT_NAME"]:
            field_name = self.c_dict[f"{data_src}_OUTPUT_NAME"]
        else:
            field_name = var_info[f"{data_src.lower()}_name"]

            self.logger.warning(f'{data_src}_PCP_COMBINE_OUTPUT_NAME is not set. Using '
                                f'{field_name} from {data_src}_VAR{var_info.get("index")}_NAME.')

        # get number of seconds relative to valid time
        accum_seconds = time_util.get_seconds_from_string(accum_string,
                                                          default_unit='H',
                                                          valid_time=time_info['valid'])
        if accum_seconds is None:
            self.log_error(f'Invalid accumulation specified: {accum_string}')
            return

        # create list of tuples for input levels and optional field names
        self.build_input_accum_list(data_src, time_info)

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.input_dir = in_dir

        if not self.get_accumulation(time_info, accum_string, data_src):
            self.log_error(f'Could not find files to build accumulation in {in_dir} using template {in_template}')
            return None

        self.outdir = out_dir
        time_info['level'] = int(accum_seconds)
        pcp_out = do_string_sub(out_template,
                                **time_info)
        self.outfile = pcp_out
        self.args.append("-name " + field_name)
        return self.get_command()

    def setup_derive_method(self, time_info, var_info, data_src):
        """!Setup pcp_combine to derive stats
        Args:
          @param time_info dictionary containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        if self.c_dict[f"{data_src}_NAMES"]:
            self.field_name = self.c_dict[f"{data_src}_NAMES"][0]

        if self.c_dict[f"{data_src}_LEVELS"]:
            self.field_level = self.c_dict[f"{data_src}_LEVELS"][0]

        if self.c_dict[f"{data_src}_OUTPUT_NAME"]:
            self.output_name = self.c_dict[f"{data_src}_OUTPUT_NAME"]
            # if list of output names, remove whitespace between items
            self.output_name = [name.strip() for name in self.output_name.split(',')]
            self.output_name = ','.join(self.output_name)

        if self.c_dict[f"{data_src}_OPTIONS"]:
            self.field_extra = do_string_sub(self.c_dict[f'{data_src}_OPTIONS'][0],
                                             **time_info)

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.input_dir = in_dir

        # create list of tuples for input levels and optional field names
        self.build_input_accum_list(data_src, time_info)

        # get files
        lookback = self.c_dict[data_src+'_DERIVE_LOOKBACK']
        lookback_seconds = time_util.get_seconds_from_string(lookback,
                                                             default_unit='H',
                                                             valid_time=time_info['valid'])
        if lookback_seconds is None:
            self.log_error(f'Invalid format for derived lookback: {lookback}')
            return

        if not self.get_accumulation(time_info,
                                     lookback,
                                     data_src):
            self.log_error(f'Could not find files in {in_dir} using template {in_template}')
            return None

        # set output
        self.outdir = out_dir
        time_info['level'] = lookback_seconds
        pcp_out = do_string_sub(out_template,
                             **time_info)
        self.outfile = pcp_out

        # set STAT_LIST for data type (FCST/OBS)
        self.c_dict['STAT_LIST'] = self.c_dict[f"{data_src}_STAT_LIST"]
        return self.get_command()

    def setup_user_method(self, time_info, data_src):
        """!Setup pcp_combine to call user defined command
        Args:
          @param time_info dictionary containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        command_template = self.config.getraw('config', data_src + '_PCP_COMBINE_COMMAND')
        self.user_command = do_string_sub(command_template, **time_info)

        # get output accumulation in case output template uses level
        accum_string = '0'
        if self.c_dict[f"{data_src}_OUTPUT_ACCUM"]:
            accum_string = self.c_dict[f"{data_src}_OUTPUT_ACCUM"]
            _, accum_string = util.split_level(accum_string)

        accum_seconds = time_util.get_seconds_from_string(accum_string, 'H')
        if accum_seconds is not None:
            time_info['level'] = int(accum_seconds)

        # add output path to user defined command
        self.outdir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        self.outfile = do_string_sub(out_template,
                                     **time_info)

        out_path = self.get_output_path()

        # create outdir (including subdir in outfile) if it doesn't exist
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        self.user_command += ' ' + out_path

        return '{} -v {} {}'.format(self.app_path, self.c_dict['VERBOSITY'], self.user_command)

    def build_input_accum_list(self, data_src, time_info):
        accum_list = self.c_dict[data_src + '_ACCUMS']
        level_list = self.c_dict[data_src + '_LEVELS']
        name_list = self.c_dict[data_src + '_NAMES']
        extra_list = self.c_dict[data_src + '_OPTIONS']

        # if no name list, create list of None values
        if not name_list:
            name_list = [None] * len(accum_list)

        # do the same for level list
        if not level_list:
            level_list = [None] * len(accum_list)

        # do the same for extra list
        if not extra_list:
            extra_list = [None] * len(accum_list)

        accum_dict_list = []
        for accum, level, name, extra in zip(accum_list, level_list, name_list, extra_list):

            template = None
            # if accum is forecast lead, set amount to 999999 and save template
            if 'lead' in accum:
                template = accum
                accum = '9999999S'

            # convert accum amount to seconds from time string
            amount = time_util.get_seconds_from_string(accum, 'H', time_info['valid'])

            accum_dict_list.append({'amount': amount,
                                    'name': name,
                                    'level': level,
                                    'template': template,
                                    'extra': extra})

        self.c_dict['ACCUM_DICT_LIST'] = accum_dict_list
