"""grid_diag
Program Name: grid_diag_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs grid_diag
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files: nc files
Condition codes: 0 for success, 1 for failure
"""

import os

from ..util import do_string_sub, parse_var_list, sub_var_list
from . import RuntimeFreqWrapper

'''!@namespace GridDiagWrapper
@brief Wraps the Grid-Diag tool
@endcode
'''


class GridDiagWrapper(RuntimeFreqWrapper):

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_PER_INIT_OR_VALID'
    RUNTIME_FREQ_SUPPORTED = 'ALL'

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_DESC',
        'METPLUS_REGRID_DICT',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_DATA_DICT',
        'METPLUS_MASK_DICT',
        'METPLUS_OUTPUT_FLAG_DICT',
    ]

    # deprecated env vars that are no longer supported in the wrapped MET conf
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'DESC',
        'DATA_FIELD',
        'DATA_FILE_TYPE',
        'VERIF_MASK',
    ]

    OUTPUT_FLAGS = [
        'histogram_1d',
        'histogram_2d',
        'info_theory',
    ]

    def __init__(self, config, instance=None):
        self.app_name = "grid_diag"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_GRID_DIAG_VERBOSITY',
                                                 c_dict['VERBOSITY'])
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file('GridDiagConfig_wrapped')

        self.get_input_templates_multiple(c_dict)

        # error if no input templates are set
        if not c_dict['TEMPLATE_DICT']:
            self.log_error('Must set GRID_DIAG_INPUT_TEMPLATE to run')

        # if True, pair each field with the corresponding input template,
        # passing -data for each. If False, read all fields from all files
        c_dict['PAIRED'] = self.config.getbool('config', 'GRID_DIAG_PAIRED',
                                               True)

        c_dict['OUTPUT_DIR'] = self.config.getdir('GRID_DIAG_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('config', 'GRID_DIAG_OUTPUT_TEMPLATE')

        data_type = self.config.getraw('config', 'GRID_DIAG_FILE_TYPE')
        if not data_type:
            data_type = self.config.getraw('config', 'GRID_DIAG_INPUT_DATATYPE')

        if data_type:
            c_dict['DATA_FILE_TYPE'] = f"file_type = {data_type};"

        # values used in configuration file

        # set regrid dictionary values
        self.handle_regrid(c_dict)

        self.handle_description()

        self.handle_mask(single_value=False)

        self.handle_censor_val_and_thresh()

        self.handle_flags('OUTPUT')

        c_dict['VAR_LIST_TEMP'] = parse_var_list(self.config,
                                                 data_type='FCST',
                                                 met_tool=self.app_name,
                                                 var_options=self.var_options)

        # handle setting VERIF_MASK for old wrapped MET config files
        self.add_met_config(name='poly',
                            data_type='list',
                            env_var_name='METPLUS_VERIF_MASK',
                            metplus_configs=['GRID_DIAG_MASK_POLY',
                                             'GRID_DIAG_POLY',
                                             ('GRID_DIAG_'
                                              'VERIFICATION_MASK_TEMPLATE')],
                            extra_args={'allow_empty': True})
        self.env_var_dict['VERIF_MASK'] = (
            self.env_var_dict.get('METPLUS_VERIF_MASK', '')
        )

        return c_dict

    def set_environment_variables(self, time_info=None):
        """!Set environment variables that will be read by the MET config file.
             Reformat as needed. Print list of variables that were set and
              their values.

            @param time_info dictionary containing timing info from current run
        """
        data_dict = self.format_met_config_dict(self.c_dict,
                                                'data',
                                                ['DATA_FILE_TYPE',
                                                 'DATA_FIELD_FMT'])
        self.env_var_dict['METPLUS_DATA_DICT'] = data_dict
        super().set_environment_variables(time_info)

    def get_command(self):
        cmd = self.app_path

        # add input files
        if self.c_dict['PAIRED']:
            for infile in self.infiles:
                cmd += f" -data {infile}"
        else:
            cmd += f" -data {' '.join(self.infiles)}"

        # add other arguments
        cmd += f" {' '.join(self.args)}"

        # add output path
        out_path = self.get_output_path()
        cmd += f' -out {out_path}'

        # add verbosity
        cmd += f" -v {self.c_dict['VERBOSITY']}"
        return cmd

    def run_at_time_once(self, time_info):
        for file_dict in self.c_dict['ALL_FILES']:
            if file_dict is None: continue
            self.clear()
            if not self.c_dict['PAIRED']:
                file_dict = self._merge_input_files(file_dict)
            self.add_to_infiles(file_dict, time_info)

        # get output path
        if not self.find_and_check_output_file(time_info):
            return

        # get field information to set in MET config
        if not self.set_data_field(time_info):
            return

        self._check_paired_inputs_match_fields()

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # set environment variables if using config file
        self.set_environment_variables(time_info)

        # build command and run
        self.build()

    @staticmethod
    def _merge_input_files(file_dict):
        """!Combine the files from all input templates into a single input
        so that they are passed to a single -data argument. Duplicate files
        are only included once.

        @param file_dict dictionary of input files for each input template
        @returns new file dictionary with all input files under a single key
        """
        merged_dict = {}
        all_files = []
        for key, value in file_dict.items():
            if key in ('var_list', 'time_info', 'input_time_info'):
                merged_dict[key] = value
                continue
            if not value:
                continue
            for item in value:
                if item not in all_files:
                    all_files.append(item)

        merged_dict['input'] = all_files
        return merged_dict

    def _check_paired_inputs_match_fields(self):
        """!If running in paired mode with multiple -data arguments, warn if
        the number of -data arguments does not match the number of fields.
        """
        if not self.c_dict['PAIRED'] or len(self.infiles) < 2:
            return

        num_fields = self.c_dict.get('NUM_FIELDS', 0)
        if len(self.infiles) == num_fields:
            return

        self.logger.warning(
            f'Number of input templates ({len(self.infiles)}) does not match '
            f'the number of fields ({num_fields}). When GRID_DIAG_PAIRED is '
            'True and multiple input templates are set, grid_diag reads the '
            'first field from the files of the first template, the second '
            'field from the files of the second template, etc. Set '
            'GRID_DIAG_PAIRED to False to read all fields from all files.'
        )

    def set_data_field(self, time_info):
        """!Get list of fields from config to process. Build list of field info
            that are formatted to be read by the MET config file. Set
            DATA_FIELD item of c_dict with the formatted list of fields.
            Args:
                @param time_info time dictionary to use for string substitution
                @returns True if field list could be built, False if not.
        """
        all_fields = []
        for field in self.c_dict['VAR_LIST_TEMP']:
            field_info = self.get_field_list('fcst', field, time_info)
            if not field_info:
                return False

            all_fields.extend(field_info)

        self.c_dict['NUM_FIELDS'] = len(all_fields)
        data_field = ','.join(all_fields)
        self.c_dict['DATA_FIELD_FMT'] = f"field = [ {data_field} ];"

        # support old method of setting environment variable
        self.c_dict['DATA_FIELD'] = data_field

        return True

    def set_command_line_arguments(self, time_info):
        """! add config file passing through do_string_sub to get custom
         string if set

            @param time_info dictionary containing time information
        """
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
        self.args.append(f"-config {config_file}")
