#!/usr/bin/env python
from __future__ import print_function

import logging, os, shutil, sys, datetime
from produtil.run import batchexe, run, checkrun
import errno
import time
import calendar
import re
import string_template_substitution as sts
import run_tc_stat as tcs

''' A collection of utility functions used to perform necessary series
    analysis tasks and other METPlus related tasks, .


'''


def round_0p5(val):
    '''Round to the nearest point five (ie 3.3 rounds to 3.5, 3.1 rounds to 3.0)
       Take the input value, multiply by two, round to integer (no decimal places)
       then divide by two.  Expect any input value of n.0, n.1, or n.2 to round
       down to n.0, and any input value of n.5, n.6 or n.7 to round to n.5.
       Finally, any input value of n.8 or n.9 will round to (n+1).0

       Args:
          val :  The number to be rounded to the nearest .5

       Returns:
          pt_five:  The n.0, n.5, or (n+1).0 value as
                            a result of rounding the input value, val.

    '''

    val2 = val * 2
    rval = round_to_int(val2)
    pt_five = round(rval, 0) / 2
    return pt_five


def round_to_int(val):
    ''' Round to integer value
    '''
    val += 0.5
    rval = int(val)
    return rval


def mkdir_p(path):
    '''From stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
       Creates the entire directory path if it doesn't exist (including any 
       required intermediate directories).  
       
       Args:
           path : The full directory path to be created
       Returns
           None: Creates the full directory path if it doesn't exist, does nothing
                 otherwise.  
    

    '''

    try:
        # ***Note***:
        # For Python 3.2 and beyond, os.makedirs has a third optional argument,
        # exist_ok, that when set to True will enable the mkdir -p functionality.
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

def _rmtree_onerr(function,path,exc_info,logger=None):
    """!Internal function used to log errors.

    This is an internal implementation function called by
    shutil.rmtree when an underlying function call failed.  See
    the Python documentation of shutil.rmtree for details.
    @param function the funciton that failed
    @param path the path to the function that caused problems
    @param exc_info the exception information
    @protected"""
    if logger:
        logger.warning('%s: %s failed: %s'%(
                str(path),str(function),str(exc_info)))

def rmtree(tree,logger=None):
    """!Deletes the tree, if possible.
    @protected
    @param tree the directory tree to delete"""
    try:
        # If it is a file, special file or symlink we can just
        # delete it via unlink:
        os.unlink(tree)
        return
    except EnvironmentError as e:
        pass
    # We get here for directories.
    if logger:
        logger.info('%s: rmtree'%(tree,))
    #shutil.rmtree(tree,ignore_errors=False,onerror=_rmtree_onerr)
    shutil.rmtree(tree,ignore_errors=False)


def get_logger(p):
    '''Gets a logger

       Args:
           p:   the METplus produtil.ProdConfig object

       Returns:
           logger: the logger
    '''

    # Retrieve all logging related parameters from the param file
    log_dir = p.getdir('LOG_DIR')
    log_level = p.getstr('config', 'LOG_LEVEL')
    log_path_basename = os.path.splitext(p.getstr('config','LOG_FILENAME'))[0]
    log_ext = os.path.splitext(p.getstr('config','LOG_FILENAME'))[1]
    log_filename = log_path_basename+'.'\
                   +datetime.datetime.now().strftime("%Y%m%d")\
                   +log_ext.strip()

    #TODO review, use builtin produtil.fileop vs. mkdir_p ?
    #import produtil.fileop
    #produtil.fileop.makedirs(log_dir,logger=None)

    # Check if the directory path for the log exists, if
    # not create it.
    if not os.path.exists(log_dir):
        mkdir_p(log_dir)

    # Get the current filename and method, set up
    # the filehandler and the formatter, etc.
    log_path = os.path.join(log_dir, log_filename)

    formatter = logging.Formatter('%(asctime)s : %(message)s')
    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger(log_path)
    logger.setLevel(log_level)
    fileHandler = logging.FileHandler(log_path, mode='a')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger


def file_exists(filename):
    ''' Determines if a file exists
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
            filename (string):  the full filename (full path) 
        Returns:
            boolean : True if file exists, False otherwise
    '''

    try:
        if os.path.isfile(filename):
            return True
        else:
            return False
    except IOError as e:
        pass
        return False


def is_dir_empty(directory):
    ''' Determines if a directory exists and is not empty 
    
        Args:
           directory (string):  The directory to check for existence and 
                                for contents.
     
        Returns:
           True              :  If the directory exists and isn't empty
           False             :  Otherwise
            
         
    '''
    if not os.listdir(directory):
        # Directory is empty
        return True
    else:
        return False


