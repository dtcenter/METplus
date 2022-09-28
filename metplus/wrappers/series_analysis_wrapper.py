"""
Program Name: series_analysis_wrapper.py
Contact(s): George McCabe
Abstract: Builds command for and runs SeriesAnalysis. Optionally produce plots
 and animated gifs of the output
History Log:  Initial version
Usage:
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
"""

import os

# handle if module can't be loaded to run wrapper
WRAPPER_CANNOT_RUN = False
EXCEPTION_ERR = ''
try:
    import netCDF4
except Exception as err_msg:
    WRAPPER_CANNOT_RUN = True
    EXCEPTION_ERR = err_msg

from ..util import getlist, get_storms, mkdir_p
from ..util import do_string_sub, parse_template, get_tags
from ..util import get_lead_sequence, get_lead_sequence_groups
from ..util import ti_get_hours_from_lead, ti_get_seconds_from_lead
from ..util import ti_get_lead_string, ti_calculate
from ..util import ti_get_seconds_from_relativedelta
from ..util import parse_var_list
from ..util import add_to_time_input
from ..util import field_read_prob_info
from .plot_data_plane_wrapper import PlotDataPlaneWrapper
from . import RuntimeFreqWrapper

class SeriesAnalysisWrapper(RuntimeFreqWrapper):
    """!  Performs series analysis with filtering options
    """

    WRAPPER_ENV_VAR_KEYS = [
        'METPLUS_MODEL',
        'METPLUS_OBTYPE',
        'METPLUS_DESC',
        'METPLUS_REGRID_DICT',
        'METPLUS_CAT_THRESH',
        'METPLUS_FCST_FILE_TYPE',
        'METPLUS_FCST_FIELD',
        'METPLUS_OBS_FILE_TYPE',
        'METPLUS_OBS_FIELD',
        'METPLUS_CLIMO_MEAN_DICT',
        'METPLUS_CLIMO_STDEV_DICT',
        'METPLUS_BLOCK_SIZE',
        'METPLUS_VLD_THRESH',
        'METPLUS_OUTPUT_STATS_DICT',
        'METPLUS_HSS_EC_VALUE',
        'METPLUS_FCST_CAT_THRESH',
        'METPLUS_OBS_CAT_THRESH',
        'METPLUS_CLIMO_CDF_DICT',
    ]

    # handle deprecated env vars used pre v4.0.0
    DEPRECATED_WRAPPER_ENV_VAR_KEYS = [
        'CLIMO_MEAN_FILE',
        'CLIMO_STDEV_FILE',
        'METPLUS_CTS_LIST',
        'METPLUS_STAT_LIST',
    ]

    # variable names of output_stats dictionary
    OUTPUT_STATS = [
        'fho',
        'ctc',
        'cts',
        'mctc',
        'mcts',
        'cnt',
        'sl1l2',
        'sal1l2',
        'pct',
        'pstd',
        'pjc',
        'prc',
    ]

    def __init__(self, config, instance=None):
        self.app_name = 'series_analysis'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)

        super().__init__(config, instance=instance)

        if self.c_dict['GENERATE_PLOTS']:
            self.plot_data_plane = self._plot_data_plane_init()

        if WRAPPER_CANNOT_RUN:
            self.log_error("There was a problem importing modules: "
                           f"{EXCEPTION_ERR}\n")

        self.logger.debug("Initialized SeriesAnalysisWrapper")

    def create_c_dict(self):
        """! Populate c_dict dictionary with values from METplusConfig """
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config',
                               'LOG_SERIES_ANALYSIS_VERBOSITY',
                               c_dict['VERBOSITY'])
        )

        self.add_met_config(name='model',
                            data_type='string',
                            metplus_configs=['MODEL'])

        self.add_met_config(name='obtype',
                            data_type='string',
                            metplus_configs=['OBTYPE'])

        # handle old format of MODEL and OBTYPE
        c_dict['MODEL'] = self.config.getstr('config', 'MODEL', 'WRF')
        c_dict['OBTYPE'] = self.config.getstr('config', 'OBTYPE', 'ANALYS')

        self.handle_description()

        self.handle_regrid(c_dict)

        self.add_met_config(name='cat_thresh',
                            data_type='list',
                            extra_args={'remove_quotes': True})

        self.add_met_config(name='vld_thresh',
                            data_type='float',
                            metplus_configs=['SERIES_ANALYSIS_VLD_THRESH',
                                             'SERIES_ANALYSIS_VALID_THRESH',])

        self.add_met_config(name='block_size',
                            data_type='string',
                            extra_args={'remove_quotes': True})

        # handle all output_stats dictionary values
        output_stats_dict = {}
        for key in self.OUTPUT_STATS:
            nicknames = [
                f'SERIES_ANALYSIS_OUTPUT_STATS_{key.upper()}',
                f'SERIES_ANALYSIS_{key.upper()}_LIST',
                f'SERIES_ANALYSIS_{key.upper()}'
            ]
            # add legacy support for STAT_LIST for cnt
            if key == 'cnt':
                nicknames.append('SERIES_ANALYSIS_STAT_LIST')
                # read cnt stat list to get stats to loop over for plotting
                self.add_met_config(name='cnt',
                                    data_type='list',
                                    env_var_name='STAT_LIST',
                                    metplus_configs=nicknames)
                c_dict['STAT_LIST'] = getlist(
                    self.get_env_var_value('METPLUS_STAT_LIST')
                )

            value = ('list', None, None, nicknames)
            output_stats_dict[key] = value
        self.add_met_config_dict('output_stats', output_stats_dict)

        # set legacy stat list to set output_stats.cnt in MET config file
        self.add_met_config(name='cnt',
                            data_type='list',
                            env_var_name='METPLUS_STAT_LIST',
                            metplus_configs=['SERIES_ANALYSIS_STAT_LIST',
                                             'SERIES_ANALYSIS_CNT'])

        # set legacy cts list to set output_stats.cts in MET config file
        self.add_met_config(name='cts',
                            data_type='list',
                            env_var_name='METPLUS_CTS_LIST',
                            metplus_configs=['SERIES_ANALYSIS_CTS_LIST',
                                             'SERIES_ANALYSIS_CTS'])

        c_dict['PAIRED'] = self.config.getbool('config',
                                               'SERIES_ANALYSIS_IS_PAIRED',
                                               False)

        # read probabilistic variables for FCST and OBS fields
        field_read_prob_info(config=self.config,
                             c_dict=c_dict,
                             data_types=('FCST', 'OBS'),
                             app_name=self.app_name)

        # get input dir, template, and datatype for FCST, OBS, and BOTH
        for data_type in ('FCST', 'OBS', 'BOTH'):

            # check if {data_type}_{app}_FILE_LIST is set
            c_dict[f'{data_type}_INPUT_FILE_LIST'] = (
                self.config.getraw(
                    'config',
                    f'{data_type}_SERIES_ANALYSIS_INPUT_FILE_LIST'
                )
            )

            c_dict[f'{data_type}_INPUT_DIR'] = (
              self.config.getdir(f'{data_type}_SERIES_ANALYSIS_INPUT_DIR', '')
            )
            c_dict[f'{data_type}_INPUT_TEMPLATE'] = (
              self.config.getraw('config',
                                 f'{data_type}_SERIES_ANALYSIS_INPUT_TEMPLATE',
                                 '')
            )

            c_dict[f'{data_type}_INPUT_DATATYPE'] = (
              self.config.getstr('config',
                                 f'{data_type}_SERIES_ANALYSIS_INPUT_DATATYPE',
                                 '')
            )

            # initialize list path to None for each type
            c_dict[f'{data_type}_LIST_PATH'] = None

            # read and set file type env var for FCST and OBS
            if data_type == 'BOTH':
                continue

            self.add_met_config(
                name='file_type',
                data_type='string',
                env_var_name=f'{data_type}_FILE_TYPE',
                metplus_configs=[f'{data_type}_SERIES_ANALYSIS_FILE_TYPE',
                                 f'SERIES_ANALYSIS_{data_type}_FILE_TYPE',
                                 f'{data_type}_FILE_TYPE',
                                 f'{data_type}_SERIES_ANALYSIS_INPUT_DATATYPE',
                                 'SERIES_ANALYSIS_FILE_TYPE'],
                extra_args={'remove_quotes': True,
                            'uppercase': True})

            self.add_met_config(
                name='cat_thresh',
                data_type='list',
                env_var_name=f'METPLUS_{data_type}_CAT_THRESH',
                metplus_configs=[f'{data_type}_SERIES_ANALYSIS_CAT_THRESH',
                                 f'SERIES_ANALYSIS_{data_type}_CAT_THRESH',
                                 f'{data_type}_CAT_THRESH'],
                extra_args={'remove_quotes': True}
            )

        c_dict['USING_BOTH'] = (c_dict['BOTH_INPUT_TEMPLATE'] or
                                c_dict['BOTH_INPUT_FILE_LIST'])

        if c_dict['USING_BOTH']:

            # check if using explicit file list for BOTH
            if c_dict['BOTH_INPUT_FILE_LIST']:
                c_dict['EXPLICIT_FILE_LIST'] = True
            else:
                # set *_WINDOW_* variables for BOTH
                # used in CommandBuilder.find_data function)
                self.handle_file_window_variables(c_dict, data_types=['BOTH'])

            prob_thresh = self.config.getraw(
                'config',
                'BOTH_SERIES_ANALYSIS_PROB_THRESH'
            )
            c_dict['FCST_PROB_THRESH'] = prob_thresh
            c_dict['OBS_PROB_THRESH'] = prob_thresh

        # if BOTH is not set, both FCST or OBS must be set
        else:
            fcst_input_list = c_dict['FCST_INPUT_FILE_LIST']
            obs_input_list = c_dict['OBS_INPUT_FILE_LIST']
            if fcst_input_list and obs_input_list:
                c_dict['EXPLICIT_FILE_LIST'] = True
            elif not fcst_input_list and not obs_input_list:
                if (not c_dict['FCST_INPUT_TEMPLATE'] or
                        not c_dict['OBS_INPUT_TEMPLATE']):
                    self.log_error(
                        "Must either set "
                        "BOTH_SERIES_ANALYSIS_INPUT_TEMPLATE or both "
                        "FCST_SERIES_ANALYSIS_INPUT_TEMPLATE and "
                        "OBS_SERIES_ANALYSIS_INPUT_TEMPLATE to run "
                        "SeriesAnalysis wrapper."
                    )

                # set *_WINDOW_* variables for FCST and OBS
                self.handle_file_window_variables(c_dict)
            # if fcst input list or obs input list are not set
            else:
                self.log_error('Cannot set '
                               'FCST_SERIES_ANALYSIS_INPUT_FILE_LIST '
                               'without OBS_SERIES_ANALYSIS_INPUT_FILE_LIST '
                               'and vice versa')

            c_dict['FCST_PROB_THRESH'] = (
                    self.config.getraw('config',
                                       'FCST_SERIES_ANALYSIS_PROB_THRESH')
            )

            c_dict['OBS_PROB_THRESH'] = (
                    self.config.getraw('config',
                                       'OBS_SERIES_ANALYSIS_PROB_THRESH')
            )

        c_dict['TC_STAT_INPUT_DIR'] = (
            self.config.getdir('SERIES_ANALYSIS_TC_STAT_INPUT_DIR', '')
        )

        c_dict['TC_STAT_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'SERIES_ANALYSIS_TC_STAT_INPUT_TEMPLATE')
        )

        c_dict['OUTPUT_DIR'] = self.config.getdir('SERIES_ANALYSIS_OUTPUT_DIR',
                                                  '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'SERIES_ANALYSIS_OUTPUT_TEMPLATE')
        )
        if not c_dict['OUTPUT_DIR']:
            self.log_error("Must set SERIES_ANALYSIS_OUTPUT_DIR to run.")

        # get the MET config file path or use default
        c_dict['CONFIG_FILE'] = (
            self.get_config_file('SeriesAnalysisConfig_wrapped')
        )

        c_dict['BACKGROUND_MAP'] = (
            self.config.getbool('config',
                                'SERIES_ANALYSIS_BACKGROUND_MAP',
                                False)
        )

        c_dict['VAR_LIST'] = parse_var_list(self.config,
                                            met_tool=self.app_name)
        if not c_dict['VAR_LIST']:
            self.log_error("No fields specified. Please set "
                           "[FCST/OBS]_VAR<n>_[NAME/LEVELS]")

        c_dict['GENERATE_PLOTS'] = (
            self.config.getbool('config',
                                'SERIES_ANALYSIS_GENERATE_PLOTS',
                                False)
        )

        c_dict['GENERATE_ANIMATIONS'] = (
            self.config.getbool('config',
                                'SERIES_ANALYSIS_GENERATE_ANIMATIONS',
                                False)
        )

        c_dict['CONVERT_EXE'] = self.config.getexe('CONVERT')
        if c_dict['GENERATE_ANIMATIONS'] and not c_dict['CONVERT_EXE']:
            self.log_error("[exe] CONVERT must be set correctly if "
                           "SERIES_ANALYSIS_GENERATE_ANIMATIONS is True")

        c_dict['PNG_FILES'] = {}

        c_dict['RUN_ONCE_PER_STORM_ID'] = (
            self.config.getbool('config',
                                'SERIES_ANALYSIS_RUN_ONCE_PER_STORM_ID',
                                False)
        )
        if (c_dict['RUN_ONCE_PER_STORM_ID'] and
                not c_dict['TC_STAT_INPUT_TEMPLATE']):
            self.log_error("Must set SERIES_ANALYSIS_TC_STAT_INPUT_TEMPLATE "
                           "if SERIES_ANALYSIS_RUN_ONCE_PER_STORM_ID is True")

        # get climatology config variables
        self.handle_climo_dict()

        # get climo_cdf dictionary
        self.handle_climo_cdf_dict(write_bins=False)

        self.add_met_config(name='hss_ec_value',
                            data_type='float',
                            metplus_configs=['SERIES_ANALYSIS_HSS_EC_VALUE'])

        # if no forecast lead sequence is specified,
        # use wildcard (*) so all leads are used
        c_dict['WILDCARD_LEAD_IF_EMPTY'] = True

        # allow multiple files so wildcards can be used to get input files
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        return c_dict

    def _plot_data_plane_init(self):
        """! Set values to allow successful initialization of
              PlotDataPlane wrapper

             @returns instance of PlotDataPlaneWrapper
        """
        plot_overrides = {'PLOT_DATA_PLANE_INPUT_TEMPLATE': 'template',
                          'PLOT_DATA_PLANE_OUTPUT_TEMPLATE': 'template',
                          'PLOT_DATA_PLANE_FIELD_NAME': 'field_name',
                          'PLOT_DATA_PLANE_CONVERT_TO_IMAGE': True,
                          }

        if not self.c_dict['BACKGROUND_MAP']:
            plot_overrides['PLOT_DATA_PLANE_FIELD_EXTRA'] = (
                "map_data={ source=[];}"
            )

        instance = 'plot_data_plane_sa'
        if not self.config.has_section(instance):
            self.config.add_section(instance)
        for key, value in plot_overrides.items():
            self.config.set(instance, key, value)

        pdp_wrapper = PlotDataPlaneWrapper(self.config,
                                           instance=instance)
        return pdp_wrapper

    def clear(self):
        """! Call parent's clear function and clear additional values """
        super().clear()
        for data_type in ('FCST', 'OBS', 'BOTH'):
            self.c_dict[f'{data_type}_LIST_PATH'] = None

    def run_all_times(self):
        """! Process all run times defined for this wrapper """
        super().run_all_times()

        if self.c_dict['GENERATE_ANIMATIONS']:
            self.generate_animations()

        return self.all_commands

    def run_once_per_lead(self, custom):
        """! Run once per forecast lead

             @param value of current CUSTOM_LOOP_LIST iteration
             @returns True if all runs were successful, False otherwise
        """
        self.logger.debug("Running once for forecast lead time")
        success = True

        lead_groups = get_lead_sequence_groups(self.config)
        if not lead_groups:
            lead_seq = get_lead_sequence(self.config,
                                         input_dict=None,
                                         wildcard_if_empty=True)
            for index, lead in enumerate(lead_seq):
                lead_hours = ti_get_hours_from_lead(lead)

                # if cannot get lead hours, use index of forecast lead
                # hours cannot be computed from months or years without
                # knowing the valid time
                if lead_hours is None:
                    lead_hours = index
                else:
                    lead_hours = f"F{str(lead_hours).zfill(3)}"

                lead_groups[f'series_{lead_hours}'] = [lead]

        for lead_group in lead_groups.items():
            # create input dict and only set 'now' item
            # create a new dictionary each iteration in case the function
            # that it is passed into modifies it
            input_dict = {}
            add_to_time_input(input_dict,
                              clock_time=self.config.getstr('config',
                                                            'CLOCK_TIME'),
                              instance=self.instance,
                              custom=custom)

            input_dict['init'] = '*'
            input_dict['valid'] = '*'
            lead_hours = [ti_get_lead_string(item, plural=False) for
                          item in lead_group[1]]

            self.logger.debug(f"Processing {lead_group[0]} - forecast leads: "
                              f"{', '.join(lead_hours)}")

            self.c_dict['ALL_FILES'] = (
                self.get_all_files_for_leads(input_dict, lead_group[1])
            )

            # if only 1 forecast lead is being processed, set it in time dict
            if len(lead_group[1]) == 1:
                input_dict['lead'] = lead_group[1][0]

            if not self.run_at_time_once(input_dict, lead_group):
                success = False

        return success

    def get_all_files_for_leads(self, input_dict, leads):
        all_files = []
        current_input_dict = input_dict.copy()
        for lead in leads:
            current_input_dict['lead'] = lead
            new_files = self.get_all_files_for_lead(current_input_dict)
            all_files.extend(new_files)
        return all_files

    def run_at_time_once(self, time_info, lead_group=None):
        """! Attempt to build series_analysis command for run time

            @param time_info dictionary containing time information
            @param lead_group (optional) dictionary where key is label and
             value is a list of forecast leads to process.
            @returns True on success, False otherwise
        """
        self.logger.debug("Starting SeriesAnalysis")

        # if running for each storm ID, get list of storms
        storm_list = self.get_storm_list(time_info)
        if not storm_list:
            return False

        # loop over storm list and process for each
        # this loop will execute once if not filtering by storm ID
        for storm_id in storm_list:
            # Create FCST and OBS ASCII files
            fcst_path, obs_path = (
                self._get_fcst_and_obs_path(time_info,
                                            storm_id,
                                            lead_group)
            )
            if not fcst_path or not obs_path:
                self.log_error('No ASCII file lists were created. Skipping.')
                continue

            # Build up the arguments to and then run the MET tool series_analysis.
            if not self.build_and_run_series_request(time_info,
                                                     fcst_path,
                                                     obs_path):
                continue

            if self.c_dict['GENERATE_PLOTS']:
                self._generate_plots(fcst_path,
                                     time_info,
                                     storm_id)
            else:
                self.logger.debug("Skip plotting output. Change "
                                  "SERIES_ANALYSIS_GENERATE_PLOTS to True to "
                                  "run this step.")

        self.logger.debug("Finished series analysis")
        return True

    def get_storm_list(self, time_info):
        """! Find the .tcst filter file for the current run time and get the
             list of storm IDs that are found in the file.

            @param time_info dictionary containing time information
            @returns A list of all the storms ids that correspond to the
             current init time or None if filter file does not exist
        """
        if not self.c_dict['RUN_ONCE_PER_STORM_ID']:
            return ['*']

        # Retrieve filter files, first create the filename
        # by piecing together the out_dir_base with the cur_init.
        filter_template = os.path.join(self.c_dict['TC_STAT_INPUT_DIR'],
                                       self.c_dict['TC_STAT_INPUT_TEMPLATE'])
        filter_file = do_string_sub(filter_template, **time_info)
        self.logger.debug(f"Getting storms from filter file: {filter_file}")
        if not os.path.exists(filter_file):
            self.log_error(f"Filter file does not exist: {filter_file}")
            return None

        # Now that we have the filter filename for the init time, let's
        # extract all the storm ids in this filter file.
        storm_list = get_storms(filter_file, id_only=True)
        if not storm_list:
            # No storms for this init time, check next init time in list
            self.logger.debug("No storms found for current runtime")
            return None

        return storm_list

    def get_files_from_time(self, time_info):
        """! Create dictionary containing time information (key time_info) and
             any relevant files for that runtime. The parent implementation of
             this function creates a dictionary and adds the time_info to it.
             This wrapper gets all files for the current runtime and adds it to
             the dictionary with keys 'fcst' and 'obs'

             @param time_info dictionary containing time information
             @returns dictionary containing time_info dict and any relevant
             files with a key representing a description of that file
        """
        file_dict_list = []
        # get all storm IDs
        storm_list = self.get_storm_list(time_info)
        if not storm_list:
            return None

        for storm_id in storm_list:
            time_info['storm_id'] = storm_id
            file_dict = super().get_files_from_time(time_info)
            if self.c_dict['USING_BOTH']:
                fcst_files = self.find_input_files(time_info, 'BOTH')
                obs_files = fcst_files
            else:
                fcst_files = self.find_input_files(time_info, 'FCST')
                obs_files = self.find_input_files(time_info, 'OBS')

            if fcst_files is None or obs_files is None:
                return None

            fcst_key, obs_key = self._get_fcst_obs_keys(storm_id)

            file_dict[fcst_key] = fcst_files
            file_dict[obs_key] = obs_files
            file_dict_list.append(file_dict)

        return file_dict_list

    @staticmethod
    def _get_fcst_obs_keys(storm_id):
        fcst_key = 'fcst'
        obs_key = 'obs'
        if storm_id != '*':
            fcst_key = f'{fcst_key}_{storm_id}'
            obs_key = f'{obs_key}_{storm_id}'
        return fcst_key, obs_key

    def find_input_files(self, time_info, data_type):
        """! Loop over list of input templates and find files for each

             @param time_info time dictionary to use for string substitution
             @param data_type type of data to find, i.e. FCST or OBS
             @returns Input file list if all files were found, None if not.
        """
        input_files = self.find_data(time_info,
                                     return_list=True,
                                     data_type=data_type,
                                     mandatory=False)
        return input_files

    def compare_time_info(self, runtime, filetime):
        """! Call parents implementation then if the current run time and file
              time may potentially still not match, use storm_id to check

             @param runtime dictionary containing time information for current
              runtime
             @param filetime dictionary containing time information for file
              that is being evaluated
             @returns True if the file should be processed in the current
              run or False if not
        """
        if not super().compare_time_info(runtime, filetime):
            return False

        # compare storm_id
        if runtime['storm_id'] == '*':
            return True

        return bool(filetime['storm_id'] == runtime['storm_id'])

    def _get_fcst_and_obs_path(self, time_info, storm_id, lead_group):
        """! Creates the list of ASCII files that contain the storm id and init
             times.  The list is used to create an ASCII file which will be
             used as the option to the -obs or -fcst flag to the MET
             series_analysis tool.

             @param time_info dictionary containing time information
             @param storm_id storm ID to process
             @param lead_group dictionary where key is label and value is a
              list of forecast leads to process. If no label was defined, the
              key will match the format "NoLabel_<n>" and if no lead groups
              are defined, the dictionary should be replaced with None
        """
        if not self._check_python_embedding():
            return None, None

        time_info['storm_id'] = storm_id

        # get label and lead list if grouping by forecast leads
        if lead_group:
            label = lead_group[0]
            leads = lead_group[1]
        else:
            label = ''
            leads = None

        # if file list are explicitly specified,
        # return the file list file paths
        if self.c_dict.get('EXPLICIT_FILE_LIST', False):
            # set forecast lead to last lead in list to set in output filename
            if leads:
                time_info['lead'] = leads[-1]

            if self.c_dict['USING_BOTH']:
                both_path = do_string_sub(self.c_dict['BOTH_INPUT_FILE_LIST'],
                                          **time_info)
                self.logger.debug(f"Explicit BOTH file list file: {both_path}")
                if not os.path.exists(both_path):
                    self.log_error(f'Could not find file: {both_path}')
                    return None, None

                return both_path, both_path

            fcst_path = do_string_sub(self.c_dict['FCST_INPUT_FILE_LIST'],
                                      **time_info)
            self.logger.debug(f"Explicit FCST file list file: {fcst_path}")
            if not os.path.exists(fcst_path):
                self.log_error(f'Could not find forecast file: {fcst_path}')
                fcst_path = None

            obs_path = do_string_sub(self.c_dict['OBS_INPUT_FILE_LIST'],
                                     **time_info)
            self.logger.debug(f"Explicit OBS file list file: {obs_path}")
            if not os.path.exists(obs_path):
                self.log_error(f'Could not find observation file: {obs_path}')
                obs_path = None

            return fcst_path, obs_path

        output_dir = self.get_output_dir(time_info, storm_id, label)

        list_file_dict = self.subset_input_files(time_info,
                                                 output_dir=output_dir,
                                                 leads=leads)
        if not list_file_dict:
            return None, None

        # add storm_id and label to time_info for output filename
        self._add_storm_id_and_label(time_info, storm_id, label)
        fcst_key, obs_key = self._get_fcst_obs_keys(storm_id)
        fcst_path = list_file_dict[fcst_key]
        if self.c_dict['USING_BOTH']:
            return fcst_path, fcst_path
        obs_path = list_file_dict[obs_key]
        return fcst_path, obs_path

    def _check_python_embedding(self):
        """! Check if any of the field names contain a Python embedding script.
              See CommandBuilder.check_for_python_embedding for more info.

            @returns False if something is not configured correctly or True
        """
        for var_info in self.c_dict['VAR_LIST']:
            if self.c_dict['USING_BOTH']:
                if not self.check_for_python_embedding('BOTH', var_info):
                    return False
            else:
                if not self.check_for_python_embedding('FCST', var_info):
                    return False
                if not self.check_for_python_embedding('OBS', var_info):
                    return False

        return True

    def get_output_dir(self, time_info, storm_id, label):
        """! Determine directory that will contain output data from the
              OUTPUT_DIR and OUTPUT_TEMPLATE. This will include any
              subdirectories specified in the filename template.

             @param time_info dictionary containing time information for
             current run
             @param storm_id storm ID to process
             @param label label defined for forecast lead groups to identify
              them
             @returns path to output directory with filename templates
              substituted with the information for the current run
        """
        output_dir_template = os.path.join(self.c_dict['OUTPUT_DIR'],
                                           self.c_dict['OUTPUT_TEMPLATE'])
        output_dir_template = os.path.dirname(output_dir_template)

        # get output directory including storm ID and label
        current_time_info = time_info.copy()
        self._add_storm_id_and_label(current_time_info, storm_id, label)
        output_dir = do_string_sub(output_dir_template,
                                   **current_time_info)
        return output_dir

    @staticmethod
    def _add_storm_id_and_label(time_info, storm_id, label):
        if storm_id == '*':
            storm_id_out = 'all_storms'
        else:
            storm_id_out = storm_id

        time_info['storm_id'] = storm_id_out
        time_info['label'] = label

    def build_and_run_series_request(self, time_info, fcst_path, obs_path):
        """! Build up the -obs, -fcst, -out necessary for running the
             series_analysis MET tool, then invoke series_analysis.

             @param time_info dictionary containing time information for
             current run
             @param storm_id storm ID to process
             @returns True if all runs succeeded, False if there was a problem
             with any of the runs
        """
        success = True

        num, beg, end = self.get_fcst_file_info(fcst_path)
        if num is None:
            self.logger.debug("Could not get fcst_beg and fcst_end values. "
                              "Those values cannot be used in filename "
                              "templates")

        time_info['fcst_beg'] = beg
        time_info['fcst_end'] = end

        # build the command and run series_analysis for each variable
        for var_info in self.c_dict['VAR_LIST']:
            if self.c_dict['USING_BOTH']:
                self.c_dict['BOTH_LIST_PATH'] = fcst_path
            else:
                self.c_dict['FCST_LIST_PATH'] = fcst_path
                self.c_dict['OBS_LIST_PATH'] = obs_path

            self.add_field_info_to_time_info(time_info, var_info)

            # get formatted field dictionary to pass into the MET config file
            fcst_field, obs_field = self.get_formatted_fields(var_info,
                                                              fcst_path,
                                                              obs_path)

            self.format_field('FCST', fcst_field)
            self.format_field('OBS', obs_field)

            self.set_environment_variables(time_info)

            self.set_command_line_arguments(time_info)

            self.find_and_check_output_file(time_info)

            if not self.build():
                success = False

            self.clear()

        return success

    def set_environment_variables(self, time_info):
        """! Set the env variables based on settings in the METplus config
             files.

             @param time_info dictionary containing time information
             @param fcst_field formatted forecast field information
             @param obs_field formatted observation field information
        """
        self.logger.info('Setting env variables from config file...')

        # Set all the environment variables referenced in the MET config file
        self.add_env_var("FCST_FILE_TYPE", self.c_dict.get('FCST_FILE_TYPE',
                                                           ''))
        self.add_env_var("OBS_FILE_TYPE", self.c_dict.get('OBS_FILE_TYPE',
                                                          ''))

        self.add_env_var("FCST_FIELD",
                         self.c_dict.get('FCST_FIELD', ''))
        self.add_env_var("OBS_FIELD",
                         self.c_dict.get('OBS_FIELD', ''))

        # set old env var settings for backwards compatibility
        self.add_env_var('MODEL', self.c_dict.get('MODEL', ''))
        self.add_env_var("OBTYPE", self.c_dict.get('OBTYPE', ''))
        self.add_env_var('REGRID_TO_GRID',
                         self.c_dict.get('REGRID_TO_GRID', ''))

        # format old stat list
        stat_list = self.c_dict.get('STAT_LIST')
        if not stat_list:
            stat_list = "[]"
        else:
            stat_list = '","'.join(stat_list)
            stat_list = f'["{stat_list}"]'
        self.add_env_var('STAT_LIST', stat_list)

        super().set_environment_variables(time_info)

    def set_command_line_arguments(self, time_info):
        """! Set arguments that will be passed into the MET command

             @param time_info dictionary containing time information
        """
        # add input data format if set
        if self.c_dict['PAIRED']:
            self.args.append(" -paired")

        # add config file - passing through do_string_sub
        # to get custom string if set
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                    **time_info)
        self.args.append(f" -config {config_file}")

    def get_command(self):
        """! Build command to run

             @returns string of the command that will be called
        """
        cmd = self.app_path

        if self.c_dict['USING_BOTH']:
            cmd += f" -both {self.c_dict['BOTH_LIST_PATH']}"
        else:
            cmd += f" -fcst {self.c_dict['FCST_LIST_PATH']}"
            cmd += f" -obs {self.c_dict['OBS_LIST_PATH']}"

        # add output path
        cmd += f' -out {self.get_output_path()}'

        # add arguments
        cmd += ''.join(self.args)

        # add verbosity
        cmd += ' -v ' + self.c_dict['VERBOSITY']
        return cmd

    def _generate_plots(self, fcst_path, time_info, storm_id):
        """! Generate the plots from the series_analysis output.

             @param fcst_path path to forecast file list file
             @param time_info dictionary containing time information
             @param storm_id storm ID to process
        """
        output_dir = os.path.dirname(fcst_path)
        output_filename = os.path.basename(self.c_dict['OUTPUT_TEMPLATE'])
        output_template = os.path.join(output_dir, output_filename)

        for var_info in self.c_dict['VAR_LIST']:
            name = var_info['fcst_name']
            level = var_info['fcst_level']
            self.add_field_info_to_time_info(time_info, var_info)

            # change wildcard storm ID to all_storms
            if storm_id == '*':
                time_info['storm_id'] = 'all_storms'
            else:
                time_info['storm_id'] = storm_id

            # get the output directory where the series_analysis output
            # was written. Plots will be written to the same directory
            plot_input = do_string_sub(output_template,
                                       **time_info)

            # Get the number of forecast tile files and the name of the
            # first and last in the list to be used in the -title
            num, beg, end = self.get_fcst_file_info(fcst_path)
            if num is None:
                self.log_error("Could not get any forecast lead info "
                               f"from {fcst_path}")
                self.logger.debug(f"Skipping plot for {storm_id}")
                continue

            _, nseries = self._get_netcdf_min_max(plot_input,
                                                  'series_cnt_TOTAL')
            nseries_str = '' if nseries is None else f" (N = {nseries})"
            time_info['nseries'] = nseries_str

            # Assemble the input file, output file, field string, and title
            for cur_stat in self.c_dict['STAT_LIST']:
                key = f"{name}_{level}_{cur_stat}"
                if self.c_dict['PNG_FILES'].get(key) is None:
                    self.c_dict['PNG_FILES'][key] = []

                min_value, max_value = (
                    self._get_netcdf_min_max(plot_input,
                                             f'series_cnt_{cur_stat}')
                )
                range_min_max = f"{min_value} {max_value}"

                plot_output = (f"{os.path.splitext(plot_input)[0]}_"
                               f"{cur_stat}.ps")

                time_info['num_leads'] = num
                time_info['fcst_beg'] = beg
                time_info['fcst_end'] = end
                time_info['stat'] = cur_stat
                self.plot_data_plane.c_dict['INPUT_TEMPLATE'] = plot_input
                self.plot_data_plane.c_dict['OUTPUT_TEMPLATE'] = plot_output
                self.plot_data_plane.c_dict['FIELD_NAME'] = f"series_cnt_{cur_stat}"
                self.plot_data_plane.c_dict['FIELD_LEVEL'] = level
                self.plot_data_plane.c_dict['RANGE_MIN_MAX'] = range_min_max
                self.plot_data_plane.run_at_time_once(time_info)
                self.all_commands.extend(self.plot_data_plane.all_commands)
                self.plot_data_plane.all_commands.clear()

                png_filename = f"{os.path.splitext(plot_output)[0]}.png"
                self.c_dict['PNG_FILES'][key].append(png_filename)

    def generate_animations(self):
        """! Use ImageMagick convert to create an animated gif from the png
              images generated from the current run
        """
        success = True

        convert_exe = self.c_dict.get('CONVERT_EXE')
        if not convert_exe:
            self.log_error("[exe] CONVERT not set correctly. Cannot generate"
                           "image file.")
            return False

        animate_dir = os.path.join(self.c_dict['OUTPUT_DIR'],
                                   'series_animate')
        mkdir_p(animate_dir)

        for group, files in self.c_dict['PNG_FILES'].items():
            # write list of files to a text file
            list_file = f'series_animate_{group}_files.txt'
            self.write_list_file(list_file,
                                 files,
                                 output_dir=animate_dir)

            gif_file = f'series_animate_{group}.gif'
            gif_filepath = os.path.join(animate_dir, gif_file)
            convert_command = (f"{convert_exe} -dispose Background -delay 100 "
                               f"{' '.join(files)} {gif_filepath}")
            if not self.run_command(convert_command):
                success = False

        return success

    def get_fcst_file_info(self, fcst_path):
        """! Get the number of all the gridded forecast n x m tile
            files. Determine the filename of the
            first and last files.  This information is used to create
            the title value to the -title opt in plot_data_plane.

            @param fcst_path path to forecast ascii list file to process
            @returns num, beg, end:  A tuple representing the number of
            forecast tile files, and the first and last file. If info cannot
            be parsed, return (None, None, None)
        """
        # read the file but skip the first line because it contains 'file_list'
        with open(fcst_path, 'r') as file_handle:
            files_of_interest = file_handle.readlines()

        if len(files_of_interest) < 2:
            self.log_error(f"No files found in file list: {fcst_path}")
            return None, None, None

        files_of_interest = files_of_interest[1:]
        num = str(len(files_of_interest))

        data_type = 'BOTH' if self.c_dict['USING_BOTH'] else 'FCST'
        template = os.path.join(self.c_dict[f'{data_type}_INPUT_DIR'],
                                self.c_dict[f'{data_type}_INPUT_TEMPLATE'])

        smallest_fcst = 99999999
        largest_fcst = -99999999
        beg = None
        end = None
        for filepath in files_of_interest:
            filepath = filepath.strip()
            file_time_info = parse_template(template,
                                            filepath,
                                            self.logger)
            if not file_time_info:
                continue
            lead = ti_get_seconds_from_lead(file_time_info.get('lead'),
                                            file_time_info.get('valid'))
            if lead < smallest_fcst:
                smallest_fcst = lead
                beg = str(ti_get_hours_from_lead(lead)).zfill(3)
            if lead > largest_fcst:
                largest_fcst = lead
                end = str(ti_get_hours_from_lead(lead)).zfill(3)

        if beg is None or end is None:
            return None, None, None

        return num, beg, end

    @staticmethod
    def _get_netcdf_min_max(filepath, variable_name):
        """! Determine the min and max for all lead times for each
           statistic and variable pairing.

           @param filepath NetCDF file to inspect
           @param variable_name name of variable to read
           @returns tuple containing the minimum and maximum values or
            None, None if something went wrong
        """
        try:
            nc_var = netCDF4.Dataset(filepath).variables[variable_name]
            min_value = nc_var[:].min()
            max_value = nc_var[:].max()
            return min_value, max_value
        except (FileNotFoundError, KeyError):
            return None, None

    def get_formatted_fields(self, var_info, fcst_path, obs_path):
        """! Get forecast and observation field information for var_info and
            format it so it can be passed into the MET config file

            @param var_info dictionary containing info to format
            @returns tuple containing strings of the formatted forecast and
            observation information or None, None if something went wrong
        """
        fcst_field_list = self._get_field_list('fcst', var_info, obs_path)
        obs_field_list = self._get_field_list('obs', var_info, fcst_path)

        if not fcst_field_list or not obs_field_list:
            return None, None

        fcst_fields = ','.join(fcst_field_list)
        obs_fields = ','.join(obs_field_list)

        return fcst_fields, obs_fields

    def _get_field_list(self, data_type, var_info, file_list_path):
        other = 'OBS' if data_type == 'fcst' else 'FCST'
        # check if time filename template tags are used in field level
        if not self._has_time_tag(var_info[f'{data_type}_level']):
            # get field info for a single field to pass to the MET config file
            return self.get_field_info(
                v_level=var_info[f'{data_type}_level'],
                v_thresh=var_info[f'{data_type}_thresh'],
                v_name=var_info[f'{data_type}_name'],
                v_extra=var_info[f'{data_type}_extra'],
                d_type=data_type.upper()
            )

        field_list = []
        # loop through fcst and obs files to extract time info
        template = os.path.join(self.c_dict[f'{other}_INPUT_DIR'],
                                self.c_dict[f'{other}_INPUT_TEMPLATE'])
        # for each file apply time info to field info and add to list
        for file_time_info in self._get_times_from_file_list(file_list_path,
                                                             template):
            level = do_string_sub(var_info[f'{data_type}_level'],
                                  **file_time_info)
            field = self.get_field_info(
                v_level=level,
                v_thresh=var_info[f'{data_type}_thresh'],
                v_name=var_info[f'{data_type}_name'],
                v_extra=var_info[f'{data_type}_extra'],
                d_type=data_type.upper()
            )
            if field:
                field_list.extend(field)

        return field_list

    @staticmethod
    def _has_time_tag(level):
        return any(item in ['init', 'valid', 'lead']
                   for item in get_tags(level))

    @staticmethod
    def _get_times_from_file_list(file_path, template):
        with open(file_path, 'r') as file_handle:
            file_list = file_handle.read().splitlines()[1:]

        for file_name in file_list:
            file_time_info = parse_template(template, file_name)
            if not file_time_info:
                continue
            yield file_time_info
