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
        'METPLUS_STORM_ID',
        'METPLUS_BASIN',
        'METPLUS_CYCLONE',
        'METPLUS_STORM_NAME',
        'METPLUS_INIT_BEG',
        'METPLUS_INIT_END',
        'METPLUS_INIT_INC',
        'METPLUS_INIT_EXC',
        'METPLUS_VALID_BEG',
        'METPLUS_VALID_END',
        'METPLUS_VALID_INC',
        'METPLUS_VALID_EXC',
        'METPLUS_INIT_HOUR',
        'METPLUS_VALID_HOUR',
        'METPLUS_LEAD',
        'METPLUS_INIT_MASK',
        'METPLUS_VALID_MASK',
        'METPLUS_CATEGORY',
        'METPLUS_COLUMN_THRESH_NAME',
        'METPLUS_COLUMN_THRESH_VAL',
        'METPLUS_INIT_THRESH_NAME',
        'METPLUS_INIT_THRESH_VAL',
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

        # handle all of the MET configs that are strings or lists
        for config_name, config_type in [
            ('model', 'list'),
            ('storm_id', 'list'),
            ('basin', 'list'),
            ('cyclone', 'list'),
            ('storm_name', 'list'),
            ('init_beg', 'string'),
            ('init_end', 'string'),
            ('init_inc', 'list'),
            ('init_exc', 'list'),
            ('valid_beg', 'string'),
            ('valid_end', 'string'),
            ('valid_inc', 'list'),
            ('valid_exc', 'list'),
            ('init_hour', 'list'),
            ('valid_hour', 'list'),
            ('lead', 'list'),
            ('init_mask', 'string'),
            ('valid_mask', 'string'),
            ('category', 'list'),
            ('column_thresh_name', 'list'),
            ('column_thresh_val', 'list'),
            ('init_thresh_name', 'list'),
            ('init_thresh_val', 'list'),
        ]:
            metplus_configs = [f'RMW_ANALYSIS_{config_name.upper()}']

            # add MODEL METplus config as an option for setting model
            if config_name == 'model':
                metplus_configs.append('MODEL')

            # add synonyms for include/exclude lists, e.g. INCLUDE for INC
            if config_name.endswith('_inc') or config_name.endswith('_exc'):
                metplus_configs.append(f'RMW_ANALYSIS_{config_name.upper()}LUDE')

            # add synonyms for begin, e.g. BEGIN for BEG
            if config_name.endswith('_beg'):
                metplus_configs.append(f'RMW_ANALYSIS_{config_name.upper()}IN')

            extra_args = {}
            # remove quotation marks from *_thresh_val lists
            if 'thresh_val' in config_name:
                extra_args['remove_quotes'] = True

            self.add_met_config(name=config_name, data_type=config_type,
                                metplus_configs=metplus_configs,
                                extra_args=extra_args)

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