def grep(pattern, file, greedy=False):
    ''' Python version of grep, searches the file line-by-line 
        to find a match to the pattern. Returns upon finding the 
        first match.

        Args:
            pattern (string):  The pattern to be matched
            file (string):     The filename with full filepath in which to 
                               search for the pattern
            greedy (boolean):  Default is false, if True, returns a list of
                               all matches
        Returns:
            line (string):     The matching string

    '''

    matching_lines = []
    with open(file, 'r') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                matching_lines.append(line)
                # if you got here, you didn't find anything
    return matching_lines


def get_filepaths_for_grbfiles(dir):
    '''Generates the grb2 file names in a directory tree
       by walking the tree either top-down or bottom-up.
       For each directory in the tree rooted at
       the directory top (including top itself), it
       produces a 3-tuple: (dirpath, dirnames, filenames).

       This solution was found on Stack Overflow:
       http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python#3207973

       **scroll down to the section with "Getting Full File Paths From a Directory and All Its Subdirectories"

    Args:
        dir (string): The base directory from which we
                      begin the search for grib2 filenames.
    Returns:
        file_paths (list): A list of the full filepaths
                           of the data to be processed.


    '''

    # Create an empty list which will eventually store
    # all the full filenames
    file_paths = []

    # Walk the tree
    for root, directories, files in os.walk(dir):
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
    ''' Get each storm as identified by its STORM_ID in the filter file
        save these in a set so we only save the unique ids and sort them.

        Args:
            filter_filename (string):  The name of the filter file to read
                                       and extract the storm id
            logger (string):  The name of the logger for logging useful info

        Returns:
            sorted_storms (List):  a list of unique, sorted storm ids
    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

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
    ''' Get all the files (with a particular
        naming format) by walking
        through the directories.
   
        Args:
          filedir (String):  The topmost directory from which the
                             search begins.
          filename_regex (string):  The regular expression that
                                    defines the naming format
                                    of the files of interest.
       Returns:
          file_paths (string): a list of filenames (with full filepath)

    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    file_paths = []
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
    '''   Retrieve the variable name and level from a list of
          variable/level combinations.  

          Args:
             var_combo(string):  A combination of the variable and the level
                                 separated by '/'
  
          Returns:
             name,level: A tuple of name and level derived from the
                         name/level combination. 

    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    match = re.match(r'(.*)/(.*)', var_combo)
    name = match.group(1)
    level = match.group(2)

    return name, level


def check_for_tiles(tile_dir, fcst_file_regex, anly_file_regex, logger):
    ''' Checks for the presence of forecast and analysis
        tiles that were created by extract_tiles

        Args:
            tile_dir (string):  The directory where the expected
                                tiled files should reside.

            fcst_file_regex (string): The regexp describing the format of the
                                  forecast tile file.

            anly_file_regex (string): The regexp describing the format of the
                                  analysis tile file.

            logger (string):    The logger to which all log messages
                                should be directed.

        Returns:
            None  raises OSError if expected files are missing

    '''
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
        logger.info("INFO: There are a different number of anly and fcst tiles...")


def extract_year_month(init_time, logger):
    ''' Retrieve the YYYYMM from the initialization time with format YYYYMMDD_hh

        Args:
            init_time (string):  The initialization time of expected format YYYYMMDD_hh

        Returns:
            year_month (string):  The YYYYMM portion of the initialization time

    '''

    # Useful for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Match on anything that starts with 1 or 2 (for the century) followed by 5 digits
    # for the remainder of the YYYMM
    ym = re.match(r'^((1|2)[0-9]{5})', init_time)
    # ym = re.match(r'^2[0-9]{5}',init_time)
    if ym:
        year_month = ym.group(0)
        return year_month
    else:
        logger.warning("WARNING|" + "[" + cur_filename + ":" + cur_function + "]" +
                       " | Cannot extract YYYYMM from initialization time, unexpected format")
        raise Warning("Cannot extract YYYYMM from initialization time, unexpected format")


def retrieve_and_regrid(tmp_filename, cur_init, cur_storm, out_dir, logger, p):
    ''' Retrieves the data from the GFS_DIR (defined in constants_pdef.py) that
        corresponds to the storms defined in the tmp_filename:
        1) create the analysis tile and forecast file names from the 
           tmp_filename file. 
        2) perform regridding via MET tool (regrid_data_plane) and store results
           (netCDF files) in the out_dir or via

           Regridding via  regrid_data_plane on the forecast and analysis files via a latlon
                           string with the following format:
                           latlon Nx Ny lat_ll lon_ll delta_lat delta_lon
                           NOTE:  thes values are defined in
                                  the extract_tiles_parm parameter/config
                                  file as NLAT, NLON.
   
        Args:
        tmp_filename:      Filename of the temporary filter file in 
                           the /tmp directory. Contains rows 
                           of data corresponding to a storm id of varying
                           times.

        cur_init:          The current init time
     
        cur_storm:         The current storm 
      
        out_dir:           The directory where regridded netCDF or grib2 output is saved
                           depending on which regridding methodology is requested.  If
                           the MET tool regrid_data_plane is requested, then netCDF data
                           is produced.  If wgrib2 is requested, then grib2 data is produced.

   

        logger     :       The name of the logger used in logging.
        p          :       Referenct to the ConfigMaster constants_pdef.py
                           param/config file.
     
        Returns:
           None

    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Get variables, etc. from constants_pdef.py param/config file.
    gfs_dir = p.getdir('GFS_DIR')
    regrid_data_plane_exe = p.getexe('REGRID_DATA_PLANE_EXE')
    wgrib2_exe = p.getexe('WGRIB2')
    egrep_exe = p.getexe('EGREP_EXE')
    regrid_with_MET_tool = p.getbool('config','REGRID_USING_MET_TOOL')
    overwrite_flag = p.getbool('config','OVERWRITE_TRACK')
    
    # Extract the columns of interest: init time, lead time,
    # valid time lat and lon of both  tropical cyclone tracks, etc.
    # Then calculate the forecast hour and other things.
    with open(tmp_filename, "r") as tf:
        # read header
        header = tf.readline().split()
        # get column number for columns on interest
        print('header{}:'.format(header))
        header_colnum_init, header_colnum_lead, header_colnum_valid = header.index('INIT'), header.index('LEAD'), header.index('VALID')
        header_colnum_alat, header_colnum_alon = header.index('ALAT'), header.index('ALON')
        header_colnum_blat, header_colnum_blon = header.index('BLAT'), header.index('BLON')
        for line in tf:
            col = line.split()
            init, lead, valid, alat, alon, blat, blon = col[header_colnum_init], col[header_colnum_lead], col[header_colnum_valid], col[header_colnum_alat], col[header_colnum_alon], col[header_colnum_blat], col[header_colnum_blon]
 
            # integer division for both Python 2 and 3
            lead_time = int(lead)
            fcst_hr = lead_time // 10000

            init_ymd_match = re.match(r'[0-9]{8}', init)
            if init_ymd_match:
                init_ymd = init_ymd_match.group(0)
            else:
                raise RuntimeError('init time has unexpected format for YMD')
                logger.WARN("RuntimeError raised")

            init_ymdh_match = re.match(r'[0-9|_]{11}', init)
            if init_ymdh_match:
                init_ymdh = init_ymdh_match.group(0)
            else:
                logger.WARN("RuntimeError raised")

            valid_ymd_match = re.match(r'[0-9]{8}', valid)
            if valid_ymd_match:
                valid_ymd = valid_ymd_match.group(0)
            else:
                logger.WARN("RuntimeError raised")

            valid_ymdh_match = re.match(r'[0-9|_]{11}', valid)
            if valid_ymdh_match:
                valid_ymdh = valid_ymdh_match.group(0)
            else:
                logger.WARN("RuntimeError raised")

            lead_str = str(fcst_hr).zfill(3)
            fcst_dir = os.path.join(gfs_dir, init_ymd)
            init_ymdh_split = init_ymdh.split("_")
            init_YYYYmmddHH = "".join(init_ymdh_split)
            anly_dir = os.path.join(gfs_dir, valid_ymd)
            valid_ymdh_split = valid_ymdh.split("_")
            valid_YYYYmmddHH = "".join(valid_ymdh_split)

            # Create output filenames for regridding
            # wgrib2 used to regrid.
            # Create the filename for the regridded file, which is a
            # grib2 file.
            fcstSTS = sts.StringTemplateSubstitution(logger,
                                                     p.getraw('filename_templates','GFS_FCST_FILE_TMPL'),
                                                     init=init_YYYYmmddHH,
                                                     lead=lead_str)

            anlySTS = sts.StringTemplateSubstitution(logger,
                                                     p.getraw('filename_templates', 'GFS_ANLY_FILE_TMPL'),
                                                     valid=valid_YYYYmmddHH,
                                                     lead=lead_str)

            fcst_file = fcstSTS.doStringSub()
            fcst_filename = os.path.join(fcst_dir, fcst_file)
            anly_file = anlySTS.doStringSub()
            anly_filename = os.path.join(anly_dir, anly_file)

            # Check if the forecast input file exists. If it doesn't
            # exist, just log it
            if file_exists(fcst_filename):
                msg = ("INFO| [" + cur_filename + ":" + cur_function +
                       " ] | Forecast file: " + fcst_filename)
                logger.debug(msg)
            else:
                msg = ("WARNING| [" + cur_filename + ":" +
                       cur_function + " ] | " +
                       "Can't find forecast file, continuing anyway: " +
                       fcst_filename)
                logger.debug(msg)
                continue

            # Check if the analysis input file exists. If it doesn't
            # exist, just log it.
            if file_exists(anly_filename):
                msg = ("INFO| [" + cur_filename + ":" +
                       cur_function + " ] | Analysis file: " +
                       anly_filename)
                logger.debug(msg)

            else:
                msg = ("WARNING| [" + cur_filename + ":" +
                       cur_function + " ] | " +
                       "Can't find analysis file, continuing anyway: " +
                       anly_filename)
                logger.debug(msg)
                continue

            # Create the arguments used to perform regridding.  NOTE: the base name
            # is the same for both the fcst and anly filenames, so use either one
            # to derive the base name that will be used to create the fcst_regridded_filename
            # and anly_regridded_filename.
            fcst_anly_base = os.path.basename(fcst_filename)

            fcst_grid_spec = create_grid_specification_string(alat, alon,
                                                              logger, p)
            anly_grid_spec = create_grid_specification_string(blat, blon,
                                                              logger, p)
            if regrid_with_MET_tool:
                nc_fcst_anly_base = re.sub("grb2", "nc", fcst_anly_base)
                fcst_anly_base = nc_fcst_anly_base

            tile_dir = os.path.join(out_dir, cur_init, cur_storm)
            fcst_hr_str = str(fcst_hr).zfill(3)

            fcst_regridded_filename = p.getstr('regex_pattern','FCST_TILE_PREFIX') + fcst_hr_str + "_" + fcst_anly_base
            fcst_regridded_file = os.path.join(tile_dir, fcst_regridded_filename)
            anly_regridded_filename = p.getstr('regex_pattern','ANLY_TILE_PREFIX') + fcst_hr_str + "_" + fcst_anly_base
            anly_regridded_file = os.path.join(tile_dir, anly_regridded_filename)

            # Regrid the fcst file only if a fcst tile 
            # file does NOT already exist or if the overwrite flag is True.
            # Create new gridded file for fcst tile
            if file_exists(fcst_regridded_file) and not overwrite_flag:
                msg = ("INFO| [" + cur_filename + ":" +
                       cur_function + " ] | Forecast tile file " +
                       fcst_regridded_file + " exists, skip regridding")
                logger.debug(msg)
            else:
                # Perform fcst regridding on the records of interest
                var_level_string = retrieve_var_info(p, logger)
                if regrid_with_MET_tool:
                    # Perform regridding using MET Tool regrid_data_plane
                    fcst_cmd_list = [regrid_data_plane_exe, ' ',
                                     fcst_filename, ' ',
                                     fcst_grid_spec, ' ',
                                     fcst_regridded_file, ' ',
                                     var_level_string,
                                     ' -method NEAREST ']
                    regrid_cmd_fcst = ''.join(fcst_cmd_list)
                    regrid_cmd_fcst = batchexe('sh')['-c',regrid_cmd_fcst].err2out() 
                    #regrid_cmd_fcst = batchexe(regrid_cmd_fcst.split()[0])[regrid_cmd_fcst.split()[1:]].err2out()
                    msg = ("INFO|[regrid]| regrid_data_plane regrid command:" +
                           regrid_cmd_fcst.to_shell())
                    logger.debug(msg)
                    regrid_fcst_out = run(regrid_cmd_fcst)

                else:
                    # Perform regridding via wgrib2 
                    requested_records = retrieve_var_info(p, logger)
                    fcst_cmd_list = [wgrib2_exe, ' ', fcst_filename, ' | ',
                                     egrep_exe, ' ', requested_records, '|',
                                     wgrib2_exe, ' -i ', fcst_filename,
                                     ' -new_grid ', fcst_grid_spec, ' ',
                                     fcst_regridded_file]
                    wgrb_cmd_fcst = ''.join(fcst_cmd_list)
                    wgrb_cmd_fcst = batchexe('sh')['-c',wgrb_cmd_fcst].err2out()
                    #wgrb_cmd_fcst = batchexe(wgrb_cmd_fcst.split()[0])[wgrb_cmd_fcst.split()[1:]].err2out()
                    msg = ("INFO|[wgrib2]| wgrib2 regrid command:" +
                           wgrb_cmd_fcst.to_shell())
                    logger.debug(msg)
                    wgrb_fcst_out = run(wgrb_cmd_fcst)


            # Create new gridded file for anly tile
            if file_exists(anly_regridded_file) and not overwrite_flag:
                logger.debug("INFO| [" + cur_filename + ":" +
                             cur_function + " ] |" +
                             " Analysis tile file: " +
                             anly_regridded_file +
                             " exists, skip regridding")
            else:
                # Perform anly regridding on the records of interest
                var_level_string = retrieve_var_info(p, logger)
                if regrid_with_MET_tool:
                    anly_cmd_list = [regrid_data_plane_exe, ' ',
                                     anly_filename, ' ',
                                     anly_grid_spec, ' ',
                                     anly_regridded_file, ' ',
                                     var_level_string, ' ',
                                     ' -method NEAREST ']
                    regrid_cmd_anly = ''.join(anly_cmd_list)
                    regrid_cmd_anly = batchexe('sh')['-c',regrid_cmd_anly].err2out()
                    #regrid_cmd_anly = batchexe(regrid_cmd_anly.split()[0])[regrid_cmd_anly.split()[1:]].err2out()
                    regrid_anly_out = run(regrid_cmd_anly)
                    msg = ("INFO|[regrid]| on anly file:" + anly_regridded_file)
                    logger.debug(msg)
                else:
                    # Regridding via wgrib2.
                    requested_records = retrieve_var_info(p, logger)
                    anly_cmd_list = [wgrib2_exe, ' ', anly_filename, ' | ',
                                     egrep_exe, ' ', requested_records, '|',
                                     wgrib2_exe, ' -i ', anly_filename,
                                     ' -new_grid ', anly_grid_spec, ' ',
                                     anly_regridded_file]
                    wgrb_cmd_anly = ''.join(anly_cmd_list)
                    wgrb_cmd_anly = batchexe('sh')['-c',wgrb_cmd_anly].err2out()
                    #wgrb_cmd_anly = batchexe(wgrb_cmd_anly.split()[0])[wgrb_cmd_anly.split()[1:]].err2out()
                    msg = ("INFO|[wgrib2]| Regridding via wgrib2:" +
                           wgrb_cmd_anly.to_shell())
                    wgrb_anly_out = run(wgrb_cmd_anly)
                    logger.debug(msg)


