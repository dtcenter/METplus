"""tc_diag
Program Name: tc_diag_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs tc_diag
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import time_util
from . import RuntimeFreqWrapper
from ..util import do_string_sub, get_lead_sequence
from ..util import parse_var_list, sub_var_list, getlist
from ..util import find_indices_in_config_section
from ..util.met_config import add_met_config_dict_list

'''!@namespace TCDiagWrapper
@brief Wraps the TC-Diag tool
@endcode
'''


class TCDiagWrapper(RuntimeFreqWrapper):
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_PER_INIT_OR_VALID'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_PER_INIT_OR_VALID']

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_STORM_ID',
        'METPLUS_BASIN',
        'METPLUS_CYCLONE',
        'METPLUS_INIT_INCLUDE',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_VALID_INCLUDE_LIST',
        'METPLUS_VALID_EXCLUDE_LIST',
        'METPLUS_VALID_HOUR_LIST',
        'METPLUS_LEAD_LIST',
        'METPLUS_DIAG_SCRIPT',
        'METPLUS_DOMAIN_INFO_LIST',
        'METPLUS_DATA_FILE_TYPE',
        'METPLUS_DATA_DOMAIN',
        'METPLUS_DATA_LEVEL',
        'METPLUS_DATA_FIELD',
        'METPLUS_REGRID_DICT',
        'METPLUS_COMPUTE_TANGENTIAL_AND_RADIAL_WINDS',
        'METPLUS_U_WIND_FIELD_NAME',
        'METPLUS_V_WIND_FIELD_NAME',
        'METPLUS_TANGENTIAL_VELOCITY_FIELD_NAME',
        'METPLUS_TANGENTIAL_VELOCITY_LONG_FIELD_NAME',
        'METPLUS_RADIAL_VELOCITY_FIELD_NAME',
        'METPLUS_RADIAL_VELOCITY_LONG_FIELD_NAME',
        'METPLUS_VORTEX_REMOVAL',
        'METPLUS_VORTEX_REMOVAL',
        'METPLUS_NC_DIAG_FLAG',
        'METPLUS_NC_CYL_GRID_FLAG',
        'METPLUS_CIRA_DIAG_FLAG',
        'METPLUS_OUTPUT_BASE_FORMAT',
        'METPLUS_ONE_TIME_PER_FILE_FLAG',
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'OUTPUT_PREFIX',
        'METPLUS_OUTPUT_PREFIX',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_CONVERT',
    ]

    def __init__(self, config, instance=None):
        self.app_name = "tc_diag"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_TC_DIAG_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        # skip RuntimeFreq wrapper logic to find files
        c_dict['FIND_FILES'] = False

        # get command line arguments domain and tech id list for -data
        self._read_data_inputs(c_dict)

        # get -deck argument dir/template
        c_dict['DECK_INPUT_DIR'] = self.config.getdir('TC_DIAG_DECK_INPUT_DIR',
                                                      '')
        c_dict['DECK_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'TC_DIAG_DECK_TEMPLATE')
        )

        # get output dir/template
        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_DIAG_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'TC_DIAG_OUTPUT_TEMPLATE')
        )

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('TCDiagConfig_wrapped')

        # get variables to set in wrapped MET config file
        self.add_met_config(name='model',
                            data_type='list',
                            metplus_configs=['TC_DIAG_MODEL', 'MODEL'])

        self.add_met_config(name='storm_id', data_type='string')

        self.add_met_config(name='basin', data_type='string')

        self.add_met_config(name='cyclone', data_type='string')

        self.add_met_config(name='init_inc',
                            data_type='string',
                            env_var_name='METPLUS_INIT_INCLUDE',
                            metplus_configs=['TC_DIAG_INIT_INC',
                                             'TC_DIAG_INIT_INCLUDE'])

        self.add_met_config(name='valid_beg',
                            data_type='string',
                            metplus_configs=['TC_DIAG_VALID_BEG',
                                             'TC_DIAG_VALID_BEGIN'])

        self.add_met_config(name='valid_end',
                            data_type='string',
                            metplus_configs=['TC_DIAG_VALID_END'])

        self.add_met_config(name='valid_inc',
                            data_type='list',
                            env_var_name='METPLUS_VALID_INCLUDE_LIST',
                            metplus_configs=['TC_DIAG_VALID_INCLUDE_LIST',
                                             'TC_DIAG_VALID_INC_LIST',
                                             'TC_DIAG_VALID_INCLUDE',
                                             'TC_DIAG_VALID_INC',
                                             ])

        self.add_met_config(name='valid_exc',
                            data_type='list',
                            env_var_name='METPLUS_VALID_EXCLUDE_LIST',
                            metplus_configs=['TC_DIAG_VALID_EXCLUDE_LIST',
                                             'TC_DIAG_VALID_EXC_LIST',
                                             'TC_DIAG_VALID_EXCLUDE',
                                             'TC_DIAG_VALID_EXC',
                                             ])

        self.add_met_config(name='valid_hour',
                            data_type='list',
                            env_var_name='METPLUS_VALID_HOUR_LIST',
                            metplus_configs=['TC_DIAG_VALID_HOUR_LIST',
                                             'TC_DIAG_VALID_HOUR',
                                             ])

        self.add_met_config(name='diag_script', data_type='list')

        dict_items = {
            'domain': 'string',
            'n_range': 'int',
            'n_azimuth': 'int',
            'delta_range_km': 'float',
            'diag_script': 'list',
        }
        if not add_met_config_dict_list(config=self.config,
                                        app_name=self.app_name,
                                        output_dict=self.env_var_dict,
                                        dict_name='domain_info',
                                        dict_items=dict_items):
            self.isOK = False

        # handle data dictionary, including field, domain, level, and file_type
        c_dict['VAR_LIST_TEMP'] = parse_var_list(self.config,
                                                 data_type='FCST',
                                                 met_tool=self.app_name)

        self.add_met_config(name='domain', data_type='list',
                            env_var_name='METPLUS_DATA_DOMAIN',
                            metplus_configs=['TC_DIAG_DATA_DOMAIN'])

        self.add_met_config(name='level', data_type='list',
                            env_var_name='METPLUS_DATA_LEVEL',
                            metplus_configs=['TC_DIAG_DATA_LEVEL'])

        self.add_met_config(name='file_type',
                            data_type='string',
                            env_var_name='METPLUS_DATA_FILE_TYPE',
                            metplus_configs=['TC_DIAG_INPUT_DATATYPE',
                                             'TC_DIAG_DATA_FILE_TYPE',
                                             'TC_DIAG_FILE_TYPE',])

        self.handle_regrid(c_dict, set_to_grid=False)

        self.add_met_config(name='compute_tangential_and_radial_winds',
                            data_type='bool')
        self.add_met_config(name='u_wind_field_name', data_type='string')
        self.add_met_config(name='v_wind_field_name', data_type='string')
        self.add_met_config(name='tangential_velocity_field_name',
                            data_type='string')
        self.add_met_config(name='tangential_velocity_long_field_name',
                            data_type='string')
        self.add_met_config(name='radial_velocity_field_name',
                            data_type='string')
        self.add_met_config(name='radial_velocity_long_field_name',
                            data_type='string')

        self.add_met_config(name='vortex_removal', data_type='bool')

        self.add_met_config(name='one_time_per_file_flag', data_type='bool')

        self.add_met_config(name='nc_cyl_grid_flag', data_type='bool')
        self.add_met_config(name='nc_diag_flag', data_type='bool')
        self.add_met_config(name='cira_diag_flag', data_type='bool')

        self.add_met_config(name='output_base_format', data_type='string')

        return c_dict

    def _read_data_inputs(self, c_dict):
        """! Parse the -data arguments from the METplusConfig object.
        Sets c_dict DATA_INPUTS key with a list of dictionaries.
        Each input should include domain, tech_id_list, and dir/template.
        Logs error if any required variables are not set.

        @param c_dict dictionary to save values into
        """
        # get template indices
        indices = list(
            find_indices_in_config_section(r'TC_DIAG_INPUT(\d+)_TEMPLATE$',
                                           self.config,
                                           index_index=1).keys()
        )

        # if no template indices were found, look for file list indices
        if not indices:
            indices = list(
                find_indices_in_config_section(r'TC_DIAG_INPUT(\d+)_FILE_LIST$',
                                               self.config,
                                               index_index=1).keys()
            )
            # error if no file list or template indices were found
            if not indices:
                self.log_error(
                    'Must set TC_DIAG_INPUT<n>_TEMPLATE/DOMAIN/TECH_ID_LIST'
                )
                return

        c_dict['DATA_INPUTS'] = []
        for index in indices:
            prefix = f'TC_DIAG_INPUT{index}_'
            directory = self.config.getdir(f'{prefix}DIR')
            template = self.config.getraw('config', f'{prefix}TEMPLATE')

            # get file list if template is not set
            if template:
                file_list = None
            else:
                file_list = self.config.getraw('config', f'{prefix}FILE_LIST')

            domain = self.config.getraw('config', f'{prefix}DOMAIN')
            if not domain:
                self.log_error(f'Must set {prefix}DOMAIN')

            tech_id_list = getlist(
                self.config.getraw('config', f'{prefix}TECH_ID_LIST')
            )
            if not tech_id_list:
                self.log_error(f'Must set {prefix}TECH_ID_LIST')

            data_dict = {
                'template': template,
                'directory': directory,
                'file_list': file_list,
                'domain': domain,
                'tech_id_list': tech_id_list,
            }
            c_dict['DATA_INPUTS'].append(data_dict)

    def get_command(self):
        cmd = self.app_path

        # add deck
        cmd += ' -deck ' + self.c_dict['DECK_FILE']

        # add arguments
        cmd += ' ' + ' '.join(self.args)

        # add output path
        out_path = self.get_output_path()
        cmd += ' -outdir ' + out_path

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
        return cmd

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run ascii2nc
             Args:
                @param time_info dictionary containing timing information
        """
        self.clear()
        time_info = time_util.ti_calculate(time_info)

        # get input files
        if not self.find_input_files(time_info):
            return

        # get output path
        if not self.find_and_check_output_file(time_info, is_directory=True):
            return

        # get field information to set in MET config
        if not self.set_data_field(time_info):
            return

        # set forecast lead list for MET config
        self.set_lead_list(time_info)

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # set environment variables if using config file
        self.set_environment_variables(time_info)

        self.build()

    def set_data_field(self, time_info):
        """!Get list of fields from config to process. Build list of field info
            that are formatted to be read by the MET config file. Set DATA_FIELD
            item of c_dict with the formatted list of fields.
            Args:
                @param time_info time dictionary to use for string substitution
                @returns True if field list could be built, False if not.
        """
        field_list = sub_var_list(self.c_dict['VAR_LIST_TEMP'], time_info)
        if not field_list:
            self.log_error("Could not get field information from config.")
            return False

        all_fields = []
        for field in field_list:
            field_list = self.get_field_info(d_type='FCST',
                                             v_name=field['fcst_name'],
                                             v_level=field['fcst_level'],
                                             )
            if field_list is None:
                return False

            all_fields.extend(field_list)

        data_field = ','.join(all_fields)
        self.env_var_dict['METPLUS_DATA_FIELD'] = f'field = [{data_field}];'

        return True

    def find_input_files(self, time_info):
        """!Get DECK file and list of input data files and set c_dict items.
            Args:
                @param time_info time dictionary to use for string substitution
                @returns Input file list if all files were found, None if not.
        """
        # get deck file
        deck_file = self.find_data(time_info, data_type='DECK')
        if not deck_file:
            return False
        self.c_dict['DECK_FILE'] = deck_file

        # get files and values for -data arguments
        lead_seq = get_lead_sequence(self.config, time_info)
        for data_dict in self.c_dict['DATA_INPUTS']:
            if not self._find_data_inputs(data_dict, lead_seq, time_info,
                                          deck_file):
                return False
        return True

    def _find_data_inputs(self, data_dict, lead_seq, time_info, deck_file):
        # check if file list file is set and use that instead of template/dir
        input_file_list = data_dict['file_list']
        if input_file_list:
            self.logger.debug(f"Explicit file list file: {input_file_list}")
            list_file = do_string_sub(input_file_list, **time_info)
            if not os.path.exists(list_file):
                self.log_error(f'Could not find file list: {list_file}')
                return False
        else:
            # set c_dict variables that are used in find_data function
            self.c_dict['INPUT_DIR'] = data_dict['directory']
            self.c_dict['INPUT_TEMPLATE'] = data_dict['template']

            all_input_files = []
            for lead in lead_seq:
                time_info_lead = time_info.copy()
                time_info_lead['lead'] = lead
                time_info_lead = time_util.ti_calculate(time_info_lead)

                # get a list of the input data files,
                # write to an ascii file if there are more than one
                input_files = self.find_data(time_info_lead, return_list=True)
                if not input_files:
                    continue

                all_input_files.extend(input_files)

            if not all_input_files:
                return False

            # create an ascii file with a list of the input files
            list_file = f"{os.path.basename(deck_file)}_data_files.txt"
            list_file = self.write_list_file(list_file, all_input_files)

        # build argument with file list file, domain, and tech id list
        domain = data_dict['domain']
        tech_ids = ','.join(data_dict['tech_id_list'])
        self.args.append(f'-data {domain} {tech_ids} {list_file}')
        return True

    def set_lead_list(self, time_info):
        self.env_var_dict['METPLUS_LEAD_LIST'] = ''

        lead_seq = get_lead_sequence(self.config, time_info)
        # set LEAD_LIST to list of forecast leads used
        if lead_seq == [0]:
            return

        lead_list = []
        for lead in lead_seq:
            lead_hours = (
                time_util.ti_get_hours_from_relativedelta(lead,
                                                          valid_time=time_info['valid'])
                )
            lead_list.append(f'"{str(lead_hours).zfill(2)}"')

        self.env_var_dict['METPLUS_LEAD_LIST'] = f"lead = [{', '.join(lead_list)}];"

    def set_command_line_arguments(self, time_info):
        # add config file - passing through do_string_sub to get custom string if set
        if self.c_dict['CONFIG_FILE']:
            config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                        **time_info)
            self.args.append(f"-config {config_file}")
