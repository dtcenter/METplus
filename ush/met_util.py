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



def get_env_var(env_name, p, logger):
    '''Get the environment variable, if it isn't found, look for
       it in the param/config file.  If it hasn't been found, then
       log and exit.

    '''
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
    if env_name not in os.environ:
        # Look for env_name in param/config file
        try:
          var = p.opt[env_name]
          os.environ[env_name] = var
          logger.info('INFO|'+ cur_filename + ':' + cur_function + '|' + 'Setting ' + env_name + ' to ' + var)
        except NameError as e:
          logger.error('ERROR|'+ cur_filename + ':' + cur_function + '|' +'No env name defined in param file, exiting')
        except KeyError as k:
          logger.error('ERROR|'+ cur_filename + ':' + cur_function + '|' +'No env name defined in param file, exiting')
        else:
          val = os.environ[env_name]
          logger.info('INFO|' + cur_filename + ':' + cur_function + '|' + 'Now ' + env_name + ' is set to ' + val)



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


