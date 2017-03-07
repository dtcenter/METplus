#!/usr/bin/env python
from __future__ import print_function

import constants_pdef as P
import logging
import os
import sys
import met_util as util

def main():
    '''
        Master MET+ script that invokes the necessary Python scripts
        to perform various activities, such as series analysis.
    '''
    # Retrieve parameters from corresponding param file
    p = P.Params() 
    p.init(__doc__)

    # Used for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name
   
    logger = util.get_logger(p)

    # Get the list of processes to call
    process_list = p.opt["PROCESS_LIST"]

    # Get the name of the config file to use
    config_file = p.getConfigFilePath()

    for item in process_list:

        if config_file == None:
            cmd = "%s" % item
            logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Running: " + cmd)
            ret = os.system(cmd)
            if ret != 0:
                logger.error("ERROR | [" + cur_filename +  ":" + cur_function + "] | " + "Problem executing: " + cmd)
                exit(0)
        else:
            cmd = "%s -c %s" % (item, config_file)
            logger.info("INFO | [" + cur_filename +  ":" + cur_function + "] | " + "Running: " + cmd)
            ret = os.system(cmd)
            if ret != 0:
                logger.error("ERROR | [" + cur_filename +  ":" + cur_function + "] | " + "Problem executing: " + cmd)
                exit(0)
            
        
if __name__ == "__main__":
    main()
