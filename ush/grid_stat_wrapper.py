#!/usr/bin/env python

'''
Program Name: grid_stat_wrapper.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage: 
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division)

import os
import met_util as util
from compare_gridded_wrapper import CompareGriddedWrapper

'''!@namespace GridStatWrapper
@brief Wraps the MET tool grid_stat to compare gridded datasets
@endcode
'''
class GridStatWrapper(CompareGriddedWrapper):
    '''!Wraps the MET tool grid_stat to compare gridded datasets
    '''
    def __init__(self, p, logger):
        super(GridStatWrapper, self).__init__(p, logger)
        met_install_dir = p.getdir('MET_INSTALL_DIR')
        self.app_path = os.path.join(met_install_dir, 'bin/grid_stat')
        self.app_name = os.path.basename(self.app_path)
        self.create_cg_dict()


    def create_cg_dict(self):
        self.cg_dict = dict()
        self.cg_dict['LOOP_BY_INIT'] = self.p.getbool('config', 'LOOP_BY_INIT', True)
        self.cg_dict['LEAD_SEQ'] = util.getlistint(self.p.getstr('config', 'LEAD_SEQ', '0'))
        self.cg_dict['MODEL_TYPE'] = self.p.getstr('config', 'MODEL_TYPE', 'FCST')
        self.cg_dict['OB_TYPE'] = self.p.getstr('config', 'OB_TYPE', 'OBS')
        self.cg_dict['CONFIG_DIR'] = self.p.getdir('CONFIG_DIR',
                                                   self.p.getdir('METPLUS_BASE')+'/parm/met_config')
        self.cg_dict['CONFIG_FILE'] = self.p.getstr('config', 'GRID_STAT_CONFIG',
                                                    self.cg_dict['CONFIG_DIR']+'/GridStatConfig_MEAN')
        self.cg_dict['FCST_IS_PROB'] = self.p.getbool('config', 'FCST_IS_PROB', False)
        self.cg_dict['OBS_INPUT_DIR'] = \
          self.p.getdir('OBS_GRID_STAT_INPUT_DIR')
        self.cg_dict['OBS_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'OBS_GRID_STAT_INPUT_TEMPLATE')
        self.cg_dict['FCST_INPUT_DIR'] = \
          self.p.getdir('FCST_GRID_STAT_INPUT_DIR')
        self.cg_dict['FCST_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'FCST_GRID_STAT_INPUT_TEMPLATE')
        self.cg_dict['OUTPUT_DIR'] =  self.p.getdir('GRID_STAT_OUT_DIR')
        self.cg_dict['INPUT_BASE'] =  self.p.getdir('INPUT_BASE')
        self.cg_dict['FCST_MAX_FORECAST'] = self.p.getint('config', 'FCST_MAX_FORECAST', 24)
        self.cg_dict['FCST_INIT_INTERVAL'] = self.p.getint('config', 'FCST_INIT_INTERVAL', 12)
        self.cg_dict['WINDOW_RANGE_BEG'] = \
          self.p.getint('config', 'WINDOW_RANGE_BEG', -3600)
        self.cg_dict['WINDOW_RANGE_END'] = \
          self.p.getint('config', 'WINDOW_RANGE_END', 3600)
        self.cg_dict['OBS_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                              'OBS_EXACT_VALID_TIME',
                                                              True)
        # these are not used by grid_stat, only mode
        self.cg_dict['QUILT'] = "FALSE"
        self.cg_dict['CONV_RADIUS'] = 5
        self.cg_dict['CONV_THRESH'] = 0.5
        self.cg_dict['MERGE_THRESH'] = 0.45
        self.cg_dict['MERGE_FLAG'] = "THRESH"


    def do_wrapper_specific_operations(self):
        self.add_env_var("INPUT_BASE", self.cg_dict["INPUT_BASE"])
        self.print_env_item("INPUT_BASE")
        self.logger.debug("")
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(["MODEL", "FCST_VAR", "OBS_VAR",
                             "LEVEL", "OBTYPE", "CONFIG_DIR",
                             "FCST_FIELD", "OBS_FIELD",
                             "INPUT_BASE",
                             "MET_VALID_HHMM"])
        self.logger.debug("")


if __name__ == "__main__":
        util.run_stand_alone("grid_stat_wrapper", "GridStat")
