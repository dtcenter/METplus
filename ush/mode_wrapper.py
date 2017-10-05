#!/usr/bin/env python

'''
Program Name: mode_wrapper.py
Contact(s): George McCabe
Abstract: Runs mode
History Log:  Initial version
Usage: 
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division)

import logging
import os
import sys
import met_util as util
import re
import csv
import subprocess
from CommandBuilder import CommandBuilder


class ModeWrapper(CommandBuilder):

    def __init__(self, p, logger):
        super(Mode, self).__init__(p, logger)
        self.app_path = self.p.getstr('exe', 'MODE')
        self.app_name = os.path.basename(self.app_path)

    def set_output_dir(self, outdir):
        self.outdir = "-outdir "+outdir

    def get_command(self):
        if self.app_path is None:
            self.logger.error(self.app_name + ": No app path specified. "\
                              "You must use a subclass")
            return None

        cmd = self.app_path + " "
        for a in self.args:
            cmd += a + " "

        if len(self.infiles) == 0:
            self.logger.error(self.app_name+": No input filenames specified")
            return None

        for f in self.infiles:
            cmd += f + " "

        if self.param != "":
            cmd += self.param + " "

        if self.outdir == "":
            self.logger.error(self.app_name+": No output directory specified")
            return None

        cmd += self.outdir
        return cmd

    def run_at_time(self, init_time, accum, ob_type, fcst_var):
        # TODO: Need to get model_path!
        model_type = self.p.getstr('config', 'MODEL_TYPE')
        obs_var = self.p.getstr('config', ob_type+"_VAR")
        config_dir = self.p.getstr('config', 'CONFIG_DIR')

        fcst_fields = list()
        obs_fields = list()
        for fcst_thresh in fcst_threshs:
            fcst_fields.append("{ name=\"" + fcst_var + "\"; level=\"A" +
                               accum + "\";}")
        for obs_thresh in obs_threshs:
            obs_fields.append("{ name=\"" + obs_var + "_" + accum +
                              "\"; level=\"(*,*)\";}")

        for idx, fcst in enumerate(fcst_fields):
            self.add_input_file(model_path)
            self.add_input_file(regrid_path)
            self.set_param_file(self.p.getstr('config', 'MET_CONFIG_MD'))
            self.set_output_dir(self.p.getstr('config', 'MODE_OUT_DIR'))
            self.add_env_var("MODEL", model_type)
            self.add_env_var("FCST_VAR", fcst_var)
            self.add_env_var("OBS_VAR", obs_var)
            self.add_env_var("ACCUM", accum)
            self.add_env_var("OBTYPE", ob_type)
            self.add_env_var("CONFIG_DIR", config_dir)
            self.add_env_var("FCST_FIELD", fcst)
            self.add_env_var("OBS_FIELD", obs_fields[idx])
            self.logger.debug("")
            self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
            self.print_env_item("MODEL")
            self.print_env_item("FCST_VAR")
            self.print_env_item("OBS_VAR")
            self.print_env_item("ACCUM")
            self.print_env_item("OBTYPE")
            self.print_env_item("CONFIG_DIR")
            self.print_env_item("FCST_FIELD")
            self.print_env_item("OBS_FIELD")
            self.logger.info("")
            cmd = run_mode.get_command()
            if cmd is None:
                print("ERROR: mode could not generate command")
                continue
            print("RUNNING: " + str(cmd))
            self.build()
