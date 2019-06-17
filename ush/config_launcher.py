from __future__ import print_function
import os
import re
import sys
import logging
import collections
import datetime
import produtil.fileop
import produtil.run
import produtil.log
# from produtil.fileop import isnonempty
# from produtil.run import batchexe, run, checkrun
# from produtil.log import jlogger
from os.path import dirname, realpath
# from random import Random
from produtil.config import ProdConfig
import met_util as util
from config_wrapper import ConfigWrapper

"""!Creates the initial METplus directory structure,
loads information into each job.

This module is used to create the initial METplus conf file in the
first METplus job via the metplus.config_launcher.launch().
The metplus.config_launcher.load() then reloads that configuration.
The launch() function does more than just create the conf file though.
It creates several initial files and  directories and runs a sanity check
on the whole setup.

The METplusLauncher class is used in place of a produtil.config.ProdConfig
throughout the METplus system.  It can be used as a drop-in replacement
for a produtil.config.ProdConfig, but has additional features needed to
support sanity checks, and initial creation of the METplus system.
"""

'''!@var __all__
All symbols exported by "from metplus.launcher import *"
'''
__all__ = ['load', 'launch', 'parse_launch_args', 'load_baseconfs',
           'METplusLauncher']

# baseinputconfs = ['metplus.conf','metplus.override.conf','usecase.conf']
# baseinputconfs = ['metplus.conf']
baseinputconfs = ['metplus_config/metplus_system.conf',
                  'metplus_config/metplus_data.conf',
                  'metplus_config/metplus_runtime.conf',
                  'metplus_config/metplus_logging.conf']

# Note: This is just a developer reference comment, in case we continue
# extending the metplus capabilities, by following hwrf patterns.
# These metplus configuration variables map to the following
# HWRF variables.
# METPLUS_BASE == HOMEmetplus, OUTPUT_BASE == WORKmetplus
# METPLUS_CONF == CONFmetplus, METPLUS_USH == USHmetplus
# PARM_BASE == PARMmetplus

'''!@var METPLUS_BASE
The METplus installation directory
'''
METPLUS_BASE = None

'''!@var METPLUS_USH
The ush/ subdirectory of the METplus installation directory
'''
METPLUS_USH = None

'''!@var PARM_BASE
The parameter directory
'''
PARM_BASE = None

if os.environ.get('METPLUS_BASE', ''):
    METPLUS_BASE = os.environ['METPLUS_BASE']
if os.environ.get('METPLUS_USH', ''):
    METPLUS_USH = os.environ['METPLUS_USH']
if os.environ.get('PARM_BASE', ''):
    PARM_BASE = os.environ['PARM_BASE']

# Based on METPLUS_BASE, Will set METPLUS_USH, or PARM_BASE if not
# already set in the environment.
if METPLUS_BASE is None:
    METPLUS_BASE = dirname(dirname(realpath(__file__)))
    USHguess = os.path.join(METPLUS_BASE, 'ush')
    PARMguess = os.path.join(METPLUS_BASE, 'parm')
    if os.path.isdir(USHguess) and os.path.isdir(PARMguess):
        if METPLUS_USH is None:
            METPLUS_USH = USHguess
        if PARM_BASE is None:
            PARM_BASE = PARMguess
else:
    if os.path.isdir(METPLUS_BASE):
        if METPLUS_USH is None:
            METPLUS_USH = os.path.join(METPLUS_BASE, 'ush')
        if PARM_BASE is None:
            PARM_BASE = os.path.join(METPLUS_BASE, 'parm')
    else:
        print("$METPLUS_BASE is not a directory: {} \n"
              "Please set $METPLUS_BASE "
              "in the environment.".format(METPLUS_BASE), file=sys.stderr)
        sys.exit(2)

# For METplus, this is assumed to already be set.
if METPLUS_USH not in sys.path:
    sys.path.append(METPLUS_USH)


