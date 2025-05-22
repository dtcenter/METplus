"""
Program Name: rmw_analysis_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs RMWAnalysis
"""

import os

from ..util import parse_var_list
from . import RuntimeFreqWrapper


class RMWAnalysisWrapper(RuntimeFreqWrapper):
    """!Performs RMW analysis with filtering options"""
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE'
    RUNTIME_FREQ_SUPPORTED = [
        'RUN_ONCE',
        'RUN_ONCE_PER_INIT_OR_VALID',
        'RUN_ONCE_PER_LEAD',
    ]

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_DATA_FIELD',
        'METPLUS_MODEL',
        'METPLUS_BASIN',
        'METPLUS_STORM_NAME',
        'METPLUS_STORM_ID',
        'METPLUS_CYCLONE',
        'METPLUS_INIT_BEG',
        'METPLUS_INIT_END',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_INIT_MASK',
        'METPLUS_VALID_MASK',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'rmw_analysis'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        """! Populate the c_dict dictionary with values from METplusConfig """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config', 'LOG_RMW_ANALYSIS_VERBOSITY', c_dict['VERBOSITY'])
        )

        # if no forecast lead sequence is specified, use wildcard (*) so all leads are used
        c_dict['WILDCARD_LEAD_IF_EMPTY'] = True

        # allow multiple files so wildcards can be used to get input files
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        # set up the input data template
        self.get_input_templates(c_dict, {
            'DATA': {'prefix': 'RMW_ANALYSIS', 'required': True},
        })

        # set up the output template
        c_dict['OUTPUT_DIR'] = self.config.getdir('RMW_ANALYSIS_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('config', 'RMW_ANALYSIS_OUTPUT_TEMPLATE')
        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set RMW_ANALYSIS_OUTPUT_DIR to run.")

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('RMWAnalysisConfig_wrapped')

        c_dict['VAR_LIST_TEMP'] = parse_var_list(self.config, data_type='FCST',
                                                 met_tool=self.app_name)
        if not c_dict['VAR_LIST_TEMP']:
            self.log_error("No fields specified. Please set BOTH_VAR<n>_[NAME/LEVELS]")

        self.add_met_config(name='model', data_type='list',
                            metplus_configs=['RMW_ANALYSIS_MODEL', 'MODEL'])
        self.add_met_config(name='basin', data_type='list')
        self.add_met_config(name='storm_name', data_type='list')
        self.add_met_config(name='storm_id', data_type='list')
        self.add_met_config(name='cyclone', data_type='list')
        self.add_met_config(name='init_beg', data_type='string',
                            metplus_configs=['RMW_ANALYSIS_INIT_BEG',
                                             'RMW_ANALYSIS_INIT_BEGIN'])
        self.add_met_config(name='init_end', data_type='string')
        self.add_met_config(name='valid_beg', data_type='string',
                            metplus_configs=['RMW_ANALYSIS_VALID_BEG',
                                             'RMW_ANALYSIS_VALID_BEGIN'])
        self.add_met_config(name='valid_end', data_type='string')
        self.add_met_config(name='init_mask', data_type='string')
        self.add_met_config(name='valid_mask', data_type='string')

        return c_dict


    def find_input_files(self, time_info):
        """! Loop over list of input templates and find files for each

             @param time_info time dictionary to use for string substitution
             @returns Input file list if all files were found, None if not.
        """
        for file_dict in self.c_dict['ALL_FILES']:
            if file_dict is None: continue
            self.add_to_infiles(file_dict, time_info)

        return self.infiles


    def set_command_line_arguments(self, time_info):
        for input_file in self.infiles:
            self.args.append(f"-data {input_file}")
        self.args.append(f"-config {self.c_dict['CONFIG_FILE']}")


    def set_environment_variables(self, time_info=None):
        all_fields = []
        for file_dict in self.c_dict['ALL_FILES']:
            if file_dict is None: continue
            for var_info in file_dict['var_list']:
                fields = self.format_field_info(var_info, 'FCST')
                if not fields: continue
                all_fields.extend(fields)

        self.env_var_dict['METPLUS_DATA_FIELD'] = f"field = [{','.join(all_fields)}];"
        super().set_environment_variables(time_info)

    def get_command(self):
        return (f"{self.app_path} {' '.join(self.args)}"
                f" -out {self.get_output_path()} -v {self.c_dict['VERBOSITY']}")
