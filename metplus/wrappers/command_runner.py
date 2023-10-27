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
from datetime import datetime


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
        self.log_met_to_metplus = config.getbool('config',
                                                 'LOG_MET_OUTPUT_TO_METPLUS')

    def run_cmd(self, cmd, env=None, log_path=None, copyable_env=None, **kwargs):
        """!The command cmd is a string which is converted to a produtil
        exe Runner object and than run. Output of the command may also
        be redirected to either METplus log, MET log, or TTY.

        Some subclasses of CommandBuilder ie. series_by_init_wrapper, run
        non MET commands ie. convert, in addition to MET binary commands,
        ie. regrid_data_plane.

        @param cmd: A string, Command used in the produtil exe Runner object.
        @param env: Default None, environment for run to pass in, uses
         os.environ if not set.
        @param log_path: Path to log file or None if logging to terminal
        @param copyable_env string of commands that set environment variables
        that can be copy/pasted by the user or None
        @param kwargs Other options sent to the produtil Run constructor
        """
        if cmd is None:
            return cmd

        # if env not set, use os.environ
        env = os.environ if env is None else env

        self.logger.info("COMMAND: %s" % cmd)

        # don't run app if DO_NOT_RUN_EXE is set to True
        if self.skip_run:
            self.logger.info("Not running command (DO_NOT_RUN_EXE = True)")
            return 0, cmd

        # determine if command must be run in a shell
        run_inshell = '*' in cmd or ';' in cmd or '<' in cmd or '>' in cmd

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
        if log_path:
            self.logger.debug("Logging command output to: %s" % log_path)
            self.log_header_info(log_path, copyable_env, cmd)

            if run_inshell:
                cmd_exe = exe('sh')['-c', cmd].env(**env).err2out() >> log_path
            else:
                cmd_exe = exe(the_exe)[the_args].env(**env).err2out() >> log_path
        else:
            if run_inshell:
                cmd_exe = exe('sh')['-c', cmd].env(**env)
            else:
                cmd_exe = exe(the_exe)[the_args].env(**env).err2out()

        # get current time to calculate total time to run command
        start_cmd_time = datetime.now()

        # run command
        try:
            ret = run(cmd_exe, **kwargs)
        except Exception:
            ret = -1
        else:
            # calculate time to run
            end_cmd_time = datetime.now()
            total_cmd_time = end_cmd_time - start_cmd_time
            self.logger.info(f'Finished running {the_exe} '
                             f'- took {total_cmd_time}')

        return ret, cmd

    def log_header_info(self, log_path, copyable_env, cmd):
        with open(log_path, 'a+') as log_file_handle:
            # if logging MET command to its own log file,
            # add command that was run to that log
            if not self.log_met_to_metplus:
                # if environment variables were set and available,
                # write them to MET tool log
                if copyable_env:
                    log_file_handle.write(
                        "\nCOPYABLE ENVIRONMENT FOR NEXT COMMAND:\n")
                    log_file_handle.write(f"{copyable_env}\n\n")
                else:
                    log_file_handle.write('\n')

                log_file_handle.write(f"COMMAND:\n{cmd}\n\n")

            # write line to designate where MET tool output starts
            log_file_handle.write("OUTPUT:\n")
