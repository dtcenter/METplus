#!/usr/bin/env python
from __future__ import print_function

import logging
import os
import shutil
import sys
import datetime
import errno
import time
import calendar
import re
import gzip
import bz2
import zipfile
from collections import namedtuple
import struct
from csv import reader

import subprocess
from produtil.run import exe
from produtil.run import runstr,alias
from string_template_substitution import StringSub
from string_template_substitution import StringExtract
from gempak_to_cf_wrapper import GempakToCFWrapper
# for run stand alone
import produtil
import config_metplus


"""!@namespace met_util
 @brief Provides  Utility functions for METplus.
"""


def round_0p5(val):
    """! Round to the nearest point five (ie 3.3 rounds to 3.5, 3.1
       rounds to 3.0) Take the input value, multiply by two, round to integer
       (no decimal places) then divide by two.  Expect any input value of n.0,
       n.1, or n.2 to round down to n.0, and any input value of n.5, n.6 or
       n.7 to round to n.5. Finally, any input value of n.8 or n.9 will
       round to (n+1).0
       Args:
          @param val :  The number to be rounded to the nearest .5
       Returns:
          pt_five:  The n.0, n.5, or (n+1).0 value as
                            a result of rounding the input value, val.
    """

    val2 = val * 2
    rval = round_to_int(val2)
    pt_five = round(rval, 0) / 2
    return pt_five


def round_to_int(val):
    """! Round to integer value
         Args:
             @param val:  The value to round up
         Returns:
            rval:  The rounded up value.
    """
    val += 0.5
    rval = int(val)
    return rval


def mkdir_p(path):
    """!
       From stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
       Creates the entire directory path if it doesn't exist (including any
       required intermediate directories).
       Args:
           @param path : The full directory path to be created
       Returns
           None: Creates the full directory path if it doesn't exist,
                 does nothing otherwise.
    """

    try:
        # ***Note***:
        # For Python 3.2 and beyond, os.makedirs has a third optional argument,
        # exist_ok, that when set to True will enable the mkdir -p
        # functionality.
        # The mkdir -p functionality holds unless the mode is provided and the
        # existing directory has different permissions from the intended ones.
        # In this situation the OSError exception is raised.

        # default mode is octal 0777
        os.makedirs(path, mode=0775)
    except OSError as exc:
        # Ignore the error that gets created if the path already exists
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def _rmtree_onerr(function, path, exc_info, logger=None):
    """!Internal function used to log errors.
    This is an internal implementation function called by
    shutil.rmtree when an underlying function call failed.  See
    the Python documentation of shutil.rmtree for details.
    @param function the funciton that failed
    @param path the path to the function that caused problems
    @param exc_info the exception information
    @protected"""
    if logger:
        logger.warning('%s: %s failed: %s' % (
            str(path), str(function), str(exc_info)))


def rmtree(tree, logger=None):
    """!Deletes the tree, if possible.
       @protected
       @param tree the directory tree to delete"
       @param logger the logger, optional
    """
    try:
        # If it is a file, special file or symlink we can just
        # delete it via unlink:
        os.unlink(tree)
        return
    except EnvironmentError:
        pass
    # We get here for directories.
    if logger:
        logger.info('%s: rmtree' % (tree,))
    shutil.rmtree(tree, ignore_errors=False)


def set_logvars(config, logger=None):
    """!Sets and adds the LOG_METPLUS and LOG_TIMESTAMP
       to the config object. If LOG_METPLUS was already defined by the
       user in their conf file. It expands and rewrites it in the conf
       object and the final file.
       conf file.
       Args:
           @param config:   the config instance
           @param logger: the logger, optional
    """

    if logger is None:
        logger = config.log()

    # LOG_TIMESTAMP_TEMPLATE is not required in the conf file,
    # so lets first test for that.
    log_timestamp_template = config.getstr('config','LOG_TIMESTAMP_TEMPLATE','')
    if log_timestamp_template:
        # Note: strftime appears to handle if log_timestamp_template
        # is a string ie. 'blah' and not a valid set of % directives %Y%m%d,
        # it does return the string 'blah', instead of crashing.
        # However, I'm still going to test for a valid % directive and
        # set a default. It probably is ok to remove the if not block pattern
        # test, and not set a default, especially if causing some unintended
        # consequences or the pattern is not capturing a valid directive.
        # The reality is, the user is expected to have entered a correct
        # directive in the conf file.
        # This pattern is meant to test for a repeating set of
        # case insensitive %(AnyAlphabeticCharacter), ie. %Y%m ...
        # The basic pattern is (%+[a-z])+ , %+ allows for 1 or more
        # % characters, ie. %%Y, %% is a valid directive.
        # (?i) case insensitive, \A begin string \Z end of string
        if not re.match('(?i)\A(?:(%+[a-z])+)\Z', log_timestamp_template):
            logger.warning('Your LOG_TIMESTAMP_TEMPLATE is not '
                           'a valid strftime directive: %s' % repr(log_timestamp_template))
            logger.info('Using the following default: %Y%m%d%H')
            log_timestamp_template = '%Y%m%d%H'
        t = datetime.datetime.now()
        if config.getbool('config', 'LOG_TIMESTAMP_USE_DATATIME', False):
            if config.getbool('config', 'LOOP_BY_INIT'):
                t = datetime.datetime.strptime(config.getstr('config',
                                                             'INIT_BEG'),
                                               config.getstr('config',
                                                             'INIT_TIME_FMT'))
            else:
                t = datetime.datetime.strptime(config.getstr('config',
                                                             'VALID_BEG'),
                                               config.getstr('config',
                                                             'VALID_TIME_FMT'))
        log_filenametimestamp = t.strftime(log_timestamp_template)
    else:
        log_filenametimestamp=''

    log_dir = config.getdir('LOG_DIR')

    # NOTE: LOG_METPLUS or metpluslog is meant to include the absolute path
    #       and the metpluslog_filename,
    # so metpluslog = /path/to/metpluslog_filename

    # if LOG_METPLUS =  unset in the conf file, means NO logging.
    # Also, assUmes the user has included the intended path in LOG_METPLUS.
    user_defined_log_file = None
    if config.has_option('config','LOG_METPLUS'):
        user_defined_log_file = True
        # strinterp will set metpluslog to '' if LOG_METPLUS =  is unset.
        metpluslog = config.strinterp('config','{LOG_METPLUS}', \
                                    LOG_TIMESTAMP_TEMPLATE=log_filenametimestamp)

        # test if there is any path information, if there is, assUme it is as intended,
        # if there is not, than add log_dir.
        if metpluslog:
            if os.path.basename(metpluslog) == metpluslog:
                metpluslog = os.path.join(log_dir, metpluslog)
    else:
        # No LOG_METPLUS in conf file, so let the code try to set it,
        # if the user defined the variable LOG_FILENAME_TEMPLATE.
        # LOG_FILENAME_TEMPLATE is an 'unpublished' variable - no one knows
        # about it unless you are reading this. Why does this exist ?
        # It was from my first cycle implementation. I did not want to pull
        # it out, in case the group wanted a stand alone metplus log filename
        # template variable.

        # If metpluslog_filename includes a path, python joins it intelligently.
        # Set the metplus log filename.
        # strinterp will set metpluslog_filename to '' if LOG_FILENAME_TEMPLATE =
        if config.has_option('config', 'LOG_FILENAME_TEMPLATE'):
            metpluslog_filename = config.strinterp('config', '{LOG_FILENAME_TEMPLATE}',
                                                   LOG_TIMESTAMP_TEMPLATE=log_filenametimestamp)
        else:
            metpluslog_filename = ''
        if metpluslog_filename:
            metpluslog = os.path.join(log_dir, metpluslog_filename)
        else:
            metpluslog = ''



    # Adding LOG_TIMESTAMP to the final configuration file.
    logger.info('Adding: config.LOG_TIMESTAMP=%s' % repr(log_filenametimestamp))
    config.set('config','LOG_TIMESTAMP',log_filenametimestamp)

    # Setting LOG_METPLUS in the configuration object
    # At this point LOG_METPLUS will have a value or '' the empty string.
    if user_defined_log_file:
        logger.info('Replace [config] LOG_METPLUS with %s' % repr(metpluslog))
    else:
        logger.info('Adding: config.LOG_METPLUS=%s' % repr(metpluslog))
    # expand LOG_METPLUS to ensure it is available
    config.set('config', 'LOG_METPLUS', metpluslog)