def retrieve_var_info(p, logger):
    ''' Retrieve the variable name and level from the
        EXTRACT_TILES_VAR_FILTER and VAR_LIST.  If the
        EXTRACT_TILES_VAR_FILTER is empty, then retrieve
        the variable information from VAR_LIST.  Both are defined
        in the constants_pdef.py param file.  This will
        be used as part of the command to regrid the grib2 storm track
        files into netCDF.

        Args:
            p:       The reference to the ConfigMaster config/param
                     constants_pdef.py
            logger:  The logger to which all logging is directed.

        Returns:
            field_level_string (string):  If REGRID_USING_MET_TOOL is True, 
                                          A string with format -field
                                          'name="HGT"; level="P500";'
                                          for each variable defined in VAR_LIST.
                                          Otherwise, a string with format like:
                                          :TMP:2 |:HGT: 500|:PWAT:|:PRMSL:
                                          which will be used to regrid using
                                          wgrib2.
    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    var_list = getlist(p.getstr('config','VAR_LIST'))
    extra_var_list = getlist(p.getstr('config','EXTRACT_TILES_VAR_LIST'))
    regrid_with_MET_tool = p.getbool('config','REGRID_USING_MET_TOOL')
    full_list = []

    # Append the extra_var list to the var_list
    # and remove any duplicates. *NOTE, order
    # will be lost.
    full_var_list = var_list + extra_var_list
    unique_var_list = list(set(full_var_list))

    if regrid_with_MET_tool:
        name_str = 'name="'
        level_str = 'level="'

        for cur_var in unique_var_list:
            match = re.match(r'(.*)/(.*)', cur_var)
            name = match.group(1)
            level = match.group(2)
            level_val = "_" + level

            # Create the field info string that can be used
            # by the MET Tool regrid_data_plane to perform
            # regridding.
            cur_list = [' -field ', "'", name_str, name, '"; ',
                        level_str, level_val, '";', "'", '\\ ']
            cur_str = ''.join(cur_list)
            full_list.append(cur_str)
        field_level_string = ''.join(full_list)
    else:
        full_list = ['":']
        for cur_var in unique_var_list:
            match = re.match(r'(.*)/(.*)', cur_var)
            name = match.group(1)
            level = match.group(2)
            level_match = re.match(r'([a-zA-Z])([0-9]{1,3})', level)
            level_val = level_match.group(2)

            # Create the field info string that can be used by 
            # wgrib2 to perform regridding.
            if int(level_val) > 0:
                level_str = str(level_val) + ' '
            else:
                # For Z0, Z2, etc. just gather all available.
                level_str = ""

            cur_list = [name, ':', level_str, '|']
            tmp_str = ''.join(cur_list)
            full_list.append(tmp_str)

        # Remove the last '|' and add the terminal double quote.
        field_level_string = ''.join(full_list)
        field_level_string = field_level_string[:-1]
        field_level_string += '"'

    return field_level_string


def create_grid_specification_string(lat, lon, logger, p):
    ''' Create the grid specification string with the format:
         latlon Nx Ny lat_ll lon_ll delta_lat delta_lon
         used by the MET tool, regrid_data_plane.

         Args:
            lat (string):   The latitude of the grid point
            lon (string):   The longitude of the grid point
            logger(string): The name of the logger
            p:              ConfigMaster param/config file
                            constants_pdef.py

         Returns:
            tile_grid_str (string): the tile grid string for the
                                    input lon and lat

    '''

    # Useful for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    regrid_by_MET = p.getbool('config','REGRID_USING_MET_TOOL')

    # Initialize the tile grid string
    # and get the other values from the parameter file
    tile_grid_str = ' '
    nlat = p.getstr('config','NLAT')
    nlon = p.getstr('config','NLON')
    dlat = p.getstr('config','DLAT')
    dlon = p.getstr('config','DLON')
    lon_subtr = p.getfloat('config','LON_ADJ')
    lat_subtr = p.getfloat('config','LAT_ADJ')

    # Format for regrid_data_plane:
    # latlon Nx Ny lat_ll lon_ll delta_lat delta_lonadj_lon = float(lon) - lon_subtr
    adj_lon = float(lon) - lon_subtr
    adj_lat = float(lat) - lat_subtr
    lon0 = str(round_0p5(adj_lon))
    lat0 = str(round_0p5(adj_lat))

    msg = ("DEBUG|[" + cur_filename + ":" + cur_function + "]  nlat:" + nlat + " nlon: " +
           nlon + " lat0:" + lat0 + " lon0: " + lon0)
    logger.debug(msg)

    # Create the specification string based on the requested tool.
    if regrid_by_MET:
        grid_list = ['"', 'latlon ', nlat, ' ', nlon, ' ', lat0, ' ', lon0, ' ',
                     dlat, ' ', dlon, '"']
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
    '''Generates a list of dates of the form yyyymmdd from a being date to end date
    Inputs:
      begin_date -- such as "20070101"
      end_date -- such as "20070103"
    Returns:
      date_list -- such as ["20070101","20070102","20070103"]
    '''

    begin_tm = time.strptime(begin_date, "%Y%m%d")
    end_tm = time.strptime(end_date, "%Y%m%d")
    begin_tv = calendar.timegm(begin_tm)
    end_tv = calendar.timegm(end_tm)
    date_list = []
    for tv in xrange(begin_tv, end_tv + 86400, 86400):
        date_list.append(time.strftime("%Y%m%d", time.gmtime(tv)))
    return date_list


def gen_hour_list(hour_inc, hour_end):
    '''Generates a list of hours of the form hh or hhh
    Inputs:
      hr_inc -- increment in integer format such as 6
      hr_end -- hh or hhh string indicating the end hour for the increment such as "18"
    Returns:
      hour_list -- such as ["00", "06", "12", "18"]
    '''

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
    '''
    Generates a list of initialization date and times of the form yyyymmdd_hh or yyyymmdd_hhh
    Inputs:
      init_begin_date -- yyyymmdd string such as "20070101"
      init_end_date -- yyyymmdd string such as "20070102"
      init_hr_inc -- increment in integer format such as 6
      init_hr_end -- hh or hhh string indicating the end hour for the increment such as "18"
    Returns:
      init_list -- such as ["20070101_00", "20070101_06", "20070101_12", "20070101_18", "20070102_00", "20070102_06", "20070102_12", "20070102_18"]
    '''

    myhourlist = gen_hour_list(init_hr_inc, init_hr_end)

    mydatelist = gen_date_list(init_date_begin, init_date_end)

    date_init_list = []
    for index, my_date in enumerate(mydatelist):
        for my_hour in myhourlist:
            init_string = my_date + "_" + my_hour
            date_init_list.append(init_string)

    return date_init_list


def prune_empty(output_dir, p, logger):
    ''' Start from the output_dir, and recursively check
        all directories and files.  If there are any empty
        files or directories, delete/remove them so they 
        don't cause performance degradation or errors 
        when performing subsequent tasks.

        Input:
            output_dir:  The directory from which searching
                         should begin.


            p:           The reference to the ConfigMaster
                         constants_pdef. 

            logger:      The logger to which all logging is
                         directed.

    '''

    # Retrieve any necessary variables from the constants_pdef.py
    # param/config file.

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    file_paths = []

    # Check for empty files.
    for root, dirs, files in os.walk(output_dir):
        path = root.split('/')

        # Create a full file path by joining the path
        # and filename.
        for file in files:
            file = os.path.join(root, file)
            if os.stat(file).st_size == 0:
                msg = ("INFO|[" + cur_filename + ":" +
                       cur_function + "]|" +
                       "Empty file: " + file +
                       "...removing")

                logger.debug(msg)
                os.remove(file)

    # Now check for any empty directories, some 
    # may have been created when removing
    # empty files.
    for root, dirs, files in os.walk(output_dir):
        for dir in dirs:

            d = os.path.join(root, dir)
            if os.listdir(d) == []:
                msg = ("INFO|[" + cur_filename + ":" +
                       cur_function + "]|" +
                       "Empty directory: " + d +
                       "...removing")
                logger.debug(msg)
                os.rmdir(d)


def apply_series_filters(tile_dir, init_times, series_output_dir, p, logger):
    ''' Apply filter options, as specified in the
        constants_pdef.py param/config file.

        Args:

           tile_dir:           Directory where input data files reside.
                               e.g. data which we will be applying our filter criteria.
           init_times:          List of init times that define the input data.
           series_output_dir:  The directory where the filter results
                               will be stored.
           p       : The reference to the constants_pdef.py
                     param/config file.
           logger  : The logger to which all logging is directed.


        Returns:
            None

    '''

    # Useful for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Retrieve any necessary values from the param/config file,
    # metplus.conf.
    tc_stat_exe = p.getexe('TC_STAT')
    cur_pid = str(os.getpid())
    tmp_dir = os.path.join(p.getdir('TMP_DIR'), cur_pid)
    filter_opts = p.getstr('config','SERIES_ANALYSIS_FILTER_OPTS')

    for cur_init in init_times:
        # Create the ASCII file with the storms that meet the
        # filter criteria.
        filter_path = os.path.join(series_output_dir, cur_init)
        mkdir_p(filter_path)
        filter_file = "filter_" + cur_init + ".tcst"
        filter_filename = os.path.join(series_output_dir,
                                       cur_init, filter_file)
        tc_cmd_list = [tc_stat_exe, " -job filter ",
                       " -lookin ", tile_dir,
                       " -match_points true ",
                       " -init_inc ", cur_init,
                       " -dump_row ", filter_filename,
                       " ", filter_opts]
        tc_cmd = ''.join(tc_cmd_list)
        tcs.tc_stat(p, logger, tc_cmd, series_output_dir)
        msg = ("INFO}[" + cur_filename + ":" + cur_function +
               "]| tc command: " + tc_cmd)
        logger.debug(msg)

        # Check that the filter.tcst file isn't empty. If
        # it is, then use the files from extract_tiles as
        # input (tile_dir = extract_out_dir)
        if not file_exists(filter_filename):
            msg = ("WARN| " + cur_filename + ":" + cur_function +
                   "]| Non-existent filter file, filter " +
                   " Never created by MET Tool tc_stat.")
            logger.debug(msg)
            continue
        elif os.stat(filter_filename).st_size == 0:
            msg = ("WARN| " + cur_filename + ":" + cur_function +
                   "]| Empty filter file, filter " +
                   " options yield nothing.")
            logger.debug(msg)
            continue
        else:
            # Now retrieve the files corresponding to these
            # storm ids that resulted from filtering.
            sorted_storm_ids = get_storm_ids(filter_filename, logger)

            # Retrieve the header from filter_filename to be used in creating the temporary files.
            with open(filter_filename, 'r') as ff:
                header = ff.readline()

            for cur_storm in sorted_storm_ids:
                msg = ("INFO| [" + cur_filename + ":" +
                       cur_function +
                       " ] | Processing storm: " + cur_storm + " for file: " + filter_filename)
                logger.debug(msg)
                storm_output_dir = os.path.join(series_output_dir,
                                                cur_init, cur_storm)
                mkdir_p(storm_output_dir)
                mkdir_p(tmp_dir)
                tmp_file = "filter_" + cur_init + "_" + cur_storm
                tmp_filename = os.path.join(tmp_dir, tmp_file)
                storm_match_list = grep(cur_storm, filter_filename)
                with open(tmp_filename, "a+") as tmp_file:
                    tmp_file.write(header)
                    for storm_match in storm_match_list:
                        tmp_file.write(storm_match)

                # Create the analysis and forecast files based
                # on the storms (defined in the tmp_filename created above)
                # Store the analysis and forecast files in the
                # series_output_dir.
                retrieve_and_regrid(tmp_filename, cur_init, cur_storm,
                                    series_output_dir, logger, p)

    # Check for any empty files and directories and remove them to avoid
    # any errors or performance degradation when performing
    # series analysis.
    prune_empty(series_output_dir, p, logger)

    # Clean up the tmp dir
    rmtree(tmp_dir)


def create_filter_tmp_files(filtered_files_list, filter_output_dir, p, logger):
    ''' Creates the tmp_fcst and tmp_anly ASCII files that contain the full filepath of files that
        correspond to the filter criteria.  Useful for validating that filtering returns the expected
        results/troubleshooting.

        Args:
            filtered_files_list :  A list of the netCDF or grb2 files that result from applying filter options
                                   and running the MET tool tc_stat.

            filter_output_dir   :  The directory where the filtered data is stored

            p:                      Reference to constants_pdef.py

            logger:                The logger to where all logging is directed.

        Returns:
            None: Creates two ASCII files


    '''

    # Useful for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Create the filenames for the tmp_fcst and tmp_anly files.
    tmp_fcst_filename = os.path.join(filter_output_dir, "tmp_fcst_regridded.txt")
    tmp_anly_filename = os.path.join(filter_output_dir, "tmp_anly_regridded.txt")

    fcst_list = []
    anly_list = []

    for file in filtered_files_list:
        fcst_match = re.match(r'(.*/FCST_TILE_F.*.[grb2|nc])', file)
        if fcst_match:
            fcst_list.append(fcst_match.group(1))

        anly_match = re.match(r'(.*/ANLY_TILE_F.*.[grb2|nc])', file)
        if anly_match:
            anly_list.append(anly_match.group(1))

    # Write to the appropriate tmp file
    with open(tmp_fcst_filename, "a+") as fcst_tmpfile:
        for fcst in fcst_list:
            fcst_tmpfile.write(fcst + "\n")

    with open(tmp_anly_filename, "a+") as anly_tmpfile:
        for anly in anly_list:
            anly_tmpfile.write(anly + "\n")


def get_updated_init_times(input_dir, p, logger):
    ''' Get a list of init times, derived by the .tcst files in the
        input_dir (and below).

        Args:
            input_dir:  The topmost directory from which our search for filter.tcst files
                        begins.

            p:          Reference to constants_pdef param/config file.

            logger:     The logger to which all logging is directed.

        Returns:
            updated_init_times_list : A list of the init times represented by the
                                      forecast.tcst files found in the input_dir.
    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    updated_init_times_list = []
    init_times_list = []
    filter_list = get_files(input_dir, ".*.tcst", p)
    if len(filter_list) > 0:
        for f in filter_list:
            match = re.match(r'.*/filter_([0-9]{8}_[0-9]{2,3})', f)
            init_times_list.append(match.group(1))
        updated_init_times_list = sorted(init_times_list)

    return updated_init_times_list


