#!/usr/bin/env python

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

from __future__ import (print_function, division)

import os
import met_util as util
import datetime
import string_template_substitution as sts

from reformat_gridded_wrapper import ReformatGriddedWrapper
import time_util

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
    def __init__(self, config, logger):
        super(PCPCombineWrapper, self).__init__(config, logger)
        self.app_name = 'pcp_combine'
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)
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
        self.logfile = ""
        self.compress = -1
        self.custom_command = ''

    def create_c_dict(self):
        c_dict = super(PCPCombineWrapper, self).create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_PCP_COMBINE_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['SKIP_IF_OUTPUT_EXISTS'] = self.config.getbool('config', 'PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS', False)

        if self.config.getbool('config', 'FCST_PCP_COMBINE_RUN', False):
            c_dict = self.set_fcst_or_obs_dict_items('FCST', c_dict)

        if self.config.getbool('config', 'OBS_PCP_COMBINE_RUN', False):
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
        c_dict[d_type+'_OUTPUT_ACCUM'] = self.config.getstr('config', d_type+'_PCP_COMBINE_OUTPUT_ACCUM', '')
        c_dict[d_type+'_OUTPUT_NAME'] = self.config.getstr('config', d_type+'_PCP_COMBINE_OUTPUT_NAME', '')
        c_dict[d_type+'_OUTPUT_EXTRA'] = self.config.getstr('config', d_type+'_PCP_COMBINE_OUTPUT_EXTRA', '')
        c_dict[d_type+'_INPUT_DIR'] = self.config.getdir(d_type+'_PCP_COMBINE_INPUT_DIR', '')
        c_dict[d_type+'_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                              d_type+'_PCP_COMBINE_INPUT_TEMPLATE', '')
        c_dict[d_type+'_OUTPUT_DIR'] = self.config.getdir(d_type+'_PCP_COMBINE_OUTPUT_DIR', '')
        c_dict[d_type+'_OUTPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                     d_type+'_PCP_COMBINE_OUTPUT_TEMPLATE')
        c_dict[d_type+'_STAT_LIST'] = \
            util.getlist(self.config.getstr('config',
                                       d_type+'_PCP_COMBINE_STAT_LIST', ''))

        c_dict[d_type+'_RUN_METHOD'] = \
            self.config.getstr('config', d_type+'_PCP_COMBINE_METHOD')

        if c_dict[d_type+'_RUN_METHOD'] == 'DERIVE' and \
           len(c_dict[d_type+'_STAT_LIST']) == 0:
            self.logger.error('Statistic list is empty. ' + \
              'Must set ' + d_type + '_PCP_COMBINE_STAT_LIST if running ' +\
                              'derive mode')
            exit(1)

        c_dict[d_type+'_DERIVE_LOOKBACK'] = \
            self.config.getint('config', d_type+'_PCP_COMBINE_DERIVE_LOOKBACK', 0)

        c_dict[d_type+'_BUCKET_INTERVAL'] = self.config.getseconds('config',
                                                                   d_type+'_PCP_COMBINE_BUCKET_INTERVAL',
                                                                   0)

        return c_dict

    def clear(self):
        super(PCPCombineWrapper, self).clear()
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
        self.logfile = ""
        self.compress = -1
        self.custom_command = ''

    def add_input_file(self, filename, addon):
        self.infiles.append(filename)
        self.inaddons.append(str(addon))

    def get_dir_and_template(self, data_type, in_or_out):
        dirr = self.c_dict[data_type+'_'+in_or_out+'_DIR']
        template = self.c_dict[data_type+'_'+in_or_out+'_TEMPLATE']

        if dirr is '':
            self.logger.error(data_type+'_PCP_COMBINE_'+in_or_out+'_DIR must be set.')
            exit(1)

        if template is '' and self.method != 'SUM':
            self.logger.error(data_type+'_PCP_COMBINE_'+in_or_out+'_TEMPLATE must be set.')
            exit(1)

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
            fSts = sts.StringSub(self.logger,
                                 template,
                                 **time_info)
            search_file = os.path.join(self.input_dir,
                                       fSts.do_string_sub())

            search_file = util.preprocess_file(search_file,
                                self.c_dict[dtype+'_INPUT_DATATYPE'],
                                               self.config)

            if search_file is not None:
                return search_file, forecast_lead
            forecast_lead += smallest_input_accum
        return None

    def get_daily_file(self, time_info, accum, data_src, file_template):
        """!Pull accumulation out of file that contains a full day of data
        Args:
          @param valid_time valid time to search
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
            dSts = sts.StringSub(self.logger,
                                 file_template,
                                 valid=search_time)
            search_file = os.path.join(self.input_dir,
                                       dSts.do_string_sub())
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
        search_time_info = { 'valid' : search_time }

        # get name of input level item that matches the accumulation to extract from daily file
        accum_seconds = time_util.get_seconds_from_string(accum, 'H')
        accum_dict_list = self.c_dict['ACCUM_DICT_LIST']
        fname = next((item['name'] for item in accum_dict_list if item['amount'] == accum_seconds), '-1')
        # if accumulation was not found in levels dictionary list, error and return
        if fname == '-1':
            self.logger.error(f'Accumulation {accum} was not specified in the {data_src}'
                              '_PCP_COMBINE_INPUT_ACCUMS list')
            return False

        # if name was not set in the input levels list, use accumulation time in MET time format
        if fname is None:
            addon = time_util.time_string_to_met_time(accum, default_unit='S')
        else:
            fname = sts.StringSub(self.logger, fname, **search_time_info).do_string_sub()
            addon = "'name=\"" + fname + "\";"

            # if name is a python script, don't set level
            if not util.is_python_script(fname):
                addon += " level=\"(" + str(lead) + ",*,*)\";"

            addon += "'"

        self.add_input_file(search_file, addon)
        return True

    def get_addon(self, field_name, search_accum, search_time, field_level):
        if field_name is not None:
            # perform string substitution on name in case it uses filename templates
            field_name = sts.StringSub(self.logger, field_name, valid=search_time).do_string_sub()
            addon = "'name=\"" + field_name + "\";"
            if not util.is_python_script(field_name):
                if field_level is not None:
                    addon += f" level=\"{field_level}\";"

            addon += "'"
        else:
            addon = search_accum

        return addon

    def find_input_file(self, in_template, search_time, search_accum, data_src):
        if '{lead?' in in_template or ('{init?' in in_template and '{valid?' in in_template) :
            return self.getLowestForecastFile(search_time, data_src, in_template)

        fSts = sts.StringSub(self.logger,
                             in_template,
                             valid=search_time,
                             level=(int(search_accum)))
        search_file = os.path.join(self.input_dir,
                                   fSts.do_string_sub())

        return util.preprocess_file(search_file,
                                    self.c_dict[data_src+'_INPUT_DATATYPE'],
                                    self.config), 0

    def get_template_accum(self, accum_dict, search_time, lead, data_src):
        # apply string substitution to accum amount
        search_time_dict = {'valid': search_time, 'lead_seconds': lead}
        search_time_info = time_util.ti_calculate(search_time_dict)

        amount = sts.StringSub(self.logger,
                               accum_dict['template'],
                               **search_time_info).do_string_sub()
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

                search_file, lead = self.find_input_file(in_template, search_time,
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
                    addon = self.get_addon(accum_dict['name'], accum_met_time, search_time,
                                           accum_dict['level'])
                    # add file to input list and step back in time to find more data
                    self.add_input_file(search_file, addon)
                    self.logger.debug(f"Adding input file: {search_file} with {addon}")
                    search_time = search_time - datetime.timedelta(seconds=accum_amount)
                    total_accum -= accum_amount
                    found = True
                    break

            # if we don't need any more accumulation, break out of loop and run
            if total_accum == 0:
                break

            # if we still need to find more accum but we couldn't find it, fail
            if not found:
                return False

        # fail if no files were found or if we didn't find
        #  the entire accumulation needed
        if len(self.infiles) is 0 or total_accum != 0:
            return False

        return True
        
    def get_command(self):
        if self.app_path is None:
            self.logger.error("No app path specified. You must use a subclass")
            return None

        cmd = '{} -v {} '.format(self.app_path, self.c_dict['VERBOSITY'])

        for a in self.args:
            cmd += a + " "

        if self.method == "CUSTOM":
            cmd += self.custom_command
            return cmd
        elif self.method == "SUM":
            if self.init_time == -1:
                (self.logger).error("No init time specified")
                return None

            if self.valid_time == -1:
                (self.logger).error("No valid time specified")
                return None

            if self.in_accum == -1:
                (self.logger).error("No input accumulation specified")
                return None

            if self.out_accum == -1:
                (self.logger).error("No output accumulation specified")
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
                cmd += ','.join(self.c_dict['STAT_LIST'])

            if len(self.infiles) == 0:
                (self.logger).error("No input filenames specified")
                return None

            for idx, f in enumerate(self.infiles):
                cmd += f + " "
                if self.method != 'DERIVE':
                    cmd += self.inaddons[idx] + " "


        # set -field options if set
        if self.field_name is not None:
            cmd += " -field 'name=\""+self.field_name+"\";"
            if self.field_level != "":
                cmd += " level=\""+self.field_level+"\";"
            if self.field_extra != "":
                cmd += ' ' + self.field_extra
            cmd += "' "

        if self.output_name != '':
            cmd += f' -name "{self.output_name}" '

        if self.outfile == "":
            self.logger.error("No output filename specified")
            return None

        if self.outdir == "":
            self.logger.error("No output directory specified")
            return None

        out_path = self.get_output_path()

        # create outdir (including subdir in outfile) if it doesn't exist
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        cmd += out_path

        if self.pcp_dir != "":
            cmd += " -pcpdir "+self.pcp_dir

        if self.pcp_regex != "":
            cmd += " -pcprx "+self.pcp_regex

        if self.name != "":
            cmd += " -name "+self.name

        if self.logfile != "":
            cmd += " -log "+self.logfile

        if self.compress != -1:
            cmd += " -compress "+str(self.compress)

        return cmd

    def run_at_time_once(self, time_info, var_info, data_src):
        self.clear()
        cmd = None
        self.clear()
        self.method = self.c_dict[data_src+'_RUN_METHOD'].upper()
        if self.method == "CUSTOM":
            cmd = self.setup_custom_method(time_info, data_src)
        else:
            if var_info is None and not self.c_dict[f"{data_src}_OUTPUT_ACCUM"]:
                self.logger.error('Cannot run PCPCombine without specifying fields to process '
                                  'unless running in CUSTOM mode. You must set '
                                  f'{data_src}_VAR<n>_[NAME/LEVELS] or {data_src}_OUTPUT_[NAME/LEVEL]')
                return

            if self.method == "ADD":
                cmd = self.setup_add_method(time_info, var_info, data_src)
            elif self.method == "SUM":
                cmd = self.setup_sum_method(time_info, var_info, data_src)
            elif self.method == "SUBTRACT":
                cmd = self.setup_subtract_method(time_info, var_info, data_src)
            elif self.method == "DERIVE":
                cmd = self.setup_derive_method(time_info, var_info, data_src)
            else:
                self.logger.error('Invalid ' + data_src + '_PCP_COMBINE_METHOD specified.'+\
                                  ' Options are ADD, SUM, and SUBTRACT.')
                exit(1)

        if cmd is None:
            init_time = time_info['init_fmt']
            lead = time_info['lead_hours']
            self.logger.error("pcp_combine could not generate command")
            return

        # if output file exists and we want to skip it, warn and continue
        outfile = self.get_output_path()
        if not self.method == "CUSTOM" and os.path.exists(outfile) and \
          self.c_dict['SKIP_IF_OUTPUT_EXISTS'] is True:
            self.logger.debug('Skip writing output file {} because it already '
                              'exists. Remove file or change '
                              'PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS to True to process'
                              .format(outfile))
            return True

        self.build()

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

        if self.c_dict[f"{data_src}_OUTPUT_ACCUM"]:
            accum = self.c_dict[f"{data_src}_OUTPUT_ACCUM"]
            level_type = 'A'
        else:
            level = var_info[f'{data_src.lower()}_level']
            level_type, accum = util.split_level(level)

        lead = time_info['lead_hours']
        lead2 = lead - int(accum)

        # set output file information
        outSts = sts.StringSub(self.logger,
                               out_template,
                               level=(int(accum) * 3600),
                               **time_info)
        out_file = outSts.do_string_sub()
        self.outfile = out_file
        self.outdir = out_dir

        # get first file
        pcpSts1 = sts.StringSub(self.logger,
                                in_template,
                                level=(int(accum) * 3600),
                                **time_info)
        file1_expected = os.path.join(in_dir, pcpSts1.do_string_sub())
        file1 = util.preprocess_file(file1_expected,
                                     self.c_dict[data_src+'_INPUT_DATATYPE'],
                                     self.config)

        if file1 is None:
            self.logger.error(f'Could not find {data_src} file {file1_expected} using template {in_template}')
            return None

        # if level type is A (accum) and second lead is 0, then
        # run PCPCombine in -add mode with just the first file
        if lead2 == 0 and level_type == 'A':
            self.method = 'ADD'
            self.add_input_file(file1, lead)
            return self.get_command()

        # else continue building -subtract command

        # set time info for second lead
        input_dict2 = { 'init' : time_info['init'],
                       'lead_hours' : lead2 }
        time_info2 = time_util.ti_calculate(input_dict2)
        pcpSts2 = sts.StringSub(self.logger,
                                in_template,
                                level=(int(accum) * 3600),
                                **time_info2)
        file2_expected = os.path.join(in_dir, pcpSts2.do_string_sub())
        file2 = util.preprocess_file(file2_expected,
                                     self.c_dict[data_src+'_INPUT_DATATYPE'],
                                     self.config)

        if file2 is None:
            self.logger.error(f'Could not find {data_src} file {file2_expected} using template {in_template}')
            return None

        if self.c_dict[data_src+'_INPUT_DATATYPE'] != 'GRIB':
            field_name_1 = sts.StringSub(self.logger, field_name, **time_info).do_string_sub()
            lead = "'name=\"" + field_name_1 + "\";'"
            field_name_2 = sts.StringSub(self.logger, field_name, **time_info2).do_string_sub()
            lead2 = "'name=\"" + field_name_2 + "\";'"
            # TODO: need to add level if NetCDF input - how to specify levels for each?

        self.add_input_file(file1,lead)
        self.add_input_file(file2,lead2)

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

        if self.c_dict[data_src+'_OUTPUT_NAME']:
            self.output_name = self.c_dict[data_src+'_OUTPUT_NAME']

        # set field name and level if set in config
        if self.c_dict[f'{data_src}_NAMES']:
            self.field_name = self.c_dict[f'{data_src}_NAMES'][0]
        if self.c_dict[f'{data_src}_LEVELS']:
            self.field_level = self.c_dict[f'{data_src}_LEVELS'][0]

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

        pcpSts = sts.StringSub(self.logger,
                                out_template,
                                **time_info)
        pcp_out = pcpSts.do_string_sub()
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
        if self.c_dict[f"{data_src}_OUTPUT_NAME"]:
            field_name = self.c_dict[f"{data_src}_OUTPUT_NAME"]
        else:
            field_name = var_info[f"{data_src.lower()}_name"]

        if self.c_dict[f"{data_src}_OUTPUT_ACCUM"]:
            accum_string = self.c_dict[f"{data_src}_OUTPUT_ACCUM"]
        else:
            level = var_info[f'{data_src.lower()}_level']
            _, accum_string = util.split_level(level)

        # get number of seconds relative to valid time
        accum_seconds = time_util.get_seconds_from_string(accum_string,
                                                          default_unit='H',
                                                          valid_time=time_info['valid'])
        if accum_seconds is None:
            self.logger.error(f'Invalid accumulation specified: {accum_string}')
            return

        # create list of tuples for input levels and optional field names
        if not self.build_input_accum_list(data_src, time_info):
            return

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.input_dir = in_dir

        if not self.get_accumulation(time_info, accum_string, data_src):
            self.logger.error(f'Could not find files to build accumulation in {in_dir} using template {in_template}')
            return None

        self.outdir = out_dir
        time_info['level'] = int(accum_seconds)
        pcpSts = sts.StringSub(self.logger,
                               out_template,
                               **time_info)
        pcp_out = pcpSts.do_string_sub()
        self.outfile = pcp_out
        self.args.append("-name " + field_name + "_" + accum_string)
        return self.get_command()

    def setup_derive_method(self, time_info, var_info, data_src):
        """!Setup pcp_combine to derive stats
        Args:
          @param time_info dictionary containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        # if [FCST/OBS]_OUTPUT_[NAME/ACCUM] are set, use them instead of
        # [FCST/OBS]_VAR<n>_[NAME/LEVELS]
        if self.c_dict[f"{data_src}_OUTPUT_NAME"]:
            self.field_name = self.c_dict[f"{data_src}_OUTPUT_NAME"]
        else:
            self.field_name = var_info[f"{data_src.lower()}_name"]

        if self.c_dict[f"{data_src}_OUTPUT_ACCUM"]:
            self.field_level = self.c_dict[f"{data_src}_OUTPUT_ACCUM"]
        else:
            self.field_level = var_info[f'{data_src.lower()}_level']

        if self.c_dict[f"{data_src}_OUTPUT_EXTRA"]:
            self.field_extra = self.c_dict[f"{data_src}_OUTPUT_EXTRA"]
        else:
            self.field_extra = var_info[f'{data_src.lower()}_extra']

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # get files
        lookback = self.c_dict[data_src+'_DERIVE_LOOKBACK']
        lookback_seconds = time_util.get_seconds_from_string(lookback,
                                                             default_unit='H',
                                                             valid_time=time_info['valid'])
        if lookback_seconds is None:
            self.logger.error(f'Invalid format for derived lookback: {lookback}')
            return

        if not self.get_accumulation(time_info,
                                     lookback,
                                     data_src):
            self.logger.error(f'Could not find files in {in_dir} using template {in_template}')
            return None

        # set output
        self.outdir =out_dir
        time_info['level'] = lookback_seconds
        psts = sts.StringSub(self.logger,
                                out_template,
                                **time_info)
        pcp_out = psts.do_string_sub()
        self.outfile = pcp_out
        return self.get_command()

    def setup_custom_method(self, time_info, data_src):
        """!Setup pcp_combine to derive stats
        Args:
          @param time_info dictionary containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        command_template = self.config.getraw('config', data_src + '_PCP_COMBINE_COMMAND')
        self.custom_command = sts.StringSub(self.logger, command_template, **time_info).do_string_sub()
        return '{} -v {} {}'.format(self.app_path, self.c_dict['VERBOSITY'], self.custom_command)

    def build_input_accum_list(self, data_src, time_info):
        accum_list = self.c_dict[data_src + '_ACCUMS']
        level_list = self.c_dict[data_src + '_LEVELS']
        name_list = self.c_dict[data_src + '_NAMES']

        if not accum_list:
            self.logger.error(f'{data_src}_PCP_COMBINE_INPUT_ACCUMS must be specified.')
            return False

        # name list should either be empty or the same length as accum list
        if name_list:
            if len(accum_list) != len(name_list):
                msg = f'{data_src}_PCP_COMBINE_INPUT_ACCUM_NAMES list should be ' +\
                      'either empty or the same length as ' +\
                      f'{data_src}_PCP_COMBINE_INPUT_ACCUMS list.'
                self.logger.error(msg)
                return False
        else:
            # if no name list, create list of None values
            name_list = [None] * len(accum_list)

        # do the same for level list
        if level_list:
            if len(accum_list) != len(level_list):
                msg = f'{data_src}_PCP_COMBINE_INPUT_LEVELS list should be ' +\
                      'either empty or the same length as ' +\
                      f'{data_src}_PCP_COMBINE_INPUT_ACCUMS list.'
                self.logger.error(msg)
                return False
        else:
            # if no level list, create list of None values
            level_list = [None] * len(accum_list)

        accum_dict_list = []
        for accum, level, name in zip(accum_list, level_list, name_list):

            template = None
            # if accum is forecast lead, set amount to 999999 and save template
            if 'lead' in accum:
                template = accum
                accum = '9999999S'

            # convert accum amount to seconds from time string
            amount = time_util.get_seconds_from_string(accum, 'H', time_info['valid'])

            accum_dict_list.append({'amount' : amount, 'name' : name, 'level': level, 'template': template})

        self.c_dict['ACCUM_DICT_LIST'] = accum_dict_list
        return True

if __name__ == "__main__":
    util.run_stand_alone("pcp_combine_wrapper", "PCPCombine")
