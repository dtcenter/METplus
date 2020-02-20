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

import metplus_check_python_version

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

        # get climatology config variables
        self.read_climo_wrapper_specific('GRID_STAT', c_dict)

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

        return c_dict

    def set_environment_variables(self, fcst_field, obs_field, time_info):
        """!Set environment variables that are referenced by the MET config file"""
        var_info = self.c_dict['VAR_LIST'][0]
        if self.c_dict['CURRENT_VAR_INFO'] is not None:
            var_info = self.c_dict['CURRENT_VAR_INFO']

        self.config.set('config', 'CURRENT_FCST_NAME', var_info['fcst_name'])
        self.config.set('config', 'CURRENT_OBS_NAME', var_info['obs_name'])
        self.config.set('config', 'CURRENT_FCST_LEVEL', var_info['fcst_level'])
        self.config.set('config', 'CURRENT_OBS_LEVEL', var_info['obs_level'])

        # set environment variables needed for MET application
        self.add_env_var("OBTYPE", self.c_dict['OBTYPE'])
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)

        # set climatology environment variables
        self.set_climo_env_vars()

        self.add_env_var("FCST_TIME", str(time_info['lead_hours']).zfill(3))
        self.add_env_var("INPUT_BASE", self.c_dict["INPUT_BASE"])

        # add additional env vars if they are specified
        self.add_env_var('NEIGHBORHOOD_WIDTH',
                         self.c_dict['NEIGHBORHOOD_WIDTH'])

        self.add_env_var('NEIGHBORHOOD_SHAPE',
                         self.c_dict['NEIGHBORHOOD_SHAPE'])

        self.add_env_var('VERIF_MASK',
                         self.c_dict['VERIFICATION_MASK'])

        self.add_env_var('OUTPUT_PREFIX', self.get_output_prefix(time_info))

        self.add_common_envs(time_info)

        # send environment variables to logger
        self.print_all_envs()


if __name__ == "__main__":
    util.run_stand_alone(__file__, "GridStat")
