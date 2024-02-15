"""
Program Name: gfdl_tracker_wrapper.py
Contact(s): George McCabe
Abstract: Builds commands to run GFDL Tracker
History Log:  Initial version
Usage: Not meant to be run
Parameters: None
Input Files: None
Output Files: None
Condition codes: 0 for success, 1 for failure
"""

import os
import shutil
import glob
from dateutil.relativedelta import relativedelta

from ..util import do_string_sub, ti_calculate, get_lead_sequence
from ..util import remove_quotes, parse_template
from . import RuntimeFreqWrapper


class GFDLTrackerWrapper(RuntimeFreqWrapper):
    """!Configures and runs GFDL Tracker"""

    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE', 'RUN_ONCE_PER_INIT_OR_VALID']

    CONFIG_NAMES = {
        "DATEIN_INP_MODEL": "int",
        "DATEIN_INP_MODTYP": "string",
        "DATEIN_INP_LT_UNITS": "string",
        "DATEIN_INP_FILE_SEQ": "string",
        "DATEIN_INP_NESTTYP": "string",
        "ATCFINFO_ATCFNUM": "int",
        "ATCFINFO_ATCFNAME": "string",
        "ATCFINFO_ATCFFREQ": "int",
        "TRACKERINFO_TYPE": "string",
        "TRACKERINFO_MSLPTHRESH": "float",
        "TRACKERINFO_USE_BACKUP_MSLP_GRAD_CHECK": "bool",
        "TRACKERINFO_V850THRESH": "float",
        "TRACKERINFO_USE_BACKUP_850_VT_CHECK": "bool",
        "TRACKERINFO_ENABLE_TIMING": "int",
        "TRACKERINFO_GRIDTYPE": "string",
        "TRACKERINFO_CONTINT": "float",
        "TRACKERINFO_WANT_OCI": "string-no-quotes",
        "TRACKERINFO_OUT_VIT": "bool",
        "TRACKERINFO_USE_LAND_MASK": "bool",
        "TRACKERINFO_INP_DATA_TYPE": "string",
        "TRACKERINFO_GRIBVER": "int",
        "TRACKERINFO_G2_JPDTN": "int",
        "TRACKERINFO_G2_MSLP_PARM_ID": "int",
        "TRACKERINFO_G1_MSLP_PARM_ID": "int",
        "TRACKERINFO_G1_SFCWIND_LEV_TYP": "int",
        "TRACKERINFO_G1_SFCWIND_LEV_VAL": "int",
        "TRACKERINFO_WESTBD": "int",
        "TRACKERINFO_EASTBD": "int",
        "TRACKERINFO_SOUTHBD": "int",
        "TRACKERINFO_NORTHBD": "int",
        "PHASEINFO_PHASEFLAG": "bool",
        "PHASEINFO_PHASESCHEME": "string",
        "PHASEINFO_WCORE_DEPTH": "float",
        "STRUCTINFO_STRUCTFLAG": "bool",
        "STRUCTINFO_IKEFLAG": "bool",
        "FNAMEINFO_GMODNAME": "string",
        "FNAMEINFO_RUNDESCR": "string",
        "FNAMEINFO_ATCFDESCR": "string",
        "WAITINFO_USE_WAITFOR": "bool",
        "WAITINFO_WAIT_MIN_AGE": "int",
        "WAITINFO_WAIT_MIN_SIZE": "int",
        "WAITINFO_WAIT_MAX_WAIT": "int",
        "WAITINFO_WAIT_SLEEPTIME": "int",
        "WAITINFO_USE_PER_FCST_COMMAND": "bool",
        "WAITINFO_PER_FCST_COMMAND": "string",
        "NETCDFINFO_LAT_NAME": "string",
        "NETCDFINFO_LMASKNAME": "string",
        "NETCDFINFO_LON_NAME": "string",
        "NETCDFINFO_MSLPNAME": "string",
        "NETCDFINFO_NETCDF_FILENAME": "string",
        "NETCDFINFO_NUM_NETCDF_VARS": "int",
        "NETCDFINFO_RV700NAME": "string",
        "NETCDFINFO_RV850NAME": "string",
        "NETCDFINFO_TIME_NAME": "string",
        "NETCDFINFO_TIME_UNITS": "string",
        "NETCDFINFO_TMEAN_300_500_NAME": "string",
        "NETCDFINFO_U500NAME": "string",
        "NETCDFINFO_U700NAME": "string",
        "NETCDFINFO_U850NAME": "string",
        "NETCDFINFO_USFCNAME": "string",
        "NETCDFINFO_V500NAME": "string",
        "NETCDFINFO_V700NAME": "string",
        "NETCDFINFO_V850NAME": "string",
        "NETCDFINFO_VSFCNAME": "string",
        "NETCDFINFO_Z200NAME": "string",
        "NETCDFINFO_Z300NAME": "string",
        "NETCDFINFO_Z350NAME": "string",
        "NETCDFINFO_Z400NAME": "string",
        "NETCDFINFO_Z450NAME": "string",
        "NETCDFINFO_Z500NAME": "string",
        "NETCDFINFO_Z550NAME": "string",
        "NETCDFINFO_Z600NAME": "string",
        "NETCDFINFO_Z650NAME": "string",
        "NETCDFINFO_Z700NAME": "string",
        "NETCDFINFO_Z750NAME": "string",
        "NETCDFINFO_Z800NAME": "string",
        "NETCDFINFO_Z850NAME": "string",
        "NETCDFINFO_Z900NAME": "string",
        "USER_WANTS_TO_TRACK_ZETA700": "bool",
        "USER_WANTS_TO_TRACK_WCIRC850": "bool",
        "USER_WANTS_TO_TRACK_WCIRC700": "bool",
        "USER_WANTS_TO_TRACK_GPH850": "bool",
        "USER_WANTS_TO_TRACK_GPH700": "bool",
        "USER_WANTS_TO_TRACK_MSLP": "bool",
        "USER_WANTS_TO_TRACK_WCIRCSFC": "bool",
        "USER_WANTS_TO_TRACK_ZETASFC": "bool",
        "USER_WANTS_TO_TRACK_THICK500850": "bool",
        "USER_WANTS_TO_TRACK_THICK200500": "bool",
        "USER_WANTS_TO_TRACK_THICK200850": "bool",
        "USER_WANTS_TO_TRACK_ZETA850": "bool",
        "VERBOSE_VERB": "int",
        "VERBOSE_VERB_G2": "int",
    }

    def __init__(self, config, instance=None):
        self.app_name = 'gfdl_tracker'
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # get values from config object and set them to be accessed by wrapper
        gfdl_tracker_exec = self.config.getdir('GFDL_TRACKER_EXEC', '')
        if not gfdl_tracker_exec:
            self.log_error('GFDL_TRACKER_EXEC must be set.')
            return c_dict

        c_dict['INPUT_GRIB_VERSION'] = (
            self.config.getint('config', 'GFDL_TRACKER_GRIB_VERSION', '')
        )

        if c_dict['INPUT_GRIB_VERSION'] == 1:
            index_script_name = 'grbindex.exe'
        elif c_dict['INPUT_GRIB_VERSION'] == 2:
            index_script_name = 'grb2index.exe'
        else:
            self.log_error("GFDL_TRACKER_GRIB_VERSION "
                           f"({c_dict['INPUT_GRIB_VERSION']}) "
                           "must be 1 or 2")
            return c_dict

        c_dict['INDEX_APP'] = os.path.join(gfdl_tracker_exec,
                                           index_script_name)

        if not os.path.exists(c_dict['INDEX_APP']):
            self.log_error("GRIB index exe does not exist: "
                           f"{c_dict['INDEX_APP']}")

        c_dict['TRACKER_APP'] = os.path.join(gfdl_tracker_exec,
                                             'gettrk.exe')

        if not os.path.exists(c_dict['TRACKER_APP']):
            self.log_error("GFDL tracker exe does not exist: "
                           f"{c_dict['TRACKER_APP']}")

        c_dict['INPUT_TEMPLATE'] = (
            self.config.getraw('config', 'GFDL_TRACKER_INPUT_TEMPLATE', '')
        )
        c_dict['INPUT_DIR'] = self.config.getdir('GFDL_TRACKER_INPUT_DIR', '')

        c_dict['TC_VITALS_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'GFDL_TRACKER_TC_VITALS_INPUT_TEMPLATE', '')
        )
        c_dict['TC_VITALS_INPUT_DIR'] = (
            self.config.getdir('GFDL_TRACKER_TC_VITALS_INPUT_DIR', '')
        )

        c_dict['NML_TEMPLATE_FILE'] = (
            self.config.getraw('config', 'GFDL_TRACKER_NML_TEMPLATE_FILE', '')
        )
        if not c_dict['NML_TEMPLATE_FILE']:
            self.log_error('Must set GFDL_TRACKER_NML_TEMPLATE_FILE')
        elif not os.path.exists(c_dict['NML_TEMPLATE_FILE']):
            self.log_error("GFDL_TRACKER_NML_TEMPLATE_FILE does not "
                           f"exist: {c_dict['NML_TEMPLATE_FILE']}")

        c_dict['SGV_TEMPLATE_FILE'] = (
            self.config.getraw('config', 'GFDL_TRACKER_SGV_TEMPLATE_FILE', '')
        )

        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'GFDL_TRACKER_OUTPUT_TEMPLATE', '')
        )
        c_dict['OUTPUT_DIR'] = self.config.getdir('GFDL_TRACKER_OUTPUT_DIR',
                                                  '')

        # optional "gen_vitals" file that holds info about known storms
        c_dict['GEN_VITALS_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'GFDL_TRACKER_GEN_VITALS_INPUT_TEMPLATE', '')
        )
        c_dict['GEN_VITALS_INPUT_DIR'] = (
            self.config.getdir('GFDL_TRACKER_GEN_VITALS_INPUT_DIR', '')
        )

        # read config variables
        self._read_gfdl_config_variables(c_dict)

        c_dict['KEEP_INTERMEDIATE'] = (
            self.config.getbool('config',
                                'GFDL_TRACKER_KEEP_INTERMEDIATE',
                                False)
        )

        # allow multiple input files
        c_dict['ALLOW_MULTIPLE_FILES'] = True

        c_dict['FIRST_RUN'] = True

        if not c_dict['INPUT_TEMPLATE']:
            self.log_error('GFDL_TRACKER_INPUT_TEMPLATE must be set')

        if not c_dict['TC_VITALS_INPUT_TEMPLATE']:
            self.log_error('GFDL_TRACKER_TC_VITALS_INPUT_TEMPLATE must be set')

        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error('GFDL_TRACKER_OUTPUT_TEMPLATE must be set')

        if not c_dict['OUTPUT_DIR']:
            self.log_error('GFDL_TRACKER_OUTPUT_DIR must be set')
        # skip RuntimeFreq input file logic - remove once integrated
        c_dict['FIND_FILES'] = False
        # force error if inputs are missing
        c_dict['ALLOW_MISSING_INPUTS'] = False
        return c_dict

    def _read_gfdl_config_variables(self, c_dict):
        for name, input_type in self.CONFIG_NAMES.items():
            if input_type == 'int':
                get_fct = self.config.getint
            elif input_type == 'float':
                get_fct = self.config.getfloat
            elif input_type == 'bool':
                get_fct = self.config.getbool
            else:
                get_fct = self.config.getraw

            value = get_fct('config', f'GFDL_TRACKER_{name}', '')
            c_dict[f'REPLACE_CONF_{name}'] = value

    def run_at_time_once(self, input_dict):
        """! Do some processing for the current run time (init or valid)

        @param input_dict dictionary containing time information of current run
        @returns True if everything was successful, False if not
        """
        # get all input files
        all_input_files = self.get_all_input_files(input_dict)
        if not all_input_files:
            self.log_error("Could not find input files in "
                           f"{self.c_dict['INPUT_DIR']}.")
            return False

        # get TCVitals file
        tc_vitals_file = self.find_data(time_info=input_dict,
                                        data_type='TC_VITALS')
        if not tc_vitals_file:
            self.log_error("TCVitals file not found")
            return False

        # get output path
        if not self.find_and_check_output_file(input_dict):
            return False

        # create sym link to output directory for all files (including tcvit)
        all_output_files, tc_vitals_out = (
            self.link_files_to_output_dir(all_input_files, tc_vitals_file)
        )
        if not all_output_files:
            self.log_error("Could not create symbolic links "
                           "in output directory")
            return False

        # Run grib index application to generate index files
        if not self.run_grib_index(all_output_files):
            return False

        # create empty fort.14 file
        self.create_fort_14_file(tc_vitals_out)

        # create fort.15 file with list of all forecast leads and indices
        lead_minutes = [item.get('lead_minutes') for item in all_input_files]
        self.create_fort_15_file(lead_minutes)

        # if gen_vitals file is specified, copy it to fort.67
        if not self.handle_gen_vitals(input_dict):
            return False

        # substitute values from config into template.nml and
        # write input.nml to output directory
        input_nml_path = self.handle_templates(input_dict)
        if not input_nml_path:
            return False

        # run tracker application from output directory passing in input.nml
        if not self.run_tracker(input_nml_path):
            return False

        # rename fort.64 output file to output filename template
        if not self.rename_fort_to_output_path(input_dict):
            return False

        # check if clean up should be skipped
        if self.c_dict.get('KEEP_INTERMEDIATE', False):
            return True

        # clean up files in output directory that are no longer needed
        self.cleanup_output_dir(all_output_files,
                                tc_vitals_out)

        return True

    def handle_gen_vitals(self, input_dict):
        self.logger.debug("Checking for gen_vitals file")
        # if template not set, do nothing
        template = self.c_dict['GEN_VITALS_INPUT_TEMPLATE']
        if not template:
            self.logger.debug("No gen vitals file specified")
            return True

        # check if file exists
        filedir = self.c_dict['GEN_VITALS_INPUT_DIR']
        src_path = os.path.join(filedir, template)
        src_path = do_string_sub(src_path, **input_dict)
        if not os.path.exists(src_path):
            self.log_error(f"Gen vitals file does not exist: {src_path}")
            return False

        dest_path = os.path.join(self.c_dict['OUTPUT_DIR'],
                                 'tcvit_genesis_storms.txt')
        try:
            shutil.copyfile(src_path, dest_path)
        except (OSError, shutil.SameFileError):
            self.log_error(f"Copy failed: from {src_path} to {dest_path}")
            return False

        self.logger.debug(f"Copied gen vitals file {src_path} to {dest_path}")

        # check if fort.67 already exists in output directory
        # do not copy file if it does
        dest_path = os.path.join(self.c_dict['OUTPUT_DIR'],
                                 'fort.67')
        if os.path.exists(dest_path):
            self.logger.debug(f"Gen vitals file already exists: {dest_path}. "
                              f"Skip copying of {src_path}")
            return True

        try:
            shutil.copyfile(src_path, dest_path)
        except (OSError, shutil.SameFileError):
            self.log_error(f"Copy failed: from {src_path} to {dest_path}")
            return False

        self.logger.debug(f"Copied gen vitals file {src_path} to {dest_path}")
        return True

    def cleanup_output_dir(self, all_output_files, tc_vitals_out):
        for output_file in all_output_files:
            # remove symbolic links for input files
            self._remove_symlink(output_file)

            # remove index files
            index_file = f'{output_file}.ix'
            if os.path.exists(index_file):
                os.remove(index_file)

        # remove TCVitals symbolic link
        self._remove_symlink(tc_vitals_out)

        # remove all fort files
        all_forts = glob.glob(os.path.join(self.c_dict.get('OUTPUT_DIR'),
                                           f'fort.*'))
        for fort_file in all_forts:
            # remove symlink if link, otherwise remove file
            if not self._remove_symlink(fort_file):
                self.logger.debug(f'Removing {fort_file}')
                os.remove(fort_file)

    def get_all_input_files(self, input_dict):
        all_input_files = []

        # get forecast leads to loop over
        lead_seq = get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:

            # set forecast lead time in hours
            input_dict['lead'] = lead

            # recalculate time info items
            time_info = ti_calculate(input_dict)
            input_files = self.find_data(time_info=time_info,
                                         return_list=True)
            if not input_files:
                return None

            # add input files to list unless they are index files (.ix)
            input_files = [input_file for input_file in input_files
                           if not input_file.endswith('.ix')]
            for input_file in input_files:
                file_time_info = self._get_time_info_from_template(input_file)
                if not file_time_info:
                    self.log_error("Could not get time info from file: "
                                   f"{input_file}")
                    continue

                rename = self._get_input_file_rename(file_time_info)
                input_file_dict = {
                    'filepath': input_file,
                    'rename': rename,
                    'lead_minutes': file_time_info.get('lead_minutes'),
                }
                all_input_files.append(input_file_dict)

        return all_input_files

    def _get_time_info_from_template(self, input_file):
        # extract lead time from each file found via wildcard
        template = os.path.join(self.c_dict.get('INPUT_DIR'),
                                self.c_dict.get('INPUT_TEMPLATE'))
        file_time_info = parse_template(template, input_file)
        if not file_time_info:
            return None

        return file_time_info

    def _get_input_file_rename(self, file_time_info):
        gmodname = remove_quotes(self.c_dict[f'REPLACE_CONF_FNAMEINFO_GMODNAME'])
        rundescr = remove_quotes(self.c_dict[f'REPLACE_CONF_FNAMEINFO_RUNDESCR'])
        atcfdescr = remove_quotes(self.c_dict[f'REPLACE_CONF_FNAMEINFO_ATCFDESCR'])
        template = (f"{gmodname}.{rundescr}.{atcfdescr}."
                    "{init?fmt=%Y%m%d%H}.f{lead?fmt=%5M}")
        return do_string_sub(template, **file_time_info)

    def link_files_to_output_dir(self, all_input_files, tc_vitals_src):
        all_output_files = []

        # create symbolic links for input files
        for input_file_dict in all_input_files:
            src_path = input_file_dict.get('filepath')
            dest_path = os.path.join(self.c_dict.get('OUTPUT_DIR'),
                                     input_file_dict.get('rename'))
            self._create_symlink(src_path, dest_path)
            all_output_files.append(dest_path)

        # create symbolic links for TCVitals file
        tc_vitals_dest = os.path.join(self.c_dict.get('OUTPUT_DIR'),
                                      os.path.basename(tc_vitals_src))
        self._create_symlink(tc_vitals_src, tc_vitals_dest)

        return all_output_files, tc_vitals_dest

    def _create_symlink(self, src_path, dest_path):
        self._remove_symlink(dest_path)

        self.logger.debug(f"Creating sym link {dest_path} for {src_path}")
        os.symlink(src_path, dest_path)

    def _remove_symlink(self, link_path):
        if os.path.islink(link_path):
            self.logger.debug(f"Removing existing symbolic link: {link_path}")
            os.unlink(link_path)
            return True

        return False

    def run_grib_index(self, all_output_files):
        index_script = self.c_dict.get('INDEX_APP')
        cmd_name = os.path.basename(index_script)
        for output_file in all_output_files:
            index_file = f'{output_file}.ix'
            command = f'{index_script} {output_file} {index_file}'
            if not self.run_command(command, cmd_name=cmd_name):
                return False

        return True

    def create_fort_14_file(self, tc_vitals_out):
        output_dir = self.c_dict.get('OUTPUT_DIR')
        fort_14_path = os.path.join(output_dir, 'fort.14')

        if os.path.exists(fort_14_path):
            self.logger.debug("Removing existing fort.14 file")
            os.remove(fort_14_path)

        # if running in cyclogenesis mode (tcgen or midlat) use TCVitals
        # file for fort.14
        run_type = remove_quotes(self.c_dict["REPLACE_CONF_TRACKERINFO_TYPE"])
        if run_type == 'tcgen' or run_type == 'midlat':
            self.logger.debug("Linking TCVitals file to fort.14 "
                              "for cyclogenesis run")
            self._create_symlink(tc_vitals_out, fort_14_path)
            return

        # if not, create a blank file
        self.logger.debug(f"Writing blank fort.14 file: {fort_14_path}")
        file_handle = open(fort_14_path, 'w')
        file_handle.close()

    def create_fort_15_file(self, all_lead_minutes):
        # format must match index (starting with 1) taking up 4 characters
        # then forecast lead minutes taking up 5 characters - pad with spaces
        file_lines = []
        output_dir = self.c_dict.get('OUTPUT_DIR')

        for index, lead_minutes in enumerate(all_lead_minutes, start=1):
            file_lines.append(f"{str(index).rjust(4)} {str(lead_minutes).rjust(5)}")

        write_content = '\n'.join(file_lines)

        fort_15_path = os.path.join(output_dir, 'fort.15')
        self.logger.debug(f"Writing fort.15 file: {fort_15_path}")
        with open(fort_15_path, 'w') as file_handle:
            file_handle.write(write_content)

    def handle_templates(self, input_dict):
        template_file = self.c_dict['NML_TEMPLATE_FILE']
        if not template_file:
            return None

        # set up dictionary of text to substitute in XML file
        sub_dict = self.populate_sub_dict(input_dict)

        output_path = os.path.join(self.c_dict.get('OUTPUT_DIR'),
                                   'input.{init?fmt=%Y%m%d%H%M}.nml')
        output_path = do_string_sub(output_path, **input_dict)

        # open template file and replace any values encountered
        self.logger.debug(f"Reading nml template: {template_file}")
        self.sub_template(template_file, output_path, sub_dict)

        # only fill out sgv template file if template is specified
        # and on a 0Z run that is not the first run time
        first_run = self.c_dict['FIRST_RUN']
        self.c_dict['FIRST_RUN'] = False
        if (not self.c_dict['SGV_TEMPLATE_FILE'] or first_run or
                input_dict['init'].strftime('%H') != '00'):
            return output_path

        sgv_template_file = self.c_dict['SGV_TEMPLATE_FILE']
        sgv_output_path = os.path.join(self.c_dict.get('OUTPUT_DIR'),
                                       'sgv.{init?fmt=%Y%m%d%H%M}.txt')
        sgv_output_path = do_string_sub(sgv_output_path, **input_dict)
        self.sub_template(sgv_template_file, sgv_output_path, sub_dict)

        return output_path

    def sub_template(self, template_file, output_path, sub_dict):
        with open(template_file, 'r') as file_handle:
            input_lines = file_handle.read().splitlines()

        output_lines = []
        for input_line in input_lines:
            output_line = input_line
            for replace_string, value in sub_dict.items():
                output_line = output_line.replace(f"${{{replace_string}}}",
                                                  value)
            output_lines.append(output_line)

        # write tmp file with XML content with substituted values
        self.logger.debug(f"Writing file: {output_path}")
        with open(output_path, 'w') as file_handle:
            for line in output_lines:
                file_handle.write(f'{line}\n')

    def populate_sub_dict(self, time_info):
        sub_dict = {}

        for name, input_type in self.CONFIG_NAMES.items():
            value = self.c_dict.get(f'REPLACE_CONF_{name}')
            if input_type == 'bool':
                value = '"y"' if value else '"n"'
            elif input_type == 'int' or input_type == 'float':
                value = str(value)
            else:
                value = remove_quotes(value)
                if 'no-quotes' not in input_type:
                    value = f'"{value}"'

            value = do_string_sub(value,
                                  **time_info)

            sub_dict[f'METPLUS_{name}'] = value

        # set replacement variables for time information
        init_ymdh = time_info['init'].strftime('%Y%m%d%H')
        sub_dict['METPLUS_DATEIN_INP_BCC'] = init_ymdh[0:2]
        sub_dict['METPLUS_DATEIN_INP_BYY'] = init_ymdh[2:4]
        sub_dict['METPLUS_DATEIN_INP_BMM'] = init_ymdh[4:6]
        sub_dict['METPLUS_DATEIN_INP_BDD'] = init_ymdh[6:8]
        sub_dict['METPLUS_DATEIN_INP_BHH'] = init_ymdh[8:10]
        sub_dict['METPLUS_ATCFINFO_ATCFYMDH'] = init_ymdh

        sub_dict['METPLUS_DATENOW_YY'] = init_ymdh[0:4]
        sub_dict['METPLUS_DATENOW_MM'] = init_ymdh[4:6]
        sub_dict['METPLUS_DATENOW_DD'] = init_ymdh[6:8]
        sub_dict['METPLUS_DATENOW_HH'] = init_ymdh[8:10]

        init_6ago = time_info['init'] - relativedelta(hours=6)
        init_6ago = init_6ago.strftime('%Y%m%d%H')
        sub_dict['METPLUS_DATE6AGO_YY'] = init_6ago[0:4]
        sub_dict['METPLUS_DATE6AGO_MM'] = init_6ago[4:6]
        sub_dict['METPLUS_DATE6AGO_DD'] = init_6ago[6:8]
        sub_dict['METPLUS_DATE6AGO_HH'] = init_6ago[8:10]

        init_6ahead = time_info['init'] + relativedelta(hours=6)
        init_6ahead = init_6ahead.strftime('%Y%m%d%H')
        sub_dict['METPLUS_DATE6AHEAD_YY'] = init_6ahead[0:4]
        sub_dict['METPLUS_DATE6AHEAD_MM'] = init_6ahead[4:6]
        sub_dict['METPLUS_DATE6AHEAD_DD'] = init_6ahead[6:8]
        sub_dict['METPLUS_DATE6AHEAD_HH'] = init_6ahead[8:10]

        return sub_dict

    def run_tracker(self, input_nml_path):
        output_dir = self.c_dict.get('OUTPUT_DIR')
        command = (f"cd {output_dir}; "
                   f"{self.c_dict['TRACKER_APP']} "
                   f"< {os.path.basename(input_nml_path)}; "
                   f"ret=$?; "
                   f"cd -; "
                   f"if [ $ret != 0 ]; then false; fi")
        return self.run_command(command)

    def rename_fort_to_output_path(self, time_info):
        output_dir = self.c_dict.get('OUTPUT_DIR')

        run_type = remove_quotes(self.c_dict["REPLACE_CONF_TRACKERINFO_TYPE"])
        if run_type == 'tcgen' or run_type == 'midlat':
            fort_file = 'fort.66'
        else:
            fort_file = 'fort.64'

        # check that fort.64 file was created successfully
        fort_path = os.path.join(output_dir, fort_file)
        if not os.path.exists(fort_path):
            self.log_error(f"Could not find output file: {fort_path}")
            return False

        output_path = os.path.join(output_dir,
                                   self.c_dict.get('OUTPUT_TEMPLATE'))
        output_path = do_string_sub(output_path, **time_info)

        # copy fort.64/66 file to new file name
        self.logger.debug(f"Copying {fort_file} file to: {output_path}")
        try:
            shutil.copyfile(fort_path, output_path)
        except OSError as err:
            self.log_error(f"Could not copy file: {err}")
            return False

        return True