def get_logger(config, sublog=None):
    """!This function will return a logger with a formatted file handler
    for writing to the LOG_METPLUS and it sets the LOG_LEVEL. If LOG_METPLUS is
    not defined, a logger is still returned without adding a file handler,
    but still setting the LOG_LEVEL.
       Args:
           @param config:   the config instance
           @param sublog the logging subdomain, or None
       Returns:
           logger: the logger
    """

    # Retrieve all logging related parameters from the param file
    log_dir = config.getdir('LOG_DIR')
    log_level = config.getstr('config', 'LOG_LEVEL')

    # TODO review, use builtin produtil.fileop vs. mkdir_p ?
    # import produtil.fileop
    # produtil.fileop.makedirs(log_dir,logger=None)

    # Check if the directory path for the log file exists, if
    # not create it.
    if not os.path.exists(log_dir):
        mkdir_p(log_dir)

    if sublog is not None:
        logger = config.log(sublog)
    else:
        logger = config.log()

    # Setting of the logger level from the config instance.
    # Check for log_level by Integer or LevelName.
    # Try to convert the string log_level to an integer and use that, if
    # it can't convert then we assume it is a valid LevelName, which
    # is what is should be anyway,  ie. DEBUG.
    # Note:
    # Earlier versions of python2 require setLevel(<int>), argument
    # to be an int. Passing in the LevelName, 'DEBUG' will disable
    # logging output. Later versions of python2 will accept 'DEBUG',
    # not sure which version that changed with, but the logic below
    # should work for all version. I know python 2.6.6 must be an int,
    # and python 2.7.5 accepts the LevelName.
    try:
        int_log_level = int(log_level)
        logger.setLevel(int_log_level)
    except ValueError:
        logger.setLevel(logging.getLevelName(log_level))

    # Make sure the LOG_METPLUS is defined. In this function,
    # LOG_METPLUS should already be defined in the config object,
    # even if it is empty, LOG_METPLUS =.
    if not config.has_option('config','LOG_METPLUS'):
        set_logvars(config)
    metpluslog = config.getstr('config', 'LOG_METPLUS', '')


    # TODO: Remove LOG_OUTPUT control variable.
    # This was the yes/no control variable from the first cycle logging
    # implementation to turn logging on or off. Instead LOG_METPLUS
    # is being used as the on/off switch, this is not being used.
    # I'm keeping it here until after the group review, in case it comes up
    # that folks want to define such a variable in the conf file.
    # If not used, Delete this comment and commented out code block below
    # and you are done, nothing else needs to be changed elsewhere
    # in the code base.
    #if config.getbool('config','LOG_OUTPUT',default=False,badtypeok=True):
    #    if not metpluslog:
    #        logger.warning('LOG_OUTPUT in conf file is yes, Looks like you want to log your output ?')
    #        logger.warning('However, LOG_METPLUS is not a valid file, I can not log your output.')
    #    else:
    #        logger.info('LOG_OUTPUT in your conf file is set to yes')
    #else:
    #    logger.info('LOG_OUTPUT in your conf file is set to no or not set.')
    #if metpluslog and config.getbool('config', 'LOG_OUTPUT', default=False, badtypeok=True):

    if metpluslog:
        # It is possible that more path, other than just LOG_DIR, was added
        # to the metpluslog, by either a user defining more path in
        # LOG_METPLUS or LOG_FILENAME_TEMPLATE definitions in their conf file.
        # So lets check and make more directory if needed.
        dirname = os.path.dirname(metpluslog)
        if not os.path.exists(dirname):
            mkdir_p(dirname)

        # set up the filehandler and the formatter, etc.
        # This matches the oformat log.py formatter of produtil
        # So terminal output will now match log files.
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d %(name)s (%(filename)s:%(lineno)d) "
            "%(levelname)s: %(message)s",
            "%m/%d %H:%M:%S")
        #logging.Formatter.converter = time.gmtime
        file_handler = logging.FileHandler(metpluslog, mode='a')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def file_exists(filename):
    """! Determines if a file exists
        NOTE:  Simply using os.path.isfile() is not a Pythonic way
               to check if a file exists.  You can
               still encounter a TOCTTOU bug
               "time of check to time of use"
               Instead, use the raising of
               exceptions, which is a Pythonic
               approach:
               try:
                   with open(filename) as fileobj:
                      pass # or do something fruitful
               except IOError as e:
                   logger.error("your helpful error message goes here")
        Args:
            @param filename:  the full filename (full path)
        Returns:
            boolean : True if file exists, False otherwise
    """

    try:
        return os.path.isfile(filename)
    except IOError:
        pass


def is_dir_empty(directory):
    """! Determines if a directory exists and is not empty
        Args:
           @param directory:  The directory to check for existence
                                       and for contents.
        Returns:
           True:  If the directory is empty
           False:  If the directory exists and isn't empty
    """
    if not os.listdir(directory):
        return True
    else:
        return False


def grep(pattern, infile):
    """! Python version of grep, searches the file line-by-line
        to find a match to the pattern. Returns upon finding the
        first match.
        Args:
            @param pattern:  The pattern to be matched
            @param infile:     The filename with full filepath in which to
                             search for the pattern
        Returns:
            line (string):  The matching string
    """

    matching_lines = []
    with open(infile, 'r') as file_handle:
        for line in file_handle:
            match = re.search(pattern, line)
            if match:
                matching_lines.append(line)
                # if you got here, you didn't find anything
    return matching_lines


