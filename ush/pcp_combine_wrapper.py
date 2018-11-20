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

from reformat_gridded_wrapper import ReformatGriddedWrapper
from task_info import TaskInfo
from gempak_to_cf_wrapper import GempakToCFWrapper

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


    def getLowestForecastFile(self, valid_time, dtype):
        """!Find the lowest forecast hour that corresponds to the
        valid time
        Args:
          @param valid_time valid time to search
          @param dtype data type (FCST or OBS) to get filename template
          @rtype string
          @return Path to file with the lowest forecast hour"""
        out_file = None
        template = util.getraw_interp(self.p, 'filename_templates',
                                       dtype + '_PCP_COMBINE_INPUT_TEMPLATE')
        lowest_fcst = 999999
        num_slashes = template.count('/')
        search_string = "{:s}/*"
        for n in range(num_slashes):
            search_string += "/*"

        for dirpath, dirnames, all_files in os.walk(self.input_dir):
            for filename in sorted(all_files):
                fullpath = os.path.join(dirpath, filename)
                f = fullpath.replace(self.input_dir+"/", "")
                se = util.get_time_from_file(self.logger, f, template)

                if se == None:
                    continue

                fcst = se.leadHour
                if fcst is -1:
                    self.logger.error("Could not pull forecast lead from f")
                    exit

                init = se.getInitTime("%Y%m%d%H%M")
                if init == "":
                    continue

                v = util.shift_time(init, fcst)
                if v == valid_time and fcst < lowest_fcst:
                    out_file = fullpath
                    lowest_fcst = fcst
        return out_file


    def search_day(self, dir, file_time, search_time, template):
        """!Find file path within a day before the file_time
        Args:
          @param file_time output file must have a timestamp before this value
          @param search_time time to use to get directory listing
          @param template filename template to search
          @rtype string
          @return path to file
        """
        out_file = ""
        files = sorted(glob.glob("{:s}/*{:s}*".format(dir, search_time[0:8])))
        for f in files:
            se = sts.StringExtract(self.logger, template,
                                   os.path.basename(f))
            se.parseTemplate()
            ftime = se.getValidTime("%Y%m%d%H%M")
            if ftime != None and int(ftime) < int(file_time):
                out_file = f
        return out_file

    def find_closest_before(self, dir, time, template):
        """!Find the closest file that comes before the search time
        The file may be from the previous day
        Args:
          @param dir directory to search
          @param time search time - output must come before this time
          @param template filename template to search
          @rtype string
          @return path to file"""
        day_before = util.shift_time(time, -24)
        yesterday_file = self.search_day(dir, time,
                                         str(day_before)[0:10], template)
        today_file = self.search_day(dir, time, str(time)[0:10], template)
        # need to check valid time to make sure today_file does not come after VT
        if today_file == "":
            return yesterday_file
        else:
            return today_file


    def get_daily_file(self, valid_time, accum, data_src, file_template):
        """!Pull accumulation out of file that contains a full day of data
        Args:
          @param valid_time valid time to search
          @param accum accumulation to extract from file
          @param data_src type of data (FCST or OBS)
          @param file_template filename template to search
          @rtype bool
          @return True if file was added to output list, False if not"""
        # loop accum times
        data_interval = self.p.getint('config',
                                      data_src + '_DATA_INTERVAL') * 3600
        for i in range(0, accum, data_interval):
            search_time = util.shift_time(valid_time, -i)
            # find closest file before time
            f = self.find_closest_before(self.input_dir, search_time,
                                         file_template)
            if f == "":
                continue
            # build level info string
            se = sts.StringExtract(self.logger, file_template,
                                   os.path.basename(f))
            se.parseTemplate()
            file_time = datetime.datetime.strptime(se.getInitTime("%Y%m%d%H"),"%Y%m%d%H")
            v_time = datetime.datetime.strptime(search_time[0:10], "%Y%m%d%H")
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
        return False
        
        
    def get_accumulation(self, valid_time, accum, data_src,
                         file_template, is_forecast=False):
        """!Find files to combine to build the desired accumulation
        Args:
          @param valid_time valid time to search
          @param accum desired accumulation to build
          @param data_src type of data (FCST or OBS)
          @param file_template filename template to search
          @param is_forecast handle differently if reading forecast files
          @rtype bool
          @return True if full set of files to build accumulation is found
        """
        if self.input_dir == "":
            self.logger.error(self.app_name +
                              ": Must set data dir to run get_accumulation")
            exit

        if self.p.getbool('config', data_src + '_IS_DAILY_FILE', False) is True:
            return self.get_daily_file(valid_time, accum, data_src, file_template)

        start_time = valid_time
        last_time = util.shift_time(valid_time, -(int(accum) - 1))
        total_accum = int(accum)
        level = self.p.getint('config', data_src+'_LEVEL')
        search_accum = level
        # loop backwards in time until you have a full set of accum
        while last_time <= start_time:
            if is_forecast:
                f = self.getLowestForecastFile(start_time, data_src)
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
                        start_time = util.shift_time(start_time+"00", -search_accum)
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

    # TODO: change run_* to setup_*, then run app outside of if block
    def run_at_time_once(self, task_info, var_info, rl):
        cmd = None
        if not self.p.has_option('config', 'PCP_COMBINE_METHOD') or \
          self.p.getstr('config', 'PCP_COMBINE_METHOD') == "ADD":
            cmd = self.setup_add_method(task_info, var_info, rl)
        elif self.p.getstr('config', 'PCP_COMBINE_METHOD') == "SUM":
            cmd = self.setup_sum_method(task_info, var_info, rl)
        elif self.p.getstr('config', 'PCP_COMBINE_METHOD') == "SUBTRACT":
            cmd = self.setup_subtract_method(task_info, var_info, rl)
        else:
            self.logger.error("Invalid PCP_COMBINE_METHOD specified")
            exit(1)

        if cmd is None:
            self.logger.error("pcp_combine could not generate command")
            return
        self.logger.info("")
        self.build()


    def setup_subtract_method(self, task_info, var_info, rl):
        """!Setup pcp_combine to subtract two files to build desired accumulation
        Args:
          @param ti task_info object containing timing information
          @param v var_info object containing variable information
          @params rl data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        self.clear()
        in_dir = self.p.getdir(rl+'_PCP_COMBINE_INPUT_DIR')
        in_template = util.getraw_interp(self.p, 'filename_templates',
                                     rl+'_PCP_COMBINE_INPUT_TEMPLATE')
        out_dir = self.p.getdir(rl+'_PCP_COMBINE_OUTPUT_DIR')
        out_template = util.getraw_interp(self.p, 'filename_templates',
                                     rl+'_PCP_COMBINE_OUTPUT_TEMPLATE')

        accum = var_info.obs_level
        if accum[0].isalpha():
            accum = accum[1:]
        init_time = task_info.getInitTime()
        valid_time = task_info.getValidTime()
        lead = task_info.getLeadTime()
        lead2 = lead + int(accum)

        self.set_method("SUBTRACT")
        pcpSts1 = sts.StringSub(self.logger,
                                in_template,
                                init=init_time,
                                lead=str(lead).zfill(2))
        file1 = pcpSts1.doStringSub()

        pcpSts2 = sts.StringSub(self.logger,
                                in_template,
                                init=init_time,
                                lead=str(lead2).zfill(2))
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

        # If out template has a subdir, make that directory
        mk_dir = os.path.join(out_dir, os.path.dirname(out_file))
        if not os.path.exists(mk_dir):
            os.makedirs(mk_dir)

        cmd = self.get_command()
        outfile = self.get_output_path()
        return outfile


    def setup_sum_method(self, task_info, var_info, rl):
        """!Setup pcp_combine to build desired accumulation based on
        init/valid times and accumulations
        Args:
          @param ti task_info object containing timing information
          @param v var_info object containing variable information
          @params rl data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        self.clear()
        in_accum = self.p.getstr('config', rl+'_LEVEL')
        in_dir = self.p.getdir(rl+'_PCP_COMBINE_INPUT_DIR')
        in_template = util.getraw_interp(self.p, 'filename_templates',
                                     rl+'_PCP_COMBINE_INPUT_TEMPLATE')
        out_dir = self.p.getdir(rl+'_PCP_COMBINE_OUTPUT_DIR')
        out_template = util.getraw_interp(self.p, 'filename_templates',
                                     rl+'_PCP_COMBINE_OUTPUT_TEMPLATE')

        out_accum = var_info.obs_level
        if out_accum[0].isalpha():
            out_accum = out_accum[1:]
        valid_time = task_info.getValidTime()
        init_time = task_info.getInitTime()
        in_regex = util.template_to_init_regex(in_template,
                                               init_time, self.logger)
        self.set_method("SUM")
        self.set_init_time(init_time)
        self.set_valid_time(valid_time)
        self.set_in_accum(in_accum)
        self.set_out_accum(out_accum)
        self.set_pcp_dir(in_dir)
        self.set_pcp_regex(in_regex)
        self.set_output_dir(out_dir)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        pcpSts = sts.StringSub(self.logger,
                                out_template,
                                init=init_time,
                                valid=valid_time,
                                level=str(out_accum).zfill(2))
        pcp_out = pcpSts.doStringSub()
        self.set_output_filename(pcp_out)

        cmd = self.get_command()
        if cmd is None:
            self.logger.error("pcp_combine could not generate command")
            return
        outfile = self.get_output_path()
        return outfile


    def setup_add_method(self, task_info, var_info, data_src):
        """!Setup pcp_combine to add files to build desired accumulation
        Args:
          @param ti task_info object containing timing information
          @param v var_info object containing variable information
          @params rl data type (FCST or OBS)
          @rtype string
          @return path to output file"""
        is_forecast = False
        if data_src == "FCST":
            is_forecast = True
        self.clear()
        self.set_method("ADD")

        accum = var_info.obs_level
        if accum[0].isalpha():
            accum = accum[1:]

        valid_time = task_info.getValidTime()
        init_time = task_info.getInitTime()
        # TODO: should this be fcst_name if in forecast mode?
        compare_var = var_info.obs_name

        input_dir = self.p.getdir(data_src+'_PCP_COMBINE_INPUT_DIR')
        input_template = util.getraw_interp(self.p, 'filename_templates', data_src+'_PCP_COMBINE_INPUT_TEMPLATE')
        output_dir = self.p.getdir(data_src+'_PCP_COMBINE_OUTPUT_DIR')
        output_template = util.getraw_interp(self.p, 'filename_templates',
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
            if not self.p.has_option('dir', data_src+'_GEMPAK_INPUT_DIR') or \
              not self.p.has_option('filename_templates', data_src+'_GEMPAK_TEMPLATE'):
                self.logger.warning(self.app_name + ": Could not find " \
                                    "files to compute accumulation in " \
                                    + input_dir)
                return False
            gempak_dir = self.p.getdir(data_src+'_GEMPAK_INPUT_DIR')
            gempak_template = util.getraw_interp(self.p, 'filename_templates', data_src+'_GEMPAK_TEMPLATE')
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
        outfile = self.get_output_path()
        return outfile

if __name__ == "__main__":
        util.run_stand_alone("pcp_combine_wrapper", "PcpCombine")
