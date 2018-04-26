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
            self.logger = util.get_logger(self.p,sublog='TCMPRPlotter')

        self._init_tcmpr_script()

        # The only required argument for plot_tcmpr.R, the name of
        # the tcst file to plot.
        self.input_data = p.getstr('config', 'TCMPR_DATA')

        # Optional arguments
        self.plot_config_file = p.getstr('config', 'CONFIG_FILE')
        self.output_base_dir = p.getdir('TCMPR_PLOT_OUT_DIR')
        self.prefix = p.getstr('config', 'PREFIX')
        self.title = p.getstr('config', 'TITLE')
        self.subtitle = p.getstr('config', 'SUBTITLE')
        self.xlab = p.getstr('config', 'XLAB')
        self.ylab = p.getstr('config', 'YLAB')
        self.xlim = p.getstr('config', 'XLIM')
        self.ylim = p.getstr('config', 'YLIM')
        self.filter = p.getstr('config', 'FILTER')
        self.filtered_tcst_data = p.getstr('config',
                                           'FILTERED_TCST_DATA_FILE')
        self.dep_vars = p.getstr('config', 'DEP_VARS')
        self.scatter_x = p.getstr('config', 'SCATTER_X')
        self.scatter_y = p.getstr('config', 'SCATTER_Y')
        self.skill_ref = p.getstr('config', 'SKILL_REF')
        self.series = p.getstr('config', 'SERIES')
        self.series_ci = p.getstr('config', 'SERIES_CI')
        self.legend = p.getstr('config', 'LEGEND')
        self.lead = p.getstr('config', 'LEAD')
        self.plot_types = p.getstr('config', 'PLOT_TYPES')
        self.rp_diff = p.getstr('config', 'RP_DIFF')
        self.demo_year = p.getstr('config', 'DEMO_YR')
        self.hfip_baseline = p.getstr('config', 'HFIP_BASELINE')
        self.footnote_flag = p.getstr('config', 'FOOTNOTE_FLAG')
        self.plot_config_options = p.getstr('config', 'PLOT_CONFIG_OPTS')
        self.save_data = p.getstr('config', 'SAVE_DATA')

        # Optional flags, by default these will be set to False in the
        # produtil config files.
        self.no_ee = p.getbool('config', 'NO_EE')
        self.no_log = p.getbool('config', 'NO_LOG')
        self.save = p.getbool('config', 'SAVE')

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
            if self.p.has_option('dir','MET_BUILD_BASE'):
                if self.p.has_option('dir','MET_INSTALL_DIR'):
                    os.environ['MET_INSTALL_DIR'] = self.p.getdir('MET_INSTALL_DIR')
            else:
                os.environ['MET_INSTALL_DIR'] = self.p.getdir('MET_INSTALL_DIR')

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
            os.environ['MET_BASE'] = self.p.getdir('MET_BASE')
            met_base_tcmpr_script = \
                os.path.join(self.p.getdir('MET_BASE'), 'Rscripts/plot_tcmpr.R')

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
                os.environ['RSCRIPTS_BASE'] = self.p.getdir('RSCRIPTS_BASE')

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
                os.environ['MET_BUILD_BASE'] = self.p.getdir('MET_BUILD_BASE')
                met_build_base_tcmpr_script = os.path.join(self.p.getdir('MET_BUILD_BASE'),
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
                              'Check your MET_BASE or MET_BUILD_BASE paths in conf file.')
            sys.exit(1)

    def run_all_times(self):
        """! Builds the command for invoking tcmpr.R plot script.

             Args:

             Returns:

        """
        base_cmds_list = [' Rscript ', self.tcmpr_script, ' -lookin ']
        base_cmds = ''.join(base_cmds_list)
        self.logger.debug("base_cmds " + base_cmds)
        cmds_list = []

        self.logger.debug("DEBUG: TCMPR input " + self.input_data)
        self.logger.debug("DEBUG: TCMPR config file " +
                          self.plot_config_file)
        self.logger.debug("DEBUG: output " + self.output_base_dir)

        # Create a list of all the "optional" options and flags.
        optionals_list = self.retrieve_optionals()

        # Create the output base directory
        util.mkdir_p(self.output_base_dir)

        # If input data is a file, create a single command and invoke R script.
        if os.path.isfile(self.input_data):
            self.logger.debug("Currently plotting " + self.input_data)
            cmds_list.append(base_cmds)
            cmds_list.append(self.input_data)

            # Special treatment of the "optional" output_base_dir option
            # because we are supporting the plotting of multiple tcst files
            # in a directory.
            if self.output_base_dir:
                # dated_output_dir = self.create_output_subdir(self.input_data)
                optionals_list.append(' -outdir ')
                # optionals_list.append(dated_output_dir)
                optionals_list.append(self.output_base_dir)
                optionals = ''.join(optionals_list)

            if optionals:
                cmds_list.append(optionals)
                # Due to the way cmds_list was created, join it all in to
                # one string and than split that in to a list, so element [0]
                # is 'Rscript', instead of 'Rscript self.tcmpr_script -lookin'

                # Use CommandBuilder's build() and clear(); using
                # produtil's  exe generates mpirun warnings, only on eyewall,
                # which can be ignored.
                cmds_list = ''.join(cmds_list).split()
                #cmd = exe('sh')['-c',''.join(cmds_list)] > '/dev/null'
                cmd = exe(cmds_list[0])[cmds_list[1:]] > '/dev/null'
                self.logger.debug("DEBUG: Command run " +
                                   cmd.to_shell())
                self.logger.info("INFO: Generating requested plots for " +
                                  self.input_data)
                #self.build()
                #self.clear()
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
                    if not os.listdir(self.output_base_dir):
                        os.rmdir(self.output_base_dir)
                    pass

                # Remove the empty directory
                if not os.listdir(self.output_base_dir):
                    os.rmdir(self.output_base_dir)
                    pass

        # If the input data is a directory, create a list of all the
        # files in the directory and invoke the R script for this list
        # of files.
        if os.path.isdir(self.input_data):
            self.logger.debug("plot all files in directory " +
                              self.input_data)
            cmds_list = []
            all_tcst_files_list = util.get_files(self.input_data, ".*.tcst",
                                                 self.logger)
            all_tcst_files = ' '.join(all_tcst_files_list)
            self.logger.debug("num of files " + str(len(all_tcst_files)))
            # Append the mandatory -lookin option to the base command.
            cmds_list.append(base_cmds)
            cmds_list.append(all_tcst_files)
            # dated_output_dir = self.create_output_subdir(self.output_plot)
            dated_output_dir = self.output_base_dir
            if self.output_base_dir:
                cmds_list.append(' -outdir ')
                util.mkdir_p(self.output_base_dir)
                cmds_list.append(self.output_base_dir)
                self.logger.debug("DEBUG: Creating dated output dir " +
                                  dated_output_dir)

            if optionals_list:
                remaining_options = ''.join(optionals_list)
                cmds_list.append(remaining_options)

            # Due to the way cmds_list was created, join it all in to
            # one string and than split that in to a list, so element [0]
            # is 'Rscript', instead of 'Rscript self.tcmpr_script -lookin'
            cmds_list = ''.join(cmds_list).split()
            cmd = exe(cmds_list[0])[cmds_list[1:]] > '/dev/null'
            # This can be a very long command if the user has
            # indicated a directory.  Only log this if necessary.
            # self.logger.debug("DEBUG:  Command run " + cmd.to_shell())

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
        """! Extract the base portion of the tcst filename:
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

    def get_command(self):
        """! Over-ride CommandBuilder's get_command because unlike other MET tools,
             tcmpr_plotter_wrapper handles input files differently because it wraps an R-script, plot_tcmpr.R
             rather than a typical MET tool. Build command to run from arguments"""
        if self.app_path is None:
            self.logger.error("No app path specified. You must use a subclass")
            return None

        return self.cmd

    def build(self):
        """! Override CommandBuilder's build() since the plot_"""
        cmd = self.get_command()
        if cmd is None:
            return
        self.logger.info("RUNNING: " + cmd)
        process = subprocess.Popen(cmd, env=self.env, shell=True)
        process.wait()


if __name__ == "__main__":
    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='TCMPRPlotterWrapper',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='TCMPRPlotterWrapper')
        produtil.log.postmsg('TCMPRPlotterWrapper is starting')

        # Read in the configuration object CONFIG
        CONFIG = config_metplus.setup()

        # if CONFIG.getdir('MET_BIN') not in os.environ['PATH']:
        #    os.environ['PATH'] += os.pathsep + CONFIG.getdir('MET_BIN')

        TCP = TCMPRPlotterWrapper(CONFIG, logger=None)
        TCP.run_all_times()
        produtil.log.postmsg('TCMPRPlotterWrapper completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'TCMPRPlotterWrapper failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)
