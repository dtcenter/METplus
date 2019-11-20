#!/usr/bin/env python

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

        regrid = self.config.getstr('config', 'POINT_STAT_REGRID_TO_GRID')
        # if not surrounded by quotes and not NONE, add quotes
        if regrid[0] != '"' and regrid != 'NONE':
            regrid = '"' + regrid + '"'

        c_dict['REGRID_TO_GRID'] = regrid
        c_dict['POINT_STAT_GRID'] = self.config.getstr('config', 'POINT_STAT_GRID')

        c_dict['POINT_STAT_POLY'] = util.getlist(
            self.config.getstr('config', 'POINT_STAT_POLY', ''))
        c_dict['POINT_STAT_STATION_ID'] = util.getlist(
            self.config.getstr('config', 'POINT_STAT_STATION_ID', ''))
        c_dict['POINT_STAT_MESSAGE_TYPE'] = util.getlist(
            self.config.getstr('config', 'POINT_STAT_MESSAGE_TYPE', ''))

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

        return c_dict

    def run_at_time(self, input_dict):
        """! Stub, not yet implemented """

        # loop of forecast leads and process each
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            lead_string = time_util.ti_calculate(input_dict)['lead_string']
            self.logger.info("Processing forecast lead {}".format(lead_string))

            # set current lead time config and environment variables
            self.config.set('config', 'CURRENT_LEAD_TIME', lead)
            os.environ['METPLUS_CURRENT_LEAD_TIME'] = str(lead)

            # Run for given init/valid time and forecast lead combination
            self.run_at_time_once(input_dict)

    def run_at_time_once(self, input_dict):
        if self.c_dict['FCST_INPUT_TEMPLATE'] == '':
            self.logger.error('Must set FCST_POINT_STAT_INPUT_TEMPLATE in config file')
            exit(1)

        if self.c_dict['OBS_INPUT_TEMPLATE'] == '':
            self.logger.error('Must set OBS_POINT_STAT_INPUT_TEMPLATE in config file')
            exit(1)

        if self.c_dict['OUTPUT_DIR'] == '':
            self.logger.error('Must set POINT_STAT_OUTPUT_DIR in config file')
            exit(1)

        # clear any settings leftover from previous run
        self.clear()

        time_info = time_util.ti_calculate(input_dict)
        var_list = util.parse_var_list(self.config, time_info)

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
            self.logger.error(f"Could not find observation file in {in_dir} using template {in_template} "
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
        # pylint:disable=protected-access
        # list of fields to print to log
        print_list = ["MODEL", "REGRID_TO_GRID",
                      "FCST_FIELD", "OBS_FIELD",
                      "OBS_WINDOW_BEGIN", "OBS_WINDOW_END",
                      "POINT_STAT_MESSAGE_TYPE", "POINT_STAT_GRID",
                      "POINT_STAT_POLY", "POINT_STAT_STATION_ID"]

        # Set the environment variables
        self.add_env_var('MODEL', str(self.c_dict['MODEL']))

        regrid_to_grid = self.c_dict['REGRID_TO_GRID']
        self.add_env_var('REGRID_TO_GRID', regrid_to_grid)

        # MET accepts a list of values for POINT_STAT_POLY, POINT_STAT_GRID,
        # POINT_STAT_STATION_ID, and POINT_STAT_MESSAGE_TYPE. If these
        # values are not set in the METplus config file, assign them to "[]" so
        # MET recognizes that these are empty lists, resulting in the
        # expected behavior.
        poly_str = str(self.c_dict['POINT_STAT_POLY'])
        if not poly_str:
            self.add_env_var('POINT_STAT_POLY', "[]")
        else:
            poly = poly_str.replace("\'", "\"")
            self.add_env_var('POINT_STAT_POLY', poly)

        grid_str = str(self.c_dict['POINT_STAT_GRID'])
        if not grid_str:
            self.add_env_var('POINT_STAT_GRID', "[]")
        else:
            # grid = grid_str.replace("\'", "\"")
            grid = '"' + grid_str + '"'
            self.add_env_var('POINT_STAT_GRID', grid)

        sid_str = str(self.c_dict['POINT_STAT_STATION_ID'])
        if not sid_str:
            self.add_env_var('POINT_STAT_STATION_ID', "[]")
        else:
            sid = sid_str.replace("\'", "\"")
            self.add_env_var('POINT_STAT_STATION_ID', sid)

        tmp_message_type = str(self.c_dict['POINT_STAT_MESSAGE_TYPE'])
        # Check for "empty" POINT_STAT_MESSAGE_TYPE in METplus config file and
        # set the POINT_STAT_MESSAGE_TYPE environment variable appropriately.
        if not tmp_message_type:
            self.add_env_var('POINT_STAT_MESSAGE_TYPE', "[]")
        else:
            # Not empty, set the POINT_STAT_MESSAGE_TYPE environment
            #  variable to the
            # message types specified in the METplus config file.
            tmp_message_type = str(tmp_message_type).replace("\'", "\"")
            # Remove all whitespace
            tmp_message_type = ''.join(tmp_message_type.split())
            self.add_env_var('POINT_STAT_MESSAGE_TYPE', tmp_message_type)

        self.add_env_var('FCST_FIELD', fcst_field)
        self.add_env_var('OBS_FIELD', obs_field)

        # Set the environment variables corresponding to the obs_window
        # dictionary.
        self.add_env_var('OBS_WINDOW_BEGIN',
                         str(self.c_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var('OBS_WINDOW_END', str(self.c_dict['OBS_WINDOW_END']))

        # add additional env vars if they are specified
        if self.c_dict['VERIFICATION_MASK'] != '':
            self.add_env_var('VERIF_MASK',
                             self.c_dict['VERIFICATION_MASK'])
            print_list.append('VERIF_MASK')

        # set user environment variables
        self.set_user_environment(time_info)

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for l in print_list:
            self.print_env_item(l)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)


if __name__ == "__main__":
    util.run_stand_alone("point_stat_wrapper", "PointStat")