def get_filepaths_for_grbfiles(base_dir):
    """! Generates the grb2 file names in a directory tree
       by walking the tree either top-down or bottom-up.
       For each directory in the tree rooted at
       the directory top (including top itself), it
       produces a tuple: (dirpath, dirnames, filenames).
       This solution was found on Stack Overflow:
       http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-
           directory-in-python#3207973
       **scroll down to the section with "Getting Full File Paths From a
       Directory and All Its Subdirectories"
    Args:
        @param base_dir: The base directory from which we
                      begin the search for grib2 filenames.
    Returns:
        file_paths (list): A list of the full filepaths
                           of the data to be processed.
    """

    # Create an empty list which will eventually store
    # all the full filenames
    file_paths = []

    # pylint:disable=unused-variable
    # os.walk returns tuple, we don't need to utilize all the returned
    # values in the tuple.

    # Walk the tree
    for root, directories, files in os.walk(base_dir):
        for filename in files:
            # add it to the list only if it is a grib file
            match = re.match(r'.*(grib|grb|grib2|grb2)$', filename)
            if match:
                # Join the two strings to form the full
                # filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
            else:
                continue
    return file_paths


def get_storm_ids(filter_filename, logger):
    """! Get each storm as identified by its STORM_ID in the filter file
        save these in a set so we only save the unique ids and sort them.
        Args:
            @param filter_filename:  The name of the filter file to read
                                       and extract the storm id
            @param logger:  The name of the logger for logging useful info
        Returns:
            sorted_storms (List):  a list of unique, sorted storm ids
    """
    # pylint:disable=protected-access
    # Need to call sys.__getframe() to get the filename and method/func
    # for logging information.

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    logger.debug('DEBUG|' + cur_function + '|' + cur_filename)

    # Initialize a set because we want unique storm ids.
    storm_id_list = set()
    empty_list = []

    # Check if the filter_filename is empty, if it
    # is, then return an empty list.
    if not os.path.isfile(filter_filename):
        return empty_list
    if os.stat(filter_filename).st_size == 0:
        return empty_list
    with open(filter_filename, "r") as fileobj:
        header = fileobj.readline().split()
        header_colnum = header.index('STORM_ID')
        for line in fileobj:
            storm_id_list.add(str(line.split()[header_colnum]))

    # sort the unique storm ids, copy the original
    # set by using sorted rather than sort.
    sorted_storms = sorted(storm_id_list)
    return sorted_storms


def get_files(filedir, filename_regex, logger):
    """! Get all the files (with a particular
        naming format) by walking
        through the directories.
        Args:
          @param filedir:  The topmost directory from which the
                           search begins.
          @param filename_regex:  The regular expression that
                                  defines the naming format
                                  of the files of interest.
       Returns:
          file_paths (string): a list of filenames (with full filepath)
    """
    # pylint:disable=protected-access
    # Need to call sys.__getframe() to get the filename and method/func
    # for logging information.

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    logger.debug("DEBUG|" + cur_filename + "|" + cur_function)
    file_paths = []

    # pylint:disable=unused-variable
    # os.walk returns a tuple. Not all returned values are needed.

    # Walk the tree
    for root, directories, files in os.walk(filedir):
        for filename in files:
            # add it to the list only if it is a match
            # to the specified format
            match = re.match(filename_regex, filename)
            if match:
                # Join the two strings to form the full
                # filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
            else:
                continue
    return file_paths


def get_name_level(var_combo, logger):
    """!   Retrieve the variable name and level from a list of
          variable/level combinations.
          Args:
             @param var_combo:  A combination of the variable and the level
                                 separated by '/'
          Returns:
             name,level: A tuple of name and level derived from the
                         name/level combination.
    """

    # pylint:disable=protected-access
    # Need to call sys.__getframe() to get the filename and method/func
    # for logging information.
    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    logger.debug("DEBUG|" + cur_function + "|" + cur_filename)

    match = re.match(r'(.*)/(.*)', var_combo)
    name = match.group(1)
    level = match.group(2)

    return name, level


def check_for_tiles(tile_dir, fcst_file_regex, anly_file_regex, logger):
    """! Checks for the presence of forecast and analysis
        tiles that were created by extract_tiles
        Args:
            @param tile_dir:  The directory where the expected
                              tiled files should reside.
            @param fcst_file_regex: The regexp describing the format of the
                                    forecast tile file.
            @param anly_file_regex: The regexp describing the format of the
                                    analysis tile file.
            @param logger:    The logger to which all log messages
                                should be directed.
        Returns:
            None  raises OSError if expected files are missing
    """
    anly_tiles = get_files(tile_dir, anly_file_regex, logger)
    fcst_tiles = get_files(tile_dir, fcst_file_regex, logger)

    num_anly_tiles = len(anly_tiles)
    num_fcst_tiles = len(fcst_tiles)

    # Check that there are analysis and forecast tiles
    # (which were, or should have been created earlier by extract_tiles).
    if not anly_tiles:
        # Cannot proceed, the necessary 30x30 degree analysis tiles are missing
        logger.error("ERROR: No anly tile files were found  " + tile_dir)
        raise OSError("No 30x30 anlysis tiles were found")
    elif not fcst_tiles:
        # Cannot proceed, the necessary 30x30 degree fcst tiles are missing
        logger.error("ERROR: No fcst tile files were found  " + tile_dir)
        raise OSError("No 30x30 fcst tiles were found")

    # Check for same number of fcst and analysis files
    if num_anly_tiles != num_fcst_tiles:
        # Something is wrong, we are missing
        # either an ANLY tile file or a FCST tile
        # file, this indicates a serious problem.
        logger.info("INFO: There are a different number of anly "
                    "and fcst tiles...")


def extract_year_month(init_time, logger):
    """! Retrieve the YYYYMM from the initialization time with format
         YYYYMMDD_hh
        Args:
            @param init_time:  The initialization time of expected format
            YYYYMMDD_hh
            @param logger:  Logger
        Returns:
            year_month (string):  The YYYYMM portion of the initialization time
    """
    # pylint:disable=protected-access
    # Need to call sys.__getframe() to get the filename and method/func
    # for logging information.

    # Useful for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Match on anything that starts with 1 or 2 (for the century)
    #  followed by 5 digits for the remainder of the YYYMM
    year_month = re.match(r'^((1|2)[0-9]{5})', init_time)
    if year_month:
        year_month = year_month.group(0)
        return year_month
    else:
        logger.warning("WARNING|" + "[" + cur_filename + ":" + cur_function +
                       "]" + " | Cannot extract YYYYMM from "
                       "initialization time, unexpected format")
        raise Warning("Cannot extract YYYYMM from initialization time,"
                      " unexpected format")

