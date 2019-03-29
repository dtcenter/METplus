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
        met_install_dir = util.getdir(p, 'MET_INSTALL_DIR', None, logger)
        self.app_path = os.path.join(met_install_dir, 'bin/grid_stat')
        self.app_name = os.path.basename(self.app_path)
        self.create_c_dict()


    def create_c_dict(self):
        self.c_dict = dict()
        self.c_dict['var_list'] = util.parse_var_list(self.p)
        self.c_dict['LEAD_SEQ'] = util.getlistint(self.p.getstr('config', 'LEAD_SEQ', '0'))
        self.c_dict['MODEL_TYPE'] = self.p.getstr('config', 'MODEL_TYPE', 'FCST')
        self.c_dict['OB_TYPE'] = self.p.getstr('config', 'OB_TYPE', 'OBS')
        self.c_dict['CONFIG_DIR'] = util.getdir(self.p, 'CONFIG_DIR',
                                                 self.p.getdir('METPLUS_BASE')+'/parm/met_config',
                                                 self.logger)
        self.c_dict['CONFIG_FILE'] = self.p.getstr('config', 'GRID_STAT_CONFIG',
                                                    self.c_dict['CONFIG_DIR']+'/GridStatConfig_MEAN')
        self.c_dict['INPUT_BASE'] = util.getdir(self.p, 'INPUT_BASE', None, self.logger)
        self.c_dict['FCST_IS_PROB'] = self.p.getbool('config', 'FCST_IS_PROB', False)
        self.c_dict['OBS_IS_PROB'] = self.p.getbool('config', 'OBS_IS_PROB', False)
        self.c_dict['OBS_INPUT_DIR'] = \
          util.getdir(self.p, 'OBS_GRID_STAT_INPUT_DIR', self.p.getdir('OUTPUT_BASE'), self.logger)
        self.c_dict['OBS_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'OBS_GRID_STAT_INPUT_TEMPLATE')
        self.c_dict['OBS_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'OBS_GRID_STAT_INPUT_DATATYPE', '')
        self.c_dict['FCST_INPUT_DIR'] = \
          util.getdir(self.p, 'FCST_GRID_STAT_INPUT_DIR', self.p.getdir('OUTPUT_BASE'), self.logger)
        self.c_dict['FCST_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'FCST_GRID_STAT_INPUT_TEMPLATE')
        self.c_dict['FCST_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'FCST_GRID_STAT_INPUT_DATATYPE', '')
        self.c_dict['OUTPUT_DIR'] =  util.getdir(self.p, 'GRID_STAT_OUT_DIR', self.p.getdir('OUTPUT_BASE'), self.logger)
        self.c_dict['FCST_MAX_FORECAST'] = self.p.getint('config', 'FCST_MAX_FORECAST', 24)
        self.c_dict['FCST_INIT_INTERVAL'] = self.p.getint('config', 'FCST_INIT_INTERVAL', 12)
        self.c_dict['WINDOW_RANGE_BEG'] = \
          self.p.getint('config', 'WINDOW_RANGE_BEG', -3600)
        self.c_dict['WINDOW_RANGE_END'] = \
          self.p.getint('config', 'WINDOW_RANGE_END', 3600)
        self.c_dict['OBS_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                              'OBS_EXACT_VALID_TIME',
                                                              True)
        self.c_dict['FCST_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                              'FCST_EXACT_VALID_TIME',
                                                              True)
        self.c_dict['ONCE_PER_FIELD'] = self.p.getbool('config',
                                                        'GRID_STAT_ONCE_PER_FIELD',
                                                        False)
        self.c_dict['FCST_PROB_THRESH'] = self.p.getstr('config', 'FCST_GRID_STAT_PROB_THRESH', '==0.1')
        self.c_dict['OBS_PROB_THRESH'] = self.p.getstr('config', 'OBS_GRID_STAT_PROB_THRESH', '==0.1')

        self.c_dict['ALLOW_MULTIPLE_FILES'] = False
        util.add_common_items_to_dictionary(self.p, self.c_dict)


if __name__ == "__main__":
        util.run_stand_alone("grid_stat_wrapper", "GridStat")
