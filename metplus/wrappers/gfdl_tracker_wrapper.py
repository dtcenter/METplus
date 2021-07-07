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

from ..util import do_string_sub, ti_calculate, get_lead_sequence
from . import CommandBuilder

class GFDLTrackerWrapper(CommandBuilder):
    """!Configures and runs GFDL Tracker"""

    CONFIG_NAMES = {
        '': '',
    }

    def __init__(self, config, instance=None, config_overrides={}):
        self.app_name = 'gfdl_tracker'
        super().__init__(config,
                         instance=instance,
                         config_overrides=config_overrides)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # get values from config object and set them to be accessed by wrapper
        gfdl_tracker_base = self.config.getdir('GFDL_TRACKER_BASE', '')
        if not gfdl_tracker_base:
            self.log_error('GFDL_TRACKER_BASE must be set.')
            return c_dict

        c_dict['INPUT_GRIB_VERSION'] = self.config.getint('config',
                                                          'GFDL_TRACKER_GRIB_VERSION',
                                                          '')

        if c_dict['INPUT_GRIB_VERSION'] == 1:
            index_script_name = 'grbindex.exe'
        elif c_dict['INPUT_GRIB_VERSION'] == 2:
            index_script_name = 'grb2index.exe'
        else:
            self.log_error("GFDL_TRACKER_GRIB_VERSION "
                           f"({c_dict['INPUT_GRIB_VERSION']}) "
                           "must be 1 or 2")
            return c_dict

        c_dict['INDEX_APP'] = os.path.join(gfdl_tracker_base,
                                              'trk_exec',
                                              index_script_name)

        if not os.path.exists(c_dict['INDEX_APP']):
            self.log_error("GRIB index exe does not exist: "
                           f"{c_dict['INDEX_APP']}")

        c_dict['TRACKER_APP'] = os.path.join(gfdl_tracker_base,
                                              'trk_exec',
                                              'gettrk.exe')

        if not os.path.exists(c_dict['TRACKER_APP']):
            self.log_error("GFDL tracker exe does not exist: "
                           f"{c_dict['TRACKER_APP']}")

        c_dict['INPUT_TEMPLATE'] = self.config.getraw('config',
                                                      'GFDL_TRACKER_INPUT_TEMPLATE', '')
        c_dict['INPUT_DIR'] = self.config.getdir('GFDL_TRACKER_INPUT_DIR', '')

        c_dict['TC_VITALS_INPUT_TEMPLATE'] = (
            self.config.getraw('config',
                               'GFDL_TRACKER_TC_VITALS_INPUT_TEMPLATE', '')
        )
        c_dict['TC_VITALS_INPUT_DIR'] = (
            self.config.getdir('GFDL_TRACKER_TC_VITALS_INPUT_DIR', '')
        )

        c_dict['NML_TEMPLATE_FILE'] = self.config.getraw('config',
                                                         'GFDL_TRACKER_NML_TEMPLATE_FILE')
        if not c_dict['NML_TEMPLATE_FILE']:
            self.log_error('Must set GFDL_TRACKER_NML_TEMPLATE_FILE')
        elif not os.path.exists(c_dict['NML_TEMPLATE_FILE']):
            self.log_error("GFDL_TRACKER_NML_TEMPLATE_FILE does not "
                           f"exist: {c_dict['NML_TEMPLATE_FILE']}")

        c_dict['OUTPUT_TEMPLATE'] = self.config.getraw('config',
                                                       'GFDL_TRACKER_OUTPUT_TEMPLATE', '')
        c_dict['OUTPUT_DIR'] = self.config.getdir('GFDL_TRACKER_OUTPUT_DIR', '')

        if not c_dict['INPUT_TEMPLATE']:
            self.log_error('GFDL_TRACKER_INPUT_TEMPLATE must be set. ')

        if not c_dict['TC_VITALS_INPUT_TEMPLATE']:
            self.log_error('GFDL_TRACKER_TC_VITALS_INPUT_TEMPLATE must be set. ')

        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error('GFDL_TRACKER_OUTPUT_TEMPLATE must be set. ')

        if not c_dict['OUTPUT_DIR']:
            self.log_error('GFDL_TRACKER_OUTPUT_DIR must be set. ')

        return c_dict

    def run_at_time(self, input_dict):
        """! Do some processing for the current run time (init or valid)
              Args:
                @param input_dict dictionary containing time information of current run
                        generally contains 'now' (current) time and 'init' or 'valid' time
        """
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string
            self.run_at_time_once(input_dict)

    def run_at_time_once(self, input_dict):
        """! Do some processing for the current run time (init or valid)
              Args:
                @param input_dict dictionary containing time information of current run
                        generally contains 'now' (current) time and 'init' or 'valid' time
        """
        # get all input files
        all_input_files, all_lead_minutes = self.get_all_input_files(input_dict)
        if not all_input_files:
            self.log_error("No input files found")
            return False

        # get TCVitals file
        tc_vitals_file = self.find_data(time_info=input_dict,
                                        data_type='TC_VITALS')
        if not tc_vitals_file:
            self.log_error("TCVitals file not found")
            return False

        # create output directory if it doesn't exist
        output_dir = self.c_dict.get('OUTPUT_DIR')
        if not os.path.exists(output_dir):
            self.logger.debug(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir)

        # create symbolic link to output directory for all files (including tcvit)
        all_output_files = self.link_files_to_output_dir(output_dir,
                                                         all_input_files,
                                                         tc_vitals_file)
        if not all_output_files:
            self.log_error("Could not create symbolic links in output directory")
            return False

        # Run grib index application to generate index files
        if not self.run_grib_index(all_output_files):
            return False

        # create empty fort.14 file
        self.create_fort_14_file(output_dir)

        # create fort.15 file with list of all forecast leads and indices
        self.create_fort_15_file(output_dir, all_lead_minutes)

        # substitute values from config into template.nml and write input.nml to output dir
        if not self.fill_output_nml_template(output_dir):
            return False

        # run tracker application from output directory passing in input.nml
        if not self.run_tracker(output_dir):
            return False

        # rename fort.64 output file to output filename template

        return True

    def get_all_input_files(self, input_dict):
        all_input_files = []
        all_lead_minutes = []

        # get forecast leads to loop over
        lead_seq = get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:

            # set forecast lead time in hours
            input_dict['lead'] = lead

            # recalculate time info items
            time_info = ti_calculate(input_dict)
            input_files = self.find_data(time_info=time_info,
                                         return_list=True)
            all_input_files.extend(input_files)

            all_lead_minutes.append(time_info.get('lead_minutes'))

        return all_input_files, sorted(all_lead_minutes)

    def link_files_to_output_dir(self, output_dir, all_input_files, tc_vitals_file):
        all_output_files = []

        # create symbolic links for input files
        for src_path in all_input_files:
            dest_path = self._create_symlink(src_path, output_dir)
            all_output_files.append(dest_path)

        # create symbolic links for TCVitals file
        self._create_symlink(tc_vitals_file, output_dir)

        return all_output_files

    def _create_symlink(self, src_path, output_dir):
        src_file = os.path.basename(src_path)
        dest_path = os.path.join(output_dir, src_file)

        if os.path.islink(dest_path):
            self.logger.debug(f"Removing existing symbolic link: {dest_path}")
            os.unlink(dest_path)

        self.logger.debug(f"Creating symbolic link in {output_dir} for {src_file}")
        os.symlink(src_path, dest_path)

        return dest_path

    def run_grib_index(self, all_output_files):
        index_script = self.c_dict.get('INDEX_APP')
        cmd_name = os.path.basename(index_script)
        for output_file in all_output_files:
            index_file = f'{output_file}.ix'
            command = f'{index_script} {output_file} {index_file}'
            if not self.run_command(command, cmd_name=cmd_name):
                return False

        return True

    def create_fort_14_file(self, output_dir):
        fort_14_path = os.path.join(output_dir, 'fort.14')
        self.logger.debug(f"Writing fort.14 file: {fort_14_path}")
        with open(fort_14_path, 'w') as file_handle:
            pass

    def create_fort_15_file(self, output_dir, all_lead_minutes):
        # format must match index (starting with 1) taking up 4 characters
        # then forecast lead minutes taking up 5 characters - pad with spaces
        file_lines = []

        for index, lead_minutes in enumerate(all_lead_minutes, start=1):
            file_lines.append(f"{str(index).rjust(4)} {str(lead_minutes).rjust(5)}")

        write_content = '\n'.join(file_lines)

        fort_15_path = os.path.join(output_dir, 'fort.15')
        self.logger.debug(f"Writing fort.15 file: {fort_15_path}")
        with open(fort_15_path, 'w') as file_handle:
            file_handle.write(write_content)

    def fill_output_nml_template(self, output_dir):
        template_file = self.c_dict['NML_TEMPLATE_FILE']
        if not template_file:
            return False

        # set up dictionary of text to substitute in XML file
#        sub_dict = self.populate_sub_dict(time_info)

        # open template file and replace any values encountered
        with open(template_file, 'r') as file_handle:
            input_lines = file_handle.read().splitlines()

        output_lines = []
        for input_line in input_lines:
            output_line = input_line
#            for replace_string, value in sub_dict.items():
#                output_line = output_line.replace(f"${{{replace_string}}}",
#                                                  value)
            output_lines.append(output_line)

        # write tmp file with XML content with substituted values
        out_path = os.path.join(output_dir,
                                'input.nml')
        self.logger.debug(f"Writing file: {out_path}")
        with open(out_path, 'w') as file_handle:
            for line in output_lines:
                file_handle.write(f'{line}\n')

        return True

    def run_tracker(self, output_dir):
        command = (f"cd {output_dir}; "
                   f"{self.c_dict['TRACKER_APP']} "
                   f"< input.nml; "
                   f"ret=$?; "
                   f"cd -; "
                   f"if [ $ret != 0 ]; then false; fi")
        return self.run_command(command)