def create_grid_specification_string(lat, lon, logger, config):
    """! Create the grid specification string with the format:
         latlon Nx Ny lat_ll lon_ll delta_lat delta_lon
         used by the MET tool, regrid_data_plane.
         Args:
            @param lat:   The latitude of the grid point
            @param lon:   The longitude of the grid point
            @param logger: The name of the logger
            @param config: config instance
         Returns:
            tile_grid_str (string): the tile grid string for the
                                    input lon and lat
    """

    # pylint: disable=protected-access
    # Need to access sys._getframe to capture current file and function for
    # logging information

    # Useful for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    regrid_by_met = config.getbool('config', 'REGRID_USING_MET_TOOL')

    # Initialize the tile grid string
    # and get the other values from the parameter file
    nlat = config.getstr('config', 'NLAT')
    nlon = config.getstr('config', 'NLON')
    dlat = config.getstr('config', 'DLAT')
    dlon = config.getstr('config', 'DLON')
    lon_subtr = config.getfloat('config', 'LON_ADJ')
    lat_subtr = config.getfloat('config', 'LAT_ADJ')

    # Format for regrid_data_plane:
    # latlon Nx Ny lat_ll lon_ll delta_lat delta_lonadj_lon =
    # float(lon) - lon_subtr
    adj_lon = float(lon) - lon_subtr
    adj_lat = float(lat) - lat_subtr
    lon0 = str(round_0p5(adj_lon))
    lat0 = str(round_0p5(adj_lat))

    msg = ("DEBUG|[" + cur_filename + ":" + cur_function + "]  nlat:" +
           nlat + " nlon: " + nlon + " lat0:" + lat0 + " lon0: " + lon0)
    logger.debug(msg)

    # Create the specification string based on the requested tool.
    if regrid_by_met:
        grid_list = ['"', 'latlon ', nlat, ' ', nlon, ' ', lat0, ' ',
                     lon0, ' ', dlat, ' ', dlon, '"']
    else:
        # regrid via wgrib2
        grid_list = ['latlon ', lon0, ':', nlon, ':', dlon, ' ',
                     lat0, ':', nlat, ':', dlat]

    tile_grid_str = ''.join(grid_list)
    msg = ("INFO|" + cur_filename + ":" + cur_function +
           "| complete grid specification string: " + tile_grid_str)
    logger.debug(msg)
    return tile_grid_str


def gen_date_list(begin_date, end_date):
    """! Generates a list of dates of the form yyyymmdd from a being date to
     end date
    Inputs:
      @param begin_date -- such as "20070101"
      @param end_date -- such as "20070103"
    Returns:
      date_list -- such as ["20070101","20070102","20070103"]
    """

    begin_tm = time.strptime(begin_date, "%Y%m%d")
    end_tm = time.strptime(end_date, "%Y%m%d")
    begin_tv = calendar.timegm(begin_tm)
    end_tv = calendar.timegm(end_tm)
    date_list = []
    for tv in xrange(begin_tv, end_tv + 86400, 86400):
        date_list.append(time.strftime("%Y%m%d", time.gmtime(tv)))
    return date_list


def gen_hour_list(hour_inc, hour_end):
    """! Generates a list of hours of the form hh or hhh
    Inputs:
      @param hour_inc -- increment in integer format such as 6
      @param hour_end -- hh or hhh string indicating the end hour for the
                       increment such as "18"
    Returns:
      hour_list -- such as ["00", "06", "12", "18"]
    """

    int_list = range(0, int(hour_end) + 1, hour_inc)

    zfill_val = 0
    if len(hour_end) == 2:
        zfill_val = 2
    elif len(hour_end) == 3:
        zfill_val = 3

    hour_list = []
    for my_int in int_list:
        hour_string = str(my_int).zfill(zfill_val)
        hour_list.append(hour_string)

    return hour_list


def gen_init_list(init_date_begin, init_date_end, init_hr_inc, init_hr_end):
    """!
    Generates a list of initialization date and times of the form yyyymmdd_hh
    or yyyymmdd_hhh
    Inputs:
      @param init_begin_date -- yyyymmdd string such as "20070101"
      @param init_end_date -- yyyymmdd string such as "20070102"
      @param init_hr_inc -- increment in integer format such as 6
      @param init_hr_end -- hh or hhh string indicating the end hour for the
                           increment such as "18"
    Returns:
      init_list -- such as ["20070101_00", "20070101_06", "20070101_12",
      "20070101_18", "20070102_00", "20070102_06", "20070102_12",
      "20070102_18"]
    """

    my_hour_list = gen_hour_list(init_hr_inc, init_hr_end)

    my_date_list = gen_date_list(init_date_begin, init_date_end)

    date_init_list = []

    # pylint:disable=unused-variable
    # using enumerate on my_date_list returns a tuple, and not all values
    # are needed.

    for index, my_date in enumerate(my_date_list):
        for my_hour in my_hour_list:
            init_string = my_date + "_" + my_hour
            date_init_list.append(init_string)

    return date_init_list


def prune_empty(output_dir, logger):
    """! Start from the output_dir, and recursively check
        all directories and files.  If there are any empty
        files or directories, delete/remove them so they
        don't cause performance degradation or errors
        when performing subsequent tasks.
        Input:
            @param output_dir:  The directory from which searching
                                should begin.
            @param logger: The logger to which all logging is
                           directed.
    """

    # pylint:disable=protected-access
    # Need to call sys.__getframe() to get the filename and method/func
    # for logging information.
    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Check for empty files.
    for root, dirs, files in os.walk(output_dir):
        # Create a full file path by joining the path
        # and filename.
        for a_file in files:
            a_file = os.path.join(root, a_file)
            if os.stat(a_file).st_size == 0:
                msg = ("INFO|[" + cur_filename + ":" +
                       cur_function + "]|" +
                       "Empty file: " + a_file +
                       "...removing")

                logger.debug(msg)
                os.remove(a_file)

    # Now check for any empty directories, some
    # may have been created when removing
    # empty files.
    for root, dirs, files in os.walk(output_dir):
        for direc in dirs:
            full_dir = os.path.join(root, direc)
            if not os.listdir(full_dir):
                msg = ("INFO|[" + cur_filename + ":" +
                       cur_function + "]|" +
                       "Empty directory: " + full_dir +
                       "...removing")
                logger.debug(msg)
                os.rmdir(full_dir)


def cleanup_temporary_files(list_of_files):
    """! Remove the files indicated in the list_of_files list.  The full
       file path must be indicated.
        Args:
          @param list_of_files: A list of files (full filepath) to be
          removed.
        Returns:
            None:  Removes the requested files.
    """
    for single_file in list_of_files:
        try:
            os.remove(single_file)
        except OSError:
            # Raises exception if this doesn't exist (never created or
            # already removed).  Ignore.
            pass