# def parse_launch_args(args,usage,logger,PARM_BASE=None):
# This is intended to be use to gather all the conf files on the
# command line, along with overide options on the command line.
# This includes the default conf files metplus.conf, metplus.override.conf
# along with, -c some.conf and any other conf files...
# These are than used by def launch to create a single metplus final conf file
# that would be used by all tasks.
def parse_launch_args(args, usage, filename, logger):
    """!Parsed arguments to scripts that launch the METplus system.

    This is the argument parser for the config_metplus.py
    script.  It parses the arguments (in args).
    If something goes wrong, this function calls
    sys.exit(1) or sys.exit(2).

    Options:
    * section.variable=value --- set this value in this section, no matter what
    * /path/to/file.conf --- read this conf file after the default conf files.

    Later conf files override earlier ones.  The conf files read in
    are:
    * metplus.conf

    @param args the script arguments, after script-specific ones are removed
    @param usage a function called to provide a usage message
    @param filename the module from which this was called
    @param logger a logging.Logger for log messages"""

    # stub
    # if test for something fails:
    #    usage(filename,logger)

    parm = os.path.realpath(PARM_BASE)

    # Files in this list, that don't exist or are empty,
    # will be silently ignored.
    # infiles=[ os.path.join(parm, 'metplus.conf'),
    #          os.path.join(parm, 'metplus.override.conf')
    #         ]
    infiles = list()
    for filename in baseinputconfs:
        infiles.append(os.path.join(parm, filename))

    moreopt = collections.defaultdict(dict)

    if args is None:
        return (parm, infiles, moreopt)

    # Now look for any option and conf file arguments:
    bad = False
    for iarg in range(len(args)):
        m = re.match('''(?x)
          (?P<section>[a-zA-Z][a-zA-Z0-9_]*)
           \.(?P<option>[^=]+)
           =(?P<value>.*)$''', args[iarg])
        if m:
            logger.info('Set [%s] %s = %s' % (
                m.group('section'), m.group('option'),
                repr(m.group('value'))))
            moreopt[m.group('section')][m.group('option')] = m.group('value')
        elif os.path.exists(args[iarg]):
            infiles.append(args[iarg])
        elif os.path.exists(os.path.join(parm, args[iarg])):
            infiles.append(os.path.join(parm, args[iarg]))
        else:
            bad = True
            logger.error('%s: invalid argument.  Not an config option '
                         '(a.b=c) nor a conf file.' % (args[iarg],))
    if bad:
        sys.exit(2)

    for file in infiles:
        if not os.path.exists(file):
            logger.error(file + ': conf file does not exist.')
            sys.exit(2)
        elif not os.path.isfile(file):
            logger.error(file + ': conf file is not a regular file.')
            sys.exit(2)
        elif not produtil.fileop.isnonempty(file):
            logger.warning(
                file + ': conf file is empty.  Will continue anyway.')
    return (parm, infiles, moreopt)


# This is intended to be used to create and write a final conf file
# that is used by all tasks .... though METplus isn't being run
# that way .... instead METplus tasks need to be able to run stand-alone
# so each task needs to be able to initialize the conf files.
# conf files are processed in the order they exist in the file_list
# so each succesive element overwrites the previous.
def launch(file_list, moreopt, cycle=None, init_dirs=True,
           prelaunch=None):
    for filename in file_list:
        if not isinstance(filename, str):
            raise TypeError('First input to metplus.config.for_initial_job '
                            'must be a list of strings.')

    conf = METplusLauncher()
    logger = conf.log()
    cu = ConfigWrapper(conf, logger)

    # set config variable for current time
    conf.set('config', 'CLOCK_TIME', datetime.datetime.now().strftime('%Y%m%d%H%M%S'))

    # Read in and parse all the conf files.
    for filename in file_list:
        conf.read(filename)
        logger.info("%s: Parsed this file" % (filename,))

    # Overriding or passing in specific conf items on the command line
    # ie. config.NEWVAR="a new var" dir.SOMEDIR=/override/dir/path
    # If spaces, seems like you need double quotes on command line.
    if moreopt:
        for section, options in moreopt.iteritems():
            if not conf.has_section(section):
                conf.add_section(section)
            for option, value in options.iteritems():
                logger.info('Override: %s.%s=%s'
                            % (section, option, repr(value)))
                conf.set(section, option, value)

    # All conf files and command line options have been parsed.
    # So lets set and add specific log variables to the conf object
    # based on the conf log template values.
    util.set_logvars(conf)


    # Determine if final METPLUS_CONF file already exists on disk.
    # If it does, use it instead.
    confloc = conf.getloc('METPLUS_CONF')

    # Received feedback: Users want to overwrite the final conf file if it exists.
    # Not overwriting is annoying everyone, since when one makes a conf file edit
    # you have to remember to remove the final conf file.
    # Originally based on a hwrf workflow. since launcher task only runs once, 
    # and all following tasks use the generated conf file.
    #finalconfexists = util.file_exists(confloc)

    # Force setting to False, so conf always gets overwritten
    finalconfexists = False

    if finalconfexists:
        logger.warning(
            'IGNORING all parsed conf file(s) AND any command line options or arguments, if given.')
        logger.warning('INSTEAD, Using Existing final conf:  %s' % (confloc))
        del logger
        del conf
        conf = METplusLauncher()
        logger = conf.log()
        conf.read(confloc)
        # Set moreopt to None, in case it is not None, We do not want to process
        # more options since using existing final conf file.
        moreopt = None



    # Place holder for when workflow is developed in METplus.
    # rocoto does not initialize the dirs, it returns here.
    # if not init_dirs:
    #    if prelaunch is not None:
    #        prelaunch(conf,logger,cycle)
    #    return conf

    # Initialize the output directories
    produtil.fileop.makedirs(cu.getdir('OUTPUT_BASE', logger), logger=logger)
    # A user my set the confloc METPLUS_CONF location in a subdir of OUTPUT_BASE
    # or even in another parent directory altogether, so make thedirectory
    # so the metplus_final.conf file can be written.
    if not os.path.exists(realpath(dirname(confloc))):
        produtil.fileop.makedirs(realpath(dirname(confloc)), logger=logger)

    # set METPLUS_BASE conf to location of scripts used by METplus
    # warn if user has set METPLUS_BASE to something different
    # in their conf file
    user_metplus_base = cu.getdir('METPLUS_BASE', '')
    if user_metplus_base != '' and user_metplus_base != METPLUS_BASE:
        logger.warning('METPLUS_BASE from the conf files has no effect.'+\
                       ' Overriding to '+METPLUS_BASE)
    conf.set('dir','METPLUS_BASE', METPLUS_BASE)

    version_number = util.get_version_number()
    conf.set('config', 'METPLUS_VERSION', version_number)

    # logger.info('Expand certain [dir] values to ensure availability ')
    #            'before vitals parsing.
    # frimel: Especially before vitals parsing. THIS IS ONLY NEEDED in
    # order to define the vit dictionary and use of vit|{somevar} in the
    # conf file.
    for var in ('OUTPUT_BASE', 'METPLUS_BASE'):
        expand = cu.getdir(var)
        logger.info('Replace [dir] %s with %s' % (var, expand))
        conf.set('dir', var, expand)


    # Place holder for when workflow is developed in METplus.
    # if prelaunch is not None:
    #    prelaunch(conf,logger,cycle)

    # writes the METPLUS_CONF used by all tasks.
    if not finalconfexists:
        logger.info('METPLUS_CONF: %s written here.' % (confloc,))
        with open(confloc, 'wt') as f:
            conf.write(f)
    return conf


