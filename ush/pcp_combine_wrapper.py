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

import produtil.setup
from produtil.run import batchexe, run, checkrun
import logging
import os
import sys
import met_util as util
import re
import csv
import subprocess
import glob
import datetime
import string_template_substitution as sts

from command_builder import CommandBuilder
from task_info import TaskInfo
from gempak_to_cf_wrapper import GempakToCFWrapper


class PcpCombineWrapper(CommandBuilder):
    def __init__(self, p, logger):
        super(PcpCombineWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/pcp_combine')
        self.app_name = os.path.basename(self.app_path)
        self.inaddons = []

    def clear(self):
        super(PcpCombineWrapper, self).clear()
        self.inaddons = []


    def add_input_file(self, filename, addon):
        self.infiles.append(filename)
        self.inaddons.append(str(addon))

    def getLastFile(self, valid_time, search_time, template):
        out_file = ""
        files = sorted(glob.glob("{:s}/{:s}/*".format(self.input_dir,
                                                      str(search_time)[0:8])))
        for fpath in files:
            f = os.path.join(str(search_time)[0:8], os.path.basename(fpath))
            se = sts.StringExtract(self.logger, template, f)
            se.parseTemplate()

            fcst = se.leadHour
            if fcst is -1:
                print("ERROR: Could not pull forecast lead from f")
                exit

            init = se.getInitTime("%Y%m%d%H%M")
            v = util.shift_time(init, fcst)
            if v == valid_time:
                out_file = fpath
        return out_file

    # NOTE: Assumes YYYYMMDD sub dir
    def get_lowest_forecast_at_valid(self, valid_time, dtype):
        out_file = ""
        day_before = util.shift_time(valid_time, -24)
        input_template = self.p.getraw('filename_templates',
                                       dtype + '_PCP_COMBINE_INPUT_TEMPLATE')
        # get all files in yesterday directory, get valid time from init/fcst
        # NOTE: This will only apply to forecasts up to 48  hours
        #  If more is needed, will need to add parameter to specify number of
        #  days to look back
        out_file = self.getLastFile(valid_time, day_before, input_template)
        out_file2 = self.getLastFile(valid_time, valid_time, input_template)
        if out_file2 == "":
            return out_file
        else:
            return out_file2


    def search_day(self, dir, file_time, search_time, template):
        out_file = ""
        files = sorted(glob.glob("{:s}/*{:s}*".format(dir, search_time)))
        for f in files:
            se = sts.StringExtract(self.logger, template,
                                   os.path.basename(f))
            se.parseTemplate()
            ftime = se.getValidTime("%Y%m%d%H")
            if ftime < file_time:
                out_file = f
        return out_file

    def find_closest_before(self, dir, time, template):
        day_before = util.shift_time(time, -24)
        yesterday_file = self.search_day(dir, time,
                                         str(day_before)[0:8], template)
        today_file = self.search_day(dir, time, str(time)[0:8], template)
        if today_file == "":
            return yesterday_file
        else:
            return today_file

#    def subtract_files():
    # need accum interval, valid time, directory
    # find file at valid time in directory
    # find file at valid time - accum in directory
        
    def get_accumulation(self, valid_time, accum, data_type,
                         file_template, is_forecast=False):
        if self.input_dir == "":
            self.logger.error(self.app_name +
                              ": Must set data dir to run get_accumulation")
            exit
        self.add_arg("-add")

        if self.p.getbool('config', data_type + '_IS_DAILY_FILE') is True:
            # loop accum times
            data_interval = self.p.getint('config',
                                          data_type + '_DATA_INTERVAL') * 3600
            for i in range(0, accum, data_interval):
                search_time = util.shift_time(valid_time+"00", -i)[0:10]
                # find closest file before time
                f = self.find_closest_before(self.input_dir, search_time,
                                             file_template)
                if f == "":
                    continue
                # build level info string
                # TODO: pull out YYYYMMDDHH from filename
                file_time = datetime.datetime.strptime(f[-17:-7], "%Y%m%d%H")
                v_time = datetime.datetime.strptime(search_time, "%Y%m%d%H")
                diff = v_time - file_time
                lead = int((diff.days * 24) / (data_interval / 3600))
                lead += int((v_time - file_time).seconds / data_interval) - 1
                fname = self.p.getstr('config',
                                      data_type + '_' + str(
                                          accum) + '_FIELD_NAME')
                addon = "'name=\"" + fname + "\"; level=\"(" + \
                        str(lead) + ",*,*)\";'"
                self.add_input_file(f, addon)
                return True


        start_time = valid_time
        last_time = util.shift_time(valid_time, -(int(accum) - 1))
        total_accum = int(accum)
#        search_accum = total_accum
        level = self.p.getint('config', data_type+'_LEVEL')
        search_accum = level
        # loop backwards in time until you have a full set of accum
        while last_time <= start_time:
            if is_forecast:
                f = self.get_lowest_forecast_at_valid(start_time, data_type)
                if f == "":
                    break
                ob_str = self.p.getstr('config',
                                       data_type + '_' + str(level) +
                                       '_FIELD_NAME')
                addon = "'name=\"" + ob_str + "\"; level=\"(0,*,*)\";'"
                self.add_input_file(f, addon)
                start_time = util.shift_time(start_time, -1)
                search_accum -= 1
            else:  # not looking for forecast files
                # get all files of valid_time (all accums)
                # NOTE: This assumes dated subdir, template needs to match
                files = sorted(glob.glob("{:s}/{:s}/*{:s}*"
                                         .format(self.input_dir,
                                                 start_time[0:8],
                                                 start_time)))
                # look for biggest accum that fits search
                while search_accum > 0:
                    fSts = sts.StringSub(self.logger,
                                         file_template,
                                         valid=start_time,
                                         level=str(search_accum).zfill(2))
                    search_file = os.path.join(self.input_dir,
                                               fSts.doStringSub())
                    f = None
                    for file in files:
                        if file == search_file:
                            f = file
                            break
                    # if found a file, add it to input list with info
                    if f is not None:
                        addon = ""
#                        d_type = util.get_filetype(f)
                        d_type = self.p.getstr('config', data_type +
                                                  '_NATIVE_DATA_TYPE')
                        if d_type == "GRIB":
                            addon = search_accum
                        elif d_type == "NETCDF":
#                        else:
                            ob_str = self.p.getstr('config', data_type +
                                                   '_' + str(search_accum) +
                                                   '_FIELD_NAME')
                            addon = "'name=\"" + ob_str + \
                                    "\"; level=\"(0,*,*)\";'"
                        self.add_input_file(f, addon)
                        start_time = util.shift_time(start_time+"00", -search_accum)[0:10]
                        total_accum -= search_accum
                        break
                    search_accum -= 1


                if total_accum == 0:
                    break

                if search_accum == 0:
                    return False

        if len(self.infiles) is 0:
            return False
        return True
        self.set_output_dir(self.outdir)

    def get_command(self):
        if self.app_path is None:
            self.logger.error("No app path specified. You must use a subclass")
            return None

        cmd = self.app_path + " "
        for a in self.args:
            cmd += a + " "

        if len(self.infiles) == 0:
            (self.logger).error("No input filenames specified")
            return None

        for idx, f in enumerate(self.infiles):
            cmd += f + " " + self.inaddons[idx] + " "

        if self.param != "":
            cmd += self.param + " "

        if self.outfile == "":
            (self.logger).error("No output filename specified")
            return None

        if self.outdir == "":
            (self.logger).error("No output directory specified")
            return None

        cmd += os.path.join(self.outdir, self.outfile)
        return cmd


    def run_at_time(self, init_time):
        self.logger.error("Must use PcpCombineObs or PcpCombineModel")
        exit(1)