def create_filter_tmp_files(filtered_files_list, filter_output_dir, logger=None):
    """! Creates the tmp_fcst and tmp_anly ASCII files that contain the full
        filepath of files that correspond to the filter criteria.  Useful for
        validating that filtering returns the expected results/troubleshooting.
        Args:
            @param filtered_files_list:  A list of the netCDF or grb2 files
                                          that result from applying filter
                                          options and running the MET tool
                                          tc_stat.
            @param filter_output_dir:  The directory where the filtered data is
                                       stored
            @param logger a logging.Logger for log messages
        Returns:
            None: Creates two ASCII files
    """

    # Useful for logging
    # cur_filename = sys._getframe().f_code.co_filename
    # cur_function = sys._getframe().f_code.co_name

    # Create the filenames for the tmp_fcst and tmp_anly files.
    tmp_fcst_filename = os.path.join(filter_output_dir,
                                     "tmp_fcst_regridded.txt")
    tmp_anly_filename = os.path.join(filter_output_dir,
                                     "tmp_anly_regridded.txt")

    fcst_list = []
    anly_list = []

    for filter_file in filtered_files_list:
        fcst_match = re.match(r'(.*/FCST_TILE_F.*.[grb2|nc])', filter_file)
        if fcst_match:
            fcst_list.append(fcst_match.group(1))

        anly_match = re.match(r'(.*/ANLY_TILE_F.*.[grb2|nc])', filter_file)
        if anly_match:
            anly_list.append(anly_match.group(1))

    # Write to the appropriate tmp file
    with open(tmp_fcst_filename, "a+") as fcst_tmpfile:
        for fcst in fcst_list:
            fcst_tmpfile.write(fcst + "\n")

    with open(tmp_anly_filename, "a+") as anly_tmpfile:
        for anly in anly_list:
            anly_tmpfile.write(anly + "\n")


def get_updated_init_times(input_dir, config=None):
    """ Get a list of init times, derived by the .tcst files in the
        input_dir (and below).
        Args:
            @param input_dir:  The topmost directory from which our search for
                               filter.tcst files begins.
            @param config:  Reference to metplus.conf configuration instance.
        Returns:
            updated_init_times_list : A list of the init times represented by
                                      the forecast.tcst files found in the
                                      input_dir.
    """

    # For logging
    # cur_filename = sys._getframe().f_code.co_filename
    # cur_function = sys._getframe().f_code.co_name

    updated_init_times_list = []
    init_times_list = []
    filter_list = get_files(input_dir, ".*.tcst", config)
    if filter_list:
        for filter_file in filter_list:
            match = re.match(r'.*/filter_([0-9]{8}_[0-9]{2,3})', filter_file)
            init_times_list.append(match.group(1))
        updated_init_times_list = sorted(init_times_list)

    return updated_init_times_list


def get_dirs(base_dir):
    """! Get a list of directories under a base directory.
        Args:
            @param base_dir:  The base directory from where search begins
       Returns:
           dir_list:  A list of directories under the base_dir
    """

    dir_list = []

    # pylint:disable=unused-variable
    # os.walk returns a tuple, not all returned values are needed.

    for dirname, dirs, filenames in os.walk(base_dir):
        for direc in dirs:
            dir_list.append(os.path.join(dirname, direc))

    return dir_list


def getlist(s, logger=None):
    """! Returns a list of string elements from a comma
         separated string of values.
         This function MUST also return an empty list [] if s is '' empty.
         This function is meant to handle these possible or similar inputs:
         AND return a clean list with no surrounding spaces or trailing
         commas in the elements.
         '4,4,2,4,2,4,2, ' or '4,4,2,4,2,4,2 ' or
         '4, 4, 4, 4, ' or '4, 4, 4, 4 '
         Note: getstr on an empty variable (EMPTY_VAR = ) in
         a conf file returns '' an empty string.

        @param s the string being converted to a list.
    """
    # FIRST remove surrounding comma, and spaces, form the string.
    s = s.strip().strip(',').strip()

    # remove space around commas
    s = re.sub(r'\s*,\s*', ',', s)
    # use csv reader to divide comma list while preserving strings with comma
    s = reader([s])
    # convert the csv reader to a list and get first item (which is the whole list)
    s = list(s)[0]
    return s


def getlistfloat(s):
    s = getlist(s)
    s = [float(i) for i in s]
    return s


def getlistint(s):
    s = getlist(s)
    s = [int(i) for i in s]
    return s


# minutes
def shift_time(time, shift):
    """ Adjust time by shift hours. Format is %Y%m%d%H%M
        Args:
            @param time: Start time in %Y%m%d%H%M
            @param shift: Amount to adjust time in hours
        Returns:
            New time in format %Y%m%d%H%M
    """
    return (datetime.datetime.strptime(time, "%Y%m%d%H%M") +
            datetime.timedelta(hours=shift)).strftime("%Y%m%d%H%M")

def shift_time_minutes(time, shift):
    """ Adjust time by shift minutes. Format is %Y%m%d%H%M
        Args:
            @param time: Start time in %Y%m%d%H%M
            @param shift: Amount to adjust time in minutes
        Returns:
            New time in format %Y%m%d%H%M
    """
    return (datetime.datetime.strptime(time, "%Y%m%d%H%M") +
            datetime.timedelta(minutes=shift)).strftime("%Y%m%d%H%M")

def shift_time_seconds(time, shift):
    """ Adjust time by shift seconds. Format is %Y%m%d%H%M
        Args:
            @param time: Start time in %Y%m%d%H%M
            @param shift: Amount to adjust time in seconds
        Returns:
            New time in format %Y%m%d%H%M
    """
    return (datetime.datetime.strptime(time, "%Y%m%d%H%M") +
            datetime.timedelta(seconds=shift)).strftime("%Y%m%d%H%M")


class FieldObj(object):
    __slots__ = 'fcst_name', 'fcst_level', 'fcst_extra', 'fcst_thresh', \
                'obs_name', 'obs_level', 'obs_extra', 'obs_thresh', 'index'


# TODO: Check if other characters are only <>!=&|gelt.[0-9] (?)
def starts_with_comparison(thresh_string):
    """ Ensure thresh values start with >,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le
        Args:
            @param thresh_string: String to examine, i.e. <=3.4
        Returns:
            None if string does not match any valid comparison operators or does
              not contain a number afterwards
            regex match object with comparison operator in group 1 and
            number in group 2 if valid
    """
    valid_comparisons = { ">", ">=", "==", "!=", "<", "<=", "gt", "ge", "eq", "ne", "lt", "le" }
    for comp in valid_comparisons:
        match = re.match(r'^('+comp+')([+-]?\d*\.?\d+)', thresh_string)
        if match:
            return match
    return None


def get_number_from_threshold(thresh_string):
    """ Removes comparison operator from threshold string.
        Note: This only gets the first number in a complex comparison
        Args:
            @param thresh_string String to examine, i.e. <=3.4
        Returns:
            Number without comparison operator if valid string
            None if invalid
    """
    match = starts_with_comparison(thresh_string)
    if match:
      return float(match.group(2))
    return None