def load(filename):
    """!Loads the METplusLauncher created by the launch() function.

    Creates an METplusConfig object for a METplus workflow that was
    previously initialized by metplus.config_launcher.launch.
    The only argument is the name of the config file produced by
    the launch command.

    @param filename The metplus*.conf file created by launch()"""

    conf = METplusLauncher()
    conf.read(filename)
    return conf


# A METplus Demonstration work-around ...
# Assumes and reads in only baseconfs and -c add_conf_file
# This allows calling from both master_metplus.py and via
# the command line from an individual module, such as series_by_lead.py
def load_baseconfs(add_conf_file=None):
    """ Loads the following conf files """

    parm = os.path.realpath(PARM_BASE)

    # baseconfs=[ os.path.join(parm, 'metplus.conf'),
    #          os.path.join(parm, 'metplus.override.conf')
    #         ]

    conf = ProdConfig()
    logger = conf.log()

    for filename in baseinputconfs:
        conf_file = os.path.join(parm, filename)
        logger.info("%s: Parse this file" % (conf_file,))
        conf.read(conf_file)

    # Read the added conf file last, after the base input confs.
    # Since these settings will override.
    if add_conf_file:
        conf_file = set_conf_file_path(add_conf_file)
        logger.info("%s: Parse this file" % (conf_file,))
        conf.read(conf_file)

    return conf


def set_conf_file_path(conf_file):
    return _set_conf_file_path(conf_file)


# This is meant to be used with the -c option in METplus
# for backward compatability, since users using the -c option
# are not required to add path information and the previous
# constants object found it since it was pulled in via the import
# statement and the parm directory was defined in the PYTHONPATH
def _set_conf_file_path(conf_file):
    """Do not call this directly.  It is an internal implementation
    routine. It is only used internally and is called when adding an
    additional conf using the -c command line option.

    Adds the path information to the conf file if there isn't any.
    """
    parm = os.path.realpath(PARM_BASE)

    # Determine if add_conf_file has path information /path/to/file.conf
    # If not head than there is no path information, only a filename,
    # so assUme the conf file is in the parm directory, and add that
    # parm path information
    head, tail = os.path.split(conf_file)
    if not head:
        new_conf_file = os.path.join(parm, conf_file)
        return new_conf_file

    return conf_file

# Really should have called this class METPlusConfig
class METplusLauncher(ProdConfig):
    """!A replacement for the produtil.config.ProdConfig used throughout
    the METplus system.  You should never need to instantiate one of
    these --- the launch() and load() functions do that for you.  This
    class is the underlying implementation of most of the
    functionality described in launch() and load()"""

    def __init__(self, conf=None):
        """!Creates a new METplusLauncher
        @param conf The configuration file."""
        super(METplusLauncher, self).__init__(conf)
        self._cycle = None
        self._logger=logging.getLogger('metplus')
        logger = self._logger

    ##@var _cycle
    # The cycle for this METplus run.

    # Overrides method in ProdConfig
    def log(self,sublog=None):
        """!returns a logging.Logger object

        Returns a logging.Logger object.  If the sublog argument is
        provided, then the logger will be under that subdomain of the
        "metplus" logging domain.  Otherwise, this METpluslauncher's logger
        (usually the "metplus" domain) is returned.
        @param sublog the logging subdomain, or None
        @returns a logging.Logger object"""
        if sublog is not None:
            with self:
                return logging.getLogger('metplus.'+sublog)
        return self._logger

    def sanity_check(self):
        """!Runs nearly all sanity checks.

        Runs simple sanity checks on the METplus installation directory
        and configuration to make sure everything looks okay.  May
        throw a wide variety of exceptions if sanity checks fail."""
        logger = self.log('sanity.checker')
