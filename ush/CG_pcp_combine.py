#!/usr/bin/env python

'''
Program Name: CG_pcp_combine.py
Contact(s): George McCabe
Abstract: Runs pcp_combine to merge multiple forecast files
History Log:  Initial version
Usage: CG_pcp_combine.py
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

from CommandGen import CommandGen


class CG_pcp_combine(CommandGen):

    def __init__(self, p, logger):
        super(CG_pcp_combine, self).__init__(p, logger)
        self.app_path = self.p.getstr('exe', 'PCP_COMBINE')
        self.app_name = os.path.basename(self.app_path)
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

            init = se.getInitTime("%Y%m%d%H")
            v = util.shift_time(init, fcst)
            if v == valid_time:
                out_file = fpath
        return out_file
    
    # NOTE: Assumes YYYYMMDD sub dir
    def get_lowest_forecast_at_valid(self, valid_time, dtype):
        out_file = ""
        day_before = util.shift_time(valid_time, -24)
        input_template = self.p.getraw('filename_templates',
                                       dtype+'_INPUT_TEMPLATE')
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
#        files = sorted(glob.glob("{:s}/{:s}/*".format(self.input_dir,
#                                                      str(day_before)[0:8])))
#        for fpath in files:
#            f = os.path.join(str(day_before)[0:8], os.path.basename(fpath))
#            se = sts.StringExtract(self.logger, input_template, f)
#            se.parseTemplate()

#            fcst = se.leadHour
#            if fcst is -1:
#                print("ERROR: Could not pull forecast lead from f")
#                exit

#            init = se.getInitTime("%Y%m%d%H")
#            v = util.shift_time(init, fcst)
#            if v == valid_time:
#                out_file = fpath

#        files = sorted(glob.glob("{:s}/{:s}/*".format(self.input_dir,
#                                                      str(valid_time)[0:8])))
#        for fpath in files:
#            f = os.path.join(str(day_before)[0:8], os.path.basename(fpath))
#            se = sts.StringExtract(self.logger, input_template, f)
#            se.parseTemplate()
#            fcst = se.leadHour

#            if fcst is -1:
#                print("ERROR: Could not pull forecast lead from f")
#                exit

#            init = se.getInitTime("%Y%m%d%H")
#            v = util.shift_time(init, fcst)
#            if v == valid_time:
#                out_file = fpath
#        return out_file

    def search_day(self, dir, file_time, search_time, template):
        out_file = ""
        print("Search:"+dir+" and "+search_time)
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
        print("Y:"+yesterday_file)
        print("T:"+today_file)
        if today_file == "":
            return yesterday_file
        else:
            return today_file

    def get_accumulation(self, valid_time, accum, ob_type, is_forecast=False):
        # TODO: pass in template (input/native) so this isn't assumed
        file_template = self.p.getraw('filename_templates',
                                      ob_type+"_INPUT_TEMPLATE")

        if self.input_dir == "":
            self.logger.error(self.app_name +
                              ": Must set data dir to run get_accumulation")
            exit
        self.add_arg("-add")

        if self.p.getbool('config', ob_type+'_IS_DAILY_FILE') is True:
            # loop accum times
            data_interval = self.p.getint('config',
                                          ob_type+'_DATA_INTERVAL')*3600
            for i in range(0, accum, data_interval):
                search_time = util.shift_time(valid_time, -i)
                # find closest file before time
                f = self.find_closest_before(self.input_dir, search_time,
                                             file_template)
                if f == "":
                    continue
                # build level info string
                file_time = datetime.datetime.strptime(f[-18:-8], "%Y%m%d%H")
                v_time = datetime.datetime.strptime(search_time, "%Y%m%d%H")
                diff = v_time - file_time
                lead = int((diff.days*24) / (data_interval/3600))
                lead += int((v_time - file_time).seconds/data_interval) - 1
                fname = self.p.getstr('config',
                                      ob_type+'_'+str(accum)+'_FIELD_NAME')
                addon = "'name=\"" + fname + "\"; level=\"(" + \
                        str(lead)+",*,*)\";'"
                self.add_input_file(f, addon)
        else:  # not a daily file
            # if field that corresponds to search accumulation exists
            # in the files,
            #  check the file with valid time before moving backwards in time
            if self.p.has_option('config',
                                 ob_type+'_'+str(accum)+'_FIELD_NAME') and ob_type != "NATIONAL_BLEND":
#                print("XXXX"+self.p.getstr('config',ob_type+'_'+str(accum)+'_FIELD_NAME'))
                fSts = sts.StringSub(self.logger,
                                     file_template,
                                     valid=valid_time,
                                     accum=str(accum).zfill(2))
                # TODO: This assumes max 99 accumulation.
                # zfill to 3 if above that is possible
#                print("F:"+file_template+" "+valid_time+" "+ob_type)
                search_file = os.path.join(self.input_dir, fSts.doStringSub())

                if os.path.exists(search_file):
                    data_type = self.p.getstr('config',
                                              ob_type+'_NATIVE_DATA_TYPE')
                    if data_type == "GRIB":
                        addon = accum
                    elif data_type == "NETCDF":
                        fname = self.p.getstr('config',
                                              ob_type + '_' + str(accum) +
                                              '_FIELD_NAME')
                        addon = "'name=\"" + fname + "\"; level=\"(0,*,*)\";'"
                    self.add_input_file(search_file, addon)
                    self.set_output_dir(self.outdir)
                    return

        start_time = valid_time
        last_time = util.shift_time(valid_time, -(accum-1))
        total_accum = accum
        search_accum = total_accum
        # loop backwards in time until you have a full set of accum
        while last_time <= start_time:
            if is_forecast:
                f = self.get_lowest_forecast_at_valid(start_time, ob_type)
                if f == "":
                    break
                # TODO: assumes 1hr accum (6 for NB) in these files for now
                if ob_type == "NATIONAL_BLEND":
                    ob_str = self.p.getstr('config',
                                           ob_type + '_'+str(6) +
                                           '_FIELD_NAME')
                    addon = "'name=\"" + ob_str + "\"; level=\"(0,*,*)\";'"
                else:
                    ob_str = self.p.getstr('config',
                                           ob_type + '_'+str(1) +
                                           '_FIELD_NAME')
                    addon = "'name=\"" + ob_str + "\"; level=\"(0,*,*)\";'"
                self.add_input_file(f, addon)
                start_time = util.shift_time(start_time, -1)
                search_accum -= 1
            else:  # not looking for forecast files
                # get all files of valid_time (all accums)
                files = sorted(glob.glob("{:s}/{:s}/*{:s}*"
                                         .format(self.input_dir,
                                                 start_time[0:8], start_time)))
                # look for biggest accum that fits search
                while search_accum > 0:
                    fSts = sts.StringSub(self.logger,
                                         file_template,
                                         valid=start_time,
                                         accum=str(search_accum).zfill(2))
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
                        data_type = self.p.getstr('config', ob_type +
                                                  '_NATIVE_DATA_TYPE')
                        if data_type == "GRIB":
                            addon = search_accum
                        elif data_type == "NETCDF":
                            ob_str = self.p.getstr('config', ob_type +
                                                   '_'+str(search_accum) +
                                                   '_FIELD_NAME')
                            addon = "'name=\"" + ob_str + \
                                    "\"; level=\"(0,*,*)\";'"
                        self.add_input_file(f, addon)
                        start_time = util.shift_time(start_time, -search_accum)
                        total_accum -= search_accum
                        search_accum = total_accum
                        break
                    search_accum -= 1

                    if total_accum == 0:
                        break

                if search_accum == 0:
                    self.logger.warning(self.app_name + ": Could not find "\
                                        "files to compute accumulation")
                    return None

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

    def run_at_time(self, valid_time, accum, ob_type,
                    fcst_var, is_forecast=False):
        input_dir = self.p.getstr('config', ob_type+'_INPUT_DIR')
        native_dir = self.p.getstr('config', ob_type+'_NATIVE_DIR')
        bucket_dir = self.p.getstr('config', ob_type+'_BUCKET_DIR')
        bucket_template = self.p.getraw('filename_templates',
                                        ob_type+'_BUCKET_TEMPLATE')

        ymd_v = valid_time[0:8]
        if not os.path.exists(os.path.join(native_dir, ymd_v)):
            os.makedirs(os.path.join(native_dir, ymd_v))
        if not os.path.exists(os.path.join(bucket_dir, ymd_v)):
            os.makedirs(os.path.join(bucket_dir, ymd_v))

        self.set_input_dir(input_dir)
        self.set_output_dir(bucket_dir)
        self.get_accumulation(valid_time, int(accum), ob_type, is_forecast)

        #  call GempakToCF if native file doesn't exist
        infiles = self.get_input_files()
        for idx, infile in enumerate(infiles):
            # replace input_dir with native_dir, check if file exists
            nfile = infile.replace(input_dir, native_dir)
            data_type = self.p.getstr('config', ob_type+'_NATIVE_DATA_TYPE')
            if data_type == "NETCDF":
                nfile = os.path.splitext(nfile)[0]+'.nc'
            if not os.path.isfile(nfile):
                print("Calling GempakToCF to convert to NetCDF")
                run_g2c = CG_GempakToCF(self.p, self.logger)
                run_g2c.add_input_file(infile)
                run_g2c.set_output_path(nfile)
                cmd = run_g2c.get_command()
                if cmd is None:
                    print("ERROR: GempakToCF could not generate command")
                    continue
                print("RUNNING:"+str(cmd))
                run_g2c.run()
            infiles[idx] = nfile

            pcpSts = sts.StringSub(self.logger,
                                   bucket_template,
                                   valid=valid_time,
                                   accum=str(accum).zfill(2))
            pcp_out = pcpSts.doStringSub()
            self.set_output_filename(pcp_out)
#            if(is_forecast):
#              varname = self.p.getstr('config', fcst_var+"_VAR")
#            else:
            varname = self.p.getstr('config', ob_type+"_VAR")                
            self.add_arg("-name "+varname+"_"+accum)
            cmd = self.get_command()
            if cmd is None:
                print("ERROR: pcp_combine could not generate command")
                continue
            print("RUNNING: "+str(cmd))
            self.logger.info("")
            self.run()
            outfile = self.get_output_path()
