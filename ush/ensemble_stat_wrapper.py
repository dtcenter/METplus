#!/usr/bin/env python

'''
Program Name: ensemble_stat_wrapper.py
Contact(s): metplus-dev
Abstract:  Initial template based on grid_stat_wrapper by George McCabe
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
from compare_ensemble_wrapper import CompareEnsembleWrapper

"""!@namespace EnsembleStatWrapper
@brief Wraps the MET tool ensemble_stat to compare ensemble datasets
@endcode
"""
class EnsembleStatWrapper(CompareEnsembleWrapper):
    """!Wraps the MET tool ensemble_stat to compare ensemble datasets
    """
    def __init__(self, p, logger):
        super(EnsembleStatWrapper, self).__init__(p, logger)
        self.met_install_dir = p.getdir('MET_INSTALL_DIR')
        self.app_path = os.path.join(self.met_install_dir, 'bin/ensemble_stat')
        self.app_name = os.path.basename(self.app_path)

        # create the ensemble stat dictionary.
        self.ce_dict = self.create_ce_dict()

    def create_ce_dict(self):
        """!Create a dictionary containing the values set in the config file
           that are required for running ensemble stat.
           This will make it easier for unit testing.

           Returns:
               @returns A dictionary of the ensemble stat values 
                        from the config file.
        """

        ce_dict = dict()

        # Loop by initialization times 
        ce_dict['LOOP_BY_INIT'] = \
            self.p.getbool('config', 'LOOP_BY_INIT', True)

        # A list of forecast hours from the initialization time that will
        # be processed.
        ce_dict['LEAD_SEQ'] = \
            util.getlistint(self.p.getstr('config', 'LEAD_SEQ', '0'))

        ce_dict['MODEL'] = self.p.getstr('config', 'MODEL', 'HRRRE')

        ce_dict['GRID_VX'] = self.p.getstr('config', 'GRID_VX', 'FCST')

        ce_dict['OB_TYPE'] = self.p.getstr('config', 'OB_TYPE', 'OBS')

        ce_dict['CONFIG_DIR'] = \
            self.p.getdir('CONFIG_DIR',
                          self.p.getdir('PARM_BASE')+'/use_cases/ensemble//met_config')
        ce_dict['MET_CONFIG_FILE'] = \
            self.p.getstr('config', 'ENSEMBLE_STAT_CONFIG',
                          ce_dict['CONFIG_DIR']+'/EnsembleStatConfig_SFC')

        # met_obs_error_table is not required, if it is not defined
        # set it to the empty string '', that way the MET default is used.
        ce_dict['MET_OBS_ERROR_TABLE'] = \
            self.p.getstr('config', 'MET_OBS_ERROR_TABLE','')

        # TODO: jtf This is beta functionality
        # This fully works and has been tested ... but present to the
        # team to see if we want something like this ...
        # The following text is meant to be moved to the conf file it
        # we add this capability ...
        # [user_env_vars]
        # user_env_vars section:
        # Use this section to define new environment variable that you would
        # like exported to the runtime environment, where they can be accessed
        # and used by MET. This is really just a convenience so any new
        # environment variables you may want to be defined can be maintained
        # in this conf file. rather than putting them in your login shell.
        #
        # All variables in the user_env_vars section will be exported
        # The user_env_vars section is not required.
        # The user_env_vars section can be empty

        # Setup the user_env_vars section.
        # All variables in the user_env_vars section of a conf file will
        # be exported to the environment, where they may be accessed
        # and used by MET.
        # We add a user_env_vars section to the conf object if it does not exist.
        # Doing so simplifies the use of  user_env_vars in the code
        # since you will not have to check for the existence of the section
        # with each reference, at the very least it will
        # be an empty list [] and any for loops will not be entered.
        if 'user_env_vars' not in self.p.sections():
            self.p.add_section('user_env_vars')
        for env_var in self.p.keys('user_env_vars'):
            ce_dict[env_var]=self.p.getstr('user_env_vars',env_var,'')

        # No Default being set this is REQUIRED TO BE DEFINED in conf file.
        ce_dict['N_ENSEMBLE_MEMBERS'] = \
            self.p.getstr('filename_templates','N_ENSEMBLE_MEMBERS')

        ce_dict['FCST_IS_PROB'] = self.p.getbool('config', 'FCST_IS_PROB', False)

        ce_dict['OBS_INPUT_DIR'] = \
          self.p.getdir('OBS_ENSEMBLE_STAT_INPUT_DIR')

        # The Observations input files used by ensemble_stat. 
        # This is a raw string and will be interpreted to generate the 
        # filenames.
        ce_dict['OBS_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'OBS_INPUT_TEMPLATE')

        # The ensemble forecast files input directory and filename templates
        ce_dict['FCST_INPUT_DIR'] = \
          self.p.getdir('FCST_ENSEMBLE_STAT_INPUT_DIR')

        # This is a raw string and will be interpreted to generate the 
        # ensemble member filenames. This may be a list of 1 or n members.
        ce_dict['FCST_INPUT_TEMPLATE'] = \
          util.getlist(util.getraw_interp(self.p, 'filename_templates',
                               'FCST_ENSEMBLE_STAT_INPUT_TEMPLATE'))


        ce_dict['OUTPUT_DIR'] =  self.p.getdir('ENSEMBLE_STAT_OUT_DIR')
        ce_dict['INPUT_BASE'] =  self.p.getdir('INPUT_BASE')

        # The max forecast lead in hours.
        ce_dict['FCST_MAX_FORECAST'] = \
            self.p.getint('config', 'FCST_MAX_FORECAST', 24)
        ce_dict['FCST_INIT_INTERVAL'] = \
            self.p.getint('config', 'FCST_INIT_INTERVAL', 12)

        ce_dict['OBS_WINDOW_BEGIN'] = \
          self.p.getint('config', 'OBS_WINDOW_BEGIN', -3600)
        ce_dict['OBS_WINDOW_END'] = \
          self.p.getint('config', 'OBS_WINDOW_END', 3600)
        ce_dict['OBS_EXACT_VALID_TIME'] = \
            self.p.getbool('config','OBS_EXACT_VALID_TIME',True)
        return ce_dict


if __name__ == "__main__":
        util.run_stand_alone("ensemble_stat_wrapper", "EnsembleStat")
