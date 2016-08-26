#!/usr/bin/python
from __future__ import print_function

import constants_pdef as P
import os
import errno
import logging
import time
import re
import math

''' A collection of utility functions used to perform necessary series
    analysis tasks and other preprocessing tasks.


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
        # exist_ok, that when set to True will enable the mkdir -p functionality
        # unless mode is provided and the existing directory has different permissions
        # from the intended ones.  In this situation the OSError exception is raised.
        #

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
    output_dir = p.opt["OUT_DIR"]
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
    #logger.setLevel(log_level)
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


def get_filepaths(dir):
    '''Generates the file names in a directory tree
       by walking the tree either top-down or bottom-up.
       For each directory in the tree rooted at
       the directory top (including top itself), it
       produces a 3-tuple: (dirpath, dirnames, filenames).

       This solution was found on Stack Overflow:
       http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python#3207973

       **scroll down to the section with "Getting Full File Paths From a Directory and All Its Subdirectories"

    Args:
        dir (string): The base directory from which we
                      begin the search for filenames.
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
