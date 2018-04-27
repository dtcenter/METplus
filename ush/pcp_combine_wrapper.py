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
#from produtil.run import batchexe, run, checkrun
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
        self.method = "ADD"
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


    def clear(self):
        super(PcpCombineWrapper, self).clear()
        self.inaddons = []
        self.method = "ADD"
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


    def getLowestForecastFile(self, valid_time, search_time, template):
        # search for dated dir and without, combine two glob results and sort
        out_file = None
        # used to find lowest forecast
        lowest_fcst = 999999
        num_slashes = template.count('/')
        search_string = "{:s}/*"
        for n in range(num_slashes):
            search_string += "/*"

        all_files = glob.glob(search_string.format(self.input_dir))
        files = sorted(all_files)

        for fpath in files:
            # TODO: Replace with util.get_time_from_file(fpath, template)
            # check if result is a file or not
#            if os.path.isdir(fpath):
#                continue

            # Check number of / in template, get same number from file path
#            path_split = fpath.split('/')
#            f = ""
#            for n in range(num_slashes, -1, -1):
#                f = os.path.join(f,path_split[-(n+1)])

#            se = sts.StringExtract(self.logger, template, f)
            se = util.get_time_from_file(self.logger, fpath, template)
            
            # TODO: should parseTemplate return false on failure instead of crashing?
#            se.parseTemplate()
            if se == None:
                return None

            fcst = se.leadHour
            if fcst is -1:
                self.logger.error("Could not pull forecast lead from f")
                exit

            init = se.getInitTime("%Y%m%d%H%M")
