"""
Program Name: compare_gridded_wrapper.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import do_string_sub, ti_calculate
from ..util import parse_var_list
from ..util import get_lead_sequence, skip_time, sub_var_list
from ..util import field_read_prob_info, add_field_info_to_time_info
from . import LoopTimesWrapper

'''!@namespace CompareGriddedWrapper
@brief Common functionality to wrap similar MET applications
that compare gridded data
Call as follows:
@code{.sh}
Cannot be called directly. Must use child classes.
@endcode
'''


class CompareGriddedWrapper(LoopTimesWrapper):
    """!Common functionality to wrap similar MET applications
that reformat gridded data
    """

    def __init__(self, config, instance=None):
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        """!Create dictionary from config items to be used in the wrapper
            Allows developer to reference config items without having to know
            the type and consolidates config get calls so it is easier to see
            which config variables are used in the wrapper"""
        c_dict = super().create_c_dict()

        self.add_met_config(name='model',
                            data_type='string',
                            metplus_configs=['MODEL'])

        self.add_met_config(name='obtype',
                            data_type='string',
                            metplus_configs=['OBTYPE'])

        # read probabilistic variables for FCST and OBS fields
        field_read_prob_info(config=self.config,
                             c_dict=c_dict,
                             data_types=('FCST', 'OBS'),
                             app_name=self.app_name)

        c_dict['FCST_PROB_THRESH'] = None
        c_dict['OBS_PROB_THRESH'] = None

        c_dict['ALLOW_MULTIPLE_FILES'] = False
        c_dict['NEIGHBORHOOD_WIDTH'] = ''
        c_dict['NEIGHBORHOOD_SHAPE'] = ''

        self.handle_regrid(c_dict)

        self.handle_description()

        # handle window variables [FCST/OBS]_[FILE_]_WINDOW_[BEGIN/END]
        self.handle_file_window_variables(c_dict)

        self.add_met_config(name='output_prefix', data_type='string')

        c_dict['VAR_LIST_TEMP'] = parse_var_list(self.config,
                                                 met_tool=self.app_name)

        return c_dict

    def run_at_time_once(self, time_info):
        """! Build MET command for a given init/valid time and
         forecast lead combination.

            @param time_info dictionary containing timing information
        """
        var_list = sub_var_list(self.c_dict['VAR_LIST_TEMP'], time_info)

        if not var_list and not self.c_dict.get('VAR_LIST_OPTIONAL', False):
            self.log_error('No input fields were specified. You must set '
                           f'[FCST/OBS]_VAR<n>_[NAME/LEVELS].')
            return None

        if self.c_dict.get('ONCE_PER_FIELD', False):
            # loop over all fields and levels (and probability thresholds) and
            # call the app once for each
            for var_info in var_list:
                self.clear()
                self.c_dict['CURRENT_VAR_INFO'] = var_info
                add_field_info_to_time_info(time_info, var_info)
                self.run_at_time_one_field(time_info, var_info)
        else:
            # loop over all variables and all them to the field list,
            # then call the app once
            if var_list:
                self.c_dict['CURRENT_VAR_INFO'] = var_list[0]
                add_field_info_to_time_info(time_info, var_list[0])

            self.clear()
            self.run_at_time_all_fields(time_info)

    def run_at_time_one_field(self, time_info, var_info):
        """! Build MET command for a single field for a given
             init/valid time and forecast lead combination
              Args:
                @param time_info dictionary containing timing information
                @param var_info object containing variable information
        """

        # get model to compare, return None if not found
        model_path = self.find_model(time_info,
                                     mandatory=True,
                                     return_list=True)
        if model_path is None:
            return

        self.infiles.extend(model_path)
        # get observation to compare, return None if not found
        obs_path, time_info = self.find_obs_offset(time_info,
                                                   mandatory=True,
                                                   return_list=True)
        if obs_path is None:
            return

        self.infiles.extend(obs_path)

        # get field info field a single field to pass to the MET config file
        fcst_field_list = self.format_field_info(var_info=var_info,
                                                 data_type='FCST')

        obs_field_list = self.format_field_info(var_info=var_info,
                                                data_type='OBS')

        if fcst_field_list is None or obs_field_list is None:
            return

        fcst_fields = ','.join(fcst_field_list)
        obs_fields = ','.join(obs_field_list)

        self.format_field('FCST', fcst_fields)
        self.format_field('OBS', obs_fields)

        self.process_fields(time_info)

    def run_at_time_all_fields(self, time_info):
        """! Build MET command for all of the field/level combinations for a
             given init/valid time and forecast lead combination

             @param time_info dictionary containing timing information
        """
        var_list = sub_var_list(self.c_dict['VAR_LIST_TEMP'], time_info)

        # get model from first var to compare
        model_path = self.find_model(time_info,
                                     mandatory=True,
                                     return_list=True)
        if not model_path:
            return

        # if there is more than 1 file, create file list file
        if len(model_path) > 1:
            list_filename = (f"{time_info['init_fmt']}_"
                             f"{time_info['lead_hours']}_"
                             f"{self.app_name}_fcst.txt")
            model_path = self.write_list_file(list_filename, model_path)
        else:
            model_path = model_path[0]

        self.infiles.append(model_path)

        # get observation to from first var compare
        obs_path, time_info = self.find_obs_offset(time_info,
                                                   mandatory=True,
                                                   return_list=True)
        if obs_path is None:
            return

        # if there is more than 1 file, create file list file
        if len(obs_path) > 1:
            list_filename = (f"{time_info['init_fmt']}_"
                             f"{time_info['lead_hours']}_"
                             f"{self.app_name}_obs.txt")
            obs_path = self.write_list_file(list_filename, obs_path)
        else:
            obs_path = obs_path[0]

        self.infiles.append(obs_path)

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
                return

            fcst_field_list.extend(next_fcst)
            obs_field_list.extend(next_obs)

        fcst_field = ','.join(fcst_field_list)
        obs_field = ','.join(obs_field_list)

        self.format_field('FCST', fcst_field)
        self.format_field('OBS', obs_field)

        self.process_fields(time_info)

    def process_fields(self, time_info):
        """! Set and print environment variables, then build/run MET command

             @param time_info dictionary with time information
        """
        # set config file since command is reset after each run
        self.param = do_string_sub(self.c_dict['CONFIG_FILE'],
                                   **time_info)

        self.set_current_field_config()

        # set up output dir with time info
        if not self.find_and_check_output_file(time_info,
                                               is_directory=True):
            return

        # set command line arguments
        self.set_command_line_arguments(time_info)

        # set environment variables needed by MET config file
        self.set_environment_variables(time_info)

        # run the MET command
        self.build()

    def set_command_line_arguments(self, time_info):
        """!Set command line arguments in self.args to add to command to run.
        Nothing is done for CompareGridded wrapper. This function can be
        overwritten in subclasses.

        @param time_info dictionary with time information
        """
        return None

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.log_error('No app path specified. '
                              'You must use a subclass')
            return None

        cmd = '{} -v {} '.format(self.app_path, self.c_dict['VERBOSITY'])
        for arg in self.args:
            cmd += arg + " "

        if len(self.infiles) == 0:
            self.log_error("No input filenames specified")
            return None

        # add forecast file
        fcst_file = self.infiles[0]
        if fcst_file.startswith('PYTHON'):
            fcst_file = f"'{fcst_file}'"
        cmd += f'{fcst_file} '

        # add observation file
        obs_file = self.infiles[1]
        if obs_file.startswith('PYTHON'):
            obs_file = f"'{obs_file}'"
        cmd += f'{obs_file} '

        if self.param == '':
            self.log_error('Must specify config file to run MET tool')
            return None

        cmd += self.param + ' '

        if self.outdir == "":
            self.log_error("No output directory specified")
            return None

        cmd += '-outdir {}'.format(self.outdir)
        return cmd

    def handle_interp_dict(self, uses_field=False):
        """! Reads config variables for interp dictionary, i.e.
             _INTERP_VLD_THRESH, _INTERP_SHAPE, _INTERP_METHOD, and
             _INTERP_WIDTH. Also _INTERP_FIELD if specified

            @param uses_field if True, read field variable as well
             (default is False)
        """
        items = {
            'vld_thresh': 'float',
            'shape': ('string', 'remove_quotes'),
            'type': ('dict', None, {
                'method': ('list', 'remove_quotes'),
                'width': ('list', 'remove_quotes'),
            }),
        }
        if uses_field:
            items['field'] = ('string', 'remove_quotes')

        self.add_met_config_dict('interp', items)
