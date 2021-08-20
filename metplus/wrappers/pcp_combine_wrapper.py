'''
Program Name: pcp_combine_wrapper.py
Contact(s): George McCabe
Abstract: Builds commands to run MET tool pcp_combine
'''

import os
from datetime import timedelta

from ..util import met_util as util
from ..util import do_string_sub, getlist
from ..util import get_seconds_from_string, ti_get_lead_string, ti_calculate
from ..util import get_relativedelta, ti_get_seconds_from_relativedelta
from ..util import time_string_to_met_time, seconds_to_met_time
from . import ReformatGriddedWrapper

'''!@namespace PCPCombineWrapper
@brief Wraps the MET tool pcp_combine to combine/divide
precipitation accumulations or derive additional fields
'''
class PCPCombineWrapper(ReformatGriddedWrapper):
    """! Wraps the MET tool pcp_combine to combine or divide
         precipitation accumulations """

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
        self.field_name = None
        self.field_level = ""
        self.output_name = ""

    def create_c_dict(self):
        """! Create dictionary from config items to be used in the wrapper
            Allows developer to reference config items without having to know
            the type and consolidates config get calls so it is easier to see
            which config variables are used in the wrapper

            @returns dictionary of values to use in wrapper
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_PCP_COMBINE_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        fcst_run = self.config.getbool('config', 'FCST_PCP_COMBINE_RUN', False)
        obs_run = self.config.getbool('config', 'OBS_PCP_COMBINE_RUN', False)

        if not fcst_run and not obs_run:
            self.log_error("Must set either FCST_PCP_COMBINE_RUN or "
                           "OBS_PCP_COMBINE_RUN")
            return c_dict

        if fcst_run:
            c_dict = self.set_fcst_or_obs_dict_items('FCST', c_dict)
            c_dict['VAR_LIST_FCST'] = util.parse_var_list(
                self.config,
                data_type='FCST',
                met_tool=self.app_name
            )
        if obs_run:
            c_dict = self.set_fcst_or_obs_dict_items('OBS', c_dict)
            c_dict['VAR_LIST_OBS'] = util.parse_var_list(
                self.config,
                data_type='OBS',
                met_tool=self.app_name
            )

        return c_dict

    def set_fcst_or_obs_dict_items(self, d_type, c_dict):
        """! Set c_dict values specific to either forecast (FCST) or
        observation (OBS) data.

            @param d_type data type, either FCST or OBS
            @param c_dict config dictionary to populate
            @returns c_dict with values for given data type set
        """
        # handle run method
        run_method = self.config.getstr(
            'config',
            f'{d_type}_PCP_COMBINE_METHOD', ''
        ).upper()

        # change CUSTOM (deprecated) to USER_DEFINED
        if run_method == 'CUSTOM':
            run_method = 'USER_DEFINED'

        if run_method not in self.valid_run_methods:
            self.log_error(f"Invalid value for {d_type}_PCP_COMBINE_METHOD: "
                           f"{run_method}. Valid options are "
                           f"{','.join(self.valid_run_methods)}.")
            return c_dict

        c_dict[f'{d_type}_RUN_METHOD'] = run_method

        # get lookback from _LOOKBACK or _OUTPUT_ACCUM or _DERIVE_LOOKBACK
        c_dict[f'{d_type}_LOOKBACK'] = self._handle_lookback(c_dict, d_type)

        c_dict[f'{d_type}_MIN_FORECAST'] = self.config.getstr(
            'config',
            f'{d_type}_PCP_COMBINE_MIN_FORECAST', '0'
        )
        c_dict[f'{d_type}_MAX_FORECAST'] = self.config.getstr(
            'config',
            f'{d_type}_PCP_COMBINE_MAX_FORECAST', '256H'
        )

        c_dict[f'{d_type}_INPUT_DATATYPE'] = self.config.getstr(
            'config',
            f'{d_type}_PCP_COMBINE_INPUT_DATATYPE', ''
        )

        c_dict[f'{d_type}_ACCUMS'] = getlist(
            self.config.getraw('config',
                               f'{d_type}_PCP_COMBINE_INPUT_ACCUMS', '')
        )

        c_dict[f'{d_type}_NAMES'] = getlist(
            self.config.getraw('config',
                               f'{d_type}_PCP_COMBINE_INPUT_NAMES', '')
        )
        c_dict[f'{d_type}_LEVELS'] = getlist(
            self.config.getraw('config',
                               f'{d_type}_PCP_COMBINE_INPUT_LEVELS', '')
        )
        c_dict[f'{d_type}_OPTIONS'] = getlist(
            self.config.getraw('config',
                               f'{d_type}_PCP_COMBINE_INPUT_OPTIONS', '')
        )

        c_dict[f'{d_type}_OUTPUT_NAME'] = self.config.getstr(
            'config',
            f'{d_type}_PCP_COMBINE_OUTPUT_NAME', ''
        )
        c_dict[f'{d_type}_INPUT_DIR'] = self.config.getdir(
            f'{d_type}_PCP_COMBINE_INPUT_DIR', ''
        )
        c_dict[f'{d_type}_INPUT_TEMPLATE'] = self.config.getraw(
            'config',
            f'{d_type}_PCP_COMBINE_INPUT_TEMPLATE'
        )

        c_dict[f'{d_type}_OUTPUT_DIR'] = self.config.getdir(
            f'{d_type}_PCP_COMBINE_OUTPUT_DIR', ''
        )
        c_dict[f'{d_type}_OUTPUT_TEMPLATE'] = self.config.getraw(
            'config',
            f'{d_type}_PCP_COMBINE_OUTPUT_TEMPLATE'
        )

        c_dict[f'{d_type}_STAT_LIST'] = getlist(
            self.config.getstr('config',
                               f'{d_type}_PCP_COMBINE_STAT_LIST', '')
        )

        c_dict[f'{d_type}_BUCKET_INTERVAL'] = self.config.getseconds(
            'config',
            f'{d_type}_PCP_COMBINE_BUCKET_INTERVAL', 0
        )

        c_dict[f'{d_type}_CONSTANT_INIT'] = self.config.getbool(
            'config',
            f'{d_type}_PCP_COMBINE_CONSTANT_INIT', False
        )

        # read any additional names/levels to add to command
        c_dict[f'{d_type}_EXTRA_NAMES'] = getlist(
            self.config.getraw('config',
                               f'{d_type}_PCP_COMBINE_EXTRA_NAMES', '')
        )
        c_dict[f'{d_type}_EXTRA_LEVELS'] = getlist(
            self.config.getraw('config',
                               f'{d_type}_PCP_COMBINE_EXTRA_LEVELS', '')
        )
        # fill in missing extra level values with None
        fill_num = (len(c_dict[f'{d_type}_EXTRA_NAMES']) -
                    len(c_dict[f'{d_type}_EXTRA_LEVELS']))
        if fill_num > 0:
            for num in range(fill_num):
                c_dict[f'{d_type}_EXTRA_LEVELS'].append(None)

        c_dict[f'{d_type}_EXTRA_OUTPUT_NAMES'] = getlist(
            self.config.getraw('config',
                               f'{d_type}_PCP_COMBINE_EXTRA_OUTPUT_NAMES', '')
        )

        if run_method == 'DERIVE' and not c_dict[f'{d_type}_STAT_LIST']:
            self.log_error('Statistic list is empty. Must set '
                           f'{d_type}_PCP_COMBINE_STAT_LIST if running '
                           'derive mode')

        if (not c_dict[f'{d_type}_INPUT_TEMPLATE'] and
                c_dict[f'{d_type}_RUN_METHOD'] != 'SUM'):
            self.log_error(f"Must set {d_type}_PCP_COMBINE_INPUT_TEMPLATE "
                           "unless using SUM method")

        if not c_dict[f'{d_type}_OUTPUT_TEMPLATE']:
            self.log_error(f"Must set {d_type}_PCP_COMBINE_OUTPUT_TEMPLATE")

        if run_method == 'DERIVE' or run_method == 'ADD':
            if not c_dict[f'{d_type}_ACCUMS']:
                self.log_error(f'{d_type}_PCP_COMBINE_INPUT_ACCUMS '
                               'must be specified.')

            # name list should either be empty or the same length as accum list
            len_names = len(c_dict[f'{d_type}_NAMES'])
            len_accums = len(c_dict[f'{d_type}_ACCUMS'])
            len_levels = len(c_dict[f'{d_type}_LEVELS'])
            if c_dict[f'{d_type}_NAMES'] and len_accums != len_names:
                self.log_error(f'{d_type}_PCP_COMBINE_INPUT_ACCUM_NAMES list '
                               'should be either empty or the same length as '
                               f'{d_type}_PCP_COMBINE_INPUT_ACCUMS list.')

            if c_dict[f'{d_type}_LEVELS'] and len_accums != len_levels:
                self.log_error(f'{d_type}_PCP_COMBINE_INPUT_LEVELS list '
                               'should be either empty or the same length as '
                               f'{d_type}_PCP_COMBINE_INPUT_ACCUMS list.')

        return c_dict

    def _handle_lookback(self, c_dict, d_type):
        lookback = self.config.getstr('config',
                                      f'{d_type}_PCP_COMBINE_LOOKBACK', '')
        if lookback:
            return lookback

        # if _PCP_COMBINE_LOOKBACK is not set
        # prioritize DERIVE_LOOKBACK over OUTPUT_ACCUM if in -derive mode
        # or vice versa otherwise
        if c_dict[f'{d_type}_RUN_METHOD'] == "DERIVE":
            ordered_synonyms = [
                'DERIVE_LOOKBACK',
                'OUTPUT_ACCUM',
            ]
        else:
            ordered_synonyms = [
                'OUTPUT_ACCUM',
                'DERIVE_LOOKBACK',
            ]

        for synonym in ordered_synonyms:
            lookback = self.config.getstr(
                'config',
                f'{d_type}_PCP_COMBINE_{synonym}', '')
            if lookback:
                return lookback

        # if none of the variables are set, return integer 0
        return 0

    def clear(self):
        super().clear()
        self.inaddons = []
        self.method = ""
        self.field_name = None
        self.field_level = ""
        self.field_extra = ""
        self.output_name = ""
        self.extra_fields = None
        self.extra_output = None

    def add_input_file(self, filename, addon):
        self.infiles.append(filename)
        self.inaddons.append(str(addon))

    def get_dir_and_template(self, data_type, in_or_out):
        prefix = f'{data_type}_{in_or_out}'
        data_dir = self.c_dict[f'{prefix}_DIR']
        template = self.c_dict[f'{prefix}_TEMPLATE']

        return data_dir, template

    def getLowestForecastFile(self, valid_time, dtype, template):
        """! Find the lowest forecast hour that corresponds to the valid time

          @param valid_time valid time to search
          @param dtype data type (FCST or OBS) to get filename template
          @rtype string
          @return Path to file with the lowest forecast hour
    """

        # search for file with lowest forecast,
        # then loop up into you find a valid one
        min_forecast = get_seconds_from_string(
            self.c_dict[dtype+'_MIN_FORECAST'], 'H'
        )
        max_forecast = get_seconds_from_string(
            self.c_dict[dtype+'_MAX_FORECAST'], 'H'
        )
        smallest_input_accum = min(
            [lev['amount'] for lev in self.c_dict['ACCUM_DICT_LIST']]
        )

        # if smallest input accumulation is greater than an hour, search hourly
        if smallest_input_accum > 3600:
            smallest_input_accum = 3600

        min_forecast_string = ti_get_lead_string(min_forecast)
        max_forecast_string = ti_get_lead_string(max_forecast)
        smallest_input_accum_string = ti_get_lead_string(smallest_input_accum,
                                                         plural=False)
        self.logger.debug("Looking for file with lowest forecast lead valid "
                          f"at {valid_time} between {min_forecast_string} "
                          f"and {max_forecast_string} using "
                          f"{smallest_input_accum_string} intervals")

        forecast_lead = min_forecast
        while forecast_lead <= max_forecast:
            input_dict = {}
            input_dict['valid'] = valid_time
            input_dict['lead_seconds'] = forecast_lead
            time_info = ti_calculate(input_dict)
            time_info['custom'] = self.c_dict.get('CUSTOM_STRING', '')
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

    def get_addon(self, accum_dict, search_accum, search_time):
        field_name = accum_dict['name']
        field_level = accum_dict['level']
        field_extra = accum_dict['extra']
        if field_name is None:
            return search_accum

        # perform string substitution on name
        field_name = do_string_sub(field_name,
                                   valid=search_time,
                                   custom=self.c_dict.get('CUSTOM_STRING', ''))
        addon = "'name=\"" + field_name + "\";"

        if not util.is_python_script(field_name) and field_level is not None:
            addon += f" level=\"{field_level}\";"

        if field_extra:
            search_time_info = {'valid': search_time,
                                'custom': self.c_dict.get('CUSTOM_STRING', '')}

            field_extra = do_string_sub(field_extra,
                                        **search_time_info)

            field_extra = field_extra.replace('"', '\"')
            addon += f" {field_extra}"

        addon += "'"
        return addon

    def find_input_file(self, in_template, init_time, valid_time, search_accum,
                        data_src):
        lead = 0

        if ('{lead?' in in_template or
                ('{init?' in in_template and '{valid?' in in_template)):
            if not self.c_dict[f'{data_src}_CONSTANT_INIT']:
                return self.getLowestForecastFile(valid_time, data_src,
                                                  in_template)

            # set init time and lead in time dict if init should be constant
            # ti_calculate cannot currently handle both init and valid
            lead = (valid_time - init_time).total_seconds()
            input_dict = {'init': init_time,
                          'lead': lead}
        else:
            if self.c_dict[f'{data_src}_CONSTANT_INIT']:
                input_dict = {'init': init_time}
            else:
                input_dict = {'valid': valid_time}


        time_info = ti_calculate(input_dict)
        time_info['custom'] = self.c_dict.get('CUSTOM_STRING', '')
        input_file = do_string_sub(in_template,
                                   level=int(search_accum),
                                   **time_info)
        input_path = os.path.join(self.input_dir, input_file)

        return util.preprocess_file(input_path,
                                    self.c_dict[f'{data_src}_INPUT_DATATYPE'],
                                    self.config), lead

    def get_template_accum(self, accum_dict, search_time, lead, data_src):
        # apply string substitution to accum amount
        search_time_dict = {'valid': search_time, 'lead_seconds': lead}
        search_time_info = ti_calculate(search_time_dict)
        search_time_info['custom'] = self.c_dict.get('CUSTOM_STRING', '')
        amount = do_string_sub(accum_dict['template'],
                               **search_time_info)
        amount = get_seconds_from_string(amount, default_unit='S',
                                         valid_time=search_time)

        # if bucket interval is provided, adjust the accumulation amount
        # if adjustment sets amount to 0, set it to the bucket interval
        bucket_interval = self.c_dict[f"{data_src}_BUCKET_INTERVAL"]
        if bucket_interval != 0:
            self.logger.debug("Applying bucket interval "
                              f"{ti_get_lead_string(bucket_interval)}"
                              f" to {ti_get_lead_string(amount)}")
            amount = amount % bucket_interval
            if amount == 0:
                amount = bucket_interval

            self.logger.debug("New accumulation amount is "
                              f"{ti_get_lead_string(amount)}")

        return amount

    def get_accumulation(self, time_info, accum, data_src):
        """! Find files to combine to build the desired accumulation

          @param time_info dictionary containing time information
          @param accum desired accumulation to build
          @param data_src type of data (FCST or OBS)
          @rtype bool
          @return True if full set of files to build accumulation is found
        """
        in_template = self.c_dict[data_src+'_INPUT_TEMPLATE']

        search_time = time_info['valid']
        # last time to search is the output accumulation subtracted from the
        # valid time, then add back the smallest accumulation that is available
        # in the input. This is done because data contains an accumulation from
        # the file/field time backwards in time
        # If building 6 hour accumulation from 1 hour accumulation files,
        # last time to process is valid - 6 + 1
        accum_relative = get_relativedelta(accum, 'H')
        # using 1 hour for now
        smallest_input_accum = min(
            [lev['amount'] for lev in self.c_dict['ACCUM_DICT_LIST']]
        )
        if smallest_input_accum == 9999999:
            smallest_input_accum = 3600

        last_time = (time_info['valid'] - accum_relative +
                     timedelta(seconds=smallest_input_accum))

        total_accum = ti_get_seconds_from_relativedelta(accum_relative,
                                                        time_info['valid'])

        # log the input and output accumulation information
        search_accum_list = []
        for lev in self.c_dict['ACCUM_DICT_LIST']:
            if lev['template'] is not None:
                search_accum_list.append(lev['template'])
            else:
                search_accum_list.append(ti_get_lead_string(lev['amount'],
                                                            plural=False))

        self.logger.debug("Trying to build a "
                          f"{ti_get_lead_string(total_accum, plural=False)} "
                          "accumulation using "
                          f"{' or '.join(search_accum_list)} input data")

        # loop backwards in time until you have a full set of accum
        while last_time <= search_time:
            found = False

            if total_accum == 0:
                break

            # look for biggest accum that fits search
            for accum_dict in self.c_dict['ACCUM_DICT_LIST']:
                if (accum_dict['amount'] > total_accum and
                        accum_dict['template'] is None):
                    continue

                search_file, lead = self.find_input_file(in_template,
                                                         time_info['init'],
                                                         search_time,
                                                         accum_dict['amount'],
                                                         data_src)

                # if found a file, add it to input list with info
                if search_file is not None:
                    # if template is used in accum, find value and
                    # apply bucket interval is set
                    if accum_dict['template'] is not None:
                        accum_amount = self.get_template_accum(accum_dict,
                                                               search_time,
                                                               lead,
                                                               data_src)
                        if accum_amount > total_accum:
                            self.logger.debug("Accumulation amount is bigger "
                                              "than remaining accumulation.")
                            continue
                    else:
                        accum_amount = accum_dict['amount']

                    accum_met_time = time_string_to_met_time(accum_amount)
                    addon = self.get_addon(accum_dict, accum_met_time,
                                           search_time)
                    # add file to input list and
                    # step back in time to find more data
                    self.add_input_file(search_file, addon)
                    self.logger.debug(f"Adding input file: {search_file} "
                                      f"with {addon}")
                    search_time = search_time - timedelta(seconds=accum_amount)
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

        cmd = f"{self.app_path} -v {self.c_dict['VERBOSITY']} "

        for arg in self.args:
            cmd += f'{arg} '

        if self.method != "SUM" and self.method != "USER_DEFINED":
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

        if self.extra_fields:
            cmd += self.extra_fields + ' '

        output_string = self.get_output_string()
        if output_string:
            cmd += f'-name {output_string} '

        if not self.outfile:
            self.log_error("No output filename specified")
            return None

        out_path = self.get_output_path()

        # create outdir (including subdir in outfile) if it doesn't exist
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        cmd += f"{out_path} "

        # remove whitespace at beginning/end and return command
        return cmd.strip()

    def get_extra_fields(self, data_src):
        extra_names = self.c_dict.get(data_src + '_EXTRA_NAMES')
        if not extra_names:
            return None, None

        extra_list = []

        extra_levels = self.c_dict.get(data_src + '_EXTRA_LEVELS')
        for name, level in zip(extra_names, extra_levels):
            field_fmt = f"-field 'name=\"{name}\";"
            if level:
                field_fmt += f" level=\"{level}\";"
            field_fmt += "'"
            extra_list.append(field_fmt)

        extra_input_fmt = ' '.join(extra_list)

        # handle extra output names if specified
        extra_output_names = self.c_dict.get(data_src + '_EXTRA_OUTPUT_NAMES')
        if not extra_output_names:
            extra_output_fmt = None
        else:
            extra_output_fmt = '","'.join(extra_output_names)
            extra_output_fmt = f'"{extra_output_fmt}"'

        return extra_input_fmt, extra_output_fmt

    def get_output_string(self):
        """! If self.output_name is set, add quotes and return the string. If
        self.extra_output is also set, add the additional names separated by
        commas inside the quotes.

        @returns formatted string if output name(s) is specified, None if not
        """
        if not self.output_name:
            return None

        output_string = f'"{self.output_name}"'
        # add extra output field names
        if self.extra_output:
            output_string = f'{output_string},{self.extra_output}'

        return output_string

    def run_at_time_once(self, time_info, var_list, data_src):

        if not var_list:
            var_list = [None]

        for var_info in var_list:
            self.run_at_time_one_field(time_info, var_info, data_src)

    def run_at_time_one_field(self, time_info, var_info, data_src):

        self.clear()

        # read additional names/levels to add to command if set
        self.extra_fields, self.extra_output = self.get_extra_fields(data_src)

        can_run = None
        self.method = self.c_dict[data_src+'_RUN_METHOD']

        # if method is not USER_DEFINED or DERIVE,
        # check that field information is set
        if self.method == "USER_DEFINED":
            can_run = self.setup_user_method(time_info, data_src)
        elif self.method == "DERIVE":
            can_run = self.setup_derive_method(time_info, var_info, data_src)
        elif not var_info and not self.c_dict[f"{data_src}_LOOKBACK"]:
            self.log_error('Cannot run PCPCombine without specifying fields '
                           'to process unless running in USER_DEFINED mode. '
                           f'You must set {data_src}_VAR<n>_[NAME/LEVELS] or '
                           f'{data_src}_OUTPUT_[NAME/LEVEL]')
            return False

        if self.method == "ADD":
            can_run = self.setup_add_method(time_info, var_info, data_src)
        elif self.method == "SUM":
            can_run = self.setup_sum_method(time_info, var_info, data_src)
        elif self.method == "SUBTRACT":
            can_run = self.setup_subtract_method(time_info, var_info, data_src)

        # invalid method should never happen because value is checked on init

        if not can_run:
            self.log_error("pcp_combine could not generate command")
            return False

        # if output file exists and we want to skip it, warn and continue
        outfile = self.get_output_path()
        if os.path.exists(outfile) and self.c_dict['SKIP_IF_OUTPUT_EXISTS']:
            self.logger.debug(f'Skip writing output file {outfile} because it '
                              'already exists. Remove file or change '
                              'PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS to True '
                              'to process')
            return True

        # set user environment variables if needed and print all envs
        self.set_environment_variables(time_info)

        return self.build()

    def setup_subtract_method(self, time_info, var_info, data_src):
        """! Setup pcp_combine to subtract two files to build accumulation

          @param time_info object containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file
        """
        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        if self.c_dict[f"{data_src}_LOOKBACK"]:
            accum = self.c_dict[f"{data_src}_LOOKBACK"]
            level_type = 'A'
        else:
            level = var_info[f'{data_src.lower()}_level']
            level_type, accum = util.split_level(level)
            self.logger.warning(f'{data_src}_PCP_COMBINE_LOOKBACK is '
                                f'not set. Using {accum} from '
                                f'{data_src}_VAR{var_info.get("index")}_LEVELS'
                                '. It is recommended that you explicitly set '
                                'the output accumulation.')

        accum = get_seconds_from_string(accum,
                                        default_unit='H',
                                        valid_time=time_info['valid'])
        if accum is None:
            self.log_error(
                "Could not get accumulation from "
                f"{data_src}_VAR{var_info.get('index')}_LEVEL or "
                f"{data_src}_PCP_COMBINE_LOOKBACK"
            )
            return False

        lead = time_info['lead_seconds']
        lead2 = lead - accum

        self.logger.debug(
            f"Attempting to build {ti_get_lead_string(accum, False)} "
            f"accumulation by subtracting {ti_get_lead_string(lead2, False)} "
            f"from {ti_get_lead_string(lead, False)}."
        )

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
            self.log_error(f'Could not find {data_src} file {file1_expected} '
                           f'using template {in_template}')
            return False

        # if level type is A (accum) and second lead is 0, then
        # run PCPCombine in -add mode with just the first file
        if lead2 == 0 and level_type == 'A':
            self.logger.debug("Subtracted accumulation is 0, so running "
                              "ADD mode on one file")
            self.method = 'ADD'
            lead = seconds_to_met_time(lead)
            self.add_input_file(file1, lead)
            return True

        # else continue building -subtract command

        # set time info for second lead
        input_dict2 = {'init': time_info['init'],
                       'lead': lead2}
        time_info2 = ti_calculate(input_dict2)
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
            self.log_error(f'Could not find {data_src} file {file2_expected} '
                           f'using template {in_template}')
            return False

        if self.c_dict[data_src+'_INPUT_DATATYPE'] == 'GRIB':
            lead = seconds_to_met_time(lead)
            lead2 = seconds_to_met_time(lead2)
        else:
            if not self.c_dict.get(f"{data_src}_NAMES"):
                return False

            if not self.c_dict.get(f"{data_src}_LEVELS"):
                return False

            field_name = self.c_dict[f"{data_src}_NAMES"][0]
            level = self.c_dict[f"{data_src}_LEVELS"][0]

            field_name_1 = do_string_sub(field_name, **time_info)
            level_1 = do_string_sub(level, **time_info)
            lead = ("'name=\"" + field_name_1 + "\";' " +
                    "'level=\"" + level_1 + "\"';")
            field_name_2 = do_string_sub(field_name, **time_info2)
            level_2 = do_string_sub(level, **time_info2)
            lead2 = ("'name=\"" + field_name_2 + "\"; " +
                     "level=\"" + level_2 + "\";'")

        self.add_input_file(file1, lead)
        self.add_input_file(file2, lead2)

        return True


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

        in_accum = time_string_to_met_time(in_accum, 'H')

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # if LOOKBACK is set, use that instead of obs_level
        # and use obs_level as field level
        if self.c_dict[data_src+'_LOOKBACK']:
            out_accum = self.c_dict[data_src+'_LOOKBACK']
        else:
            out_accum = var_info[data_src.lower()+'_level']
            if out_accum[0].isalpha():
                out_accum = out_accum[1:]

            self.logger.warning(f'{data_src}_PCP_COMBINE_LOOKBACK is '
                                f'not set. Using {out_accum} from '
                                f'{data_src}_VAR{var_info.get("index")}_LEVELS'
                                '. It is recommended that you explicitly set '
                                'the output accumulation.')

        if self.c_dict[data_src+'_OUTPUT_NAME']:
            self.output_name = self.c_dict[data_src+'_OUTPUT_NAME']
        else:
            self.output_name = var_info[f"{data_src.lower()}_name"]
            self.logger.warning(f'{data_src}_PCP_COMBINE_OUTPUT_NAME is '
                                f'not set. Using {self.output_name} from '
                                f'{data_src}_VAR{var_info.get("index")}_NAME.')

        # set field name and level if set in config
        if self.c_dict[f'{data_src}_NAMES']:
            self.field_name = self.c_dict[f'{data_src}_NAMES'][0]

        if self.c_dict[f'{data_src}_LEVELS']:
            self.field_level = self.c_dict[f'{data_src}_LEVELS'][0]

        if self.c_dict[f'{data_src}_OPTIONS']:
            self.field_extra = do_string_sub(
                self.c_dict[f'{data_src}_OPTIONS'][0],
                **time_info
            )

        init_time = time_info['init'].strftime('%Y%m%d_%H%M%S')
        valid_time = time_info['valid'].strftime('%Y%m%d_%H%M%S')

        time_info['level'] = get_seconds_from_string(out_accum,
                                                     'H',
                                                     time_info['valid'])

        out_accum = time_string_to_met_time(out_accum, 'H')

        pcp_regex = util.template_to_regex(in_template, time_info,
                                          self.logger)
        pcp_regex_split = pcp_regex.split('/')
        pcp_dir = os.path.join(in_dir, *pcp_regex_split[0:-1])
        pcp_regex = pcp_regex_split[-1]

        # set arguments
        self.args.append('-sum')
        self.args.append(init_time)
        self.args.append(in_accum)
        self.args.append(valid_time)
        self.args.append(out_accum)
        self.args.append(f"-pcpdir {pcp_dir}")
        self.args.append(f"-pcprx {pcp_regex}")

        self.outdir = out_dir
        pcp_out = do_string_sub(out_template,
                                **time_info)
        self.outfile = pcp_out

        return True


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
        if self.c_dict[f"{data_src}_LOOKBACK"]:
            accum_string = self.c_dict[f"{data_src}_LOOKBACK"]
        else:
            level = var_info[f'{data_src.lower()}_level']
            _, accum_string = util.split_level(level)

            self.logger.warning(f'{data_src}_PCP_COMBINE_LOOKBACK is '
                                f'not set. Using {accum_string} from '
                                f'{data_src}_VAR{var_info.get("index")}_LEVELS'
                                '. It is recommended that you explicitly set '
                                'the output accumulation.')

        if self.c_dict[f"{data_src}_OUTPUT_NAME"]:
            field_name = self.c_dict[f"{data_src}_OUTPUT_NAME"]
        else:
            field_name = var_info[f"{data_src.lower()}_name"]

            self.logger.warning(f'{data_src}_PCP_COMBINE_OUTPUT_NAME is '
                                f'not set. Using {field_name} from '
                                f'{data_src}_VAR{var_info.get("index")}_NAME.')

        # get number of seconds relative to valid time
        accum_seconds = get_seconds_from_string(
            accum_string,
            default_unit='H',
            valid_time=time_info['valid']
        )
        if accum_seconds is None:
            self.log_error(f'Invalid accumulation specified: {accum_string}')
            return False

        # create list of tuples for input levels and optional field names
        self.build_input_accum_list(data_src, time_info)

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.input_dir = in_dir

        if not self.get_accumulation(time_info, accum_string, data_src):
            self.log_error(f'Could not find files to build accumulation in '
                           f'{in_dir} using template {in_template}')
            return False

        self.outdir = out_dir
        time_info['level'] = int(accum_seconds)
        pcp_out = do_string_sub(out_template,
                                **time_info)
        self.outfile = pcp_out
        self.args.append("-name " + field_name)
        return True

    def setup_derive_method(self, time_info, var_info, data_src):
        """!Setup pcp_combine to derive stats
        Args:
          @param time_info dictionary containing timing information
          @param var_info object containing variable information
          @param data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        if self.c_dict[f"{data_src}_NAMES"]:
            self.field_name = self.c_dict[f"{data_src}_NAMES"][0]

        if self.c_dict[f"{data_src}_LEVELS"]:
            self.field_level = self.c_dict[f"{data_src}_LEVELS"][0]

        if self.c_dict[f"{data_src}_OUTPUT_NAME"]:
            self.output_name = self.c_dict[f"{data_src}_OUTPUT_NAME"]
            # if list of output names, remove whitespace between items
            self.output_name = [name.strip()
                                for name in self.output_name.split(',')]
            self.output_name = ','.join(self.output_name)

        if self.c_dict[f"{data_src}_OPTIONS"]:
            self.field_extra = do_string_sub(
                self.c_dict[f'{data_src}_OPTIONS'][0],
                **time_info
            )

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.input_dir = in_dir

        # create list of tuples for input levels and optional field names
        self.build_input_accum_list(data_src, time_info)

        # get files
        lookback = self.c_dict[data_src+'_LOOKBACK']
        lookback_seconds = get_seconds_from_string(
            lookback,
            default_unit='H',
            valid_time=time_info['valid']
        )
        if lookback_seconds is None:
            self.log_error(f'Invalid format for derived lookback: {lookback}')
            return False

        # if no lookback is specified, get files using the template without
        # using the get accumulation logic
        if lookback_seconds == 0:
            self.logger.debug(f"{data_src}_PCP_COMBINE_LOOKBACK unset "
                              "or set to 0. Using template to find files.")
            accum_dict = self.c_dict['ACCUM_DICT_LIST'][0]
            addon = self.get_addon(accum_dict, 0, time_info.get('valid', ''))
            input_files = self.find_data(time_info,
                                         var_info,
                                         data_type=data_src,
                                         return_list=True)
            if not input_files:
                return False

            for input_file in input_files:
                self.add_input_file(input_file, addon)

        elif not self.get_accumulation(time_info,
                                       lookback,
                                       data_src):
            self.log_error(f'Could not find files in {in_dir} '
                           f'using template {in_template}')
            return False

        # set output
        self.outdir = out_dir
        time_info['level'] = lookback_seconds
        pcp_out = do_string_sub(out_template,
                                **time_info)
        self.outfile = pcp_out

        # set STAT_LIST for data type (FCST/OBS)
        self.c_dict['STAT_LIST'] = self.c_dict[f"{data_src}_STAT_LIST"]
        return True

    def setup_user_method(self, time_info, data_src):
        """!Setup pcp_combine to call user defined command
        Args:
          @param time_info dictionary containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        command_template = self.config.getraw(
            'config',
            f'{data_src}_PCP_COMBINE_COMMAND'
        )
        user_command = do_string_sub(command_template, **time_info)
        self.args.extend(user_command.split())

        # get output accumulation in case output template uses level
        accum_string = '0'
        if self.c_dict[f"{data_src}_LOOKBACK"]:
            accum_string = self.c_dict[f"{data_src}_LOOKBACK"]
            _, accum_string = util.split_level(accum_string)

        accum_seconds = get_seconds_from_string(accum_string, 'H')
        if accum_seconds is not None:
            time_info['level'] = int(accum_seconds)

        # add output path to user defined command
        self.outdir, out_template = self.get_dir_and_template(data_src,
                                                              'OUTPUT')

        self.outfile = do_string_sub(out_template,
                                     **time_info)

        return True

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
        for accum, level, name, extra in zip(accum_list, level_list, name_list,
                                             extra_list):

            template = None
            # if accum is forecast lead, set amount to 999999 and save template
            if 'lead' in accum:
                template = accum
                accum = '9999999S'

            # convert accum amount to seconds from time string
            amount = get_seconds_from_string(accum, 'H', time_info['valid'])

            accum_dict_list.append({'amount': amount,
                                    'name': name,
                                    'level': level,
                                    'template': template,
                                    'extra': extra})

        self.c_dict['ACCUM_DICT_LIST'] = accum_dict_list