#            if init == None:
#                return None
            v = util.shift_time(init, fcst)
            if v == valid_time and fcst < lowest_fcst:
                out_file = fpath
                lowest_fcst = fcst
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
        out_file = self.getLowestForecastFile(valid_time, day_before, input_template)
        out_file2 = self.getLowestForecastFile(valid_time, valid_time, input_template)
        if out_file2 == None:
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
            if ftime != None and ftime < file_time:
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


    def get_daily_file(valid_time,accum, data_src):
        # loop accum times
        data_interval = self.p.getint('config',
                                      data_src + '_DATA_INTERVAL') * 3600
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
                                  data_src + '_' + str(
                                      accum) + '_FIELD_NAME')
            addon = "'name=\"" + fname + "\"; level=\"(" + \
                    str(lead) + ",*,*)\";'"
            self.add_input_file(f, addon)
            return True
        
        
    def get_accumulation(self, valid_time, accum, data_src,
                         file_template, is_forecast=False):
        if self.input_dir == "":
            self.logger.error(self.app_name +
                              ": Must set data dir to run get_accumulation")
            exit
        self.add_arg("-add")

        if self.p.getbool('config', data_src + '_IS_DAILY_FILE') is True:
            self.get_daily_file(valid_time, accum, data_src)

        start_time = valid_time
        last_time = util.shift_time(valid_time, -(int(accum) - 1))
        total_accum = int(accum)
        level = self.p.getint('config', data_src+'_LEVEL')
        search_accum = level
        # loop backwards in time until you have a full set of accum
        while last_time <= start_time:
            if is_forecast:
                f = self.get_lowest_forecast_at_valid(start_time, data_src)
                if f == None:
                    break
                ob_str = self.p.getstr('config',
                                       data_src + '_' + str(level) +
                                       '_FIELD_NAME')
                addon = "'name=\"" + ob_str + "\"; level=\"(0,*,*)\";'"
                self.add_input_file(f, addon)
                start_time = util.shift_time(start_time, -1)
                search_accum -= 1
            else:  # not looking for forecast files
                start_time = start_time[0:10]
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
                        d_type = self.p.getstr('config', data_src +
                                                  '_NATIVE_DATA_TYPE')
                        if d_type == "GRIB":
                            addon = search_accum
                        elif d_type == "NETCDF":
                            ob_str = self.p.getstr('config', data_src +
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

            cmd += "-sum "+self.init_time+" "+self.in_accum+" "+\
              self.valid_time+" "+self.out_accum+" "

        else:
            if self.method == "ADD":
                cmd += "-add "
            elif self.method == "SUBTRACT":
                cmd += "-subtract "

            if len(self.infiles) == 0:
                (self.logger).error("No input filenames specified")
                return None

            for idx, f in enumerate(self.infiles):
                cmd += f + " " + self.inaddons[idx] + " "


        if self.outfile == "":
            (self.logger).error("No output filename specified")
            return None

        if self.outdir == "":
            (self.logger).error("No output directory specified")
            return None

        cmd += os.path.join(self.outdir, self.outfile)

        if self.pcp_dir != "":
            cmd += " -pcpdir "+self.pcp_dir

        if self.pcp_regex != "":
            cmd += " -pcprx "+self.pcp_regex

        if self.field_name != "":
            cmd += " -field 'name=\""+self.field_name+"\";"
            if self.field_level != "":
                cmd += " level=\""+self.field_level+"\";"
            cmd += "'"

        if self.name != "":
            cmd += " -name "+self.name

        if self.logfile != "":
            cmd += " -log "+self.logfile

        if self.verbose != -1:
            cmd += " -v "+str(self.verbose)

        if self.compress != -1:
            cmd += " -compress "+str(self.compress)

        return cmd


    def run_at_time(self, init_time):
        self.logger.error("Must use PcpCombineObs or PcpCombineModel")
        exit(1)

# pcp_combine -subtract /d1/mccabe/mallory.data/prfv3rt1/20180308/gfs.t00z.pgrb.1p00.f048 48 /d1/mccabe/mallory.data/prfv3rt1/20180308/gfs.t00z.pgrb.1p00.f024 24 -field 'name="APCP"; level="L0";' ~/20180308/gfs.v24z_A24.nc

#    def run_subtract_method(self, init_time, lead, in_dir, accum_1, accum_2,
#                            in_template, out_template):
    def run_subtract_method(self, task_info, var_info, accum, in_dir,
                            out_dir, in_template, out_template):
        self.clear()
        init_time = task_info.getInitTime()
        valid_time = task_info.getValidTime()
        lead = task_info.getLeadTime()
        lead2 = lead + accum

        self.set_method("SUBTRACT")

        pcpSts1 = sts.StringSub(self.logger,
                                in_template,
                                init=init_time,
                                lead=str(lead))
        file1 = pcpSts1.doStringSub()

        pcpSts2 = sts.StringSub(self.logger,
                                in_template,
                                init=init_time,
                                lead=str(lead2))
        file2 = pcpSts2.doStringSub()

        self.add_input_file(os.path.join(in_dir,file2),lead2)
        self.add_input_file(os.path.join(in_dir,file1),lead)

        outSts = sts.StringSub(self.logger,
                               out_template,
                               valid=valid_time,
                               level=str(accum))
        out_file = outSts.doStringSub()
        self.set_output_filename(out_file)
        self.set_output_dir(out_dir)

        # TODO: If out template has a subdir, make that directory!
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        cmd = self.get_command()
        if cmd is None:
            self.logger.error("pcp_combine could not generate command")
            return
        self.logger.info("")
        self.build()
        outfile = self.get_output_path()
        return outfile


    def run_sum_method(self, valid_time, init_time, in_accum, out_accum,
                       input_dir, output_dir, output_template):
        self.clear()
        self.set_method("SUM")
        self.set_init_time(init_time)
        self.set_valid_time(valid_time)        
        self.set_in_accum(in_accum)
        self.set_out_accum(out_accum)
        self.set_pcp_dir(input_dir)
        self.set_pcp_regex(init_time[0:10])
        self.set_output_dir(output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        pcpSts = sts.StringSub(self.logger,
                                output_template,
                                init=init_time,
                                valid=valid_time,
                                level=str(out_accum).zfill(2))
        pcp_out = pcpSts.doStringSub()
        self.set_output_filename(pcp_out)

        cmd = self.get_command()
        if cmd is None:
            self.logger.error("pcp_combine could not generate command")
            return
        self.logger.info("")
        self.build()
        outfile = self.get_output_path()
        return outfile


    def run_add_method(self, valid_time, init_time, accum,
                       compare_var, data_src, is_forecast=False):
        self.clear()
        self.set_method("ADD")

        input_dir = self.p.getstr('config', data_src+'_PCP_COMBINE_INPUT_DIR')
        input_template = self.p.getraw('filename_templates', data_src+'_PCP_COMBINE_INPUT_TEMPLATE')
        output_dir = self.p.getstr('config', data_src+'_PCP_COMBINE_OUTPUT_DIR')
        output_template = self.p.getraw('filename_templates',
                                        data_src+'_PCP_COMBINE_OUTPUT_TEMPLATE')

        ymd = valid_time[0:8]
        if not os.path.exists(os.path.join(output_dir, ymd)):
            os.makedirs(os.path.join(output_dir, ymd))

        # check _PCP_COMBINE_INPUT_DIR to get accumulation files
        self.set_input_dir(input_dir)
        if self.get_accumulation(valid_time, int(accum), data_src, input_template, is_forecast) is True:
            # if success, run pcp_combine
            infiles = self.get_input_files()
        else:
            # if failure, check _GEMPAK_INPUT_DIR to get accumulation files
            if not self.p.has_option('config', data_src+'_GEMPAK_INPUT_DIR') or \
              not self.p.has_option('filename_templates', data_src+'_GEMPAK_TEMPLATE'):
                self.logger.warning(self.app_name + ": Could not find " \
                                    "files to compute accumulation in " \
                                    + input_dir)
                return False
            gempak_dir = self.p.getstr('config', data_src+'_GEMPAK_INPUT_DIR')
            gempak_template = self.p.getraw('filename_templates', data_src+'_GEMPAK_TEMPLATE')
            self.clear()
            self.set_input_dir(gempak_dir)
            if self.get_accumulation(valid_time, int(accum), data_src, gempak_template, is_forecast) is True:
                #   if success, run GempakToCF, run pcp_combine
                infiles = self.get_input_files()
                for idx, infile in enumerate(infiles):
                    # replace input_dir with native_dir, check if file exists
                    nfile = infile.replace(gempak_dir, input_dir)
                    if not os.path.exists(os.path.dirname(nfile)):
                        os.makedirs(os.path.dirname(nfile))
#                    data_type = util.get_filetype(nfile)
                    data_type = self.p.getstr('config', data_src+'_NATIVE_DATA_TYPE')
                    if data_type == "NETCDF":
                        nfile = os.path.splitext(nfile)[0] + '.nc'
                        if not os.path.isfile(nfile):
                            self.logger.info("Calling GempakToCF to convert to NetCDF")
                            run_g2c = GempakToCFWrapper(self.p, self.logger)
                            run_g2c.add_input_file(infile)
                            run_g2c.set_output_path(nfile)
                            cmd = run_g2c.get_command()
                            if cmd is None:
                                self.logger.error("GempakToCF could not generate command")
                                continue
                            run_g2c.build()
                    infiles[idx] = nfile

            else:
                #   if failure, quit
                self.logger.warning(self.app_name + ": Could not find " \
                                    "files to compute accumulation in " \
                                    + gempak_dir)
                return None

        self.set_output_dir(output_dir)
        pcpSts = sts.StringSub(self.logger,
                                output_template,
                                valid=valid_time,
                                level=str(accum).zfill(2))
        pcp_out = pcpSts.doStringSub()
        self.set_output_filename(pcp_out)
        self.add_arg("-name " + compare_var + "_" + str(accum).zfill(2))
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("pcp_combine could not generate command")
            return
        self.logger.info("")
        self.build()
        outfile = self.get_output_path()
        return outfile
