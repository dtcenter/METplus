#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import re
import produtil.setup
from produtil.run import batchexe
from produtil.run import checkrun
import met_util as util


##@namespace TCMPRPlotter
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


class TCMPRPlotter(object):
    """! A Python class than encapsulates the plot_tcmpr.R plotting script.

    Generates plots for input files with .tcst format and
    creates output subdirectory based on the input tcst file.
    The plot_tcmpr.R plot also supports additional filtering by calling
    MET tool tc_stat. This wrapper extends plot_tcmpr.R by allowing the user
    to specify as input a directory (to support plotting all files in the
    specified directory and its subdirectories). The user can now either
    indicate a file or directory in the (required) -lookin option.
    """

    def __init__(self, config):
        """!Constructor for TCMPRPlotter
        @param config:  The configuration instance, contains
                        the conf file information."""
        # pylint:disable=too-many-instance-attributes
        # All these instance attributes are needed to support the
        # plot_tcmpr.R functionality.

        # Location of the R-script, plot_tcmpr.
        self.tcmpr_script = config.getexe('PLOT_TCMPR')

        # The only required argument, the name of the tcst file to plot.
        self.input_data = config.getstr('config', 'TCMPR_DATA')

        # Optional arguments
        self.plot_config_file = config.getstr('config', 'TCMPR_PLOT_CONFIG')
        self.output_base_dir = config.getdir('TCMPR_PLOT_OUT_DIR')
        self.prefix = config.getstr('config', 'PREFIX')
        self.title = config.getstr('config', 'TITLE')
        self.subtitle = config.getstr('config', 'SUBTITLE')
        self.xlab = config.getstr('config', 'XLAB')
        self.ylab = config.getstr('config', 'YLAB')
        self.xlim = config.getstr('config', 'XLIM')
        self.ylim = config.getstr('config', 'YLIM')
        self.filter = config.getstr('config', 'FILTER')
        self.filtered_tcst_data = config.getstr('config',
                                                'FILTERED_TCST_DATA_FILE')
        self.dep_vars = config.getstr('config', 'DEP_VARS')
        self.scatter_x = config.getstr('config', 'SCATTER_X')
        self.scatter_y = config.getstr('config', 'SCATTER_Y')
        self.skill_ref = config.getstr('config', 'SKILL_REF')
        self.series = config.getstr('config', 'SERIES')
        self.series_ci = config.getstr('config', 'SERIES_CI')
        self.legend = config.getstr('config', 'LEGEND')
        self.lead = config.getstr('config', 'LEAD')
        self.plot_types = config.getstr('config', 'PLOT_TYPES')
        self.rp_diff = config.getstr('config', 'RP_DIFF')
        self.demo_year = config.getstr('config', 'DEMO_YR')
        self.hfip_baseline = config.getstr('config', 'HFIP_BASELINE')
        self.footnote_flag = config.getstr('config', 'FOOTNOTE_FLAG')
        self.plot_config_options = config.getstr('config', 'PLOT_CONFIG_OPTS')
        self.save_data = config.getstr('config', 'SAVE_DATA')

        # Optional flags, by default these will be set to False in the
        # produtil config files.
        self.no_ee = config.getbool('config', 'NO_EE')
        self.no_log = config.getbool('config', 'NO_LOG')
        self.save = config.getbool('config', 'SAVE')

        self.logger = util.get_logger(config)
        self.logger.debug("DEBUG: TCMPR input " + self.input_data)
        self.logger.debug("DEBUG: TCMPR config file " +
                          self.plot_config_file)
        self.logger.debug("DEBUG: output " + self.output_base_dir)
        self.config = config

    def create_command(self):
        """! Builds the command for invoking tcmpr.R plot script.

             Args:

             Returns:

        """
        base_cmds_list = [' Rscript ', self.tcmpr_script, ' -lookin ']
        base_cmds = ''.join(base_cmds_list)
        self.logger.debug("base_cmds " + base_cmds)
        cmds_list = []

        # Create a list of all the "optional" options and flags.
        optionals_list = self.retrieve_optionals()

        # If input data is a file, create a single command and invoke R script.
        if os.path.isfile(self.input_data):
            self.logger.debug("Currently plotting " + self.input_data)
            cmds_list.append(base_cmds)
            cmds_list.append(self.input_data)

            # Special treatment of the "optional" output_base_dir option
            # because we are supporting the plotting of multiple tcst files
            # in a directory.
            if self.output_base_dir:
                dated_output_dir = self.create_output_subdir(self.input_data)
                optionals_list.append(' -outdir ')
                optionals_list.append(dated_output_dir)
                optionals = ''.join(optionals_list)

            if optionals:
                cmds_list.append(optionals)
                # Due to the way cmds_list was created, join it all in to
                # one string and than split that in to a list, so element [0]
                # is 'Rscript', instead of 'Rscript self.tcmpr_script -lookin'
                cmds_list = ''.join(cmds_list).split()
                # cmd = batchexe('sh')['-c',''.join(cmds_list)] > '/dev/null'
                cmd = batchexe(cmds_list[0])[cmds_list[1:]] > '/dev/null'
                self.logger.debug("DEBUG: Command run " +
                                  cmd.to_shell())
                self.logger.info("INFO: Generating requested plots for " +
                                 self.input_data)

                # pylint:disable=unnecessary-pass
                # If a tc file is empty, continue to the next, thus the pass
                # isn't unnecessary.
                try:
                    checkrun(cmd)
                except produtil.run.ExitStatusException as ese:
                    self.logger.warn("WARN: plot_tcmpr.R returned non-zero"
                                     " exit status, "
                                     "tcst file may be missing data, "
                                     "continuing: " + ese)

                    # Remove the empty directory
                    if not os.listdir(dated_output_dir):
                        os.rmdir(dated_output_dir)
                    pass

        # If the input data is a directory, create a command for each
        # file in the directory and invoke the R script for each tcst file.
        if os.path.isdir(self.input_data):
            self.logger.debug("plot all files in directory " +
                              self.input_data)
            cmds_list = []
            all_tcst_files = util.get_files(self.input_data, ".*.tcst",
                                            self.logger)
            self.logger.debug("num of files " + str(len(all_tcst_files)))
            for tcst_file in all_tcst_files:
                self.logger.info("INFO: Generating requested plots for " +
                                 tcst_file)
                # Check if the file is empty, if so skip to next file.
                if os.stat(tcst_file).st_size == 0:
                    self.logger.warn("WARNING: " + tcst_file +
                                     " is empty, continue to next file"
                                     "in list.")
                    continue

                # Append the mandatory -lookin option to the base command.
                cmds_list.append(base_cmds)
                cmds_list.append(tcst_file)
                dated_output_dir = self.create_output_subdir(tcst_file)

                if self.output_base_dir:
                    cmds_list.append(' -outdir ')
                    cmds_list.append(dated_output_dir)
                    self.logger.debug("DEBUG: Creating dated output dir " +
                                      dated_output_dir)

                if optionals_list:
                    remaining_options = ''.join(optionals_list)
                    cmds_list.append(remaining_options)

                # Due to the way cmds_list was created, join it all in to
                # one string and than split that in to a list, so element [0]
                # is 'Rscript', instead of 'Rscript self.tcmpr_script -lookin'
                cmds_list = ''.join(cmds_list).split()
                cmd = batchexe(cmds_list[0])[cmds_list[1:]] > '/dev/null'
                self.logger.debug("DEBUG:  Command run " + cmd.to_shell())

                # pylint:disable=unnecessary-pass
                # If a tc file is empty, continue to the next, thus the pass
                # isn't unnecessary.
                try:
                    checkrun(cmd)
                except produtil.run.ExitStatusException as ese:
                    # If the tcst file is empty (with the exception of the
                    #  header), or there is some other problem, then
                    # plot_tcmpr.R will return with a non-zero exit status of 1
                    self.logger.warn("WARN: plot_tcmpr.R returned non-zero"
                                     " exit status, tcst file may be missing"
                                     " data... continuing: " + str(ese))
                    # Remove the empty directory
                    if not os.listdir(dated_output_dir):
                        os.rmdir(dated_output_dir)

                    pass
                # Reset empty cmds_list to prepare for next tcst file.
                cmds_list = []

        self.logger.info("INFO: Plotting complete")

    def create_output_subdir(self, tcst_file):
        """ Extract the base portion of the tcst filename:
            eg amlqYYYYMMDDhh.gfso.nnnn in
            /d1/username/tc_pairs/YYYYMM/amlqYYYYMMDDhh.gfso.nnnn and use this
            as the subdirectory (gets appended to the TCMPR output directory).
            This allows the user to determine which plots correspond to the
            input track file.

            Args:
                @param tcst_file:  The input tc-pairs file.
        """
        subdir_match = re.match(r'.*/(.*).tcst', tcst_file)
        subdir = subdir_match.group(1)
        dated_output_dir = os.path.join(self.output_base_dir, subdir)
        self.logger.debug("DEBUG: " + dated_output_dir + " for " + tcst_file)

        # Create the subdir
        util.mkdir_p(dated_output_dir)

        return dated_output_dir

    def retrieve_optionals(self):
        """Creates a list of the optional options if they are defined."""
        optionals = []
        if self.plot_config_file:
            optionals.append(' -config ')
            optionals.append(self.plot_config_file)
        if self.prefix:
            optionals.append(' -prefix ')
            optionals.append(self.prefix)
        if self.title:
            optionals.append(' -title ')
            optionals.append(self.title)
        if self.subtitle:
            optionals.append(' -subtitle ')
            optionals.append(self.subtitle)
        if self.xlab:
            optionals.append(' -xlab ')
            optionals.append(self.xlab)
        if self.ylab:
            optionals.append(' -ylab ')
            optionals.append(self.ylab)
        if self.xlim:
            optionals.append(' -xlim ')
            optionals.append(self.xlim)
        if self.ylim:
            optionals.append(' -ylim ')
            optionals.append(self.ylim)
        if self.filter:
            optionals.append(' -filter ')
            optionals.append(self.filter)
        if self.filtered_tcst_data:
            optionals.append(' -tcst ')
            optionals.append(self.filtered_tcst_data)
        if self.dep_vars:
            optionals.append(' -dep ')
            optionals.append(self.dep_vars)
        if self.scatter_x:
            optionals.append(' -scatter_x ')
            optionals.append(self.scatter_x)
        if self.scatter_y:
            optionals.append(' -scatter_y ')
            optionals.append(self.scatter_y)
        if self.skill_ref:
            optionals.append(' -skill_ref ')
            optionals.append(self.skill_ref)
        if self.series:
            optionals.append(' - series ')
            optionals.append(self.series)
        if self.series_ci:
            optionals.append(' -series_ci ')
            optionals.append(self.series_ci)
        if self.legend:
            optionals.append(' -legend ')
            optionals.append(self.legend)
        if self.lead:
            optionals.append(' -lead ')
            optionals.append(self.lead)
        if self.plot_types:
            optionals.append(' -plot ')
            optionals.append(self.plot_types)
        if self.rp_diff:
            optionals.append(' -rp_diff ')
            optionals.append(self.rp_diff)
        if self.demo_year:
            optionals.append(' -demo_yr ')
            optionals.append(self.demo_year)
        if self.hfip_baseline:
            optionals.append(' -hfip_bsln ')
            optionals.append(self.hfip_baseline)
        if self.plot_config_options:
            optionals.append(' -plot_config ')
            optionals.append(self.plot_config_options)
        if self.save_data:
            optionals.append(' -save_data ')
            optionals.append(self.save_data)

        # Flags
        if self.footnote_flag:
            optionals.append(' -footnote_flag ')
        if self.no_ee:
            optionals.append(' -no_ee ')
        if self.no_log:
            optionals.append(' -no_log ')
        if self.save:
            optionals.append(' -save')

        return optionals


if __name__ == "__main__":
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='TCMPRPlotter',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='TCMPRPlotter')
        produtil.log.postmsg('TCMPRPlotter is starting')

        # Read in the configuration object config
        import config_launcher
        if len(sys.argv) == 3:
            CONFIG = config_launcher.load_baseconfs(sys.argv[2])
        else:
            CONFIG = config_launcher.load_baseconfs()
        if 'MET_BUILD_BASE' not in os.environ:
            os.environ['MET_BUILD_BASE'] = CONFIG.getdir('MET_BUILD_BASE')
        if CONFIG.getdir('MET_BIN') not in os.environ['PATH']:
            os.environ['PATH'] += os.pathsep + CONFIG.getdir('MET_BIN')
        TCP = TCMPRPlotter(CONFIG)
        TCP.create_command()
        produtil.log.postmsg('TCMPRPlotter completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'TCMPRPlotter failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)
