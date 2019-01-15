#!/usr/bin/env python
from __future__ import (print_function, division)

"""
File Name: command_runner.py
Contact(s): Jim Frimel
Abstract:
History Log:  Initial version
Usage: Use as a has-a relationship with your object or module.
       Object has-a command runner.
Parameters: None
Input Files: N/A
Output Files: N/A
"""

##@namespace command_runner
# The purpose of this class is to run the external MET executables
# and other ancillary external programs used in METplus, such as
# wgrib2, ncdump, plot_tcmpr.R
#
# It also centralizes the output redirection to the
# METplus logs, MET logs or TTY.
#
# One BIG underlying assumption is that all commands are run
# the same way in terms of the Runner object and the Run command
# executed.
#
# Originally this capability (the methods) was placed in the
# CommandBuilder but it seemed to separating out made sense.
# CommandBuilder now has-a CommandRunner. But being in its own class
# allows it to be used elsewhere if needed.
#
# It creates a produtil Runnable object
# It determines where to redirect the output
#   METplus log file, MET logs, or TTY
# It runs the Runnable object
#
import os
from produtil.run import exe, run
import met_util as util
import shlex

class CommandRunner(object):
    """! Class for Creating and Running External Programs
    """
    def __init__(self, config, logger=None):
        """!Class for Creating and Running External Programs.
            It was intended to handle the MET executables but
            can be used by other executables."""
        self.config = config
        self.logger = logger
        if self.logger == None:
            self.logger = util.get_logger(self.config,sublog='CommandRunner')
        self.verbose = self.config.getstr('config', 'LOG_MET_VERBOSITY', '2')


    def run_cmd(self, cmd, ismetcmd = True, app_name=None, run_inshell=False,
                log_theoutput=False, **kwargs):
        """!The command cmd is a string which is converted to a produtil
        exe Runner object and than run. Output of the command may also
        be redirected to either METplus log, MET log, or TTY.

        Some subclasses of CommandBuilder ie. series_by_init_wrapper, run
        non MET commands ie. convert, in addition to MET binary commands,
        ie. regrid_data_plane.

        Args:
            @param cmd: A string, Command used in the produtil exe Runner object.
            @param ismetcmd: Default True, Will direct output to METplus log,
            Metlog , or TTY. Set to False and use the other keywords as needed.
            @param app_name: Used only when ismetcmd=True, The name of the exectable
            being run.
            @param run_inshell: Used only when ismetcmd=False, will Create a
            runner object with the cmd being run through a shell, exe('sh')['-c', cmd]
            This is required by commands, such as ncdump that are redirecting
            output to a file, and other commands such as the convert command
            when creating animated gifs.
            @param log_theoutput: Used only when ismetcmd=False, will redirect
            the stderr and stdout to a the METplus log file or tty.
            DO Not set to True if the command is redirecting output to a file.
            @param kwargs Other options sent to the produtil Run constructor
        """

        if cmd is None:
            return cmd

        if ismetcmd:

            # self.app_name MUST be defined in the subclass' constructor,
            # this code block is a safety net in case that was not done.
            # self.app_name is used to generate the MET log output name,
            # if output is directed there, based on the conf settings.
            #
            # cmd.split()[0] 'should' be the /path/to/<some_met_binary>
            if not app_name:
                app_name = os.path.basename(cmd.split()[0])
                self.logger.warning('MISSING self.app_name, '
                                    'setting name to: %s' % repr(app_name))
                self.logger.warning('Fix the code and edit the following objects'
                                    ' contructor: %s, ' % repr(self))

            # Determine where to send the output from the MET command.
            log_dest = self.cmdlog_destination(cmdlog=app_name+'.log')

            # KEEP This comment as a reference note.
            # Run the executable in a new process instead of through a shell.
            # FYI. We were originally running the command through a shell
            # which also works just fine. IF we go back to running through
            # a shell, The string ,cmd, is formatted exactly as is needed.
            # By formatted, it is as it would be when typed at the shell prompt.
            # This includes, for example, quoting or backslash escaping filenames
            # with spaces in them.

            # Run the executable and pass the arguments as a sequence.
            # Split the command in to a sequence using shell syntax.
            the_exe = shlex.split(cmd)[0]
            the_args = shlex.split(cmd)[1:]
            if log_dest:
                self.logger.info("app_name is: %s, output sent to: %s" % (app_name, log_dest))
                #cmd = exe('sh')['-c', cmd].err2out() >> log_dest
                cmd = exe(the_exe)[the_args].err2out() >> log_dest
            else:
                #cmd = exe('sh')['-c', cmd].err2out()
                cmd = exe(the_exe)[the_args].err2out()

        else:
            # This block is for all the Non-MET commands
            # Some commands still need to be run in  a shell in order to work.
            #
            # There are currently 3 cases of non met commnds that need to be handled.
            # case 1. Redirecting to a file in cmd string, which must be through a shell
            #         ie. cmd = ncdump ...series_F006/min.nc > .../min.txt
            #             cmd = exe('sh')['-c', cmd]
            # case 2. Running the executable directly, w/ arguments, NO redirection
            #         ie. ncap2,  cmd = exe(the_exe)[the_args]
            # case 3. Runnng the command and logging the output to
            #         log_dest
            if run_inshell:
                if log_theoutput:
                    log_dest = self.cmdlog_destination()
                    cmd = exe('sh')['-c', cmd].err2out() >> log_dest
                else:
                    cmd = exe('sh')['-c', cmd]

            else:
                the_exe = shlex.split(cmd)[0]
                the_args = shlex.split(cmd)[1:]
                if log_theoutput:
                    log_dest = self.cmdlog_destination()
                    cmd = exe(the_exe)[the_args].err2out() >> log_dest
                else:
                    cmd = exe(the_exe)[the_args]


        self.logger.info("RUNNING: %s" % cmd.to_shell())
        self.logger.debug("RUNNING %s" % repr(cmd))

        ret = 0
        # run app unless DO_NOT_RUN_EXE is set to True
        if not self.config.getbool('config', 'DO_NOT_RUN_EXE', False):
            ret = run(cmd, **kwargs)

        return (ret, cmd)

    # TODO: Refactor seriesbylead.
    # For now we are back to running through a shell.
    # Can not run its cmd string, unless we run through a shell.

    # TODO refactor commands that are redirecting to a file.
    # They should be brought in to the produtil framework
    # the commands should not be required to run through a shell
    # in order to work. we can either capture the output and write
    # to a file or pass in the output_file and build the runner
    # object usng exe('ncump')['file.nc'].out(output_file,append=False)

    # The non met command where ismetcmd=False and log_theoutput=False block above
    # was created specfically for running any command that is capturing its
    # output to a file. Such as in series by lead.
    # ie. cmd = '/usr/local/bin/ncdump ...series_F006/min.nc > .../min.txt'
    # The way those commands,as of 2018Apr20, are being defined,
    # the > redirection is in the command. We don't want
    # to send the command cmd output to a log file, it will mess up the
    # intention. Also, cmd can not be run when decontructed with shlex
    # You can't have a redirect symbol as an argument, it gets quoted
    # and I'm not sure how to get around that ...
    # /usr/local/bin/ncdump ...series_F006/min.nc ">" .../min.txt
    # We don't want to use run_cmd since that function may redirect
    # output to a log file.

    # if cmdlog=None. The returned value is either the METplus log
    # or None
    def cmdlog_destination(self, cmdlog=None):
        """!Returns the location of where the command output will be sent.
           The METplus log, the MET log, or tty.
           Args:
               @param cmdlog: The cmdlog is a filename, any path info is removed.
                              It is joined with LOG_DIR. If cmdlog is None,
                              output is sent to either the METplus log or TTY.
               @returns log_dest: The destination of where to send the command output.
        """

        # Check the cmdlog argument.
        # ie. if cmdlog = '', or '/', or trailing slash /path/blah.log/ etc...,
        # os.path.basename returns '', and we can't write to '',
        # so set cmdlog to None.
        if cmdlog:
            cmdlog = os.path.basename(cmdlog)
            if not cmdlog: cmdlog = None

        # Set the default destination to None, which will be TTY
        cmdlog_dest = None

        # metpluslog is the setting used to determine if output is sent to either
        # a log file or tty.
        # metpluslog includes /path/filename.
        metpluslog = self.config.getstr('config', 'LOG_METPLUS', '')

        # This block determines where to send the command output, cmdlog_dest.
        # To the METplus log, a MET log, or tty.
        # If no metpluslog, cmlog_dest is None, which should be interpreted as tty.
        if metpluslog:
            log_met_output_to_metplus = self.config.getbool('config', 'LOG_MET_OUTPUT_TO_METPLUS')
            self.logger.debug('LOG_MET_OUTPUT_TO_METPLUS log file is %s'% repr(log_met_output_to_metplus))
            # If cmdlog is None send output to metpluslog.
            if log_met_output_to_metplus or not cmdlog:
                cmdlog_dest = metpluslog
            else:
                log_timestamp = self.config.getstr('config', 'LOG_TIMESTAMP', '')
                if log_timestamp:
                    cmdlog_dest = os.path.join(self.config.getdir('LOG_DIR'),
                                            cmdlog + '_' + log_timestamp)
                else:
                    cmdlog_dest = os.path.join(self.config.getdir('LOG_DIR'),cmdlog)


        # If cmdlog_dest None we will not redirect output to a log file
        # when building the Runner object, so it will end up going to tty.
        return cmdlog_dest

    # This method SHOULD ONLY BE USED by wrappers that build their cmd
    # outside of the command_builder.py get_command() method
    # ie. such as tc_pairs wrapper.  Objects that fully use the CommandBuilder
    # already have the metverbosity set in the command.
    def insert_metverbosity_opt(self,cmd=None):
        """!Returns the cmd with the verbosity option inserted
           and set after the first space found in the cmd string or
           after the cmd string if there are no spaces.

           There is NO CHECKING to see if the verbosity is already
           inserted in the command. If cmd is None, None is returned.

           Args:
               @param cmd: One string, The cmd string to insert the -v option.
               @returns cmd: The cmd string w/ -v <level:1-5> inserted
                             after the first white space or end if no
                             spaces. If cmd is None, None is returned.
        """

        if cmd:

            verbose_opt = " -v "+str(self.verbose) + " "
            # None splits on whitespace space, tab, newline, return, formfeed
            cmd_split = cmd.split(None, 1)

            # Handle two cases of splitting.
            # /path/to/cmd
            # /path/to/cmd blah blah blah ....
            if len(cmd_split) == 1:
                cmd = cmd_split[0] + verbose_opt
            elif len(cmd_split) == 2:
                cmd = cmd_split[0] + verbose_opt + cmd_split[1]
            else:
                self.logger.debug('Can not Insert MET verbosity option, '
                                  'command unchanged, using: %s .' % repr(cmd))

        return cmd

# TODO: Need to add methods for various runner types exe, mpirun for POE etc
