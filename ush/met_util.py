#!/usr/bin/python
from __future__ import print_function

import constants_pdef as P
import os
import errno
import logging
import time
import re
import math
import sys
import string_template_substitution as sts
import subprocess

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
    pt_five = round(rval,0) / 2
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
        

def get_logger(p):
    '''Gets a logger

       Args:
           p:   the ConfigMaster constants param file

       Returns:
           logger: the logger
    '''

    # Retrieve all logging related parameters from the param file
    log_dir = p.opt["LOG_DIR"]
    log_level = p.opt["LOG_LEVEL"]
    log_filename = p.opt["LOG_FILENAME"]

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
    fileHandler = logging.FileHandler(log_path,mode='a')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger

 
def file_exists(filename):
    ''' Determines if a file exists
        NOTE:  This is not a Python idiomatic way
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

    if os.path.isfile(filename):
        return True
    else:
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
            match = re.search(pattern,line)
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
            match = re.match(r'.*(grib|grb|grib2|grb2)$',filename)
            if match:
                # Join the two strings to form the full
                # filepath.
                filepath = os.path.join(root,filename)
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
    storm_id_list = set()
    with open(filter_filename) as fileobj:
         # skip the first line as it contains the header
         next(fileobj)
         for line in fileobj:
             # split the columns, which are separated by one or
             # more whitespace, hence the line.split() without any
             # args
             cols = line.split()

             # we are only interested in the 4th column, STORM_ID
             storm_id_list.add(str(cols[3]))

    # sort the unique storm ids, copy the original
    # set by using sorted rather than sort.
    sorted_storms  = sorted(storm_id_list)
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
    print("filedir to check: ", filedir)
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
                filepath = os.path.join(root,filename)
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

    return name,level


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
            None  raises OSError if files are missing

    '''

    anly_tiles = get_files(tile_dir, anly_file_regex, logger)
    fcst_tiles = get_files(tile_dir, fcst_file_regex, logger)

    num_anly_tiles = len(anly_tiles)
    num_fcst_tiles = len(fcst_tiles)
   
 
    # Check that there are analysis and forecast tiles (which were, or should have been created earlier by extract_tiles).
    if not anly_tiles :
        # Cannot proceed, the necessary 30x30 degree analysis tiles are missing
        logger.error("ERROR: No anly tile files were found  "+ tile_dir)
        raise OSError("No 30x30 anlysis tiles were found")
    elif not fcst_tiles :
        # Cannot proceed, the necessary 30x30 degree fcst tiles are missing
        logger.error("ERROR: No fcst tile files were found  "+ tile_dir)
        raise OSError("No 30x30 fcst tiles were found")

    # Check for same number of fcst and analysis files
    if num_anly_tiles != num_fcst_tiles:
        # Something is wrong, we are missing
        # either an ANLY tile file or a FCST tile
        # file, this indicates a serious problem.
        logger.warn("WARNING: There are a different number of anly and fcst tiles, there should be the same number...")

    return 0


def extract_year_month(init_time, logger):
    ''' Retrieve the YYYYMM from the initialization time with format YYYYMMDD_hh

        Args:
            init_time (string):  The initialization time of expected format YYYYMMDD_hh

        Returns:
            year_month (string):  The YYYYMM portion of the initialization time

    '''
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Match on anything that starts with 1 or 2 (for the century) followed by 5 digits
    # for the remainder of the YYYMM
    ym = re.match(r'^((1|2)[0-9]{5})',init_time)
    #ym = re.match(r'^2[0-9]{5}',init_time)
    if ym:
        year_month = ym.group(0)
        return year_month
    else:
        logger.warning("WARNING|" +  "[" + cur_filename + ":" + cur_function + "]" + 
                       " | Cannot extract YYYYMM from initialization time, unexpected format")
        raise Warning("Cannot extract YYYYMM from initialization time, unexpected format")



