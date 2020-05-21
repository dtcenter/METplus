#!/usr/bin/env python

"""!@namespace feature_util
 @brief Provides  Utility functions for METplus feature relative use case.
"""

import sys
import re
import os
from collections import namedtuple

from . import met_util as util

def grid2obs_file_info(g2obs_file, subdir_regex, logger):
    """! Extract date information on all prepbufr or point stat input files
         (grid2obs files) in the specified
         input directory.  This information will facilitate the naming
         of output files.

    Args:
        @param g2obs_file - The grid2obs file(full filepath) undergoing
                          conversion to NetCDF. This can be a prepBufr file
                          or any other input file used for point_stat.
        @param subdir_regex - The regular expression that describes the
                              dated subdirectory (if applicable).
        @param logger     - The logger to which all logging is to be
                            directed.
    Returns:
        g2obs_file_info -    information in the form
                             of named tuples: full_filepath, ymd,
                             cycle, lead (forecast), offset for files
                             that are in dated subdirectories (e.g.
                             nam/nam.20170601/nam.t00z.prepbufr.tm03,
                             or
                             nam/nam.20170601/nam.t00z.awphys12.tm00.grib2).

                             OR full_filepath for those which have the ymd/ymdh
                             information as part of their filename (
                             e.g. prepbufr.gdas.2018010100)


    """
    # pylint:disable=protected-access
    # Need to call sys.__getframe() to get the filename and method/func
    # for logging information.

    # Used for logging.
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    logger.info("Creating prepbufr file information")

    # For files like GDAS, there are no cycle and offset values in the
    # filename.  These will be set to None.  Some files may not have a
    # forecast/lead value, set this to None if this is not part of the
    # filename.
    Grid2ObsFile = namedtuple('Grid2ObsFile',
                              'full_filepath, date, cycle, lead, offset')

    # Check if this prepbufr data has the date in the subdirectory name
    # in the form of a dated subdirectory,
    # This is indicated by setting the directory regex, PREPBUFR_DIR_REGEX
    if subdir_regex:
        regex_compile = re.compile(subdir_regex)
        match = re.match(regex_compile, g2obs_file)
        if match:
            date = match.group(1)
        else:
            date = None

    # TODO Check if the filename has a lead
    # match = re.match(r'.*', g2obs_file)

    # Check if the filename has an offset
    match = re.match(r'.*tm([0-9]{2}).*', g2obs_file)
    if match:
        offset = match.group(1)

        # Retrieve the cycle time
        cycle_match = re.match(r'.*t([0-9]{2})z.*', g2obs_file)
        if cycle_match:
            # Files contain information to derive init and valid times
            cycle = cycle_match.group(1)
            g2obs_file_info = Grid2ObsFile(g2obs_file, date, cycle, offset)
        else:
            # Something is wrong, there should be a cycle time if
            # there is an offset time.
            logger.error('Expected cycle time not'
                                        'found. This '
                                        'data does not have '
                                        'the expected prepbufr '
                                        'filename, exiting...')
            sys.exit(1)
    else:
        # No offset, check for cycle time (these files correspond to
        # init times)
        cycle_match = re.match(r'.*t([0-9]{2})z.*', g2obs_file)
        if cycle_match:
            cycle = cycle_match.group(1)
            g2obs_file_info = Grid2ObsFile(g2obs_file, date, cycle, None)
        else:
            # no cycle or offset, the file contains YMDh information
            # in its filename corresponding to valid times.
            ymdh_match = re.match(r'.*(2[0-9]{9}).*', g2obs_file)
            if ymdh_match:
                date = ymdh_match.group(1)
                g2obs_file_info = Grid2ObsFile(g2obs_file, date, None, None)

    return g2obs_file_info


def get_date_from_path(dir_to_search, date_regex):
    """! If the directory is comprised of dated subdirectories, retrieve
         the YYYYMMDD or YYYYMMDDHH from the dated subdirectory name.
         Args:
               @param dir_to_search    - the directory from where to search
                                         for dated subdirectories
               @param date_regex       - the regular expression describing
                                         the format of the date in the
                                         subdirectory name: YYYYMMDD or
                                         YYYYMMDDHH
        Returns:
               dates_from_path         - a list of named tuples containing
                                         the subdir filepath and corresponding
                                         date (YYYYMMDD or YYYYMMDDHH)
    """
    DatePath = namedtuple('DatePath', 'subdir_filepath, data_date')
    dates_from_path = []
    subdirs_list = util.get_dirs(dir_to_search)

    if subdirs_list:
        for subdir in subdirs_list:
            match = re.match(date_regex, subdir)
            if match:
                subdir_path = os.path.join(dir_to_search, subdir)
                date_path = DatePath(subdir_path, match.group(1))
                dates_from_path.append(date_path)
    return dates_from_path
