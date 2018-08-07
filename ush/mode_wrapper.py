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

import os
from compare_gridded_wrapper import CompareGriddedWrapper

class ModeWrapper(CompareGriddedWrapper):

    def __init__(self, p, logger):
        super(ModeWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/mode')
        self.app_name = os.path.basename(self.app_path)
        self.create_cg_dict()


    def create_cg_dict(self):
        self.cg_dict = dict()
        self.cg_dict['LOOP_BY_INIT'] = self.p.getbool('config', 'LOOP_BY_INIT', True)
        self.cg_dict['LEAD_SEQ'] = util.getlistint(self.p.getstr('config', 'LEAD_SEQ'))
        self.cg_dict['MODEL_TYPE'] = self.p.getstr('config', 'MODEL_TYPE')
        self.cg_dict['OB_TYPE'] = self.p.getstr('config', 'OB_TYPE')
        self.cg_dict['CONFIG_DIR'] = self.p.getdir('CONFIG_DIR')
        self.cg_dict['CONFIG_FILE'] = self.p.getstr('config', 'MODE_CONFIG')
        self.cg_dict['FCST_IS_PROB'] = self.p.getbool('config', 'FCST_IS_PROB')
        self.cg_dict['OBS_INPUT_DIR'] = \
          self.p.getdir('OBS_MODE_INPUT_DIR')
        self.cg_dict['OBS_INPUT_TEMPLATE'] = \
          self.p.getraw_interp('filename_template',
                               'OBS_MODE_INPUT_TEMPLATE')
        self.cg_dict['FCST_INPUT_DIR'] = \
          self.p.getdir('FCST_MODE_INPUT_DIR')
        self.cg_dict['FCST_INPUT_TEMPLATE'] = \
          self.p.getraw_interp('filename_template',
                               'FCST_MODE_INPUT_TEMPLATE')
        self.cg_dict['OUTPUT_DIR'] = \
          self.p.getdir('MODE_OUT_DIR')
        self.cg_dict['FCST_MAX_FORECAST'] = self.p.getint('config', 'FCST_MAX_FORECAST')
        self.cg_dict['FCST_INIT_INTERVAL']= self.p.getint('config', 'FCST_INIT_INTERVAL')
        self.cg_dict['WINDOW_RANGE_BEG'] = \
          self.p.getint('config', 'WINDOW_RANGE_BEG', -3600)
        self.cg_dict['WINDOW_RANGE_END'] = \
          self.p.getint('config', 'WINDOW_RANGE_END', 3600)
        self.cg_dict['OBS_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                              'OBS_EXACT_VALID_TIME',
                                                              True)


if __name__ == "__main__":
    util.run_stand_alone("mode_wrapper", "Mode")
