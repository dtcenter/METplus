#!/usr/bin/env python

import metplus_check_python_version

import os
import met_util as util
import time_util
from compare_gridded_wrapper import CompareGriddedWrapper


"""
Program Name: point_stat_wrapper.py
Contact(s): Minna Win, Jim Frimel, George McCabe, Julie Prestopnik
Abstract: Wrapper to MET point_stat
History Log:  Initial version
Usage: point_stat_wrapper.py
Parameters: None
Input Files: netCDF data files
Output Files: ascii files
Condition codes: 0 for success, 1 for failure

"""


class PointStatWrapper(CompareGriddedWrapper):
    """! Wrapper to the MET tool, Point-Stat."""

    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.app_name = 'point_stat'
        self.app_path = os.path.join(config.getdir('MET_INSTALL_DIR'),
                                     'bin', self.app_name)

    def create_c_dict(self):
        """! Create a dictionary that holds all the values set in the
             METplus config file for the point-stat wrapper.

             Returns:
                 c_dict   - A dictionary containing the key-value pairs set
                             in the METplus configuration file.
        """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_POINT_STAT_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True
        c_dict['OFFSETS'] = util.getlistint(self.config.getstr('config', 'POINT_STAT_OFFSETS', '0'))
        c_dict['FCST_INPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'FCST_POINT_STAT_INPUT_TEMPLATE')
        c_dict['OBS_INPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'OBS_POINT_STAT_INPUT_TEMPLATE')

        c_dict['FCST_INPUT_DATATYPE'] = \
            self.config.getstr('config', 'FCST_POINT_STAT_INPUT_DATATYPE', '')
        c_dict['OBS_INPUT_DATATYPE'] = \
            self.config.getstr('config', 'OBS_POINT_STAT_INPUT_DATATYPE', '')

        c_dict['FCST_INPUT_DIR'] = self.config.getdir('FCST_POINT_STAT_INPUT_DIR')
        c_dict['OBS_INPUT_DIR'] = self.config.getdir('OBS_POINT_STAT_INPUT_DIR')
        c_dict['OUTPUT_DIR'] = \
            self.config.getdir('POINT_STAT_OUTPUT_DIR')

        c_dict['CLIMO_INPUT_DIR'] = self.config.getdir('CLIMO_POINT_STAT_INPUT_DIR',
                                                       '')
        c_dict['CLIMO_INPUT_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'CLIMO_POINT_STAT_INPUT_TEMPLATE',
                               '')

        # Configuration
        c_dict['CONFIG_FILE'] = \
            self.config.getstr('config', 'POINT_STAT_CONFIG_FILE')

        c_dict['MODEL'] = self.config.getstr('config', 'MODEL')
        c_dict['POINT_STAT_CONFIG_FILE'] = \
            self.config.getstr('config', 'POINT_STAT_CONFIG_FILE')

        c_dict['REGRID_TO_GRID'] = self.config.getstr('config', 'POINT_STAT_REGRID_TO_GRID', '')

        c_dict['POINT_STAT_GRID'] = self.config.getstr('config', 'POINT_STAT_GRID')
        c_dict['POINT_STAT_POLY'] = self.config.getstr('config', 'POINT_STAT_POLY', '')
        c_dict['POINT_STAT_STATION_ID'] = self.config.getstr('config', 'POINT_STAT_STATION_ID', '')
        c_dict['POINT_STAT_MESSAGE_TYPE'] = self.config.getstr('config', 'POINT_STAT_MESSAGE_TYPE', '')

        # handle window variables [FCST/OBS]_[FILE_]_WINDOW_[BEGIN/END]
        self.handle_window_variables(c_dict, 'point_stat')

        c_dict['VERIFICATION_MASK_TEMPLATE'] = \
            self.config.getraw('filename_templates',
                               'POINT_STAT_VERIFICATION_MASK_TEMPLATE')
        c_dict['VERIFICATION_MASK'] = ''

        c_dict['FCST_PROB_THRESH'] = self.config.getstr('config',
                                                        'FCST_POINT_STAT_PROB_THRESH', '==0.1')
        c_dict['OBS_PROB_THRESH'] = self.config.getstr('config',
                                                       'OBS_POINT_STAT_PROB_THRESH', '==0.1')

        if c_dict['FCST_INPUT_TEMPLATE'] == '':
            self.log_error('Must set FCST_POINT_STAT_INPUT_TEMPLATE in config file')
            self.isOK = False

        if c_dict['OBS_INPUT_TEMPLATE'] == '':
            self.log_error('Must set OBS_POINT_STAT_INPUT_TEMPLATE in config file')
            self.isOK = False

        if c_dict['OUTPUT_DIR'] == '':
            self.log_error('Must set POINT_STAT_OUTPUT_DIR in config file')
            self.isOK = False

        return c_dict

    def run_at_time(self, input_dict):
        """! Stub, not yet implemented """

        # loop of forecast leads and process each
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            lead_string = time_util.ti_calculate(input_dict)['lead_string']
            self.logger.info("Processing forecast lead {}".format(lead_string))

            # Run for given init/valid time and forecast lead combination
            self.run_at_time_once(input_dict)

    def run_at_time_once(self, input_dict):
         # clear any settings leftover from previous run
        self.clear()

        time_info = time_util.ti_calculate(input_dict)
        var_list = util.parse_var_list(self.config, time_info)

        if not var_list:
            self.log_error("Field information not set in configuration files. Must set "
                           "[FCST/OBS]_VAR<n>_[NAME/LEVELS].")
            return None

        # get verification mask if available
        self.get_verification_mask(time_info)

        # get model to compare
        model_path = self.find_model(time_info, var_list[0])
        if model_path is None:
            return False

        # get observation to compare
        obs_path = None
        # loop over offset list and find first file that matches
        for offset in self.c_dict['OFFSETS']:
            input_dict['offset_hours'] = offset
            time_info = time_util.ti_calculate(input_dict)
            obs_path = self.find_obs(time_info, var_list[0], False)

            if obs_path is not None:
                break

        if obs_path is None:
            in_dir = self.c_dict['OBS_INPUT_DIR']
            in_template = self.c_dict['OBS_INPUT_TEMPLATE']
            self.log_error(f"Could not find observation file in {in_dir} using template {in_template} "
                              f"using offsets {self.c_dict['OFFSETS']}")
            return False

        # found both fcst and obs
        self.infiles.append(model_path)
        if type(obs_path) is list:
            for obs in obs_path:
                self.infiles.append(obs)
        else:
            self.infiles.append(obs_path)

        # get field information
        fcst_field_list = []
        obs_field_list = []
        for var_info in var_list:
            next_fcst = self.get_field_info(v_level=var_info['fcst_level'],
                                            v_thresh=var_info['fcst_thresh'],
                                            v_name=var_info['fcst_name'],
                                            v_extra=var_info['fcst_extra'],
                                            d_type='FCST')

            next_obs = self.get_field_info(v_level=var_info['obs_level'],
                                           v_thresh=var_info['obs_thresh'],
                                           v_name=var_info['obs_name'],
                                           v_extra=var_info['obs_extra'],
                                           d_type='OBS')

            if next_fcst is None or next_obs is None:
                return False

            fcst_field_list.extend(next_fcst)
            obs_field_list.extend(next_obs)

        fcst_field = ','.join(fcst_field_list)
        obs_field = ','.join(obs_field_list)

        self.process_fields(time_info, fcst_field, obs_field)

    def set_environment_variables(self, fcst_field=None, obs_field=None, time_info=None):
        """! Set all the environment variables in the MET config
             file to the corresponding values in the METplus config file.

             Args:

             Returns: None - invokes parent class, CommandBuilder add_env_var
                             to add each environment variable to run the

        """
        # MET accepts a list of values for POINT_STAT_POLY, POINT_STAT_GRID,
        # POINT_STAT_STATION_ID, and POINT_STAT_MESSAGE_TYPE. If these
        # values are not set in the METplus config file, assign them to "[]" so
        # MET recognizes that these are empty lists, resulting in the
        # expected behavior.
        self.add_env_var('POINT_STAT_POLY',
                         f"[{self.format_list_string(self.c_dict['POINT_STAT_POLY'])}]")

        self.add_env_var('POINT_STAT_GRID',
                         f"[{self.format_list_string(self.c_dict['POINT_STAT_GRID'])}]")

        self.add_env_var('POINT_STAT_STATION_ID',
                         f"[{self.format_list_string(self.c_dict['POINT_STAT_STATION_ID'])}]")

        self.add_env_var('POINT_STAT_MESSAGE_TYPE',
                         f"[{self.format_list_string(self.c_dict['POINT_STAT_MESSAGE_TYPE'])}]")

        self.add_env_var('FCST_FIELD', fcst_field)
        self.add_env_var('OBS_FIELD', obs_field)

        # Set the environment variables corresponding to the obs_window
        # dictionary.
        self.add_env_var('OBS_WINDOW_BEGIN',
                         str(self.c_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var('OBS_WINDOW_END', str(self.c_dict['OBS_WINDOW_END']))

        # add additional env vars if they are specified
        self.add_env_var('VERIF_MASK',
                         self.c_dict['VERIFICATION_MASK'])

        self.add_env_var('OUTPUT_PREFIX', self.get_output_prefix(time_info))

        # climo file is set to None if not found, so need to check
        if self.c_dict['CLIMO_FILE']:
            self.add_env_var("CLIMO_FILE", self.c_dict['CLIMO_FILE'])
        else:
            self.add_env_var("CLIMO_FILE", '')

        self.add_common_envs(time_info)

        self.print_all_envs()

if __name__ == "__main__":
    util.run_stand_alone(__file__, "PointStat")
