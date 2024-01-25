"""
Program Name: gen_ens_prod_wrapper.py
Contact(s): George McCabe
"""

import os

from ..util import do_string_sub, ti_calculate, get_lead_sequence
from ..util import skip_time, parse_var_list, sub_var_list

from . import LoopTimesWrapper


class GenEnsProdWrapper(LoopTimesWrapper):
    """! Wrapper for gen_ens_prod MET application """

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_REGRID_DICT',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_CAT_THRESH',
        'METPLUS_NC_VAR_STR',
        'METPLUS_ENS_FILE_TYPE',
        'METPLUS_ENS_THRESH',
        'METPLUS_VLD_THRESH',
        'METPLUS_ENS_FIELD',
        'METPLUS_NBRHD_PROB_DICT',
        'METPLUS_NMEP_SMOOTH_DICT',
        'METPLUS_CLIMO_MEAN_DICT',
        'METPLUS_CLIMO_STDEV_DICT',
        'METPLUS_ENSEMBLE_FLAG_DICT',
        'METPLUS_ENS_MEMBER_IDS',
        'METPLUS_CONTROL_ID',
        'METPLUS_NORMALIZE',
    ]

    ENSEMBLE_FLAGS = [
        'latlon',
        'mean',
        'stdev',
        'minus',
        'plus',
        'min',
        'max',
        'range',
        'vld_count',
        'frequency',
        'nep',
        'nmep',
        'climo',
        'climo_cdp',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'gen_ens_prod'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file(
            'GenEnsProdConfig_wrapped'
        )

        # get input template/dir - template is required
        c_dict['FCST_INPUT_TEMPLATE'] = self.config.getraw(
            'config',
            'GEN_ENS_PROD_INPUT_TEMPLATE'
        )
        c_dict['FCST_INPUT_DIR'] = self.config.getdir('GEN_ENS_PROD_INPUT_DIR',
                                                      '')

        c_dict['FCST_INPUT_FILE_LIST'] = (
            self.config.getraw('config', 'GEN_ENS_PROD_INPUT_FILE_LIST')
        )

        if (not c_dict['FCST_INPUT_TEMPLATE'] and
                not c_dict['FCST_INPUT_FILE_LIST']):
            self.log_error('GEN_ENS_PROD_INPUT_TEMPLATE or '
                           'GEN_ENS_PROD_INPUT_FILE_LIST must be set')

        # not all input files are mandatory to be found
        c_dict['MANDATORY'] = False

        # fill inputs that are not found with fake path to note it is missing
        c_dict['FCST_FILL_MISSING'] = True

        # number of expected ensemble members
        c_dict['N_MEMBERS'] = (
            self.config.getint('config', 'GEN_ENS_PROD_N_MEMBERS')
        )

        # get ctrl (control) template/dir - optional
        c_dict['CTRL_INPUT_TEMPLATE'] = self.config.getraw(
            'config',
            'GEN_ENS_PROD_CTRL_INPUT_TEMPLATE'
        )
        c_dict['CTRL_INPUT_DIR'] = self.config.getdir(
            'GEN_ENS_PROD_CTRL_INPUT_DIR',
            ''
        )

        # get output template/dir - template is required
        c_dict['OUTPUT_DIR'] = self.config.getdir('GEN_ENS_PROD_OUTPUT_DIR',
                                                  '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'GEN_ENS_PROD_OUTPUT_TEMPLATE')
        )
        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error("Must set GEN_ENS_PROD_OUTPUT_TEMPLATE")

        # get MET config file overrides
        self.add_met_config(name='model',
                            data_type='string',
                            metplus_configs=['MODEL', 'GEN_ENS_PROD_MODEL'],
                            )

        self.add_met_config(name='desc',
                            data_type='string',
                            metplus_configs=['DESC', 'GEN_ENS_PROD_DESC'],
                            )

        self.handle_regrid(c_dict)

        self.add_met_config(name='censor_thresh',
                            data_type='list',
                            metplus_configs=['GEN_ENS_PROD_CENSOR_THRESH'],
                            extra_args={'remove_quotes': True},
                            )

        self.add_met_config(name='censor_val',
                            data_type='list',
                            metplus_configs=['GEN_ENS_PROD_CENSOR_VAL'],
                            extra_args={'remove_quotes': True},
                            )

        self.add_met_config(name='cat_thresh',
                            data_type='list',
                            metplus_configs=['GEN_ENS_PROD_CAT_THRESH'],
                            extra_args={'remove_quotes': True},
                            )

        self.add_met_config(name='nc_var_str',
                            data_type='string',
                            metplus_configs=['GEN_ENS_PROD_NC_VAR_STR'],
                            )

        self.add_met_config(name='ens_thresh',
                            data_type='float',
                            metplus_configs=['GEN_ENS_PROD_ENS_THRESH',
                                             'GEN_ENS_PROD_ENS_ENS_THRESH'],
                            )

        self.add_met_config(name='vld_thresh',
                            data_type='float',
                            metplus_configs=['GEN_ENS_PROD_VLD_THRESH',
                                             'GEN_ENS_PROD_ENS_VLD_THRESH'],
                            )

        self.add_met_config(name='normalize',
                            data_type='string',
                            extra_args={'remove_quotes': True},
                            )

        # parse var list for ENS fields
        c_dict['ENS_VAR_LIST_TEMP'] = parse_var_list(
            self.config,
            data_type='ENS',
            met_tool=self.app_name
        )

        self.add_met_config(name='file_type',
                            data_type='string',
                            env_var_name='ENS_FILE_TYPE',
                            metplus_configs=['GEN_ENS_PROD_ENS_FILE_TYPE',
                                             'GEN_ENS_PROD_FILE_TYPE',
                                             'ENS_FILE_TYPE'],
                            extra_args={'remove_quotes': True,
                                        'uppercase': True})

        self.add_met_config_dict('nbrhd_prob', {
            'width': ('list', 'remove_quotes'),
            'shape': ('string', 'uppercase,remove_quotes'),
            'vld_thresh': 'float',
        })

        # note: nmep_smooth.type is a list of dictionaries,
        # but only setting 1 dictionary in the list is supported
        self.add_met_config_dict('nmep_smooth', {
            'vld_thresh': 'float',
            'shape': ('string', 'uppercase,remove_quotes'),
            'gaussian_dx': 'float',
            'gaussian_radius': 'int',
            'type': ('dictlist', '', {'method': ('string',
                                                 'uppercase,remove_quotes'),
                                      'width': 'int',
                                      }
                     )
        })

        # get climatology config variables
        self.handle_climo_dict()

        self.handle_flags('ENSEMBLE')

        self.add_met_config(name='ens_member_ids',
                            data_type='list')

        self.add_met_config(name='control_id',
                            data_type='string')

        c_dict['ALLOW_MULTIPLE_FILES'] = True

        return c_dict

    def run_at_time_once(self, time_info):
        """! Build command for a given init/valid time and forecast lead

            @param time_info dictionary containing timing information
        """
        # add config file to arguments
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
        self.args.append(f"-config {config_file}")

        if not self.find_field_info(time_info):
            return False

        if not self.find_input_files(time_info):
            return False

        if not self.find_and_check_output_file(time_info):
            return False

        # set environment variables that are passed to the MET config
        self.set_environment_variables(time_info)

        return self.build()

    def find_input_files(self, time_info):
        # do not fill file list with missing if ens_member_ids is used
        fill_missing = not self.env_var_dict.get('METPLUS_ENS_MEMBER_IDS')
        if not self.find_input_files_ensemble(time_info,
                                              fill_missing=fill_missing):
            return False
        return True

    def find_field_info(self, time_info):
        """! parse var list for ENS fields

            @param time_info dictionary containing timing information
            @returns True if successful, False if something went wrong
        """
        ensemble_var_list = sub_var_list(self.c_dict['ENS_VAR_LIST_TEMP'],
                                         time_info)
        all_fields = []
        for field in ensemble_var_list:
            field_list = self.get_field_info(d_type='ENS',
                                             v_name=field['ens_name'],
                                             v_level=field['ens_level'],
                                             v_thresh=field['ens_thresh'],
                                             v_extra=field['ens_extra'])
            if field_list is None:
                return False

            all_fields.extend(field_list)

        ens_field = ','.join(all_fields)
        self.env_var_dict['METPLUS_ENS_FIELD'] = f"field = [{ens_field}];"
        return True

    def get_command(self):
        """! Builds the command to run gen_ens_prod

           @rtype string
           @return command to run
        """
        return (f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
                f" -ens {self.infiles[0]}"
                f" -out {self.get_output_path()}"
                f" {' '.join(self.args)}")
