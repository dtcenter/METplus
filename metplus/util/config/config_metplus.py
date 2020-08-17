"""
Program Name: config_metplus.py
Contact(s): George McCabe, Julie Prestopnik, Jim Frimel, Minna Win
Abstract:
History Log:  Initial version
Usage: Used to read the configuration files to setup the METplus wrappers
Parameters: None
Input Files: N/A
Output Files: N/A
"""

import os
import sys
import logging

import produtil.setup
import getopt
import argparse

from . import config_launcher

# pylint:disable=pointless-string-statement
'''!@namespace config_metplus
The initial METplus configure script for parsing the command line
options, arguments and setting up the METPLUS_CONF file.
This module setup() function should be called at the start of each task to
setup a configuration object used by all the processing tasks.
Each task that calls this MUST have run produtil.setup
'''

##@var __all__
# All symbols exported by "from config_metplus import *"
__all__ = ['usage', 'setup']

##@var logger
def usage(filename=None):
    """! How to call this function.
    @param filename the filename of the calling module.
    """

    if filename:
        filename = os.path.basename(filename)

    # Note: runtime option is not being used. remove it ?
    # -r|--runtime <arg0>     Specify initialization time to process
    print ('''
Usage: %s [ -c /path/to/additional/file.conf]...[] [options]
    -c|--config <arg0>      Specify custom configuration file to use
    -h|--help               Display this usage statement

Optional arguments: [options]
section.option=value -- override conf options on the command line
/path/to/parmfile.conf -- additional conf files to parse

'''%(filename))
    sys.exit(2)

def setup(baseinputconfs, filename=None, logger=None):
    """!The METplus setup function.
    @param filename the filename of the calling module.
    @param logger a logging.logger for log messages

    The setup function that process command line options
    and arguements and returns a configuration object."""

    # Used for logging and usage statment
    if filename is None:
        filename = sys._getframe().f_code.co_filename

    # Setup Task logger, Until a Conf object is created, Task logger is
    # only logging to tty, not a file.
    if logger is None:
        logger = logging.getLogger('metplus')

    logger.info('Starting METplus configuration setup.')

    # read command line arguments

    # if not arguments were provided, print usage and exit
    if len(sys.argv) < 2:
        usage(filename)

    # print usage statement and exit if help arg is found
    help_args = ('-h', '--help', '-help')
    for help_arg in help_args:
        if help_arg in sys.argv:
            print("USAGE")
            sys.exit(0)

    # pull out command line arguments
    args = []
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            # ignore -c and --config since they are now optional
            if arg == '-c' or arg == '--config' or arg == '-config':
                continue

            # error/exit if an argument that is not supported was used
            logger.critical('Invalid argument: %s.' % arg)
            usage(filename)

        # split up comma separated lists into individual items
        # and add each to list of arguments
        # NOTE: to support lists in a config variable override,
        # this logic will have to be enhanced
        # i.e. config.PROCESS_LIST=PCPCombine,GridStat
        args.extend(arg.split(','))

    # if no valid args were found, print usage and exit
    if not args:
        usage(filename)

    # parm, is path to parm directory
    # infiles, list of input conf files to be read and processed
    # moreopt, dictionary of conf file settings, passed in from command line.
    (parm, infiles, moreopt) = \
        config_launcher.parse_launch_args(args,
                                          usage,
                                          filename,
                                          logger,
                                          baseinputconfs)

    # Currently metplus is not handling cycle.
    # Therefore can not use conf.timestrinterp and
    # some conf file settings ie. {[a|f]YMDH} time settings.
    cycle = None
    conf = config_launcher.launch(infiles, moreopt, cycle=cycle)
    #conf.sanity_check()

    # save list of user configuration files in a variable
    conf.set('config', 'METPLUS_CONFIG_FILES', ','.join(args))

    logger.info('Completed METplus configuration setup.')

    return conf

class METplusLogFormatter(logging.Formatter):
    def __init__(self, config):
        self.default_fmt = config.getraw('config', 'LOG_LINE_FORMAT')
        self.info_fmt = config.getraw('config', 'LOG_INFO_LINE_FORMAT', self.default_fmt)
        self.debug_fmt = config.getraw('config', 'LOG_DEBUG_LINE_FORMAT', self.default_fmt)
        self.error_fmt = config.getraw('config', 'LOG_ERR_LINE_FORMAT', self.default_fmt)
        super().__init__(fmt=self.default_fmt,
                         datefmt=config.getraw('config', 'LOG_LINE_DATE_FORMAT'),
                         style='%')

    def format(self, record):
        if record.levelno == logging.ERROR:
            self._style._fmt = self.error_fmt
        elif record.levelno == logging.DEBUG:
            self._style._fmt = self.debug_fmt
        elif record.levelno == logging.INFO:
            self._style._fmt = self.info_fmt

        output = logging.Formatter.format(self, record)

        # restore default format
        self._style._fmt = self.default_fmt

        return output

# You can run this module from the command line, that is  __main__
# However, this module is intended to be imported and run via setup function.
if __name__ == "__main__":
    try:
        # If jobname is not defined, in log it is 'NO-NAME'
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='run-config_metplus',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run-config_metplus')
        produtil.log.postmsg('config_metplus is starting')

        setup()
        produtil.log.postmsg('config_metplus completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'config_metplusfailed: %s' % (str(e),), exc_info=True)
        sys.exit(2)
