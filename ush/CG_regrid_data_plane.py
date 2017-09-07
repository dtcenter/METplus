#!/usr/bin/env python

'''
Program Name: CG_regrid_data_plane.py
Contact(s): George McCabe
Abstract: Runs regrid_data_plane
History Log:  Initial version
Usage: CG_regrid_data_plane.py
Parameters: None
Input Files: nc files
Output Files: nc files
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
import string_template_substitution as sts
from CommandGen import CommandGen


class CG_regrid_data_plane(CommandGen):

    def __init__(self, p, logger):
        super(CG_regrid_data_plane, self).__init__(p, logger)
        self.app_path = self.p.getstr('exe', 'REGRID_DATA_PLANE_EXE')
        self.app_name = os.path.basename(self.app_path)

    def run_at_time(self, valid_time, accum, ob_type):
        obs_var = self.p.getstr('config', ob_type+"_VAR")
        bucket_dir = self.p.getstr('config', ob_type+'_BUCKET_DIR')
        bucket_template = self.p.getraw('filename_templates',
                                        ob_type+'_BUCKET_TEMPLATE')
        regrid_dir = self.p.getstr('config', ob_type+'_REGRID_DIR')
        regrid_template = self.p.getraw('filename_templates',
                                        ob_type+'_REGRID_TEMPLATE')

        ymd_v = valid_time[0:8]
        if not os.path.exists(os.path.join(regrid_dir, ymd_v)):
            os.makedirs(os.path.join(regrid_dir, ymd_v))

        pcpSts = sts.StringSub(self.logger,
                               bucket_template,
                               valid=valid_time,
                               accum=str(accum).zfill(2))
        outfile = os.path.join(bucket_dir, pcpSts.doStringSub())

        self.add_input_file(outfile)
        self.add_input_file(self.p.getstr('config', 'VERIFICATION_GRID'))
        regridSts = sts.StringSub(self.logger,
                                  regrid_template,
                                  valid=valid_time,
                                  accum=str(accum).zfill(2))
        regrid_file = regridSts.doStringSub()
        self.set_output_path(os.path.join(regrid_dir, regrid_file))
        field_name = "{:s}_{:s}".format(obs_var, str(accum).zfill(2))
        self.add_arg("-field 'name=\"{:s}\"; level=\"(*,*)\";'".format(
                                                                 field_name))
        self.add_arg("-method BUDGET")
        self.add_arg("-width 2")
        self.add_arg("-name "+field_name)
        cmd = self.get_command()
        if cmd is None:
            print("ERROR: regrid_data_plane could not generate command")
            return
        print("RUNNING: "+str(cmd))
        self.logger.info("")
        self.run()