def get_comparison_from_threshold(thresh_string):
    """ Removes number from threshold string
        Note: This only gets the first comparison in a complex comparison
        Args:
            @param thresh_string String to examine, i.e. <=3.4
        Returns:
            Comparison operator without number if valid string
            None if invalid
    """
    match = starts_with_comparison(thresh_string)
    if match:
      return match.group(1)
    return None


def validate_thresholds(thresh_list):
    """ Checks list of thresholds to ensure all of them have the correct format
        Args:
            @param thresh_list list of strings to check
        Returns:
            True if all items in the list are valid format, False if not
    """
    valid = True
    for thresh in thresh_list:
        match = starts_with_comparison(thresh)
        if match is None:
            valid = False

    if valid == False:
        print("ERROR: Threshold values must start with >,>=,==,!=,<,<=,gt,ge,eq,ne,lt, or le")
        return False;
    return True


def parse_var_list(p):
    """ read conf items and populate list of FieldObj containing
    information about each variable to be compared
        Args:
            @param p: Conf object
        Returns:
            list of FieldObj with variable information
    """
    var_list_fcst = parse_var_list_helper(p, "FCST", False)
    var_list_obs = parse_var_list_helper(p, "OBS", True)
    var_list = var_list_fcst + var_list_obs
    return sorted(var_list, key=lambda x: x.index)
    return var_list


def parse_var_list_helper(p, dt, dont_duplicate):
    """ helper function for parse_var_list
        Args:
            @param p: Conf object
            @param dt: data_type (FCST or OBS)
            @param dont_duplicate: if true check other data
              type and don't process if it exists
        Returns:
            list of FieldObj with variable information
    """
    # get other data type
    odt = "OBS"
    if dt == "OBS":
        odt = "FCST"

    # var_list is a list containing an list of FieldObj
    var_list = []

    # find all FCST_VARn_NAME keys in the conf files
    all_conf = p.keys('config')
    indices = []
    regex = re.compile(dt+"_VAR(\d+)_NAME")
    for conf in all_conf:
        result = regex.match(conf)
        if result is not None:
          indices.append(result.group(1))

    # loop over all possible variables and add them to list
    for n in indices:
        # don't duplicate if already entered into var list
        if dont_duplicate and p.has_option('config', odt+'_VAR'+n+'_NAME'):
            continue

        name = {}
        levels = {}
        thresh = {}
        extra = {}
        # get fcst var info if available
        if p.has_option('config', dt+"_VAR"+n+"_NAME"):
            name[dt] = p.getstr('config', dt+"_VAR"+n+"_NAME")

            extra[dt] = ""
            if p.has_option('config', dt+"_VAR"+n+"_OPTIONS"):
                extra[dt] = getraw_interp(p, 'config', dt+"_VAR"+n+"_OPTIONS")

            thresh[dt] = []
            if p.has_option('config', dt+"_VAR"+n+"_THRESH"):
                thresh[dt] = getlist(p.getstr('config', dt+"_VAR"+n+"_THRESH"))
                if validate_thresholds(thresh[dt]) == False:
                    print("  Update "+dt+"_VAR"+n+"_THRESH to match this format")
                    exit(1)

            # if OBS_VARn_X does not exist, use FCST_VARn_X
            if p.has_option('config', odt+"_VAR"+n+"_NAME"):
                name[odt] = p.getstr('config', odt+"_VAR"+n+"_NAME")
            else:
                name[odt] = name[dt]

            extra[odt] = ""
            if p.has_option('config', odt+"_VAR"+n+"_OPTIONS"):
                extra[odt] = getraw_interp(p, 'config', odt+"_VAR"+n+"_OPTIONS")

            levels[dt] = getlist(p.getstr('config', dt+"_VAR"+n+"_LEVELS"))
            if p.has_option('config', odt+"_VAR"+n+"_LEVELS"):
                levels[odt] = getlist(p.getstr('config', odt+"_VAR"+n+"_LEVELS"))
            else:
                levels[odt] = levels[dt]

            if len(levels[dt]) != len(levels[odt]):
                print("ERROR: "+dt+"_VAR"+n+"_LEVELS and "+odt+"_VAR"+n+\
                          "_LEVELS do not have the same number of elements")
                exit(1)

            # if OBS_VARn_THRESH does not exist, use FCST_VARn_THRESH
            if p.has_option('config', odt+"_VAR"+n+"_THRESH"):
                thresh[odt] = getlist(p.getstr('config', odt+"_VAR"+n+"_THRESH"))
                if validate_thresholds(thresh[odt]) == False:
                    print("  Update "+odt+"_VAR"+n+"_THRESH to match this format")
                    exit(1)
            else:
                thresh[odt] = thresh[dt]

            if len(thresh[dt]) != len(thresh[odt]):
                print("ERROR: "+dt+"_VAR"+n+"_THRESH and "+odt+"_VAR"+n+\
                          "_THRESH do not have the same number of elements")
                exit(1)

            for f,o in zip(levels[dt], levels[odt]):
                fo = FieldObj()
                fo.fcst_name = name[dt]
                fo.obs_name = name[odt]
                fo.fcst_extra = extra[dt]
                fo.obs_extra = extra[odt]
                fo.fcst_thresh = thresh[dt]
                fo.obs_thresh = thresh[odt]
                fo.fcst_level = f
                fo.obs_level = o
                fo.index = n
                var_list.append(fo)

    '''
    count = 0
    for v in var_list:
        print(" fcst_name:"+v.fcst_name)
        print(" fcst_level:"+v.fcst_level)
        print(" fcst_extra:"+v.fcst_extra)
        print(" obs_name:"+v.obs_name)
        print(" obs_level:"+v.obs_level)
        print(" obs_extra:"+v.obs_extra)
        print("")
        count += 1
    '''
    return var_list


