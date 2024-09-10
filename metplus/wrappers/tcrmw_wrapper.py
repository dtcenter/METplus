"""tc_rmw
Program Name: tc_rmw_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs tc_rmw
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import ti_calculate, ti_get_hours_from_relativedelta
from ..util import do_string_sub, skip_time, get_lead_sequence
from ..util import parse_var_list, sub_var_list
from . import RuntimeFreqWrapper

'''!@namespace TCRMWWrapper
@brief Wraps the TC-RMW tool
@endcode
'''


class TCRMWWrapper(RuntimeFreqWrapper):
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
        'METPLUS_DATA_FILE_TYPE',
        'METPLUS_DATA_FIELD',
        'METPLUS_REGRID_DICT',
        'METPLUS_N_RANGE',
        'METPLUS_N_AZIMUTH',
        'METPLUS_DELTA_RANGE_KM',
        'METPLUS_RMW_SCALE',
    ]

    def __init__(self, config, instance=None):
        self.app_name = "tc_rmw"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_TC_RMW_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('TCRMWConfig_wrapped')

        c_dict['INPUT_DIR'] = self.config.getdir('TC_RMW_INPUT_DIR', '')
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('config',
                                                      'TC_RMW_INPUT_TEMPLATE')
        c_dict['INPUT_FILE_LIST'] = self.config.getraw(
            'config', 'TC_RMW_INPUT_FILE_LIST'
        )

        c_dict['OUTPUT_DIR'] = self.config.getdir('TC_RMW_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'TC_RMW_OUTPUT_TEMPLATE')
        )

        c_dict['DECK_INPUT_DIR'] = self.config.getdir('TC_RMW_DECK_INPUT_DIR',
                                                      '')
        c_dict['DECK_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'TC_RMW_DECK_TEMPLATE')
        )

        self.add_met_config(name='file_type', data_type='string',
                            env_var_name='METPLUS_DATA_FILE_TYPE',
                            metplus_configs=['TC_RMW_INPUT_DATATYPE',
                                             'TC_RMW_FILE_TYPE'])

        self.add_met_config(name='model', data_type='string',
                            metplus_configs=['MODEL'])

        self.handle_regrid(c_dict, set_to_grid=False)

        self.add_met_config(name='n_range', data_type='int')
        self.add_met_config(name='n_azimuth', data_type='int')
        self.add_met_config(name='delta_range_km', data_type='float')
        self.add_met_config(name='rmw_scale', data_type='float')
        self.add_met_config(name='storm_id', data_type='string')
        self.add_met_config(name='basin', data_type='string')
        self.add_met_config(name='cyclone', data_type='string')

        self.add_met_config(name='init_inc', data_type='string',
                            env_var_name='METPLUS_INIT_INCLUDE',
                            metplus_configs=['TC_RMW_INIT_INC',
                                             'TC_RMW_INIT_INCLUDE'])

        self.add_met_config(name='valid_beg', data_type='string',
                            metplus_configs=['TC_RMW_VALID_BEG',
                                             'TC_RMW_VALID_BEGIN'])

        self.add_met_config(name='valid_end', data_type='string',
                            metplus_configs=['TC_RMW_VALID_END'])

        self.add_met_config(name='valid_inc', data_type='list',
                            env_var_name='METPLUS_VALID_INCLUDE_LIST',
                            metplus_configs=['TC_RMW_VALID_INCLUDE_LIST',
                                             'TC_RMW_VALID_INC_LIST',
                                             'TC_RMW_VALID_INCLUDE',
                                             'TC_RMW_VALID_INC',
                                             ])

        self.add_met_config(name='valid_exc', data_type='list',
                            env_var_name='METPLUS_VALID_EXCLUDE_LIST',
                            metplus_configs=['TC_RMW_VALID_EXCLUDE_LIST',
                                             'TC_RMW_VALID_EXC_LIST',
                                             'TC_RMW_VALID_EXCLUDE',
                                             'TC_RMW_VALID_EXC',
                                             ])

        self.add_met_config(name='valid_hour', data_type='list',
                            env_var_name='METPLUS_VALID_HOUR_LIST',
                            metplus_configs=['TC_RMW_VALID_HOUR_LIST',
                                             'TC_RMW_VALID_HOUR',
                                             ])

        c_dict['VAR_LIST_TEMP'] = parse_var_list(self.config,
                                                 data_type='FCST',
                                                 met_tool=self.app_name)
        if not c_dict['VAR_LIST_TEMP']:
            self.log_error("Could not get field information from config.")
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        return c_dict

    def get_command(self):
        cmd = self.app_path

        # don't run if no input or output files were found
        if not self.infiles:
            self.log_error("No input files were found")
            return

        if not self.outfile:
            self.log_error("No output file specified")
            return

        # add deck
        cmd += ' -adeck ' + self.c_dict['DECK_FILE']

        # add input files
        cmd += ' -data'
        for infile in self.infiles:
            cmd += ' ' + infile

        # add arguments
        cmd += ' ' + ' '.join(self.args)

        # add output path
        out_path = self.get_output_path()
        cmd += ' -out ' + out_path

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
        return cmd

    def find_input_files(self, time_info):
        """!Get DECK file and list of input data files and set c_dict items.
            Args:
                @param time_info time dictionary to use for string substitution
                @returns Input file list if all files were found, None if not.
        """
        # get deck file
        deck_file = self.find_data(time_info, data_type='DECK')
        if not deck_file:
            return None

        self.c_dict['DECK_FILE'] = deck_file

        lead_seq = get_lead_sequence(self.config, time_info)

        # get input files
        if self.c_dict['INPUT_FILE_LIST']:
            self.logger.debug("Explicit file list file: "
                              f"{self.c_dict['INPUT_FILE_LIST']}")
            list_file = do_string_sub(self.c_dict['INPUT_FILE_LIST'],
                                      **time_info)
            if not os.path.exists(list_file):
                msg = f'Could not find file list: {list_file}'
                if self.c_dict['ALLOW_MISSING_INPUTS']:
                    self.logger.warning(msg)
                else:
                    self.log_error(msg)
                return None
        else:
            all_input_files = []

            for lead in lead_seq:
                self.clear()
                time_info['lead'] = lead

                time_info = ti_calculate(time_info)

                # get a list of the input data files,
                # write to an ascii file if there are more than one
                input_files = self.find_data(time_info, return_list=True)
                if not input_files:
                    continue

                all_input_files.extend(input_files)

            if not all_input_files:
                return None

            # create an ascii file with a list of the input files
            list_file = f"{os.path.basename(deck_file)}_data_files.txt"
            list_file = self.write_list_file(list_file, all_input_files)

        self.infiles.append(list_file)

        if not self._set_data_field(time_info):
            return None

        self._set_lead_list(time_info, lead_seq)

        return time_info

    def _set_data_field(self, time_info):
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
                self.log_error(f'Could not get field info from {field}')
                return False

            all_fields.extend(field_list)

        data_field = ','.join(all_fields)
        self.env_var_dict['METPLUS_DATA_FIELD'] = f'field = [{data_field}];'
        return True

    def _set_lead_list(self, time_info, lead_seq):
        # set LEAD_LIST to list of forecast leads used
        if lead_seq == [0]:
            return

        lead_list = []
        for lead in lead_seq:
            lead_hours = (
                ti_get_hours_from_relativedelta(lead,
                                                valid_time=time_info['valid'])
            )
            lead_list.append(f'"{str(lead_hours).zfill(2)}"')

        self.env_var_dict['METPLUS_LEAD_LIST'] = f"lead = [{', '.join(lead_list)}];"

    def set_command_line_arguments(self, time_info):
        if self.c_dict['CONFIG_FILE']:
            config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                        **time_info)
            self.args.append(f"-config {config_file}")
