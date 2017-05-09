#!/usr/bin/env python

from __future__ import print_function,division

import produtil.setup
import sys
import os
import re
import met_util as util


def main():

    """Convert MET TC-Pairs output (A-deck and B-deck track files) into format for SBU cyc-new.dat and match.dat.
    Save each cyc-new.dat,match.dat pairing into a subdirectory based on their corresponding YYYYMMDD under the 
    directory specified in the constants_pdef config/param file.
    
    :return: None, creates two files: cyc-new.dat and match.dat"""

    # Retrieve any necessary values from the param/config file, constants_pdef
    input_dir = p.getdir('TC_PAIRS_DIR')
    adeck_prefix = p.getstr('config','ADECK_FILE_PREFIX')
    base_cyclone_relative_dir = p.getdir('SBU_OUTPUT_DIR')
    tc_pair_extension = '.tcst'
    regex = adeck_prefix + ".*." + tc_pair_extension
    tc_pairs = util.get_files(input_dir, regex, logger)

    cyc_dict = {}
    model_dict = {}

    for tc in tc_pairs:
        # Retrieve the date from the filename, collect all the
        # necessary values from the tc-pairs output file
        # that correspond to this date and create a cyc-new.dat
        # and model.dat file.  Each date sub-directory will have its own
        # cyc-new.dat and model.dat file corresponding to that date.
        with open(tc, "r") as cur_tc_file:
            # skip the header
            next(cur_tc_file)
            logger.info('Processing current file: {}'.format(cur_tc_file))
            for line in cur_tc_file:
                col = line.split()
                cyclone_number = col[5]
                init_time = col[7]
                fcst_lead_hh = str(col[8]).zfill(3)
                adeck_lat = col[18]
                adeck_lon = col[19]

                # Retrieve the date and create the full path and filenames.
                match = re.match(r'([0-9]{8})_[0-9]{6}', init_time)
                cur_date = match.group(1)
                cur_sub_dir = os.path.join(base_cyclone_relative_dir, cur_date)
                util.mkdir_p(cur_sub_dir)
                cyc_filename = os.path.join(cur_sub_dir, "cyc-new-test.dat")
                model_filename = os.path.join(cur_sub_dir, "model-test.dat")

                # Min SLP (MSLP) is the center pressure
                adeck_mslp = col[29]
                bdeck_mslp = col[30]
                cyc_column_elements = [cyclone_number, ' ', fcst_lead_hh, ' ', adeck_lon, ' ', adeck_lat, ' ',
                                       adeck_mslp]
                model_column_elements = [fcst_lead_hh, ' ', cyclone_number, ' ', cyclone_number, ' ']
                cyc_columns = '   '.join(cyc_column_elements)
                model_columns = '   '.join(model_column_elements)

                # If any of our columns of interest contains 'NA', skip to the next line.
                if 'NA' in cyc_columns or 'NA' in model_columns or bdeck_mslp == 'NA':
                    continue

                # Now that we don't have any 'NA' values, we can calculate the center pressure bias and
                # append that to the model_columns string.
                center_pressure_bias = int(adeck_mslp) - int(bdeck_mslp)
                logger.debug("\nReading from file:{},cyclone num:{},init_time:{}, fcst_lead:{}, lon:{}, lat:{}, AMSLP:{}, BMSLP:{}, Bias {}".format(tc, cyclone_number, init_time, fcst_lead_hh, adeck_lon, adeck_lat, adeck_mslp,
                                    bdeck_mslp, center_pressure_bias))
                model_columns = model_columns + ' ' + str(center_pressure_bias)

                # Open each file, retrieve data, write data, then close files.
                # Use a dictionary to keep track of the filename (full path) to its associated date.
                cyc_dict = update_dictionary(cyc_dict, cur_date, cyc_filename)
                model_dict = update_dictionary(model_dict, cur_date, model_filename)
                logger.info("Writing to corresponding cyc_new.dat and model.dat files for {}".format(cur_date))
                logger.debug("Day: {},Cyc column: {}".format(cur_date, cyc_columns)) 
                cyc_file = open(cyc_filename, 'a')
                model_file = open(model_filename, 'a')
                cyc_file.write(cyc_columns)
                cyc_file.write("\n")
                logger.debug("Day: {},Model column: {}".format(cur_date, model_columns)) 
                model_file.write(model_columns)
                model_file.write("\n")

                # Close the files.
                model_file.close()
                cyc_file.close()

    logger.info("Finished")


def update_dictionary(cur_dict, cur_key, cur_file):
    """ Update the dictionary with a new key-value
        pair if the key doesn't already exist 
    """

    if cur_key not in cur_dict:
        logger.debug("Adding new key {} and value: {} to dictionary".format(cur_key, cur_file))
        cur_dict[cur_key] = cur_file
    return cur_dict


if __name__ == "__main__":

    # sleep is for debugging in pycharm so I can attach to this process
    # from the os.system call in master_met_plus.py
    #import time
    #time.sleep(60)

    # Testing constants_pdef until produtil is fully integrated.
    #import constants_pdef as P
    #test = P.Params()
    #test.init(__doc__) ## Put description of the code here


    try:
        if 'JLOGFILE' in os.environ:
            produtil.setup.setup(send_dbn=False, jobname='tc2cyclone_relative',jlogfile=os.environ['JLOGFILE'])
        else:
            produtil.setup.setup(send_dbn=False, jobname='tc2cyclone_relative')
        produtil.log.postmsg('tc2cyclone_relative is starting')

        # Read in the configuration object p
        import config_launcher
        if len(sys.argv) == 3:
            p = config_launcher.load_baseconfs(sys.argv[2])
        else:
            p = config_launcher.load_baseconfs()
        logger = util.get_logger(p)
        if 'MET_BASE' not in os.environ:
            os.environ['MET_BASE'] = p.getdir('MET_BASE')
        main()
        produtil.log.postmsg('tc2cyclone_relative completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'tc2cyclone_relative failed: %s'%(str(e),),exc_info=True)
        sys.exit(2)