def get_dirs(base_dir, p, logger):
    '''Get a list of directories under a base directory.

        Args:
            base_dir:  The base directory from where search begins
            p:         The reference to constants_pdef.py, the param/config file.
            logger:    The logger to which all logging is directed.

       Returns:
           dir_list:  A list of directories under the base_dir
    '''

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    dir_list = []
    for dirname, dirs, filenames in os.walk(base_dir):
        for d in dirs:
            dir_list.append(os.path.join(dirname, d))

    return dir_list

def getlist(s,logger=None):

    # returns a list of string elements from a comma or space
    # separated string of values, returns and empty list
    # if s is ''
    # '4,4,2,4,2,4,2, ' or '4,4,2,4,2,4,2 ' or
    # '4, 4, 4, 4, ' or '4, 4, 4, 4 '

    # removes surrounding comma, and spaces, if present.
    s = s.strip().strip(',').strip()

    if ',' in s:
        s = s.split(',')
        s = [item.strip() for item in s]
    else:
        s = s.split()

    return s

def getlistfloat(s):
    s = getlist(s)
    s = [float(i) for i in s]
    return s

def getlistint(s):
    s = getlist(s)
    s = [int(i) for i in s]
    return s

if __name__ == "__main__":
    # test grep
    # pattern = "abcd"
    # file = "./test.txt"
    # m =  grep(pattern, file)
    # if m:
    #     print("Found a match")
    # else:
    #     print( "No match found")


    # test the rounding to the nearest n.5

    # counter = 0
    # vals =     [3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0]
    # expected = [3.0,3.0,3.0,3.5,3.5,3.5,3.5,3.5,4.0,4.0,4.0]
    # for val in vals:
    #    pt = round_0p5(val)
    #    if(pt != expected[counter]):
    #       raise Exception("round_0p5 failed to round the input value to expected value.")
    #    counter +=1



    # val = -14.1
    # pt = round_0p5(val)
    # print("{:.1f} rounded = {:.1f}".format(val,pt))
    # val = 14.1
    # pt = round_0p5(val)
    # print("{:.1f} rounded = {:.1f}".format(val,pt))

    init_list = []
    init_list = gen_init_list("20141201", "20150331", 6, "18")
