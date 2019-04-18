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
    def __init__(self, config, logger):
        super(GridStatWrapper, self).__init__(config, logger)
        met_install_dir = self.config.getdir('MET_INSTALL_DIR')
        self.app_path = os.path.join(met_install_dir, 'bin/grid_stat')
        self.app_name = os.path.basename(self.app_path)
        self.c_dict = self.create_c_dict()


    def create_c_dict(self):
        c_dict = super(GridStatWrapper, self).create_c_dict()
        c_dict['CONFIG_FILE'] = self.config.getstr('config', 'GRID_STAT_CONFIG', '')
        c_dict['OBS_INPUT_DIR'] = \
          self.config.getdir('OBS_GRID_STAT_INPUT_DIR', self.config.getdir('OUTPUT_BASE'))
        c_dict['OBS_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                               'OBS_GRID_STAT_INPUT_TEMPLATE')
        c_dict['OBS_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'OBS_GRID_STAT_INPUT_DATATYPE', '')

        c_dict['FCST_INPUT_DIR'] = \
          self.config.getdir('FCST_GRID_STAT_INPUT_DIR', self.config.getdir('OUTPUT_BASE'))
        c_dict['FCST_INPUT_TEMPLATE'] = \
          self.config.getraw('filename_templates',
                               'FCST_GRID_STAT_INPUT_TEMPLATE')
        c_dict['FCST_INPUT_DATATYPE'] = \
          self.config.getstr('config', 'FCST_GRID_STAT_INPUT_DATATYPE', '')


        c_dict['CLIMO_INPUT_DIR'] = ''
        c_dict['CLIMO_INPUT_TEMPLATE'] = ''
        if self.config.has_option('dir', 'CLIMO_GRID_STAT_INPUT_DIR'):
            c_dict['CLIMO_INPUT_DIR'] = \
              self.config.getdir('CLIMO_GRID_STAT_INPUT_DIR', '')
            c_dict['CLIMO_INPUT_TEMPLATE'] = \
              self.config.getraw('filename_templates',
                                   'CLIMO_GRID_STAT_INPUT_TEMPLATE')

        c_dict['OUTPUT_DIR'] =  self.config.getdir('GRID_STAT_OUT_DIR', self.config.getdir('OUTPUT_BASE'))
        c_dict['ONCE_PER_FIELD'] = self.config.getbool('config',
                                                        'GRID_STAT_ONCE_PER_FIELD',
                                                        False)
        c_dict['FCST_PROB_THRESH'] = self.config.getstr('config', 'FCST_GRID_STAT_PROB_THRESH', '==0.1')
        c_dict['OBS_PROB_THRESH'] = self.config.getstr('config', 'OBS_GRID_STAT_PROB_THRESH', '==0.1')

        c_dict['ALLOW_MULTIPLE_FILES'] = False
        c_dict['NEIGHBORHOOD_WIDTH'] = self.config.getstr('config', 'GRID_STAT_NEIGHBORHOOD_WIDTH', '')
        c_dict['NEIGHBORHOOD_SHAPE'] = self.config.getstr('config', 'GRID_STAT_NEIGHBORHOOD_SHAPE', '')
        c_dict['VERIFICATION_MASK_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'GRID_STAT_VERIFICATION_MASK_TEMPLATE')
        c_dict['VERIFICATION_MASK'] = ''

        # if window begin/end is set specific to grid_stat, override
        # OBS_WINDOW_BEGIN/END
        if self.config.has_option('config', 'OBS_GRID_STAT_WINDOW_BEGIN'):
            c_dict['OBS_WINDOW_BEGIN'] = \
              self.config.getint('config', 'OBS_GRID_STAT_WINDOW_BEGIN')
        if self.config.has_option('config', 'OBS_GRID_STAT_WINDOW_END'):
            c_dict['OBS_WINDOW_END'] = \
              self.config.getint('config', 'OBS_GRID_STAT_WINDOW_END')

        # same for FCST_WINDOW_BEGIN/END
        if self.config.has_option('config', 'FCST_GRID_STAT_WINDOW_BEGIN'):
            c_dict['FCST_WINDOW_BEGIN'] = \
              self.config.getint('config', 'FCST_GRID_STAT_WINDOW_BEGIN')
        if self.config.has_option('config', 'FCST_GRID_STAT_WINDOW_END'):
            c_dict['FCST_WINDOW_END'] = \
              self.config.getint('config', 'FCST_GRID_STAT_WINDOW_END')

        return c_dict


if __name__ == "__main__":
        util.run_stand_alone("grid_stat_wrapper", "GridStat")
