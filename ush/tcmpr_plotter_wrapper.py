#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import re
import subprocess
import produtil.setup
from produtil.run import exe
from produtil.run import checkrun
import met_util as util
from command_builder import CommandBuilder
import config_metplus


##@namespace TCMPRPlotterWrapper
# A Python class than encapsulates the plot_tcmpr.R plotting script.
#
# Generates plots for input files with .tcst format and
# creates output subdirectory based on the input tcst file.
# The plot_tcmpr.R plot also supports additional filtering by calling MET tool
# tc_stat. This wrapper extends plot_tcmpr.R by allowing the user to specify
# as input a directory (to support plotting all files in the specified
# directory and its subdirectories). The user can now either indicate a file
# or directory in the (required) -lookin option.
# Call as follows:
# @code{.sh}
# tcmpr_plotter_wrapper.py [-c /path/to/user.template.conf]
# @endcode
#


class TCMPRPlotterWrapper(CommandBuilder):
    """! A Python class than encapsulates the plot_tcmpr.R plotting script.

    Generates plots for input files with .tcst format and
    creates output subdirectory based on the input tcst file.
    The plot_tcmpr.R plot also supports additional filtering by calling
    MET tool tc_stat. This wrapper extends plot_tcmpr.R by allowing the user
    to specify as input a directory (to support plotting all files in the
    specified directory and its subdirectories). The user can now either
    indicate a file or directory in the (required) -lookin option.
    """

    def __init__(self, p, logger):
        """!Constructor for TCMPRPlotterWrapper
            Args:
            @param p:  The configuration instance, contains
                            the conf file information.
            @param logger:  A logger, can be None
        """

        # pylint:disable=too-many-instance-attributes
        # All these instance attributes are needed to support the
        # plot_tcmpr.R functionality.
        super(TCMPRPlotterWrapper, self).__init__(p, logger)
        self.app_name = 'plot_tcmpr.R'
        self.config = p
        self.logger = logger
        if self.logger is None:
            self.logger = util.get_logger(self.p, sublog='TCMPRPlotter')

        self._init_tcmpr_script()

        # The only required argument for plot_tcmpr.R, the name of
        # the tcst file to plot.
        self.input_data = self.cu.getstr('config', 'TCMPR_DATA')

        # Optional arguments
        self.plot_config_file = self.cu.getstr('config', 'CONFIG_FILE')
        self.output_base_dir = self.cu.getdir('TCMPR_PLOT_OUT_DIR')
        self.prefix = self.cu.getstr('config', 'PREFIX')
        self.title = self.cu.getstr('config', 'TITLE')
        self.subtitle = self.cu.getstr('config', 'SUBTITLE')
        self.xlab = self.cu.getstr('config', 'XLAB')
        self.ylab = self.cu.getstr('config', 'YLAB')
        self.xlim = self.cu.getstr('config', 'XLIM')
        self.ylim = self.cu.getstr('config', 'YLIM')
        self.filter = self.cu.getstr('config', 'FILTER')
        self.filtered_tcst_data = self.cu.getstr('config',
                                           'FILTERED_TCST_DATA_FILE')
        self.dep_vars = util.getlist(self.cu.getstr('config', 'DEP_VARS'))
        self.scatter_x = self.cu.getstr('config', 'SCATTER_X')
        self.scatter_y = self.cu.getstr('config', 'SCATTER_Y')
        self.skill_ref = self.cu.getstr('config', 'SKILL_REF')
        self.series = self.cu.getstr('config', 'SERIES')
        self.series_ci = self.cu.getstr('config', 'SERIES_CI')
        self.legend = self.cu.getstr('config', 'LEGEND')
        self.lead = self.cu.getstr('config', 'LEAD')
        self.plot_types = util.getlist(self.cu.getstr('config', 'PLOT_TYPES'))
        self.rp_diff = self.cu.getstr('config', 'RP_DIFF')
        self.demo_year = self.cu.getstr('config', 'DEMO_YR')
        self.hfip_baseline = self.cu.getstr('config', 'HFIP_BASELINE')
        self.footnote_flag = self.cu.getstr('config', 'FOOTNOTE_FLAG')
        self.plot_config_options = self.cu.getstr('config', 'PLOT_CONFIG_OPTS')
        self.save_data = self.cu.getstr('config', 'SAVE_DATA')

        # Optional flags, by default these will be set to False in the
        # produtil config files.
        self.no_ee = self.cu.getbool('config', 'NO_EE')
        self.no_log = self.cu.getbool('config', 'NO_LOG')
        self.save = self.cu.getbool('config', 'SAVE')

    def _init_tcmpr_script(self):
        """! Called by the constructor to set up the environment variables
        used by the plot_tcmpr.R script and  to set the self.tcmpr_script
        variable."""
        # User environment variable settings take precedence over
        # configuration files.
        # The purpose of this method is to support MET 6.0 and later,
        # and to not throw a superfluous error, due to a missing  env variable
        # that is version specific.
        # For example,
        # MET_INSTALL_DIR is required starting with met-6.1, so we don't
        # want to throw an error if it is not defined and we are running
        # with an earlier version of met.
        #
        # Ultimately, the plot_tcmpr.R script will throw an error
        # indicating any missing required environment variables.
        # So if all else fails, we defer to plot_tcmpr.R,
        # We are being nice and trying to catch/prevent it here.

        # The logic in this method is not perfect. So it is entirely
        # possible for a scenario to exist that may cause this to
        # break. It would be much easier if there was a way to check
        # for the version of met. Hopefully it covers 99% of the cases.

        # Environment variables and met versions required by the plot_tcmpr.R
        # met-6.1 and later: MET_INSTALL_DIR, MET_BASE
        # met-6.0: MET_BUILD_BASE, RSCRIPTS_BASE

        # At some point in the future MET_BUILD_BASE and RSCRIPTS_BASE
        # should go-away from all METplus references. When we no longer
        # need to support MET 6.0, this method  can be simplified.

        # MET_INSTALL_DIR introduced in METplus conf file, for met-6.1 and later
        if 'MET_INSTALL_DIR' in os.environ:
            self.logger.info('Using MET_INSTALL_DIR setting from user '
                             'environment instead of metplus configuration '
                             'file. Using: %s' % os.environ['MET_INSTALL_DIR'])
        else:

            # If MET_BUILD_BASE is defined in conf file, assume we are
            # running with met-6.0 and earlier. Which means MET_INSTALL_DIR
            # is NOT required, so we don't want to throw an error, if it is
            # not defined.
            if self.p.has_option('dir', 'MET_BUILD_BASE'):
                if self.p.has_option('dir', 'MET_INSTALL_DIR'):
                    os.environ['MET_INSTALL_DIR'] = \
                        self.cu.getdir('MET_INSTALL_DIR')
            else:
                os.environ['MET_INSTALL_DIR'] = self.cu.getdir('MET_INSTALL_DIR')

        # MET_BASE has always been defined in METplus, so it 'should'
        # exist, so we will throw an error, if it is not defined,
        # even though it is not required if running METplus against
        # met-6.0 and earlier.
        if 'MET_BASE' in os.environ:
            self.logger.info('Using MET_BASE setting from user '
                             'environment instead of metplus configuration '
                             'file. Using: %s' % os.environ['MET_BASE'])
            met_base_tcmpr_script = \
                os.path.join(os.environ['MET_BASE'], 'Rscripts/plot_tcmpr.R')
        else:
            os.environ['MET_BASE'] = self.cu.getdir('MET_BASE')
            met_base_tcmpr_script = \
                os.path.join(self.cu.getdir('MET_BASE'), 'Rscripts/plot_tcmpr.R')

        # RSCRIPTS_BASE introduced and used ONLY in met-6.0 release.
        # Will go away when we no longer support met-6.0 and earlier.
        # RSCRIPTS_BASE /path/to/scripts/Rscripts
        if 'RSCRIPTS_BASE' in os.environ:
            self.logger.info('Using RSCRIPTS_BASE setting from user '
                             'environment instead of metplus configuration '
                             'file. Using: %s' % os.environ['RSCRIPTS_BASE'])
        else:
            # If MET_BUILD_BASE is defined in conf file, assume we are
            # running with met-6.0 and earlier. Which means RSCRIPTS_BASE
            # is required, so throw an error, if it is not defined.
            if self.p.has_option('dir', 'MET_BUILD_BASE'):
                os.environ['RSCRIPTS_BASE'] = self.cu.getdir('RSCRIPTS_BASE')

        # MET_BUILD_BASE has always been defined in METplus.
        # Will go away when we no longer support met-6.0 and earlier.
        if 'MET_BUILD_BASE' in os.environ:
            self.logger.info('Using MET_BUILD_BASE setting from user '
                             'environment instead of metplus configuration '
                             'file. Using: %s' % os.environ['MET_BUILD_BASE'])
            met_build_base_tcmpr_script = \
                os.path.join(os.environ['MET_BUILD_BASE'],
                             'scripts/Rscripts/plot_tcmpr.R')
        else:
            if self.p.has_option('dir', 'MET_BUILD_BASE'):
                os.environ['MET_BUILD_BASE'] = self.cu.getdir('MET_BUILD_BASE')
                met_build_base_tcmpr_script = os.path.join(
                    self.cu.getdir('MET_BUILD_BASE'),
                    'scripts/Rscripts/plot_tcmpr.R')
            else:
                # Set to empty string since we test it later.
                met_build_base_tcmpr_script = ''

        if util.file_exists(met_base_tcmpr_script):
            self.tcmpr_script = met_base_tcmpr_script
            self.logger.info('Using MET_BASE plot_tcmpr script: %s '
                             % met_base_tcmpr_script)
        elif util.file_exists(met_build_base_tcmpr_script):
            self.tcmpr_script = met_build_base_tcmpr_script
            self.logger.info('Using MET_BUILD_BASE plot_tcmpr script: %s '
                             % met_build_base_tcmpr_script)
        else:
            self.logger.error('NO tcmpr_plot.R script could be found, '
                              'Check your MET_BASE or MET_BUILD_BASE ',
                              'paths in conf file.')
            sys.exit(1)

    def run_all_times(self):
        """! Builds the command for invoking tcmpr.R plot script.

             Args:

             Returns:

        """

        self.logger.debug("TCMPR input " + self.input_data)
        self.logger.debug("TCMPR config file " +
                          self.plot_config_file)
        self.logger.debug("output " + self.output_base_dir)

        # Create a dictionary of all the "optional" options and flags.
        cmds_dict = self.retrieve_optionals()

        # Create the TCMPR output base directory, where the final plots
        # will be saved.
        util.mkdir_p(self.output_base_dir)

        # If input data is a file, create a single command and invoke R script.
        if os.path.isfile(self.input_data):
            self.logger.debug("Currently plotting " + self.input_data)
            cmds_dict[' -lookin '] = self.input_data

            # Special treatment of the "optional" output_base_dir option
            # because we are supporting the plotting of multiple tcst files
            # in a directory.
            if self.output_base_dir:
                # dated_output_dir = self.create_output_subdir(self.input_data)
                cmds_dict[' -outdir '] = self.output_base_dir

            # Generate the list, where the -args are separated by their
            # values.
            full_cmd_list = ['Rscript' + self.tcmpr_script]
            for key, value in cmds_dict.iteritems():
                full_cmd_list.append(key)
                full_cmd_list.append(value)

            # Separate the 'Rscript' portion from the args, to conform to
            # produtil's exe syntax.
            cmd = exe(full_cmd_list[0])[full_cmd_list[1:]] > '/dev/null'
            self.logger.debug("Command run " +
                              cmd.to_shell())
            self.logger.info("Generating requested plots for " +
                             self.input_data)
            # pylint:disable=unnecessary-pass
            # If a tc file is empty, continue to the next, thus the pass
            # isn't unnecessary.
            try:
                checkrun(cmd)
            except produtil.run.ExitStatusException as ese:
                self.logger.warn("plot_tcmpr.R returned non-zero"
                                 " exit status, "
                                 "tcst file may be missing data, "
                                 "continuing: " + repr(ese))

        # If the input data is a directory, create a list of all the
        # files in the directory and invoke the R script for this list
        # of files.
        elif os.path.isdir(self.input_data):
            self.logger.debug("plot all files in directory " +
                              self.input_data)
            cmds_dict = self.retrieve_optionals()
            all_tcst_files_list = util.get_files(self.input_data, ".*.tcst",
                                                 self.logger)
            all_tcst_files = ' '.join(all_tcst_files_list)
            self.logger.debug("num of files " + str(len(all_tcst_files)))
            # Append the mandatory -lookin option to the base command.
            cmds_dict['-lookin'] = all_tcst_files
            if self.output_base_dir:
                cmds_dict['-outdir'] = self.output_base_dir
                self.logger.debug("Creating dated output dir " +
                                  self.output_base_dir)

            # Create the full_cmd_list from the keys and values of the
            # cmds_dict and then form one command list.
            full_cmd_list = list()
            full_cmd_list.append("Rscript")
            full_cmd_list.append(self.tcmpr_script)
            for key, value in cmds_dict.iteritems():
                full_cmd_list.append(key)
                if key == '-lookin':
                    # treat the list of dirs in -lookin differently,
                    # append each individual directory to replicate original
                    # implementation's behavior of splitting the commands
                    # by whitespace and assigning each command to an item
                    # in a list.
                    for tcst_file in all_tcst_files_list:
                        full_cmd_list.append(tcst_file)
                elif key == '-plot':
                    # plot types list is also appended as a single string,
                    # delimited by ','.
                    full_cmd_list.append(','.join(value))
                elif key == '-dep':
                    # dependant variables list items are appended
                    # as one string.  Convert list into a string delimited
                    # by ','.
                    full_cmd_list.append(','.join(value))

                else:
                    full_cmd_list.append(value)

            # Separate the 'Rscript' portion from the args, to conform to
            # produtil's exe syntax.
            cmd = exe(full_cmd_list[0])[full_cmd_list[1:]] > '/dev/null'

            # This can be a very long command if the user has
            # indicated a directory.  Only log this if necessary.
            # self.logger.debug("DEBUG:  Command run " + cmd.to_shell())
            # cmd_str = ' '.join(full_cmd_list)
            # cmd_list = 'Rscript ' + cmd_str
            # self.logger.debug('TCMPR Command run: ' + cmd_str)

            # Now run the command via produtil
            try:
                checkrun(cmd)
            except produtil.run.ExitStatusException as ese:
                # If the tcst file is empty (with the exception of the
                #  header), or there is some other problem, then
                # plot_tcmpr.R will return with a non-zero exit status of 1
                self.logger.error("plot_tcmpr.R returned non-zero"
                                  " exit status, tcst file may be missing"
                                  " data... continuing: " + str(ese))
                sys.exit(1)
        else:
            self.logger.error("Expected input is neither a file nor directory,"
                              "exiting...")
            sys.exit(1)

        self.logger.info("Plotting complete")

    def create_output_subdir(self, tcst_file):
        """! Extract the base portion of the tcst filename:
            eg amlqYYYYMMDDhh.gfso.nnnn in
            /d1/username/tc_pairs/YYYYMM/amlqYYYYMMDDhh.gfso.nnnn and use this
            as the subdirectory (gets appended to the TCMPR output directory).
            This allows the user to determine which plots correspond to the
            input track file.

            Args:
                @param tcst_file:  The input tc-pairs file.
            Returns:
                dated_output_dir:  The output dir where the final tcmpr plots
                                   will be saved
        """
        subdir_match = re.match(r'.*/(.*).tcst', tcst_file)
        subdir = subdir_match.group(1)
        dated_output_dir = os.path.join(self.output_base_dir, subdir)
        self.logger.debug(dated_output_dir + " for " + tcst_file)

        # Create the subdir
        util.mkdir_p(dated_output_dir)

        return dated_output_dir

    def retrieve_optionals(self):
        """Creates a dictionary of the options and their values.
           Args:

           Returns:
               options_dict: a dictionary of the values to the optional args
                          in a format where the argument is the key, and
                          the args value is the dictionary value.  This is
                          useful in keeping the args separate from their
                          values, where values with whitespaces aren't
                          compromised (i.e. whitespaces are retained).


        """
        options_dict = dict()

        if self.plot_config_file:
            options_dict['-config'] = self.plot_config_file
        if self.prefix:
            options_dict['-prefix'] = self.prefix
        if self.title:
            options_dict['-title'] = '"' + self.title + '"'
        if self.subtitle:
            options_dict['-subtitle'] = '"' + self.subtitle + '"'
        if self.xlab:
            options_dict['-xlab'] = '"' + self.xlab + '"'
        if self.ylab:
            options_dict['-ylab'] = '"' + self.ylab + '"'
        if self.xlim:
            options_dict['-xlim'] = self.xlim
        if self.ylim:
            options_dict['-ylim'] = self.ylim
        if self.filter:
            options_dict['-filter'] = self.filter
        if self.filtered_tcst_data:
            options_dict['-tcst'] = self.filtered_tcst_data
        if self.dep_vars:
            options_dict['-dep'] = self.dep_vars
        if self.scatter_x:
            options_dict['-scatter_x'] = self.scatter_x
        if self.scatter_y:
            options_dict['-scatter_y'] = self.scatter_y
        if self.skill_ref:
            options_dict['-skill_ref'] = self.skill_ref
        if self.series:
            options_dict['-series'] = self.series
        if self.series_ci:
            options_dict['-series_ci'] = self.series_ci
        if self.legend:
            options_dict['-legend'] = '"' + self.legend + '"'
        if self.lead:
            options_dict['-lead'] = self.lead
        if self.plot_types:
            options_dict['-plot'] = self.plot_types
        if self.rp_diff:
            options_dict['-rp_diff'] = self.rp_diff
        if self.demo_year:
            options_dict['-demo_yr'] = self.demo_year
        if self.hfip_baseline:
            options_dict['-hfip_bsln'] = self.hfip_baseline
        if self.plot_config_options:
            options_dict['-plot_config'] = self.plot_config_file
        if self.save_data:
            options_dict['-save_data'] = self.save_data

        # Flags
        if self.footnote_flag:
            options_dict['-footnote_flag'] = ''
        if self.no_ee:
            options_dict['-no_ee'] = ''
        if self.no_log:
            options_dict['-no_log'] = ''
        if self.save:
            options_dict['-save'] = ''

        return options_dict

    def get_command(self):
        """! Over-ride CommandBuilder's get_command because unlike
             other MET tools, tcmpr_plotter_wrapper handles input
             files differently because it wraps an R-script, plot_tcmpr.R
             rather than a typical MET tool. Build command to run from
             arguments"""
        if self.app_path is None:
            self.logger.error("No app path specified. You must use a subclass")
            return None

        return self.cmd

    def build(self):
        """! Override CommandBuilder's build() since the plot_tcmpr.R plot
             is set up differently from the other MET tools."""
        cmd = self.get_command()
        if cmd is None:
            return
        self.logger.info("RUNNING: " + cmd)
        process = subprocess.Popen(cmd, env=self.env, shell=True)
        process.wait()


if __name__ == "__main__":
    util.run_stand_alone("tcmpr_plotter_wrapper", "TCMPRPlotter")
