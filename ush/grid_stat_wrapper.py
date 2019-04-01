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
        self.c_dict = self.create_c_dict()


    def create_c_dict(self):
        c_dict = super(GridStatWrapper, self).create_c_dict()
        c_dict['CONFIG_FILE'] = self.p.getstr('config', 'GRID_STAT_CONFIG', '')
        c_dict['OBS_INPUT_DIR'] = \
          util.getdir(self.p, 'OBS_GRID_STAT_INPUT_DIR', self.p.getdir('OUTPUT_BASE'), self.logger)
        c_dict['OBS_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'OBS_GRID_STAT_INPUT_TEMPLATE')
        c_dict['OBS_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'OBS_GRID_STAT_INPUT_DATATYPE', '')

        c_dict['FCST_INPUT_DIR'] = \
          util.getdir(self.p, 'FCST_GRID_STAT_INPUT_DIR', self.p.getdir('OUTPUT_BASE'), self.logger)
        c_dict['FCST_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'FCST_GRID_STAT_INPUT_TEMPLATE')
        c_dict['FCST_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'FCST_GRID_STAT_INPUT_DATATYPE', '')

        c_dict['CLIMO_INPUT_DIR'] = \
          util.getdir(self.p, 'CLIMO_GRID_STAT_INPUT_DIR', '', self.logger)
        c_dict['CLIMO_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'CLIMO_GRID_STAT_INPUT_TEMPLATE')

        c_dict['OUTPUT_DIR'] =  util.getdir(self.p, 'GRID_STAT_OUT_DIR', self.p.getdir('OUTPUT_BASE'), self.logger)
        c_dict['ONCE_PER_FIELD'] = self.p.getbool('config',
                                                        'GRID_STAT_ONCE_PER_FIELD',
                                                        False)
        c_dict['FCST_PROB_THRESH'] = self.p.getstr('config', 'FCST_GRID_STAT_PROB_THRESH', '==0.1')
        c_dict['OBS_PROB_THRESH'] = self.p.getstr('config', 'OBS_GRID_STAT_PROB_THRESH', '==0.1')

        c_dict['ALLOW_MULTIPLE_FILES'] = False
        return c_dict


if __name__ == "__main__":
        util.run_stand_alone("grid_stat_wrapper", "GridStat")
