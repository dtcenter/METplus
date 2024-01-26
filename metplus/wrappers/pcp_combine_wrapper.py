'''
Program Name: pcp_combine_wrapper.py
Contact(s): George McCabe
Abstract: Builds commands to run MET tool pcp_combine
'''

import os
from datetime import timedelta

from ..util import do_string_sub, getlist, preprocess_file
from ..util import get_seconds_from_string, ti_get_lead_string, ti_calculate
from ..util import get_relativedelta, ti_get_seconds_from_relativedelta
from ..util import time_string_to_met_time, seconds_to_met_time
from ..util import parse_var_list, template_to_regex, split_level
from ..util import add_field_info_to_time_info, sub_var_list
from . import ReformatGriddedWrapper

'''!@namespace PCPCombineWrapper
@brief Wraps the MET tool pcp_combine to combine/divide
precipitation accumulations or derive additional fields
'''


class PCPCombineWrapper(ReformatGriddedWrapper):
    """! Wraps the MET tool pcp_combine to combine or divide
         precipitation accumulations """

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    # valid values for [FCST/OBS]_PCP_COMBINE_METHOD
    valid_run_methods = ['ADD', 'SUM', 'SUBTRACT', 'DERIVE', 'USER_DEFINED']

    def __init__(self, config, instance=None):
        self.app_name = 'pcp_combine'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

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
            c_dict['VAR_LIST_FCST'] = parse_var_list(
                self.config,
                data_type='FCST',
                met_tool=self.app_name
            )
        if obs_run:
            c_dict = self.set_fcst_or_obs_dict_items('OBS', c_dict)
            c_dict['VAR_LIST_OBS'] = parse_var_list(
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
            for _ in range(fill_num):
                c_dict[f'{d_type}_EXTRA_LEVELS'].append(None)

        c_dict[f'{d_type}_EXTRA_OUTPUT_NAMES'] = getlist(
            self.config.getraw('config',
                               f'{d_type}_PCP_COMBINE_EXTRA_OUTPUT_NAMES', '')
        )

        c_dict[f'{d_type}_USE_ZERO_ACCUM'] = self.config.getbool(
            'config',
            f'{d_type}_PCP_COMBINE_USE_ZERO_ACCUM', False
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

    def run_at_time_once(self, time_info):
        var_list = sub_var_list(self.c_dict['VAR_LIST'], time_info)
        data_src = self.c_dict['DATA_SRC']

        if not var_list:
            var_list = [None]

        for var_info in var_list:
            self.run_at_time_one_field(time_info, var_info, data_src)

    def run_at_time_one_field(self, time_info, var_info, data_src):

        self.clear()

        method = self.c_dict[data_src+'_RUN_METHOD']

        self.c_dict['OUTPUT_DIR'] = self.c_dict[f'{data_src}_OUTPUT_DIR']
        self.c_dict['OUTPUT_TEMPLATE'] = (
            self.c_dict[f'{data_src}_OUTPUT_TEMPLATE']
        )

        # get lookback/output accum seconds and add it to time info dictionary
        lookback_seconds = self._get_lookback_seconds(time_info=time_info,
                                                      var_info=var_info,
                                                      data_src=data_src)
        if lookback_seconds is None:
            return False

        time_info['level'] = lookback_seconds
        add_field_info_to_time_info(time_info, var_info)

        # if method is not USER_DEFINED or DERIVE,
        # check that field information is set
        if method == "USER_DEFINED":
            can_run = self.setup_user_method(time_info, data_src)
        elif method == "DERIVE":
            can_run = self.setup_derive_method(time_info, lookback_seconds,
                                               data_src)
        elif method == "ADD":
            can_run = self.setup_add_method(time_info, lookback_seconds,
                                            data_src)
        elif method == "SUM":
            can_run = self.setup_sum_method(time_info, lookback_seconds,
                                            data_src)
        elif method == "SUBTRACT":
            can_run = self.setup_subtract_method(time_info, lookback_seconds,
                                                 data_src)
        else:
            can_run = None

        if not can_run:
            self.log_error("pcp_combine could not generate command")
            return False

        # set time info level back to lookback seconds
        time_info['level'] = lookback_seconds

        self._handle_extra_field_arguments(data_src, time_info)

        # add -name argument
        output_name = self.c_dict.get(f'{data_src}_OUTPUT_NAME')
        if not output_name and var_info:
            output_name = var_info.get(f"{data_src.lower()}_name")
            self.logger.warning(
                f'{data_src}_PCP_COMBINE_OUTPUT_NAME is '
                f'not set. Using {output_name} from '
                f'{data_src}_VAR{var_info.get("index")}_NAME.'
            )

        if output_name:
            self._handle_name_argument(output_name, data_src)

        if not self.find_and_check_output_file(time_info=time_info):
            return True

        # set user environment variables if needed and print all envs
        self.set_environment_variables(time_info)

        return self.build()

    def setup_user_method(self, time_info, data_src):
        """! Setup pcp_combine to call user defined command

          @param time_info dictionary containing timing information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file
        """
        command_template = self.config.getraw(
            'config',
            f'{data_src}_PCP_COMBINE_COMMAND'
        )
        user_command = do_string_sub(command_template, **time_info)
        self.args.extend(user_command.split())

        return True

    def setup_subtract_method(self, time_info, accum, data_src):
        """! Setup pcp_combine to subtract two files to build accumulation

          @param time_info object containing timing information
          @param accum accumulation amount to compute in seconds
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file
        """
        self.args.append('-subtract')

        lead = time_info['lead_seconds']
        lead2 = lead - accum

        self.logger.debug(
            f"Attempting to build {ti_get_lead_string(accum, False)} "
            f"accumulation by subtracting {ti_get_lead_string(lead2, False)} "
            f"from {ti_get_lead_string(lead, False)}."
        )

        files_found = []

        full_template = os.path.join(self.c_dict[f'{data_src}_INPUT_DIR'],
                                     self.c_dict[f'{data_src}_INPUT_TEMPLATE'])

        # get first file
        filepath1 = do_string_sub(full_template, **time_info)
        file1 = preprocess_file(filepath1,
                                self.c_dict[data_src+'_INPUT_DATATYPE'],
                                self.config)

        if file1 is None:
            self.log_error(f'Could not find {data_src} file {filepath1} '
                           f'using template {full_template}')
            return None

        # handle field information
        field_args = {}
        if self.c_dict.get(f"{data_src}_NAMES"):
            field_args['name'] = self.c_dict[f"{data_src}_NAMES"][0]

        if self.c_dict.get(f"{data_src}_LEVELS"):
            field_args['level'] = self.c_dict[f"{data_src}_LEVELS"][0]

        if self.c_dict.get(f"{data_src}_OPTIONS"):
            field_args['extra'] = self.c_dict[f"{data_src}_OPTIONS"][0]

        # if data is GRIB and second lead is 0, then
        # run PCPCombine in -add mode with just the first file
        if lead2 == 0 and not self.c_dict[f'{data_src}_USE_ZERO_ACCUM']:
            self.logger.info("Subtracted accumulation is 0,"
                             " so running ADD mode on one file."
                             "To use 0 accum data, set "
                             f"{data_src}_PCP_COMBINE_USE_ZERO_ACCUM = True")
            self.args.clear()
            self.args.append('-add')
            field_info = self.get_field_string(
                time_info=time_info,
                search_accum=seconds_to_met_time(lead),
                **field_args
            )
            self.args.append(file1)
            self.args.append(field_info)
            files_found.append((file1, field_info))
            return files_found

        # else continue building -subtract command

        # set time info for second lead
        input_dict2 = {'init': time_info['init'],
                       'lead': lead2}
        time_info2 = ti_calculate(input_dict2)
        time_info2['level'] = accum
        time_info2['custom'] = time_info.get('custom', '')

        filepath2 = do_string_sub(full_template, **time_info2)
        file2 = preprocess_file(filepath2,
                                self.c_dict[data_src+'_INPUT_DATATYPE'],
                                self.config)

        if file2 is None:
            self.log_error(f'Could not find {data_src} file {filepath2} '
                           f'using template {full_template}')
            return None

        field_info1 = self.get_field_string(
            time_info=time_info,
            search_accum=seconds_to_met_time(lead),
            **field_args
        )
        field_info2 = self.get_field_string(
            time_info=time_info2,
            search_accum=seconds_to_met_time(lead2),
            **field_args
        )

        self.args.append(file1)
        self.args.append(field_info1)

        self.args.append(file2)
        self.args.append(field_info2)
        files_found.append((file1, field_info1))
        files_found.append((file2, field_info2))

        return files_found

    def setup_sum_method(self, time_info, lookback, data_src):
        """! Setup pcp_combine to build desired accumulation based on
        init/valid times and accumulations

          @param time_info object containing timing information
          @param lookback accumulation amount to compute in seconds
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file
        """
        self.args.append('-sum')

        if self.c_dict[f"{data_src}_ACCUMS"]:
            in_accum = self.c_dict[data_src+'_ACCUMS'][0]
        else:
            in_accum = 0

        in_accum = time_string_to_met_time(in_accum, 'H')
        out_accum = time_string_to_met_time(lookback, 'S')

        time_info['level'] = in_accum
        pcp_regex = template_to_regex(
            self.c_dict[f'{data_src}_INPUT_TEMPLATE']
        )
        pcp_regex = do_string_sub(pcp_regex, **time_info)
        pcp_regex_split = pcp_regex.split('/')
        pcp_dir = os.path.join(self.c_dict[f'{data_src}_INPUT_DIR'],
                               *pcp_regex_split[0:-1])
        pcp_regex = pcp_regex_split[-1]

        # set arguments
        # init time
        self.args.append(time_info['init'].strftime('%Y%m%d_%H%M%S'))
        # input accum
        self.args.append(in_accum)
        # valid time
        self.args.append(time_info['valid'].strftime('%Y%m%d_%H%M%S'))
        # output accum
        self.args.append(out_accum)
        self.args.append(f"-pcpdir {pcp_dir}")
        self.args.append(f"-pcprx {pcp_regex}")

        # set -field name and level if set in config
        self._handle_field_argument(data_src, time_info)

        return True

    def setup_add_method(self, time_info, lookback, data_src):
        """! Setup pcp_combine to add files to build desired accumulation

          @param time_info dictionary containing timing information
          @param lookback accumulation amount to compute in seconds
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file
        """
        self.args.append('-add')

        # create list of tuples for input levels and optional field names
        self._build_input_accum_list(data_src, time_info)

        self.run_count += 1
        files_found = self.get_accumulation(time_info, lookback, data_src)
        if not files_found:
            self.missing_input_count += 1
            self.log_error(
                f'Could not find files to build accumulation in '
                f"{self.c_dict[f'{data_src}_INPUT_DIR']} using template "
                f"{self.c_dict[f'{data_src}_INPUT_TEMPLATE']}")
            return False

        return files_found

    def setup_derive_method(self, time_info, lookback, data_src):
        """! Setup pcp_combine to derive stats

          @param time_info dictionary containing timing information
          @param lookback accumulation amount to compute in seconds
          @param data_src data type (FCST or OBS)
          @rtype string
          @return path to output file
        """
        self.args.append('-derive')

        # add list of statistics
        self.args.append(','.join(self.c_dict[f"{data_src}_STAT_LIST"]))

        # create list of tuples for input levels and optional field names
        self._build_input_accum_list(data_src, time_info)

        # if no lookback is specified, get files using the template without
        # using the get accumulation logic
        if not lookback:
            self.logger.debug(f"{data_src}_PCP_COMBINE_LOOKBACK unset "
                              "or set to 0. Using template to find files.")
            accum_dict = self.c_dict['ACCUM_DICT_LIST'][0]
            field_info = self.get_field_string(time_info=time_info,
                                               search_accum=0,
                                               name=accum_dict['name'],
                                               level=accum_dict['level'],
                                               extra=accum_dict['extra'])
            self.run_count += 1
            input_files = self.find_data(time_info,
                                         data_type=data_src,
                                         return_list=True)
            if not input_files:
                self.missing_input_count += 1
                return None

            files_found = []
            for input_file in input_files:
                # exclude field info and set it with -field
                self.args.append(input_file)
                files_found.append((input_file, field_info))

        else:
            self.run_count += 1
            files_found = self.get_accumulation(time_info,
                                                lookback,
                                                data_src,
                                                field_info_after_file=False)
            if not files_found:
                self.missing_input_count += 1
                self.log_error(
                    f'Could not find files to build accumulation in '
                    f"{self.c_dict[f'{data_src}_INPUT_DIR']} using template "
                    f"{self.c_dict[f'{data_src}_INPUT_TEMPLATE']}")
                return None

        # set -field name and level from first file field info
        self.args.append(f'-field {files_found[0][1]}')

        return files_found

    def _handle_lookback(self, c_dict, d_type):
        """! Get value for lookback time from config.
        [FCST/OBS]_PCP_COMBINE_LOOKBACK is used if set. If not, use synonyms
        [FCST/OBS]_PCP_COMBINE_DERIVE_LOOKBACK or
        [FCST/OBS]_PCP_COMBINE_OUTPUT_ACCUM. Priority of synonyms is based on
        run method (derive mode prioritizes DERIVE_LOOKBACK, all other
        prioritize OUTPUT_ACCUM). This is done because we want to handle the
        lookback with the same value for all run methods, but the clearest
        name depending on the method.

            @param c_dict config dictionary to populate
            @param d_type data type (FCST or OBS)
            @returns lookback time / desired accumulation in seconds
        """
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

        # if none of the variables are set, return None
        return None

    def _get_lookback_seconds(self, time_info, var_info, data_src):
        if self.c_dict[f"{data_src}_LOOKBACK"]:
            lookback = self.c_dict[f"{data_src}_LOOKBACK"]
        elif var_info:
                lookback = var_info[f'{data_src.lower()}_level']
                self.logger.warning(
                    f'{data_src}_PCP_COMBINE_LOOKBACK is '
                    f'not set. Using {lookback} from '
                    f'{data_src}_VAR{var_info.get("index")}_LEVELS'
                    '. It is recommended that you explicitly set '
                    'the output accumulation.')
        else:
            lookback = '0'

        _, lookback = split_level(lookback)

        lookback_seconds = get_seconds_from_string(
            lookback,
            default_unit='H',
            valid_time=time_info['valid']
        )
        if lookback_seconds is None:
            self.log_error(f'Invalid format for derived lookback: {lookback}')

        return lookback_seconds

    def get_accumulation(self, time_info, accum, data_src,
                         field_info_after_file=True):
        """! Find files to combine to build the desired accumulation

          @param time_info dictionary containing time information
          @param accum desired accumulation to build in seconds
          @param data_src type of data (FCST or OBS)
          @rtype bool
          @return True if full set of files to build accumulation is found
        """
        search_time = time_info['valid']
        custom = time_info.get('custom', '')
        # last time to search is the output accumulation subtracted from the
        # valid time, then add back the smallest accumulation that is available
        # in the input. This is done because data contains an accumulation from
        # the file/field time backwards in time
        # If building 6 hour accumulation from 1 hour accumulation files,
        # last time to process is valid - 6 + 1
        accum_relative = get_relativedelta(accum, 'S')
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

        files_found = []

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

                search_file, lead = self.find_input_file(time_info['init'],
                                                         search_time,
                                                         accum_dict['amount'],
                                                         data_src,
                                                         custom)

                if not search_file:
                    continue

                # if found a file, add it to input list with info
                # if template is used in accum, find value and
                # apply bucket interval is set
                if accum_dict['template'] is not None:
                    accum_amount = self.get_template_accum(accum_dict,
                                                           search_time,
                                                           lead,
                                                           data_src,
                                                           custom)
                    if accum_amount > total_accum:
                        self.logger.debug("Accumulation amount is bigger "
                                          "than remaining accumulation.")
                        continue
                else:
                    accum_amount = accum_dict['amount']

                search_time_info = {
                    'valid': search_time,
                    'lead': lead,
                }
                field_info = self.get_field_string(
                    time_info=search_time_info,
                    search_accum=time_string_to_met_time(accum_amount),
                    name=accum_dict['name'],
                    level=accum_dict['level'],
                    extra=accum_dict['extra']
                )
                # add file to input list and step back to find more data
                self.args.append(search_file)
                if field_info_after_file:
                    self.args.append(field_info)

                files_found.append((search_file, field_info))
                self.logger.debug(f"Adding input file: {search_file} "
                                  f"with {field_info}")
                search_time -= timedelta(seconds=accum_amount)
                total_accum -= accum_amount
                found = True
                break

            # if we don't need any more accumulation, break out of loop and run
            if not total_accum:
                break

            # if we still need to find more accum but we couldn't find it, fail
            if not found:
                return None

        # fail if no files were found or if we didn't find
        #  the entire accumulation needed
        if not files_found or total_accum:
            return None

        return files_found

    def get_lowest_fcst_file(self, valid_time, data_src, custom):
        """! Find the lowest forecast hour that corresponds to the valid time

          @param valid_time valid time to search
          @param data_src data type (FCST or OBS) to get filename template
          @param custom string from custom loop list to use in template sub
          @rtype string
          @return Path to file with the lowest forecast hour
    """
        # search for file with lowest forecast,
        # then loop up into you find a valid one
        min_forecast = get_seconds_from_string(
            self.c_dict[data_src+'_MIN_FORECAST'], 'H'
        )
        max_forecast = get_seconds_from_string(
            self.c_dict[data_src+'_MAX_FORECAST'], 'H'
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
            input_dict = {
                'valid': valid_time,
                'lead_seconds': forecast_lead
            }
            time_info = ti_calculate(input_dict)
            time_info['custom'] = custom
            search_file = os.path.join(self.c_dict[f'{data_src}_INPUT_DIR'],
                                       self.c_dict[data_src+'_INPUT_TEMPLATE'])
            search_file = do_string_sub(search_file, **time_info)
            self.logger.debug(f"Looking for {search_file}")

            search_file = preprocess_file(
                search_file,
                self.c_dict[data_src+'_INPUT_DATATYPE'],
                self.config)

            if search_file is not None:
                return search_file, forecast_lead
            forecast_lead += smallest_input_accum

        return None, 0

    def get_field_string(self, time_info=None, search_accum=0, name=None,
                         level=None, extra=None):
        if name is None:
            name = 'APCP'
            level = f'A{str(search_accum).zfill(2)}'
            self.logger.debug("Field name not specified. Assuming "
                              f"{name}/{level}")

        field_info = self.get_field_info(v_name=name,
                                         v_level=level,
                                         v_extra=extra,
                                         add_curly_braces=False)[0]

        # string sub values into full field info string using search time info
        if time_info:
            field_info = do_string_sub(field_info, **time_info)
        return field_info

    def find_input_file(self, init_time, valid_time, search_accum, data_src,
                        custom):
        lead = 0

        in_template = self.c_dict[data_src+'_INPUT_TEMPLATE']

        if ('{lead?' in in_template or
                ('{init?' in in_template and '{valid?' in in_template)):
            if not self.c_dict[f'{data_src}_CONSTANT_INIT']:
                return self.get_lowest_fcst_file(valid_time, data_src, custom)

            # set init time and lead in time dict if init should be constant
            # ti_calculate cannot currently handle both init and valid
            lead = (valid_time - init_time).total_seconds()
            input_dict = {'init': init_time, 'lead': lead}
        else:
            if self.c_dict[f'{data_src}_CONSTANT_INIT']:
                input_dict = {'init': init_time}
            else:
                input_dict = {'valid': valid_time}

        time_info = ti_calculate(input_dict)
        time_info['custom'] = custom
        time_info['level'] = int(search_accum)
        input_path = os.path.join(self.c_dict[f'{data_src}_INPUT_DIR'],
                                  in_template)
        input_path = do_string_sub(input_path, **time_info)

        return preprocess_file(input_path,
                               self.c_dict[f'{data_src}_INPUT_DATATYPE'],
                               self.config), lead

    def get_template_accum(self, accum_dict, search_time, lead, data_src,
                           custom):
        # apply string substitution to accum amount
        search_time_dict = {'valid': search_time, 'lead_seconds': lead}
        search_time_info = ti_calculate(search_time_dict)
        search_time_info['custom'] = custom
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

    def get_command(self):

        cmd = (f"{self.app_path} -v {self.c_dict['VERBOSITY']} "
               f"{' '.join(self.args)} {self.get_output_path()}")
        return cmd

    def _handle_extra_field_arguments(self, data_src, time_info=None):
        extra_names = self.c_dict.get(data_src + '_EXTRA_NAMES')
        if not extra_names:
            return

        extra_levels = self.c_dict.get(data_src + '_EXTRA_LEVELS')
        for name, level in zip(extra_names, extra_levels):
            field_string = self.get_field_string(time_info=time_info,
                                                 name=name,
                                                 level=level)
            field_format = f"-field {field_string}"
            self.args.append(field_format)

    def _handle_field_argument(self, data_src, time_info):
        if not self.c_dict[f'{data_src}_NAMES']:
            return

        field_args = {'name': self.c_dict[f'{data_src}_NAMES'][0]}

        if self.c_dict[f'{data_src}_LEVELS']:
            field_args['level'] = self.c_dict[f'{data_src}_LEVELS'][0]

        if self.c_dict[f'{data_src}_OPTIONS']:
            field_args['extra'] = self.c_dict[f'{data_src}_OPTIONS'][0]

        field_string = self.get_field_string(time_info=time_info,
                                             **field_args)
        field_string = f'-field {field_string}'
        self.args.append(field_string)

    def _handle_name_argument(self, output_name, data_src):
        if not output_name:
            return

        # if list of output names, remove whitespace between items
        output_names = [name.strip() for name in output_name.split(',')]

        # handle extra output names if specified
        extra_output_names = self.c_dict.get(data_src + '_EXTRA_OUTPUT_NAMES')
        if extra_output_names:
            output_names.extend(extra_output_names)

        name_format = '","'.join(output_names)
        name_format = f'-name "{name_format}"'
        self.args.append(name_format)

    def _build_input_accum_list(self, data_src, time_info):
        accum_list = self.c_dict[data_src + '_ACCUMS']
        level_list = self.c_dict[data_src + '_LEVELS']
        name_list = self.c_dict[data_src + '_NAMES']
        extra_list = self.c_dict[data_src + '_OPTIONS']

        # if no list, create list of None values
        if not name_list:
            name_list = [None] * len(accum_list)
        if not level_list:
            level_list = [None] * len(accum_list)
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