def reformat_fields_for_met(all_vars_list, logger):
        """! Reformat the fcst or obs field values defined in the
             MET+ config file to the MET field dictionary.
             Args:
                 all_vars_list - The list of all variables/fields retrieved
                                 from the MET+ configuration file
                 logger        - The log to which any logging is directed.
             Returns:
                 met_fields - a named tuple containing the fcst field and
                              obs field key-value pairs needed by MET.
        """
        # pylint:disable=protected-access
        # Need to call sys.__getframe() to get the filename and method/func
        # for logging information.

        # Used for logging.
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name
        logger.info("INFO|:" + cur_function + '|' + cur_filename + '| ' +
                    "Reformatting field dictionary ...")

        # Named tuple (so we don't have to remember the order of the fields)
        # containing the string corresponding to the fcst or obs field
        # key-values for the MET config file.
        MetFields = namedtuple("MetFields", "fcst_field, obs_field")

        # Two types of fields in the MET fields dictionary, fcst and obs. Use
        # this to create the key-value pairs.
        field_list = ['fcst', 'obs']
        fcst_field = ''
        obs_field = ''
        for var in all_vars_list:
            # Create the key-value pairs in the fcst field and obs field
            # dictionaries as defined in the MET configuration file:
            # fcst = {
            #    field = [
            #       {
            #         name = "TMP";
            #         level = ["P500", "P400", "P300"];
            #         cat_thresh = [ > 80.0];
            #         GRIB_lvl_typ = 202;
            #       },
            #       {
            #         name = "HGT";
            #         level = ["P500"];
            #         cat_thresh = [ > 0.0];
            #         GRIB_lvl_typ = 202;
            #       },
            #    ]
            # }
            # obs = fcst;
            #
            # The reformatting involves creating the field key-value pairs in
            # the fcst and obs dictionaries.

            # Iterate over the field types fcst and obs
            for field in field_list:
                if field == 'fcst':
                    name = var.fcst_name
                    level = var.fcst_level.zfill(2)
                    extra = var.fcst_extra
                elif field == 'obs':
                    name = var.obs_name
                    level = var.obs_level
                    extra = var.obs_extra

                name_level_extra_list = ['{ name = "', name,
                                         '"; level = [ "', level, '" ]; ']
                if extra:
                    # End the text for this field.  If this is the last field,
                    # end the dictionary appropriately.
                    if var == all_vars_list[-1]:
                        # This is the last field, terminate it appropriately.
                        extra_str = extra + '; }'
                    else:
                        # More field(s) to go
                        extra_str = extra + '; },'
                    name_level_extra_list.append(extra_str)
                else:
                    # End the text for this field.  If this is the last field,
                    # end the dictionary appropriately.
                    if var == all_vars_list[-1]:
                        # This is the last field, terminate it appropriately.
                        name_level_extra_list.append('}')
                    else:
                        # More field(s) to go
                        name_level_extra_list.append('}, ')

                # Create the long string that will comprise the dictionary in
                # the MET point_stat config file.
                if field == 'fcst':
                    fcst_field += ''.join(name_level_extra_list)
                elif field == 'obs':
                    obs_field += ''.join(name_level_extra_list)

        met_fields = MetFields(fcst_field, obs_field)

        return met_fields

def get_filetype(filepath, logger=None):
    """!This function determines if the filepath is a NETCDF or GRIB file
       based on the first eight bytes of the file.
       It returns the string GRIB, NETCDF, or a None object.

       Note: If it is NOT determined to ba a NETCDF file,
       it returns GRIB, regardless.
       Unless there is an IOError exception, such as filepath refers
       to a non-existent file or filepath is only a directory, than
       None is returned, without a system exit.

       Args:
           @param filepath:  path/to/filename
           @param logger the logger, optional
       Returns:
           @returns The string GRIB, NETCDF or a None object
    """
    # Developer Note
    # Since we have the impending code-freeze, keeping the behavior the same,
    # just changing the implementation.
    # The previous logic did not test for GRIB it would just return 'GRIB'
    # if you couldn't run ncdump on the file.
    # Also note:
    # As John indicated ... there is the case when a grib file
    # may not start with GRIB ... and if you pass the MET command filtetype=GRIB
    # MET will handle it ok ...

    # Notes on file format and determining type.
    # https://www.wmo.int/pages/prog/www/WDM/Guides/Guide-binary-2.html
    # https://www.unidata.ucar.edu/software/netcdf/docs/faq.html
    # http: // www.hdfgroup.org / HDF5 / doc / H5.format.html

    # Interpreting single byte by byte - so ok to ignore endianess
    # od command:
    #   od -An -c -N8 foo.nc
    #   od -tx1 -N8 foo.nc
    # GRIB
    # Octet no.  IS Content
    # 1-4        'GRIB' (Coded CCITT-ITA No. 5) (ASCII);
    # 5-7        Total length, in octets, of GRIB message(including Sections 0 & 5);
    # 8          Edition number - currently 1
    # NETCDF .. ie. od -An -c -N4 foo.nc which will output
    # C   D   F 001
    # C   D   F 002
    # 211   H   D   F
    # HDF5
    # Magic numbers   Hex: 89 48 44 46 0d 0a 1a 0a
    # ASCII: \211 HDF \r \n \032 \n

    # Below is a reference that may be used in the future to
    # determine grib version.
    # import struct
    # with open ("foo.grb2","rb")as binary_file:
    #     binary_file.seek(7)
    #     one_byte = binary_file.read(1)
    #
    # This would return an integer with value 1 or 2,
    # B option is an unsigned char.
    #  struct.unpack('B',one_byte)[0]

    try:
        # read will return up to 8 bytes, if file is 0 bytes in length,
        # than first_eight_bytes will be the empty string ''.
        # Don't test the file length, just adds more time overhead.
        with open(filepath, "rb") as binary_file:
            binary_file.seek(0)
            first_eight_bytes = binary_file.read(8)

        # From the first eight bytes of the file, unpack the bytes
        # of the known identifier byte locations, in to a string.
        # Example, if this was a netcdf file than ONLY name_cdf would
        # equal 'CDF' the other variables, name_hdf would be 'DF '
        # name_grid 'CDF '
        name_cdf, name_hdf, name_grib = [None] * 3
        if len(first_eight_bytes) == 8:
            name_cdf =  struct.unpack('3s',first_eight_bytes[:3])[0]
            name_hdf =  struct.unpack('3s',first_eight_bytes[1:4])[0]
            name_grib = struct.unpack('4s',first_eight_bytes[:4])[0]

        # Why not just use a else, instead of elif else if we are going to
        # return GRIB ? It allows for expansion, ie. Maybe we pass in a
        # logger and log the cases we can't determine the type.
        if name_cdf == 'CDF' or name_hdf == 'HDF':
            return "NETCDF"
        elif name_grib == 'GRIB':
            return "GRIB"
        else:
            # This mimicks previous behavoir, were we at least will always return GRIB.
            # It also handles the case where GRIB was not in the first 4 bytes
            # of a legitimate grib file, see John.
            # logger.info('Can't determine type, returning GRIB
            # as default %s'%filepath)
            return "GRIB"

    except IOError:
        # Skip the IOError, and keep processing data.
        # ie. filepath references a file that does not exist
        # or filepath is a directory.
        return None

    # Previous Logic
    # ncdump_exe = config.getexe('NCDUMP_EXE')
    #try:
    #    result = subprocess.check_output([ncdump_exe, filepath])

    #except subprocess.CalledProcessError:
    #    return "GRIB"

    #regex = re.search("netcdf", result)
    #if regex is not None:
    #    return "NETCDF"
    #else:
    #    return None