def retrieve_and_regrid(tmp_filename, cur_init, cur_storm, out_dir, logger, p):
    ''' Retrieves the data from the GFS_DIR (defined in constants_pdef.py) that
        corresponds to the storms defined in the tmp_filename:
        1) create the analysis tile and forecast file names from the 
           tmp_filename file. 
        2) perform regridding via MET tool (regrid_data_plane) and store results
           (netCDF files) in the out_dir or via 
   
        Args:
        tmp_filename:      Filename of the temporary filter file in 
                           the /tmp directory. Contains rows 
                           of data corresponding to a storm id of varying
                           lead times.

        cur_init:          The current init time
     
        cur_storm:         The current storm 
      
        out_dir:           The directory where regridded netCDF output is saved.
   

        logger     :       The name of the logger used in logging.
        p          :       Referenct to the ConfigMaster constants_pdef.py
                           param/config file.
     
        Returns:
        None:              Performs regridding via invoking regrid_data_plane
                           on the forecast and analysis files via a latlon 
                           string with the following format: 
                           latlon Nx Ny lat_ll lon_ll delta_lat delta_lon 
                           NOTE:  thes values are defined in 
                                  the extract_tiles_parm parameter/config 
                                  file as NLAT, NLON.

    '''

    # Extract the columns of interest: init time, lead time, 
    # valid time lat and lon of both  tropical cyclone tracks, etc. 
    # Then calculate the forecast hour and other things.
   
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    gfs_dir = p.opt["GFS_DIR"]
    regrid_data_plane_exe = p.opt["REGRID_DATA_PLANE"]
    wgrib2_exe = p.opt["WGRIB2"]
    egrep_exe = p.opt["EGREP_EXE"]
 
    regrid_with_MET_tool = p.opt["REGRID_USING_MET_TOOL"]
   

    # obtain the gfs_fcst dir
    with open(tmp_filename, "r") as tf:
        for line in tf:
            col = line.split()
            # Columns of interest are 8, 9, 10, 19, 20, 21, and 22
            # for init time, lead time, valid time, alat, alon, 
            # blat, and blon (positions of the two extra-tropical
            # cyclone tracks)  but Python is zero-based so indices 
            # differ by 1.
            init, lead, valid, alat, alon, blat, blon = col[7], col[8], col[9],col[18],\
                                                        col[19],col[20], col[21]

            # integer division for both Python 2 and 3
            lead_time = int(lead)
            fcst_hr = lead_time // 10000
            fcst_hr_str = str(fcst_hr)

            init_ymd_match = re.match(r'[0-9]{8}',init)
            if init_ymd_match:
                init_ymd = init_ymd_match.group(0)
            else:
                raise RuntimeError('init time has unexpected format for YMD')
                logger.WARN("RuntimeError raised")

            init_ymdh_match = re.match(r'[0-9|_]{11}',init)
            if init_ymdh_match:
                init_ymdh = init_ymdh_match.group(0)
            else:
                logger.WARN("RuntimeError raised")
                #raise RuntimeError('init time has unexpected format for YMDH')

            valid_ymd_match = re.match(r'[0-9]{8}',valid)
            if valid_ymd_match:
                valid_ymd = valid_ymd_match.group(0)
            else:
                logger.WARN("RuntimeError raised")
                #raise RuntimeError('valid time has unexpected format for YMD')

            valid_ymdh_match = re.match(r'[0-9|_]{11}',valid)
            if valid_ymdh_match:
                valid_ymdh = valid_ymdh_match.group(0)
            else:
                logger.WARN("RuntimeError raised")
                #raise RuntimeError('valid time has unexpected format for YMDH')

                
            lead_str = str(fcst_hr).zfill(3)
                
            fcst_dir = os.path.join(gfs_dir, init_ymd)
            init_ymdh_split = init_ymdh.split("_")
            init_YYYYmmddHH = "".join(init_ymdh_split)
            fcstSTS = sts.StringTemplateSubstitution(logger,
                                                     p.opt["GFS_FCST_FILE_TMPL"],
                                                     init=init_YYYYmmddHH, 
                                                     lead=lead_str)

            fcst_file = fcstSTS.doStringSub()
            fcst_filename = os.path.join(fcst_dir, fcst_file)

            anly_dir =  os.path.join(gfs_dir, valid_ymd)
            valid_ymdh_split = valid_ymdh.split("_")
            valid_YYYYmmddHH = "".join(valid_ymdh_split)
            anlySTS = sts.StringTemplateSubstitution(logger, 
                                                p.opt["GFS_ANLY_FILE_TMPL"],
                                                valid=valid_YYYYmmddHH,
                                                lead=lead_str)
            anly_file = anlySTS.doStringSub()
            anly_filename = os.path.join(anly_dir, anly_file)

            # Do regridding via MET Tool or wgrib2 tool.
            if regrid_with_MET_tool:
                # MET Tool regrid_data_plane used to regrid.
                # Create the filename for the regridded file, which is a 
                # netCDF file.
                fcstSTS = sts.StringTemplateSubstitution(logger,
                                                    p.opt["GFS_FCST_NC_FILE_TMPL"],                                                 
                                                    init=init_YYYYmmddHH, 
                                                    lead=lead_str)
                fcst_file = fcstSTS.doStringSub()
                fcst_filename = os.path.join(fcst_dir, fcst_file)

  
                anlySTS = sts.StringTemplateSubstitution(logger, 
                                                  p.opt["GFS_ANLY_NC_FILE_TMPL"],
                                                  valid=valid_YYYYmmddHH,
                                                  lead=lead_str)
      
                anly_file = anlySTS.doStringSub()
                anly_filename = os.path.join(anly_dir, anly_file)

            else:
                # wgrib2 used to regrid.
                # Create the filename for the regridded file, which is a 
                # grib2 file.
                fcstSTS = sts.StringTemplateSubstitution(logger,
                                                    p.opt["GFS_FCST_FILE_TMPL"],                                                 
                                                    init=init_YYYYmmddHH, 
                                                    lead=lead_str)
                fcst_file = fcstSTS.doStringSub()
                fcst_filename = os.path.join(fcst_dir, fcst_file)

  
                anlySTS = sts.StringTemplateSubstitution(logger, 
                                                  p.opt["GFS_ANLY_FILE_TMPL"],
                                                  valid=valid_YYYYmmddHH,
                                                  lead=lead_str)
      
                anly_file = anlySTS.doStringSub()
                anly_filename = os.path.join(anly_dir, anly_file)

            
            # Create the tmp file to be used for troubleshooting 
            # and verification.  The file will contain all the 
            # fcst and analysis files that will be used as input 
            # for another script.
            tmp_fcst_filename = os.path.join(out_dir, 
                                             "tmp_fcst_regridded.txt")
            tmp_anly_filename = os.path.join(out_dir, 
                                             "tmp_anly_regridded.txt")
            # Check if the forecast file exists. If it doesn't 
            # exist, just log it
            if file_exists(fcst_filename):
                msg = ("INFO| [" + cur_filename + ":" + cur_function +  
                       " ] | Forecast file: " + fcst_filename)
                logger.info(msg)
                # Write this to the tmp file (to be used for 
                # troubleshooting and validation) which will be saved
                # in the EXTRACT_OUT_DIR
                with open(tmp_fcst_filename, "a+") as tmpfile:
                    tmpfile.write(fcst_filename+"\n")
                
            else:
                msg = ("WARNING| [" + cur_filename + ":" + 
                       cur_function +  " ] | " +
                       "Can't find forecast file, continuing anyway: " + 
                       fcst_filename)
                logger.warn(msg)
                continue

            # Check if the analysis file exists. If it doesn't 
            # exist, just log it.
            if file_exists(anly_filename):
                    msg = ("INFO| [" + cur_filename + ":" +
                           cur_function +  " ] | Analysis file: " + 
                           anly_filename)
                    logger.info(msg)
                    # Write this to the tmp file (to be used for 
                    # troubleshooting and validation). This will
                    # be stored in the EXTRACT_OUT_DIR
                    with open(tmp_anly_filename, "a+") as tmpfile:
                        tmpfile.write(anly_filename+"\n")
            else:
                msg = ("WARNING| [" + cur_filename + ":" + 
                       cur_function +  " ] | " + 
                       "Can't find analysis file, continuing anyway: " +
                       anly_filename)
                logger.warn(msg)
                continue

            # Create the arguments used to perform regridding.
            fcst_base = os.path.basename(fcst_filename)
            anly_base = os.path.basename(anly_filename)

            fcst_grid_spec = create_grid_specification_string(alat,alon,
                                                              logger,p)
            anly_grid_spec = create_grid_specification_string(blat,blon,
                                                              logger,p)
 
            tile_dir = os.path.join(out_dir, cur_init, cur_storm)
            fcst_hr_str = str(fcst_hr).zfill(3)
            
            fcst_regridded_filename = p.opt["FCST_TILE_PREFIX"] + \
                                      fcst_hr_str + "_" + \
                                      fcst_base
            fcst_regridded_file = os.path.join(tile_dir, fcst_regridded_filename)
            anly_regridded_filename =  p.opt["ANLY_TILE_PREFIX"] + fcst_hr_str + \
                                       "_" + anly_base
            anly_regridded_file = os.path.join(tile_dir, anly_regridded_filename)
            
            # Regrid the fcst file only if a fcst tile 
            # file does NOT already exist.
            # Create new gridded file for fcst tile
            if file_exists(fcst_regridded_file):
                msg = ("INFO| [" + cur_filename + ":" + 
                       cur_function +  " ] | Forecast tile file " + 
                       fcst_regridded_file + " exists, skip regridding")
                logger.info(msg)
            else:
                # Perform regridding on the records of interest
                var_level_string = retrieve_var_info(p,logger)
                if regrid_with_MET_tool:
                    # Perform regridding using MET Tool regrid_data_plane
                    fcst_cmd_list = [regrid_data_plane_exe, ' ', 
                                     fcst_filename, ' ',
                                     fcst_grid_spec, ' ',
                                     fcst_regridded_file, ' ',
                                     var_level_string,
                                     ' -method NEAREST '   ]
                    regrid_cmd_fcst = ''.join(fcst_cmd_list)
                    regrid_fcst_out = subprocess.check_output(regrid_cmd_fcst,
                                                              stderr=
                                                              subprocess.STDOUT,
                                                              shell=True)
                    msg = ("INFO|[regrid]| regrid_data_plane regrid command:" + 
                           regrid_cmd_fcst)
                    logger.info(msg)
                   
                else:
                    # Perform regridding via wgrib2 
                    requested_records = retrieve_var_info(p,logger)
                    fcst_cmd_list = [wgrib2_exe, ' ' , fcst_filename, ' | ', 
                                     egrep_exe, ' ', requested_records, '|', 
                                     wgrib2_exe, ' -i ', fcst_filename,
                                     ' -new_grid ', fcst_grid_spec, ' ', 
                                     fcst_regridded_file]
                    wgrb_cmd_fcst = ''.join(fcst_cmd_list)
                    msg = ("INFO|[wgrib2]| wgrib2 regrid command:" + 
                           wgrb_cmd_fcst)
                    logger.info(msg)
                    wgrb_fcst_out = subprocess.check_output(wgrb_cmd_fcst, 
                                                            stderr=
                                                            subprocess.STDOUT, 
                                                            shell=True)

            # Create new gridded file for anly tile
            if file_exists(anly_regridded_file):
                logger.info("INFO| [" + cur_filename + ":" +                                                        
                                    cur_function +  " ] |" + 
                                    " Analysis tile file: " + 
                                    anly_regridded_file + 
                                    " exists, skip regridding")
            else:
                # Perform regridding on the records of interest
                var_level_string = retrieve_var_info(p,logger)
                if regrid_with_MET_tool:
                    anly_cmd_list = [regrid_data_plane_exe, ' ',
                                     anly_filename, ' ',
                                     anly_grid_spec, ' ',
                                     anly_regridded_file, ' ',
                                     var_level_string, ' ',
                                     ' -method NEAREST ' ]
                    regrid_cmd_anly = ''.join(anly_cmd_list)
                    regrid_anly_out = subprocess.check_output(regrid_cmd_anly,                                                              
                                                              stderr= 
                                                              subprocess.STDOUT,                                                              
                                                              shell=True)
                    msg = ("INFO|[regrid]| on anly file:" + anly_regridded_file)
                    logger.info(msg)
                else:
                    # Regridding via wgrib2.
                    requested_records = retrieve_var_info(p,logger)
                    anly_cmd_list = [wgrib2_exe, ' ' , anly_filename, ' | ', 
                                     egrep_exe,' ', requested_records, '|', 
                                     wgrib2_exe, ' -i ', anly_filename,
                                     ' -new_grid ', anly_grid_spec, ' ', 
                                     anly_regridded_file]
                    wgrb_cmd_anly = ''.join(anly_cmd_list)
                    wgrb_anly_out = subprocess.check_output(wgrb_cmd_anly, 
                                                            stderr=
                                                            subprocess.STDOUT, 
                                                            shell=True)
                    msg = ("INFO|[wgrib2]| Regridding via wgrib2:" + 
                           wgrb_cmd_anly)
                    logger.info(msg)

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
            field_level_string (string):  If MET_format is True, 
                                          A string with format -field
                                          'name="HGT"; level="P500";'
                                          for each variable defined in VAR_LIST.
                                          Otherwise, a string with format like:
                                          :TMP:2 |:HGT: 500|:PWAT:|:PRMSL:
                                          which will be used to regrid using
                                          wgrib2.
    '''

    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    var_list = p.opt["VAR_LIST"]
    extra_var_list = p.opt["EXTRACT_TILES_VAR_LIST"]
    MET_format = p.opt["REGRID_USING_MET_TOOL"]
    full_list = []


    # Append the extra_var list to the var_list
    # and remove any duplicates. *NOTE, order
    # will be lost.
    full_var_list = var_list + extra_var_list
    unique_var_list = list(set(full_var_list)) 

    if MET_format:
        name_str = 'name="'
        level_str = 'level="'
        field_level_string = ''

        for cur_var in unique_var_list:
            match = re.match(r'(.*)/(.*)',cur_var)
            name = match.group(1) 
            level= match.group(2)
            level_match = re.match(r'([a-zA-Z])([0-9])', level)
            level_val = level_match.group(2)

            # Create the field info string that can be used
            # by the MET Tool regrid_data_plane to perform
            # regridding.
            cur_list = [' -field ', "'", name_str, name, '"; ',
                        level_str, level, '";', "'", '\\ ']
            cur_str = ''.join(cur_list)
            full_list.append(cur_str)
        field_level_string = ''.join(full_list)
    else:
        full_list = ['":']
        for cur_var in unique_var_list:
            match = re.match(r'(.*)/(.*)',cur_var)
            name = match.group(1) 
            level= match.group(2)
            level_match = re.match(r'([a-zA-Z])([0-9]{1,3})', level)
            level_val = level_match.group(2)
            # Create the field info string that can be used by 
            # wgrib2 to perform regridding.
            if int(level_val) > 0:
                level_str = str(level_val) + ' ' 
            else:
                # For Z0, Z2, etc. just gather all available.
                level_str = ""
            
            cur_list = [ name, ':', level_str, '|']
            tmp_str = ''.join(cur_list)
            full_list.append(tmp_str)
        # Remove the last '|' and add the terminal double quote.
        field_level_string = ''.join(full_list)
        field_level_string = field_level_string[:-1]
        field_level_string = field_level_string + '"'
           
    return field_level_string



def create_grid_specification_string(lat,lon,logger,p):
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


    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    regrid_by_MET = p.opt["REGRID_USING_MET_TOOL"]

    # initialize the tile grid string
    # and get the other values from the parameter file
    tile_grid_str = ' '
    nlat = str(p.opt["NLAT"])
    nlon = str(p.opt["NLON"])
    dlat = str(p.opt["DLAT"])
    dlon = str(p.opt["DLON"])
    lon_subtr = p.opt["LON_ADJ"]
    lat_subtr = p.opt["LAT_ADJ"]

    lon0 = str(round_0p5(float(lon)))
    lat0 = str(round_0p5(float(lat)))

    # Format for regrid_data_plane:
    # latlon Nx Ny lat_ll lon_ll delta_lat delta_lon
    if regrid_by_MET:
        grid_list = ['"', 'latlon ', nlat, ' ', nlon, ' ', lat0, ' ', lon0, ' ',
                     dlat, ' ', dlon, '"']
    else:
       adj_lon = float(lon) - lon_subtr
       adj_lat = float(lat) - lat_subtr 
       lon0 = str(round_0p5(adj_lon))
       lat0 = str(round_0p5(adj_lat))
       grid_list = ['latlon ', lon0, ':', nlon, ':', dlon, ' ', 
                    lat0, ':', nlat, ':', dlat]

    tile_grid_str = ''.join(grid_list)
    msg = ("INFO|" + cur_filename + ":" + cur_function +
           "| complete grid specification string: " + tile_grid_str)
    logger.info(msg)
    return tile_grid_str


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
            file = os.path.join(root,file)
            if os.stat(file).st_size == 0:
                msg = ("INFO|[" +cur_filename + ":" + 
                       cur_function + "]|" + 
                       "Empty file: " + file +
                       "...removing" )
                 
                log.info(msg)
                os.remove(file)


    # Now check for any empty directories, some 
    # may have been created when removing
    # empty files.
    for root,dirs, files in os.walk(output_dir):
        for dir in dirs:
            d = os.path.join(root,dir)
            if not os.listdir(d):
                msg = ("INFO|[" + cur_filename + ":" +
                       cur_function + "]|" +
                       "Empty directory: " + d +
                       "...removing")
                logger.info(msg)  
                os.rmdir(d)

       



if __name__ == "__main__":
    
    #test grep
    #pattern = "abcd"
    #file = "./test.txt"
    #m =  grep(pattern, file)
    #if m:
    #     print("Found a match")
    #else:
    #     print( "No match found")


    #test the rounding to the nearest n.5
    
    #counter = 0
    #vals =     [3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0]
    #expected = [3.0,3.0,3.0,3.5,3.5,3.5,3.5,3.5,4.0,4.0,4.0]
    #for val in vals:
    #    pt = round_0p5(val)
    #    if(pt != expected[counter]):
    #       raise Exception("round_0p5 failed to round the input value to expected value.")
    #    counter +=1
           
 
    
    val = -14.1
    pt = round_0p5(val)
    print("{:.1f} rounded = {:.1f}".format(val,pt))
    val = 14.1
    pt = round_0p5(val)
    print("{:.1f} rounded = {:.1f}".format(val,pt))


