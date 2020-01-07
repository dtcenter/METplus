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

import os
import met_util as util
from compare_gridded_wrapper import CompareGriddedWrapper

# pylint:disable=pointless-string-statement
"""!@namespace GridStatWrapper
@brief Wraps the MET tool grid_stat to compare gridded datasets
@endcode
"""

class GridStatWrapper(CompareGriddedWrapper):
    '''!Wraps the MET tool grid_stat to compare gridded datasets
    '''
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.app_name = 'grid_stat'
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_GRID_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['CONFIG_FILE'] = self.config.getstr('config', 'GRID_STAT_CONFIG_FILE', '')
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

        c_dict['CLIMO_INPUT_DIR'] = self.config.getdir('CLIMO_GRID_STAT_INPUT_DIR',
                                                       '')
        c_dict['CLIMO_INPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'CLIMO_GRID_STAT_INPUT_TEMPLATE',
                               '')

        c_dict['OUTPUT_DIR'] = self.config.getdir('GRID_STAT_OUTPUT_DIR',
                                                  self.config.getdir('OUTPUT_BASE'))
        c_dict['ONCE_PER_FIELD'] = self.config.getbool('config',
                                                       'GRID_STAT_ONCE_PER_FIELD',
                                                       False)
        c_dict['FCST_PROB_THRESH'] = self.config.getstr('config',
                                                        'FCST_GRID_STAT_PROB_THRESH', '==0.1')
        c_dict['OBS_PROB_THRESH'] = self.config.getstr('config',
                                                       'OBS_GRID_STAT_PROB_THRESH', '==0.1')

        c_dict['ALLOW_MULTIPLE_FILES'] = False
        c_dict['NEIGHBORHOOD_WIDTH'] = self.config.getstr('config',
                                                          'GRID_STAT_NEIGHBORHOOD_WIDTH', '1')
        c_dict['NEIGHBORHOOD_SHAPE'] = self.config.getstr('config',
                                                          'GRID_STAT_NEIGHBORHOOD_SHAPE', 'SQUARE')
        c_dict['VERIFICATION_MASK_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'GRID_STAT_VERIFICATION_MASK_TEMPLATE')
        c_dict['VERIFICATION_MASK'] = ''

        # handle window variables [FCST/OBS]_[FILE_]_WINDOW_[BEGIN/END]
        self.handle_window_variables(c_dict, 'grid_stat')

        c_dict['REGRID_TO_GRID'] = self.config.getstr('config', 'GRID_STAT_REGRID_TO_GRID', '')

        c_dict['OUTPUT_PREFIX'] = self.config.getstr('config', 'GRID_STAT_OUTPUT_PREFIX', '')

        return c_dict


if __name__ == "__main__":
    util.run_stand_alone(__file__, "GridStat")