def get_time_from_file(logger, filepath, template):
    valid_extensions = [ '.gz', '.bz2', '.zip' ]
    if os.path.isdir(filepath):
        return None

    se = StringExtract(logger, template, filepath)

    if se.parseTemplate():
        return se
    else:
        # check to see if zip extension ends file path, try again without extension
        for ext in valid_extensions:
            if filepath.endswith(ext):
                se = StringExtract(logger, template, filepath[:-len(ext)])
                if se.parseTemplate():
                    return se
        return None


def getraw_interp(p, sec, opt):
    """ parse parameter and replace any existing parameters
        referenced with the value (looking in same section, then
        config, dir, and os environment)
        returns raw string, preserving {valid?fmt=%Y} blocks
        Args:
            @param p: Conf object
            @param sec: Section in the conf file to look for variable
            @param opt: Variable to interpret
        Returns:
            Raw string
    """

    in_template = p.getraw(sec, opt, "")
    out_template = ""
    in_brackets = False
    for i, c in enumerate(in_template):
        if c == "{":
            in_brackets = True
            start_idx = i
        elif c == "}":
            var_name = in_template[start_idx+1:i]
            var = None
            if p.has_option(sec,var_name):
                var = p.getstr(sec,var_name)
            elif p.has_option('config',var_name):
                var = p.getstr('config',var_name)
            elif p.has_option('dir',var_name):
                var = p.getstr('dir',var_name)
            elif var_name[0:3] == "ENV":
                var = os.environ.get(var_name[4:-1])

            if var is None:
                out_template += in_template[start_idx:i+1]
            else:
                out_template += var
            in_brackets = False
        elif not in_brackets:
            out_template += c

    return out_template


def preprocess_file(filename, data_type, p, logger=None):
    """ Decompress gzip, bzip, or zip files or convert Gempak files to NetCDF
        Args:
            @param filename: Path to file without zip extensions
            @param p: Config object
            @param logger: Optional argument to allow logging
        Returns:
            Path to staged unzipped file or original file if already unzipped
    """
    if filename is None or filename == "":
        return None

    stage_dir = p.getdir('STAGING_DIR')
    # TODO: move valid_extensions so it can be used by more than one function
    valid_extensions = [ '.gz', '.bz2', '.zip' ]
    if os.path.exists(filename):
        for ext in valid_extensions:
            if filename.endswith(ext):
                return preprocess_file(filename[:-len(ext)], data_type, p, logger)
        # if extension is grd (Gempak), then look in staging dir for nc file
        if filename.endswith('.grd') or data_type == "GEMPAK":
            if filename.endswith('.grd'):
                stagefile = stage_dir + filename[:-3]+"nc"
            else:
                stagefile = stage_dir + filename+".nc"
            if os.path.exists(stagefile):
                return stagefile
            # if it does not exist, run GempakToCF and return staged nc file
            # Create staging area if it does not exist
            outdir = os.path.dirname(stagefile)
            if not os.path.exists(outdir):
                os.makedirs(outdir, mode=0775)
            run_g2c = GempakToCFWrapper(p, logger)
            run_g2c.add_input_file(filename)
            run_g2c.set_output_path(stagefile)
            cmd = run_g2c.get_command()
            if cmd is None:
                self.logger.error("GempakToCF could not generate command")
                return None
            if logger:
                logger.info("Converting Gempak file")
            run_g2c.build()
            return stagefile

        return filename

    # if file exists in the staging area, return that path
    outpath = stage_dir + filename
    if os.path.exists(outpath):
        return outpath

    # Create staging area if it does not exist
    outdir = os.path.dirname(outpath)
    if not os.path.exists(outdir):
        os.makedirs(outdir, mode=0775)

    if os.path.exists(filename+".gz"):
        if logger:
            logger.info("Decompressing gz file")
        with gzip.open(filename+".gz", 'rb') as infile:
            with open(outpath, 'wb') as outfile:
                outfile.write(infile.read())
                infile.close()
                outfile.close()
                return outpath
    elif os.path.exists(filename+".bz2"):
        if logger:
            logger.info("Decompressing bz2 file")
        with open(filename+".bz2", 'rb') as infile:
            with open(outpath, 'wb') as outfile:
                outfile.write(bz2.decompress(infile.read()))
                infile.close()
                outfile.close()
                return outpath
    elif os.path.exists(filename+".zip"):
        if logger:
            logger.info("Decompressing zip file")
        with zipfile.ZipFile(filename+".zip") as z:
            with open(outpath, 'wb') as f:
                f.write(z.read(os.path.basename(filename)))
                return outpath

    return None


def run_stand_alone(module_name, app_name):
    """ Used to allow MET tool wrappers to be run without using
    master_metplus.py
        Args:
            @param module_name: Name of wrapper with underscores, i.e.
            pcp_combine_wrapper
            @param app_name: Name of wrapper with camel case, i.e.
            PcpCombine
        Returns:
            None
    """
    try:
        # If jobname is not defined, in log it is 'NO-NAME'
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus',
                                 jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='run-METplus')
        produtil.log.postmsg(app_name + ' is starting')

        # Job Logger
        produtil.log.jlogger.info('Top of ' + app_name)


        # Used for logging and usage statment
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # Setup Task logger, Until Conf object is created, Task logger is
        # only logging to tty, not a file.
        logger = logging.getLogger(app_name)
        logger.info('logger Top of ' + app_name + ".")

        # Parse arguments, options and return a config instance.
        p = config_metplus.setup(filename=cur_filename)

        logger = get_logger(p)

        module = __import__(module_name)
        wrapper_class = getattr(module, app_name + "Wrapper")
        wrapper = wrapper_class(p, logger)

        os.environ['MET_BASE'] = p.getdir('MET_BASE')

        produtil.log.postmsg(app_name + ' Calling run_all_times.')

        wrapper.run_all_times()

        produtil.log.postmsg(app_name + ' completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            app_name + '  failed: %s' % (str(e),), exc_info=True)
        sys.exit(2)


def add_common_items_to_dictionary(p, dictionary):
    dictionary['WGRIB2'] = p.getexe('WGRIB2')
    dictionary['CUT_EXE'] = p.getexe('CUT_EXE')
    dictionary['TR_EXE'] = p.getexe('TR_EXE')
    dictionary['RM_EXE'] = p.getexe('RM_EXE')
    dictionary['NCAP2_EXE'] = p.getexe('NCAP2_EXE')
    dictionary['CONVERT_EXE'] = p.getexe('CONVERT_EXE')
    dictionary['NCDUMP_EXE'] = p.getexe('NCDUMP_EXE')
    dictionary['EGREP_EXE'] = p.getexe('EGREP_EXE')


def template_to_regex(template, init_time, valid_time, logger):
    in_template = re.sub(r'\.', '\\.', template)
    in_template = re.sub(r'{lead.*?}', '.*', in_template)
    sts = StringSub(logger,
                    in_template,
                    init=init_time,
                    valid=valid_time)
    return sts.doStringSub()

if __name__ == "__main__":
    gen_init_list("20141201", "20150331", 6, "18")
