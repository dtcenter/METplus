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

'''!@namespace PcpCombineWrapper
@brief Wraps the MET tool pcp_combine to combine or divide
precipitation accumulations
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
@todo add main function to be able to run alone via command line
'''
class PcpCombineWrapper(ReformatGriddedWrapper):
    """!Wraps the MET tool pcp_combine to combine or divide
    precipitation accumulations"""
    def __init__(self, config, logger):
        super(PcpCombineWrapper, self).__init__(config, logger)
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
        self.field_name = ""
        self.field_level = ""
        self.name = ""
        self.logfile = ""
        self.compress = -1
        self.custom_command = ''

    def create_c_dict(self):
        c_dict = super(PcpCombineWrapper, self).create_c_dict()
        c_dict['SKIP_IF_OUTPUT_EXISTS'] = self.config.getbool('config', 'PCP_COMBINE_SKIP_IF_OUTPUT_EXISTS', False)

        if self.config.getbool('config', 'FCST_PCP_COMBINE_RUN', False):
            c_dict = self.set_fcst_or_obs_dict_items('FCST', c_dict)

        if self.config.getbool('config', 'OBS_PCP_COMBINE_RUN', False):
            c_dict = self.set_fcst_or_obs_dict_items('OBS', c_dict)

        return c_dict


    def set_fcst_or_obs_dict_items(self, d_type, c_dict):
        c_dict[d_type+'_MIN_FORECAST'] = self.config.getint('config', d_type+'_PCP_COMBINE_MIN_FORECAST', 0)
        c_dict[d_type+'_MAX_FORECAST'] = self.config.getint('config', d_type+'_PCP_COMBINE_MAX_FORECAST', 256)
        c_dict[d_type+'_INPUT_DATATYPE'] = self.config.getstr('config',
                                              d_type+'_PCP_COMBINE_INPUT_DATATYPE', '')
        c_dict[d_type+'_DATA_INTERVAL'] = self.config.getint('config', d_type+'_PCP_COMBINE_DATA_INTERVAL', 1)
        c_dict[d_type+'_TIMES_PER_FILE'] = self.config.getint('config', d_type+'_PCP_COMBINE_TIMES_PER_FILE', -1)
        c_dict[d_type+'_IS_DAILY_FILE'] = self.config.getbool('config', d_type+'_PCP_COMBINE_IS_DAILY_FILE', False)
        c_dict[d_type+'_LEVEL'] = self.config.getstr('config', d_type+'_PCP_COMBINE_INPUT_LEVEL', '-1')
        c_dict[d_type+'_LEVELS'] = util.getlist(self.config.getstr('config', d_type+'_PCP_COMBINE_INPUT_LEVELS', ''))
        c_dict[d_type+'_LEVEL_NAMES'] = util.getlist(self.config.getraw('config', d_type+'_PCP_COMBINE_INPUT_LEVEL_NAMES', ''))

        c_dict[d_type+'_INPUT_DIR'] = self.config.getdir(d_type+'_PCP_COMBINE_INPUT_DIR', '')
        c_dict[d_type+'_INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                     d_type+'_PCP_COMBINE_INPUT_TEMPLATE')
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
        return c_dict

    def clear(self):
        super(PcpCombineWrapper, self).clear()
        self.inaddons = []
        self.method = ""
        self.pcp_dir = ""
        self.pcp_regex = ""
        self.init_time = -1
        self.valid_time = -1
        self.in_accum = -1
        self.out_accum = -1
        self.field_name = ""
        self.field_level = ""
        self.field_extra = ""
        self.name = ""
        self.logfile = ""
        self.compress = -1
        self.custom_command = ''

    def add_input_file(self, filename, addon):
        self.infiles.append(filename)
        self.inaddons.append(str(addon))

    def set_field(self, name, level):
        self.field_name = name
        self.field_level = level

    def set_name(self,name):
        self.name = name

    def set_logfile(self,logfile):
        self.logfile = logfile

    def set_compress(self, c):
        self.compress = c

    def set_pcp_dir(self, filepath):
        self.pcp_dir = filepath

    def set_pcp_regex(self, regexp):
        self.pcp_regex = regexp

    def set_init_time(self, init_time):
        self.init_time = init_time[0:8]+"_"+init_time[8:10]

    def set_valid_time(self, valid_time):
        self.valid_time = valid_time[0:8]+"_"+valid_time[8:10]

    def set_in_accum(self, in_accum):
        self.in_accum = in_accum

    def set_out_accum(self, out_accum):
        self.out_accum = out_accum

    def get_dir_and_template(self, data_type, in_or_out):
        dirr = self.c_dict[data_type+'_'+in_or_out+'_DIR']
        template = self.c_dict[data_type+'_'+in_or_out+'_TEMPLATE']

        if dirr is '':
            self.logger.error(data_type+'_PCP_COMBINE_'+in_or_out+'_DIR must be set.')
            exit(1)

        if template is '':
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
        min_forecast = self.c_dict[dtype+'_MIN_FORECAST']
        max_forecast = self.c_dict[dtype+'_MAX_FORECAST']
        forecast_lead = min_forecast
        self.logger.debug(f"Looking for file with lowest forecast lead valid at {valid_time}"
                          f" between {min_forecast} and {max_forecast}")

        while forecast_lead <= max_forecast:
            input_dict = {}
            input_dict['valid'] = valid_time
            input_dict['lead_hours'] = forecast_lead
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
                return search_file
            forecast_lead += 1
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
        level_dict_list = self.c_dict['LEVEL_DICT_LIST']
        fname = next((item['name'] for item in level_dict_list if item['amount'] == accum_seconds), '-1')
        # if accumulation was not found in levels dictionary list, error and return
        if fname == '-1':
            self.logger.error(f'Accumulation {accum} was not specified in the {data_src}'
                              '_PCP_COMBINE_INPUT_LEVELS list')
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


    def get_data_type(self, data_src):
        d_type = self.c_dict[data_src + '_INPUT_DATATYPE']
        # to handle deprecated config variable, allow *_NATIVE_DATA_TYPE
        # but print warning that this will be deprecated and use other
        if d_type == '':
            d_type = self.config.getstr('config',
                                        data_src+'_NATIVE_DATA_TYPE',
                                        '')

            if d_type == '':
                self.logger.error('Must set '+data_src+\
                                  '_PCP_COMBINE_INPUT_DATATYPE')
                exit(1)
            self.logger.warning(data_src+'_NATIVE_DATA_TYPE is deprecated. Please use '+\
                                data_src+'_PCP_COMBINE_INPUT_DATATYPE instead')
        return d_type


    def get_addon(self, field_name, search_accum, search_time):
        if field_name is not None:
            # perform string substitution on name in case it uses filename templates
            field_name = sts.StringSub(self.logger, field_name, valid=search_time).do_string_sub()
            addon = "'name=\"" + field_name + "\";"
            if not util.is_python_script(field_name):
               addon += " level=\"(0,*,*)\";"
            addon += "'"
        else:
            addon = time_util.time_string_to_met_time(str(search_accum), default_unit='S')

        return addon

    def find_input_file(self, in_template, search_time, search_accum, data_src):
        fSts = sts.StringSub(self.logger,
                             in_template,
                             valid=search_time,
                             level=(int(search_accum)))
        search_file = os.path.join(self.input_dir,
                                   fSts.do_string_sub())

        return util.preprocess_file(search_file,
                                    self.c_dict[data_src+'_INPUT_DATATYPE'],
                                    self.config)

    def get_accumulation(self, time_info, accum, data_src,
                         is_forecast=False):
        """!Find files to combine to build the desired accumulation
        Args:
          @param time_info dictionary containing time information
          @param accum desired accumulation to build
          @param data_src type of data (FCST or OBS)
          @param is_forecast handle differently if reading forecast files
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
        smallest_input_accum = min([lev['amount'] for lev in self.c_dict['LEVEL_DICT_LIST']])
        last_time = time_info['valid'] -\
            accum_relative +\
            datetime.timedelta(seconds=smallest_input_accum)

        total_accum = time_util.ti_get_seconds_from_relativedelta(accum_relative,
                                                                  time_info['valid'])

        # log the input and output accumulation information
        search_accum_list = ' or '.join([time_util.ti_get_lead_string(lev['amount'],plural=False) for lev in self.c_dict['LEVEL_DICT_LIST']])
        self.logger.debug(f"Trying to build a {time_util.ti_get_lead_string(total_accum, plural=False)} accumulation using {search_accum_list} input data")
        # loop backwards in time until you have a full set of accum
        while last_time <= search_time:
            found = False
            if is_forecast:
                if total_accum == 0:
                    break

                search_file = self.getLowestForecastFile(search_time, data_src, in_template)
                if search_file is None:
                    break

                # find accum field in file that is less than search accumulation
                field_name = self.c_dict['LEVEL_DICT_LIST'][0]['name']
                s_accum = time_util.time_string_to_met_time(self.c_dict['LEVEL_DICT_LIST'][0]['amount'])

                found = True
                addon = self.get_addon(field_name, s_accum, search_time)
                self.add_input_file(search_file, addon)
                self.logger.debug(f"Adding input file: {search_file}")
                s_accum_seconds = time_util.get_seconds_from_string(s_accum, 'H')
                search_time = search_time - datetime.timedelta(seconds=s_accum_seconds)
                total_accum -= s_accum_seconds
            else:  # not looking for forecast files
                # look for biggest accum that fits search
                for level_dict in self.c_dict['LEVEL_DICT_LIST']:
                    if level_dict['amount'] > total_accum:
                        continue

                    search_file = self.find_input_file(in_template, search_time,
                                                       level_dict['amount'], data_src)

                    # if found a file, add it to input list with info
                    if search_file is not None:
                        addon = self.get_addon(level_dict['name'], level_dict['amount'], search_time)
                        # add file to input list and step back in time to find more data
                        self.add_input_file(search_file, addon)
                        self.logger.debug(f"Adding input file: {search_file}")
                        search_time = search_time - datetime.timedelta(seconds=level_dict['amount'])
                        total_accum -= level_dict['amount']
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

        cmd = '{} -v {} '.format(self.app_path, self.verbose)

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
        if self.field_name != "":
            cmd += " -field 'name=\""+self.field_name+"\";"
            if self.field_level != "":
                cmd += " level=\""+self.field_level+"\";"
            if self.field_extra != "":
                cmd += ' ' + self.field_extra
            cmd += "' "

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

    def run_at_time_once(self, time_info, var_info, rl):
        self.clear()
        cmd = None
        self.clear()
        self.method = self.c_dict[rl+'_RUN_METHOD'].upper()
        if self.method == "CUSTOM":
            cmd = self.setup_custom_method(time_info, rl)
        else:
            if var_info is None:
                self.logger.error('Cannot run PcpCombine without specifying fields to process '
                                  'unless running in CUSTOM mode.')
                return

            if self.method == "ADD":
                cmd = self.setup_add_method(time_info, var_info, rl)
            elif self.method == "SUM":
                cmd = self.setup_sum_method(time_info, var_info, rl)
            elif self.method == "SUBTRACT":
                cmd = self.setup_subtract_method(time_info, var_info, rl)
            elif self.method == "DERIVE":
                cmd = self.setup_derive_method(time_info, var_info, rl)
            else:
                self.logger.error('Invalid ' + rl + '_PCP_COMBINE_METHOD specified.'+\
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


    def setup_subtract_method(self, time_info, var_info, rl):
        """!Setup pcp_combine to subtract two files to build desired accumulation
        Args:
          @param time_info object containing timing information
          @param var_info object containing variable information
          @params rl data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        in_dir, in_template = self.get_dir_and_template(rl, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(rl, 'OUTPUT')

        if rl == 'FCST':
            field_name = var_info['fcst_name']
            level = var_info['fcst_level']
        else:
            field_name = var_info['obs_name']
            level = var_info['obs_level']

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
                                     self.c_dict[rl+'_INPUT_DATATYPE'],
                                     self.config)

        if file1 is None:
            self.logger.error(f'Could not find {rl} file {file1_expected} using template {in_template}')
            return None

        # if level type is A (accum) and second lead is 0, then
        # run PcpCombine in -add mode with just the first file
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
                                     self.c_dict[rl+'_INPUT_DATATYPE'],
                                     self.config)

        if file2 is None:
            self.logger.error(f'Could not find {rl} file {file2_expected} using template {in_template}')
            return None

        if self.c_dict[rl+'_INPUT_DATATYPE'] != 'GRIB':
            field_name_1 = sts.StringSub(self.logger, field_name, **time_info).do_string_sub()
            lead = "'name=\"" + field_name_1 + "\";'"
            field_name_2 = sts.StringSub(self.logger, field_name, **time_info2).do_string_sub()
            lead2 = "'name=\"" + field_name_2 + "\";'"
            # TODO: need to add level if NetCDF input - how to specify levels for each?

        self.add_input_file(file1,lead)
        self.add_input_file(file2,lead2)

        return self.get_command()


    def setup_sum_method(self, time_info, var_info, rl):
        """!Setup pcp_combine to build desired accumulation based on
        init/valid times and accumulations
        Args:
          @param time_info object containing timing information
          @param var_info object containing variable information
          @params rl data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        in_accum = self.c_dict[rl+'_LEVEL']

        # if level is not set, default to 0 for sum mode
        if in_accum == -1:
            in_accum = 0

        in_dir, in_template = self.get_dir_and_template(rl, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(rl, 'OUTPUT')

        out_accum = var_info['obs_level']
        if out_accum[0].isalpha():
            out_accum = out_accum[1:]

        init_time = time_info['init_fmt']
        valid_time = time_info['valid_fmt']

        time_info['level'] = int(out_accum) * 3600
        in_regex = util.template_to_regex(in_template, time_info,
                                          self.logger)
        in_regex_split = in_regex.split('/')
        in_dir = os.path.join(in_dir, *in_regex_split[0:-1])
        in_regex = in_regex_split[-1]

        self.set_init_time(init_time)
        self.set_valid_time(valid_time)
        self.set_in_accum(in_accum)
        self.set_out_accum(out_accum)
        self.set_pcp_dir(in_dir)
        self.set_pcp_regex(in_regex)
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
        is_forecast = False
        if data_src == "FCST":
            is_forecast = True

        if data_src == "FCST":
            level = var_info['fcst_level']
            compare_var = var_info['fcst_name']
        else:
            level = var_info['obs_level']
            compare_var = var_info['obs_name']

        _, accum_string = util.split_level(level)

        # get number of seconds relative to valid time
        accum_seconds = time_util.get_seconds_from_string(accum_string,
                                                          default_unit='H',
                                                          valid_time=time_info['valid'])
        if accum_seconds is None:
            self.logger.error(f'Invalid accumulation specified: {accum_string}')
            return

        # create list of tuples for input levels and optional field names
        if not self.build_input_level_list(data_src, time_info):
            return

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.input_dir = in_dir

        if not self.get_accumulation(time_info, accum_string, data_src, is_forecast):
            self.logger.error(f'Could not find files to build accumulation in {in_dir} using template {in_template}')
            return None

        self.outdir = out_dir
        time_info['level'] = int(accum_seconds)
        pcpSts = sts.StringSub(self.logger,
                               out_template,
                               **time_info)
        pcp_out = pcpSts.do_string_sub()
        self.outfile = pcp_out
        self.args.append("-name " + compare_var + "_" + accum_string)
        return self.get_command()

    def setup_derive_method(self, time_info, var_info, data_src):
        """!Setup pcp_combine to derive stats
        Args:
          @param time_info dictionary containing timing information
          @param var_info object containing variable information
          @params data_src data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        is_forecast = False
        if data_src == "FCST":
            is_forecast = True

        # set field info
        if data_src == "FCST":
            self.field_level = var_info['fcst_level']
            self.field_name = var_info['fcst_name']
            self.field_extra = var_info['fcst_extra']
        else:
            self.field_level = var_info['obs_level']
            self.field_name = var_info['obs_name']
            self.field_extra = var_info['obs_extra']

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
                                     data_src,
                                     is_forecast):
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
        return '{} -v {} {}'.format(self.app_path, self.verbose, self.custom_command)

    def build_input_level_list(self, data_src, time_info):
        level_list = self.c_dict[data_src + '_LEVELS']
        name_list = self.c_dict[data_src + '_LEVEL_NAMES']

        if not level_list:
            self.logger.error(f'{data_src}_PCP_COMBINE_INPUT_LEVELS must be specified.')
            return False

        # name list should either be empty or the same length as level list
        if name_list:
            if len(level_list) != len(name_list):
                msg = f'{data_src}_PCP_COMBINE_INPUT_LEVEL_NAMES list should be ' +\
                      'either empty or the same length as ' +\
                      f'{data_src}_PCP_COMBINE_INPUT_LEVELS list.'
                self.logger.error(msg)
                return False
        else:
            # if no name list, create list of None values
            name_list = [None] * len(level_list)


        level_dict_list = []
        for level, name in zip(level_list, name_list):
            # convert accum amount to seconds from time string
            amount = time_util.get_seconds_from_string(level, 'H', time_info['valid'])
            level_dict_list.append({'amount' : amount, 'name' : name})

        self.c_dict['LEVEL_DICT_LIST'] = level_dict_list
        return True

if __name__ == "__main__":
        util.run_stand_alone("pcp_combine_wrapper", "PcpCombine")
