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


    def set_method(self, method):
        self.method = method

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
        # calling config.conf version of getter so default value is not
        # set in log and final conf because it is unnecessary
        fname = self.config.conf.getstr('config',
                              data_src + '_PCP_COMBINE_' + str(
                                  accum) + '_FIELD_NAME', '')
        if fname == '':
            self.logger.error('NetCDF field name was not set in config: {}'
                              .format(data_src+'_PCP_COMBINE_'+str(accum)+'_FIELD_NAME'))
            return False

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
            d_type = self.config.conf.getstr('config', data_src+'_NATIVE_DATA_TYPE', '')
            if d_type == '':
                self.logger.error('Must set '+data_src+\
                                  '_PCP_COMBINE_INPUT_DATATYPE')
                exit(1)
            self.logger.warning(data_src+'_NATIVE_DATA_TYPE is deprecated. Please use '+\
                                data_src+'_PCP_COMBINE_INPUT_DATATYPE instead')
        return d_type


    def get_addon(self, data_src, search_accum):
        d_type = self.get_data_type(data_src)
        if d_type == "GRIB":
            return search_accum
        # if NETCDF, GEMPAK, or PYTHON
        # calling config.conf version of getter so default value is not
        # set in log and final conf because it is unnecessary
        field_name = self.config.conf.getstr('config', data_src +
                               '_PCP_COMBINE_' + str(search_accum) +
                               '_FIELD_NAME', '')
        if field_name == '':
            return ''

        addon = "'name=\"" + field_name + "\";"
        if not util.is_python_script(field_name):
            addon += " level=\"(0,*,*)\";"
        addon += "'"
        return addon

    def find_input_file(self, in_template, search_time, search_accum, data_src):
        fSts = sts.StringSub(self.logger,
                             in_template,
                             valid=search_time,
                             level=(int(search_accum)*3600))
        search_file = os.path.join(self.input_dir,
                                   fSts.do_string_sub())

        return util.preprocess_file(search_file,
                                    self.c_dict[data_src+'_INPUT_DATATYPE'],
                                    self.config)

    def find_highest_accum_field(self, data_src, s_accum):
        field_name = ''
        while s_accum > 0:
            # calling config.conf version of getter so default value is not
            # set in log and final conf because it is unnecessary
            field_name = self.config.conf.getstr('config',
                                   data_src + '_PCP_COMBINE_' + str(s_accum) +
                                   '_FIELD_NAME', '')
            if field_name != '':
                break

            s_accum -= 1

        return field_name, s_accum

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
        valid_time = time_info['valid_fmt']
        if self.input_dir == "":
            self.logger.error(self.app_name +
                              ": Must set data dir to run get_accumulation")
            exit(1)

        if self.c_dict[data_src + '_IS_DAILY_FILE'] is True:
            return self.get_daily_file(time_info, accum, data_src, in_template)

        search_time = time_info['valid']
        last_time = time_info['valid'] - datetime.timedelta(hours=(int(accum) - 1))
        total_accum = accum
        level = int(self.c_dict[data_src+'_LEVEL'])
        if level == -1:
            search_accum = accum
        else:
            search_accum = level
        # loop backwards in time until you have a full set of accum
        while last_time <= search_time:
            if is_forecast:
                search_file = self.getLowestForecastFile(search_time, data_src, in_template)
                if search_file == None:
                    break
                # find accum field in file
                field_name, s_accum = self.find_highest_accum_field(data_src, search_accum)

                if field_name == '':
                    break

                if self.get_data_type(data_src) == "GRIB":
                    addon = search_accum
                else:
                    addon = "'name=\"" + field_name + "\";"
                    if not util.is_python_script(field_name):
                        addon += " level=\"(0,*,*)\";"
                    addon += "'"

                self.add_input_file(search_file, addon)
                search_time = search_time - datetime.timedelta(hours=s_accum)
                search_accum -= s_accum
                total_accum -= s_accum
            else:  # not looking for forecast files
                # look for biggest accum that fits search
                while search_accum > 0:
                    search_file = self.find_input_file(in_template, search_time,
                                                       search_accum, data_src)

                    # if found a file, add it to input list with info
                    if search_file is not None:
                        addon = self.get_addon(data_src, search_accum)
                        if addon == '':
                            # could not find NetCDF field to process
                            search_accum -= 1
                            continue

                        # add file to input list and step back in time to find more data
                        self.add_input_file(search_file, addon)
                        search_time = search_time - datetime.timedelta(hours=search_accum)
                        total_accum -= search_accum
                        break
                    # if file/field not found, look for a smaller accumulation
                    search_accum -= 1

            # if we don't need any more accumulation, break out of loop and run
            if total_accum == 0:
                break

            # if we still need to find more accum but we couldn't find it, fail
            if search_accum == 0:
                return False

            # if [FCST/OBS]_LEVEL is used, use that value
            # else use accumulation amount left to find
            if level == -1:
                search_accum = total_accum
            else:
                search_accum = level

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

        if self.method == "SUM":
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
        cmd = None
        run_method = self.c_dict[rl+'_RUN_METHOD'].upper()
        if run_method == "ADD":
            cmd = self.setup_add_method(time_info, var_info, rl)
        elif run_method == "SUM":
            cmd = self.setup_sum_method(time_info, var_info, rl)
        elif run_method == "SUBTRACT":
            cmd = self.setup_subtract_method(time_info, var_info, rl)
        elif run_method == "DERIVE":
            cmd = self.setup_derive_method(time_info, var_info, rl)
        else:
            self.logger.error('Invalid ' + rl + '_PCP_COMBINE_METHOD specified.'+\
                              ' Options are ADD, SUM, and SUBTRACT.')
            exit(1)

        if cmd is None:
            init_time = time_info['init_fmt']
            lead = time_info['lead_hours']
            self.logger.error("pcp_combine could not generate command for init {} and forecast lead {}".format(init_time, lead))
            return

        # if output file exists and we want to skip it, warn and continue
        outfile = self.get_output_path()
        if os.path.exists(outfile) and \
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
        self.clear()
        in_dir, in_template = self.get_dir_and_template(rl, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(rl, 'OUTPUT')

        if rl == 'FCST':
            level = var_info['fcst_level']
        else:
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
        file1 = os.path.join(in_dir, pcpSts1.do_string_sub())
        file1 = util.preprocess_file(file1, self.c_dict[rl+'_INPUT_DATATYPE'],
                                    self.config)

        if file1 is None:
            self.logger.error("Could not find file in {} for init time {} and lead {}"
                              .format(in_dir, time_info['init_fmt'], lead))
            return None

        # if level type is A (accum) and second lead is 0, then
        # run PcpCombine in -add mode with just the first file
        if lead2 == 0 and level_type == 'A':
            self.set_method("ADD")
            self.add_input_file(file1, lead)
            return self.get_command()

        # else continue building -subtract command
        self.set_method("SUBTRACT")

        # set time info for second lead
        input_dict2 = { 'init' : time_info['init'],
                       'lead_hours' : lead2 }
        time_info2 = time_util.ti_calculate(input_dict2)
        pcpSts2 = sts.StringSub(self.logger,
                                in_template,
                                level=(int(accum) * 3600),
                                **time_info2)
        file2 = os.path.join(in_dir, pcpSts2.do_string_sub())
        file2 = util.preprocess_file(file2, self.c_dict[rl+'_INPUT_DATATYPE'],
                                     self.config)

        if file2 is None:
            self.logger.error("Could not find file in {} for init time {} and lead {}"
                              .format(in_dir, time_info2['init_fmt'], lead2))
            return None

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
        self.clear()
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

        self.set_method("SUM")
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
        self.clear()
        self.set_method("ADD")

        if data_src == "FCST":
            accum = var_info['fcst_level']
            compare_var = var_info['fcst_name']
        else:
            accum = var_info['obs_level']
            compare_var = var_info['obs_name']

        if accum[0].isalpha():
            accum = accum[1:]

        init_time = time_info['init_fmt']
        valid_time = time_info['valid_fmt']

        in_dir, in_template = self.get_dir_and_template(data_src, 'INPUT')
        out_dir, out_template = self.get_dir_and_template(data_src, 'OUTPUT')

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.input_dir = in_dir

        if not self.get_accumulation(time_info, int(accum), data_src, is_forecast):
            return None

        self.outdir = out_dir
        time_info['level'] = int(accum) * 3600
        pcpSts = sts.StringSub(self.logger,
                                out_template,
                                **time_info)
        pcp_out = pcpSts.do_string_sub()
        self.outfile = pcp_out
        self.args.append("-name " + compare_var + "_" + str(accum))
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
        self.clear()
        self.set_method("DERIVE")

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
        if not self.get_accumulation(time_info, lookback, data_src, is_forecast):
            return None

        # set output
        self.outdir =out_dir
        time_info['level'] = int(lookback) * 3600
        psts = sts.StringSub(self.logger,
                                out_template,
                                **time_info)
        pcp_out = psts.do_string_sub()
        self.outfile = pcp_out
        return self.get_command()


if __name__ == "__main__":
        util.run_stand_alone("pcp_combine_wrapper", "PcpCombine")
