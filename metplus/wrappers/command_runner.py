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
import shlex
from datetime import datetime, timezone

class CommandRunner(object):
    """! Class for Creating and Running External Programs
    """
    def __init__(self, config, logger=None, verbose=2, skip_run=False):
        """!Class for Creating and Running External Programs.
            It was intended to handle the MET executables but
            can be used by other executables."""
        self.logger = logger
        self.config = config
        self.verbose = verbose
        self.skip_run = skip_run
        self.log_command_to_met_log = False

    def run_cmd(self, cmd, env=None, log_name=None,
                copyable_env=None, **kwargs):
        """!The command cmd is a string which is converted to a produtil
        exe Runner object and than run. Output of the command may also
        be redirected to either METplus log, MET log, or TTY.

        Some subclasses of CommandBuilder ie. series_by_init_wrapper, run
        non MET commands ie. convert, in addition to MET binary commands,
        ie. regrid_data_plane.

        Args:
            @param cmd: A string, Command used in the produtil exe Runner object.
            @param env: Default None, environment for run to pass in, uses
            os.environ if not set.
            @param log_name: Used only when ismetcmd=True, The name of the exectable
            being run.
            @param kwargs Other options sent to the produtil Run constructor
        """

        if cmd is None:
            return cmd

        # if env not set, use os.environ
        if env is None:
            env = os.environ

        self.logger.info("COMMAND: %s" % cmd)

        # don't run app if DO_NOT_RUN_EXE is set to True
        if self.skip_run:
            self.logger.info("Not running command (DO_NOT_RUN_EXE = True)")
            return 0, cmd

        # self.log_name MUST be defined in the subclass' constructor,
        # this code block is a safety net in case that was not done.
        # self.log_name is used to generate the MET log output name,
        # if output is directed there, based on the conf settings.
        #
        # cmd.split()[0] 'should' be the /path/to/<some_met_binary>
        if not log_name:
            log_name = os.path.basename(cmd.split()[0])
            self.logger.warning('MISSING self.log_name, '
                                'setting name to: %s' % repr(log_name))
            self.logger.warning('Fix the code and edit the following objects'
                                ' contructor: %s, ' % repr(self))

        # Determine where to send the output from the MET command.
        log_dest = self.cmdlog_destination(cmdlog=log_name+'.log')

        # determine if command must be run in a shell
        run_inshell = False
        if '*' in cmd or ';' in cmd or '<' in cmd or '>' in cmd:
            run_inshell=True

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
            self.logger.debug("log_name is: %s, output sent to: %s" % (log_name, log_dest))

            self.log_header_info(log_dest, copyable_env, cmd)

            if run_inshell:
                cmd_exe = exe('sh')['-c', cmd].env(**env).err2out() >> log_dest
            else:
                cmd_exe = exe(the_exe)[the_args].env(**env).err2out() >> log_dest
        else:
            if run_inshell:
                cmd_exe = exe('sh')['-c', cmd].env(**env)
            else:
                cmd_exe = exe(the_exe)[the_args].env(**env).err2out()

        # get current time to calculate total time to run command
        start_cmd_time = datetime.now(timezone.utc)

        # run command
        try:
            ret = run(cmd_exe, **kwargs)
        except:
            ret = -1
        else:
            # calculate time to run
            end_cmd_time = datetime.now(timezone.utc)
            total_cmd_time = end_cmd_time - start_cmd_time
            self.logger.debug(f'Finished running {the_exe} '
                              f'in {total_cmd_time}')

        return ret, cmd

    def log_header_info(self, log_dest, copyable_env, cmd):
        with open(log_dest, 'a+') as log_file_handle:
            # if logging MET command to its own log file, add command that was run to that log
            if self.log_command_to_met_log:
                # if environment variables were set and available, write them to MET tool log
                if copyable_env:
                    log_file_handle.write(
                        "\nCOPYABLE ENVIRONMENT FOR NEXT COMMAND:\n")
                    log_file_handle.write(f"{copyable_env}\n\n")
                else:
                    log_file_handle.write('\n')

                log_file_handle.write(f"COMMAND:\n{cmd}\n\n")

            # write line to designate where MET tool output starts
            log_file_handle.write("OUTPUT:\n")

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

        self.log_command_to_met_log = False

        # This block determines where to send the command output, cmdlog_dest.
        # To the METplus log, a MET log, or tty.
        # If no metpluslog, cmlog_dest is None, which should be interpreted as tty.
        if metpluslog:
            log_met_output_to_metplus = self.config.getbool('config',
                                                     'LOG_MET_OUTPUT_TO_METPLUS')
            # If cmdlog is None send output to metpluslog.
            if log_met_output_to_metplus or not cmdlog:
                cmdlog_dest = metpluslog
            else:
                self.log_command_to_met_log = True
                log_timestamp = self.config.getstr('config', 'LOG_TIMESTAMP', '')
                if log_timestamp:
                    cmdlog_dest = os.path.join(self.config.getdir('LOG_DIR'),
                                            cmdlog + '.' + log_timestamp)
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
