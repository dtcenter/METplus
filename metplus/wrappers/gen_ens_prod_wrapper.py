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

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_DESC',
        'METPLUS_REGRID_DICT',
        'METPLUS_CENSOR_THRESH',
        'METPLUS_CENSOR_VAL',
        'METPLUS_CAT_THRESH',
        'METPLUS_NC_VAR_STR',
        'METPLUS_ENS_FILE_TYPE',
        'METPLUS_ENS_ENS_THRESH',
        'METPLUS_ENS_VLD_THRESH',
        'METPLUS_ENS_FIELD',
        'METPLUS_NBRHD_PROB_DICT',
        'METPLUS_NMEP_SMOOTH_DICT',
        'METPLUS_CLIMO_MEAN_DICT',
        'METPLUS_CLIMO_STDEV_DICT',
        'METPLUS_ENSEMBLE_FLAG_DICT',
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
        'rank',
        'weight',
    ]

    def __init__(self, config, instance=None, config_overrides=None):
        self.app_name = 'gen_ens_prod'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR'),
                                     self.app_name)
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        c_dict['VERBOSITY'] = self.config.getstr('config',
                                                 'LOG_GEN_ENS_PROD_VERBOSITY',
                                                 c_dict['VERBOSITY'])

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = self.get_config_file(
            'GenEnsProdConfig_wrapped'
        )

        # get input template/dir - template is required
        c_dict['INPUT_TEMPLATE'] = self.config.getraw(
            'config',
            'GEN_ENS_PROD_INPUT_TEMPLATE'
        )
        c_dict['INPUT_DIR'] = self.config.getdir('GEN_ENS_PROD_INPUT_DIR', '')

        if not c_dict['INPUT_TEMPLATE']:
            self.log_error('GEN_ENS_PROD_INPUT_TEMPLATE must be set')

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

        self.handle_met_config_dict('regrid', {
            'to_grid': ('string', 'to_grid'),
            'method': ('string', 'uppercase,remove_quotes'),
            'width': 'int',
            'vld_thresh': 'float',
            'shape': ('string', 'uppercase,remove_quotes'),
        })

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

        # parse var list for ENS fields
        c_dict['ENS_VAR_LIST_TEMP'] = parse_var_list(
            self.config,
            data_type='ENS',
            met_tool=self.app_name
        )

        self.handle_met_config_dict('nbrhd_prob', {
            'width': ('list', 'remove_quotes'),
            'shape': ('string', 'uppercase,remove_quotes'),
            'vld_thresh': 'float',
        })

        self.handle_met_config_dict('nmep_smooth', {
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

        c_dict['ALLOW_MULTIPLE_FILES'] = True

        return c_dict

    def run_at_time_once(self, time_info):
        """! Build command for a given init/valid time and forecast lead

            @param time_info dictionary containing timing information
        """
        if not self.find_field_info(time_info):
            return False

        if not self.find_input_files(time_info):
            return False

        if not self.find_and_check_output_file(time_info):
            return False

        # add config file to arguments
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'], **time_info)
        self.args.append(f"-config {config_file}")

        if not self.find_ctrl_file(time_info):
            return False

        # set environment variables that are passed to the MET config
        self.set_environment_variables(time_info)

        return self.build()

    def find_input_files(self, time_info):
        """! Get a list of all input files

            @param time_info dictionary containing timing information
            @returns True on success
        """
        input_files = self.find_data(time_info, return_list=True)
        if not input_files:
            self.log_error("Could not find any input files")
            return False

        # write file that contains list of ensemble files
        list_filename = (f"{time_info['init_fmt']}_"
                         f"{time_info['lead_hours']}_gen_ens_prod.txt")
        list_file = self.write_list_file(list_filename, input_files)
        if not list_file:
            self.log_error("Could not write filelist file")
            return False

        self.infiles.append(list_file)

        return True

    def find_ctrl_file(self, time_info):
        """! Find optional ctrl (control) file if requested

            @param time_info dictionary containing timing information
            @returns True on success or if ctrl not requested
        """
        if not self.c_dict['CTRL_INPUT_TEMPLATE']:
            return True

        input_file = self.find_data(time_info, data_type='CTRL')
        if not input_file:
            return False

        self.args.append(f'-ctrl {input_file}')
        return True

    def find_field_info(self, time_info):
        # parse var list for ENS fields
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
        self.env_var_dict['METPLUS_ENS_FIELD'] = f"field = [ {ens_field} ];"
        return True

    def get_command(self):
        """! Builds the command to run gen_ens_prod

           @rtype string
           @return command to run
        """
        return (f"{self.app_path} -v {self.c_dict['VERBOSITY']}"
                f" -ens {self.infiles[0]} -out {self.get_output_path()}"
                f" {' '.join(self.args)}")
