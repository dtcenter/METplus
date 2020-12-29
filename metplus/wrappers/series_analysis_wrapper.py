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

import errno
import os
import re
import sys
from datetime import datetime

# handle if module can't be loaded to run wrapper
wrapper_cannot_run = False
exception_err = ''
try:
    import netCDF4
except Exception as err_msg:
    wrapper_cannot_run = True
    exception_err = err_msg

from ..util import met_util as util
from ..util import ti_calculate, do_string_sub, parse_template
from ..util import get_lead_sequence, get_lead_sequence_groups, set_input_dict
from ..util import ti_get_hours_from_lead, ti_get_seconds_from_lead
from ..util import ti_get_lead_string
from .plot_data_plane_wrapper import PlotDataPlaneWrapper
from . import RuntimeFreqWrapper

class SeriesAnalysisWrapper(RuntimeFreqWrapper):
    """!  Performs series analysis with filtering options
    """

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'series_analysis'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)

        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

        # override log name
        self.log_name = 'series_analysis'

        if self.c_dict['GENERATE_PLOTS']:
            self.plot_data_plane = self.plot_data_plane_init()

        if wrapper_cannot_run:
            self.log_error("There was a problem importing modules: "
                           f"{exception_err}\n")

        self.logger.debug("Initialized SeriesAnalysisWrapper")

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        c_dict['VERBOSITY'] = (
            self.config.getstr('config',
                               'LOG_SERIES_ANALYSIS_VERBOSITY',
                               c_dict['VERBOSITY'])
        )

        self.set_c_dict_string(c_dict,
                               'MODEL',
                               'model')
        self.set_c_dict_string(c_dict,
                               'OBTYPE',
                               'obtype')
        self.set_c_dict_string(c_dict,
                               'SERIES_ANALYSIS_DESCRIPTION',
                               'desc')

        self.handle_c_dict_regrid(c_dict, set_to_grid=True)

        self.set_c_dict_list(c_dict,
                            'SERIES_ANALYSIS_CAT_THRESH',
                            'cat_thresh',
                            remove_quotes=True)

        self.set_c_dict_float(c_dict,
                              'SERIES_ANALYSIS_VLD_THRESH',
                              'vld_thresh')

        self.set_c_dict_string(c_dict,
                               'SERIES_ANALYSIS_BLOCK_SIZE',
                               'block_size',
                               remove_quotes=True)

        # get stat list to loop over
        c_dict['STAT_LIST'] = util.getlist(
            self.config.getstr('config',
                               'SERIES_ANALYSIS_STAT_LIST',
                               '')
        )
        if not c_dict['STAT_LIST']:
            self.log_error("Must set SERIES_ANALYSIS_STAT_LIST to run.")

        # set stat list to set output_stats.cnt in MET config file
        self.set_c_dict_list(c_dict,
                             'SERIES_ANALYSIS_STAT_LIST',
                             'cnt',
                             'OUTPUT_STATS_CNT')

        # set cts list to set output_stats.cts in MET config file
        self.set_c_dict_list(c_dict,
                             'SERIES_ANALYSIS_CTS_LIST',
                             'cts',
                             'OUTPUT_STATS_CTS')

        c_dict['PAIRED'] = self.config.getbool('config',
                                               'SERIES_ANALYSIS_IS_PAIRED',
                                               False)

        # get input dir, template, and datatype for FCST, OBS, and BOTH
        for data_type in ('FCST', 'OBS', 'BOTH'):
            c_dict[f'{data_type}_INPUT_DIR'] = \
              self.config.getdir(f'{data_type}_SERIES_ANALYSIS_INPUT_DIR', '')
            c_dict[f'{data_type}_INPUT_TEMPLATE'] = \
              self.config.getraw('filename_templates',
                                 f'{data_type}_SERIES_ANALYSIS_INPUT_TEMPLATE',
                                 '')

            c_dict[f'{data_type}_INPUT_DATATYPE'] = \
              self.config.getstr('config', f'{data_type}_SERIES_ANALYSIS_INPUT_DATATYPE', '')

            # initialize list path to None for each type
            c_dict[f'{data_type}_LIST_PATH'] = None

        # if BOTH is set, neither FCST or OBS can be set
        c_dict['USING_BOTH'] = False
        if c_dict['BOTH_INPUT_TEMPLATE']:
            if c_dict['FCST_INPUT_TEMPLATE'] or c_dict['OBS_INPUT_TEMPLATE']:
                self.log_error("Cannot set FCST_SERIES_ANALYSIS_INPUT_TEMPLATE or "
                               "OBS_SERIES_ANALYSIS_INPUT_TEMPLATE "
                               "if BOTH_SERIES_ANALYSIS_INPUT_TEMPLATE is set.")

            c_dict['USING_BOTH'] = True

            # set *_WINDOW_* variables for BOTH (used in CommandBuilder.find_data function)
            self.handle_window_variables(c_dict, 'series_analysis', dtypes=['BOTH'])

        # if BOTH is not set, both FCST or OBS must be set
        else:
            if not c_dict['FCST_INPUT_TEMPLATE'] or not c_dict['OBS_INPUT_TEMPLATE']:
                self.log_error("Must either set BOTH_SERIES_ANALYSIS_INPUT_TEMPLATE or both "
                               "FCST_SERIES_ANALYSIS_INPUT_TEMPLATE and "
                               "OBS_SERIES_ANALYSIS_INPUT_TEMPLATE to run "
                               "SeriesAnalysis wrapper.")

            # set *_WINDOW_* variables for FCST and OBS
            self.handle_window_variables(c_dict, 'series_analysis', dtypes=['FCST', 'OBS'])

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

        c_dict['FCST_TILE_PREFIX'] = self.config.getstr('config',
                                              'FCST_EXTRACT_TILES_PREFIX',
                                              '')

        c_dict['ANLY_TILE_PREFIX'] = self.config.getstr('config',
                                              'OBS_EXTRACT_TILES_PREFIX',
                                              '')

        c_dict['CONFIG_FILE'] = (
            self.config.getraw('config',
                               'SERIES_ANALYSIS_CONFIG_FILE')
        )
        if not c_dict['CONFIG_FILE']:
            self.log_error("SERIES_ANALYSIS_CONFIG_FILE must be set")

        c_dict['BACKGROUND_MAP'] = (
            self.config.getbool('config',
                                'SERIES_ANALYSIS_BACKGROUND_MAP',
                                False)
        )

        c_dict['VAR_LIST'] = util.parse_var_list(self.config,
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
        self.read_climo_wrapper_specific('SERIES_ANALYSIS', c_dict)

        # if no forecast lead sequence is specified,
        # use wildcard (*) so all leads are used
        c_dict['WILDCARD_LEAD_IF_EMPTY'] = True

        # allow multiple files so wildcards can be used to get input files
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        return c_dict

    def plot_data_plane_init(self):
        # set values to allow successful initialization of PlotDataPlaneWrapper
        plot_overrides = {'PLOT_DATA_PLANE_INPUT_TEMPLATE': 'template',
                          'PLOT_DATA_PLANE_OUTPUT_TEMPLATE': 'template',
                          'PLOT_DATA_PLANE_FIELD_NAME': 'field_name',
                          'PLOT_DATA_PLANE_CONVERT_TO_IMAGE': True,
                          }

        if not self.c_dict['BACKGROUND_MAP']:
            plot_overrides['PLOT_DATA_PLANE_FIELD_EXTRA'] = (
                "map_data={ source=[];}"
            )

        pdp_wrapper = PlotDataPlaneWrapper(self.config,
                                           config_overrides=plot_overrides)
        return pdp_wrapper

    def clear(self):
        super().clear()
        for data_type in ('FCST', 'OBS', 'BOTH'):
            self.c_dict[f'{data_type}_LIST_PATH'] = None

    def run_all_times(self):
        super().run_all_times()

        if self.c_dict['GENERATE_ANIMATIONS']:
            self.generate_animations()

        return self.all_commands

    def run_once_per_lead(self, custom):
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
            input_dict = set_input_dict(loop_time=None,
                                        config=self.config,
                                        use_init=None,
                                        instance=self.instance,
                                        custom=custom)

            input_dict['init'] = '*'
            input_dict['valid'] = '*'
            lead_hours = [ti_get_lead_string(item, plural=False) for
                          item in lead_group[1]]

            self.logger.debug(f"Processing {lead_group[0]} - forecast leads: "
                              f"{', '.join(lead_hours)}")
            if not self.run_at_time_once(input_dict, lead_group):
                success = False

        return success

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
            # Create FCST and ANLY ASCII files
            fcst_path, obs_path = (
                self.create_ascii_storm_files_list(time_info,
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
                 self.generate_plots(fcst_path,
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
        storm_list = util.get_storm_ids(filter_file, self.logger)
        if not storm_list:
            # No storms for this init time, check next init time in list
            self.logger.debug(f"No storms found for current runtime")
            return None

        return storm_list

    def get_files_from_time(self, time_info):
        """! Create dictionary containing time information (key time_info) and
             any relevant files for that runtime. The parent implementation of
             this function creates a dictionary and adds the time_info to it.
             This wrapper gets all files for the current runtime and adds it to
             the dictionary with keys 'fcst' and 'anly'

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
                anly_files = fcst_files
            else:
                fcst_files = self.find_input_files(time_info, 'FCST')
                anly_files = self.find_input_files(time_info, 'OBS')

            if fcst_files is None or anly_files is None:
                return None

            file_dict['fcst'] = fcst_files
            file_dict['anly'] = anly_files
            file_dict_list.append(file_dict)

        return file_dict_list

    def find_input_files(self, time_info, data_type):
        """! Loop over list of input templates and find files for each

             @param time_info time dictionary to use for string substitution
             @returns Input file list if all files were found, None if not.
        """
        input_files = self.find_data(time_info,
                                     return_list=True,
                                     data_type=data_type)
        return input_files

    def subset_input_files(self, time_info):
        """! Obtain a subset of input files from the c_dict ALL_FILES based on
             the time information for the current run.

              @param time_info dictionary containing time information
              @returns the path to a ascii file containing the list of files
               or None if could not find any files
        """
        fcst_files = []
        anly_files = []
        for file_dict in self.c_dict['ALL_FILES']:
            # compare time information for each input file
            # add file to list of files to use if it matches
            if not self.compare_time_info(time_info, file_dict['time_info']):
                continue

            fcst_files.extend(file_dict['fcst'])
            anly_files.extend(file_dict['anly'])

        return fcst_files, anly_files

    def compare_time_info(self, runtime, filetime):
        if not super().compare_time_info(runtime, filetime):
            return False

        # compare storm_id
        if runtime['storm_id'] == '*':
            return True

        return bool(filetime['storm_id'] == runtime['storm_id'])

    def create_ascii_storm_files_list(self, time_info, storm_id, lead_group):
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
        time_info['storm_id'] = storm_id
        all_fcst_files = []
        all_anly_files = []
        if not lead_group:
            fcst_files, anly_files = self.subset_input_files(time_info)
            if not fcst_files or not anly_files:
                return None, None
            all_fcst_files.extend(fcst_files)
            all_anly_files.extend(anly_files)
            label = ''
            leads = None
        else:
            label = lead_group[0]
            leads = lead_group[1]
            for lead in leads:
                time_info['lead'] = lead
                fcst_files, anly_files = self.subset_input_files(time_info)
                if fcst_files and anly_files:
                    all_fcst_files.extend(fcst_files)
                    all_anly_files.extend(anly_files)

        # skip if no files were found
        if not all_fcst_files or not all_anly_files:
            return None, None

        output_dir = self.get_output_dir(time_info, storm_id, label)

        if not self.check_python_embedding():
            return None, None

        # create forecast (or both) file list
        if self.c_dict['USING_BOTH']:
            data_type = 'BOTH'
        else:
            data_type = 'FCST'
        fcst_ascii_filename = self.get_ascii_filename(data_type,
                                                      storm_id,
                                                      leads)
        self.write_list_file(fcst_ascii_filename,
                             all_fcst_files,
                             output_dir=output_dir)

        fcst_path = os.path.join(output_dir, fcst_ascii_filename)

        if self.c_dict['USING_BOTH']:
            return fcst_path, fcst_path

        # create analysis file list
        anly_ascii_filename = self.get_ascii_filename('ANLY',
                                                      storm_id,
                                                      leads)
        self.write_list_file(anly_ascii_filename,
                             all_anly_files,
                             output_dir=output_dir)

        obs_path = os.path.join(output_dir, anly_ascii_filename)

        return fcst_path, obs_path

    def check_python_embedding(self):
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

    def get_ascii_filename(self, data_type, storm_id, leads):
        prefix = f"{data_type}_FILES"

        # of storm ID is set (not wildcard), then add it to filename
        if storm_id == '*':
            filename = ''
        else:
            filename = f"_{storm_id}"

        # add forecast leads if specified
        if leads is not None:
            lead_hours_list = []
            for lead in leads:
                lead_hours = ti_get_hours_from_lead(lead)
                if lead_hours is None:
                    lead_hours = ti_get_lead_string(lead,
                                                    letter_only=True)
                lead_hours_list.append(lead_hours)

            # get first forecast lead, convert to hours, and add to filename
            lead_hours = min(lead_hours_list)

            lead_str = str(lead_hours).zfill(3)
            filename += f"_F{lead_str}"

            # if list of forecast leads, get min and max and add them to name
            if len(lead_hours_list) > 1:
                max_lead_hours = max(lead_hours_list)
                max_lead_str = str(max_lead_hours).zfill(3)
                filename += f"_F{max_lead_str}"

        ascii_filename = f"{prefix}{filename}"
        return ascii_filename

    def get_output_dir(self, time_info, storm_id, label):
        output_dir_template = os.path.join(self.c_dict['OUTPUT_DIR'],
                                           self.c_dict['OUTPUT_TEMPLATE'])
        output_dir_template = os.path.dirname(output_dir_template)
        if storm_id == '*':
            storm_id_out = 'all_storms'
        else:
            storm_id_out = storm_id

        # get output directory including storm ID and label
        time_info['storm_id'] = storm_id_out
        time_info['label'] = label
        output_dir = do_string_sub(output_dir_template,
                                   **time_info)
        return output_dir

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

        num, beg, end = self.get_fcst_file_info(fcst_path, time_info)
        if num is None:
            self.logger.debug(f"Could not get fcst_beg and fcst_end values. "
                              "Those values cannot be used in filename "
                              "templates")

        time_info['fcst_beg'] = beg
        time_info['fcst_end'] = end

        self.handle_climo(time_info)

        # build the command and run series_analysis for each variable
        for var_info in self.c_dict['VAR_LIST']:
            if self.c_dict['USING_BOTH']:
                self.c_dict['BOTH_LIST_PATH'] = fcst_path
            else:
                self.c_dict['FCST_LIST_PATH'] = fcst_path
                self.c_dict['OBS_LIST_PATH'] = obs_path
            self.add_field_info_to_time_info(time_info, var_info)

            # get formatted field dictionary to pass into the MET config file
            fcst_field, obs_field = self.get_formatted_fields(var_info)

            self.set_environment_variables(time_info, fcst_field, obs_field)

            self.set_command_line_arguments(time_info)

            self.find_and_check_output_file(time_info)

            if not self.build():
                success = False

            self.clear()

        return success

    def set_environment_variables(self, time_info, fcst_field, obs_field):
        """! Set the env variables based on settings in the METplus config
             files.

             @param time_info dictionary containing time information
             @param fcst_field formatted forecast field information
             @param obs_field formatted observation field information
        """
        self.logger.info('Setting env variables from config file...')

        # Set all the environment variables that are needed by the
        # MET config file.
        # Set up the environment variable to be used in the Series Analysis
        self.add_env_var("FCST_FILE_TYPE", self.c_dict.get('FCST_FILE_TYPE',
                                                           ''))
        self.add_env_var("OBS_FILE_TYPE", self.c_dict.get('OBS_FILE_TYPE',
                                                          ''))

        self.add_env_var('STAT_LIST', self.c_dict.get('OUTPUT_STATS_CNT', ''))
        self.add_env_var('CTS_LIST', self.c_dict.get('OUTPUT_STATS_CTS', ''))

        self.add_env_var('MODEL', self.c_dict.get('MODEL', ''))
        self.add_env_var("OBTYPE", self.c_dict.get('OBTYPE', ''))
        self.add_env_var("DESC", self.c_dict.get('DESC', ''))
        self.add_env_var("CAT_THRESH", self.c_dict.get('CAT_THRESH', ''))
        self.add_env_var("VLD_THRESH", self.c_dict.get('VLD_THRESH', ''))
        self.add_env_var("BLOCK_SIZE", self.c_dict.get('BLOCK_SIZE', ''))
        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)

        # set climatology environment variables
        self.set_climo_env_vars()

        self.set_regrid_dict()

        super().set_environment_variables(time_info)

    def set_command_line_arguments(self, time_info):
        # add input data format if set
        if self.c_dict['PAIRED']:
            self.args.append(" -paired")

        # add config file - passing through do_string_sub
        # to get custom string if set
        config_file = do_string_sub(self.c_dict['CONFIG_FILE'],
                                    **time_info)
        self.args.append(f" -config {config_file}")

    def get_command(self):
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

    def generate_plots(self, fcst_path, time_info, storm_id):
        """! Generate the plots from the series_analysis output.

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
            num, beg, end = self.get_fcst_file_info(fcst_path, time_info)
            if num is None:
                self.log_error("Could not get any forecast lead info "
                               f"from {fcst_path}")
                self.logger.debug(f"Skipping plot for {storm_id}")
                continue

            _, nseries = self.get_netcdf_min_max(plot_input,
                                                 'series_cnt_TOTAL')
            nseries_str = '' if nseries is None else f" (N = {nseries})"
            time_info['nseries'] = nseries_str

            # Assemble the input file, output file, field string, and title
            for cur_stat in self.c_dict['STAT_LIST']:
                key = f"{name}_{level}_{cur_stat}"
                if self.c_dict['PNG_FILES'].get(key) is None:
                    self.c_dict['PNG_FILES'][key] = []

                min, max = self.get_netcdf_min_max(plot_input,
                                                   f'series_cnt_{cur_stat}')
                range_min_max = f"{min} {max}"

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
        success = True

        convert_exe = self.c_dict.get('CONVERT_EXE')
        if not convert_exe:
            self.log_error("[exe] CONVERT not set correctly. Cannot generate"
                           "image file.")
            return False

        animate_dir = os.path.join(self.c_dict['OUTPUT_DIR'],
                                   'series_animate')
        if not os.path.exists(animate_dir):
            os.makedirs(animate_dir)

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

        if self.c_dict['USING_BOTH']:
            input_dir = self.c_dict['BOTH_INPUT_DIR']
            input_template = self.c_dict['BOTH_INPUT_TEMPLATE']
        else:
            input_dir = self.c_dict['FCST_INPUT_DIR']
            input_template = self.c_dict['FCST_INPUT_TEMPLATE']

        full_template = os.path.join(input_dir, input_template)

        smallest_fcst = 99999999
        largest_fcst = -99999999
        beg = None
        end = None
        for filepath in files_of_interest:
            filepath = filepath.strip()
            file_time_info = parse_template(full_template,
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

    def get_netcdf_min_max(self, filepath, variable_name):
        """! Determine the min and max for all lead times for each
           statistic and variable pairing.

           @param filepath NetCDF file to inspect
           @param variable_name name of variable to read
           @returns tuple containing the minimum and maximum values or
            None, None if something went wrong
        """
        try:
            nc_var = netCDF4.Dataset(filepath).variables[variable_name]
            min = nc_var[:].min()
            max = nc_var[:].max()
            return min, max
        except (FileNotFoundError, KeyError):
            return None, None

    def get_formatted_fields(self, var_info):
        # get field info field a single field to pass to the MET config file
        fcst_field_list = self.get_field_info(v_level=var_info['fcst_level'],
                                              v_thresh=var_info['fcst_thresh'],
                                              v_name=var_info['fcst_name'],
                                              v_extra=var_info['fcst_extra'],
                                              d_type='FCST')

        obs_field_list = self.get_field_info(v_level=var_info['obs_level'],
                                             v_thresh=var_info['obs_thresh'],
                                             v_name=var_info['obs_name'],
                                             v_extra=var_info['obs_extra'],
                                             d_type='OBS')

        if fcst_field_list is None or obs_field_list is None:
            return

        fcst_fields = ','.join(fcst_field_list)
        obs_fields = ','.join(obs_field_list)

        return fcst_fields, obs_fields
