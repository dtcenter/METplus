#!/usr/bin/env python

from __future__ import print_function,division

import produtil.setup
rom produtil.run import batchexe, run, checkrun, runstr
import sys
import os
import re
import met_util as util
import math

def main():

    """Convert MET TC-Pairs output (A-deck and B-deck track files) into format for SBU cyc-new.dat and match.dat.
    Save each cyc-new.dat,match.dat pairing into a subdirectory based on their corresponding YYYYMMDD under the 
    directory specified in the constants_pdef config/param file.
    
    return: None, creates four files: cyc-new.dat, match.dat, cyc-count.dat, and mcount.dat"""

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
            logger.info('Processing current file: {}'.format(cur_tc_file.name))
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

                # Output files containing the counts
                model_count_fname = os.path.join(cur_sub_dir, 'mcount.dat')
                cyc_count_fname = os.path.join(cur_sub_dir, 'cyc-count.dat')

                # Min SLP (MSLP) is the center pressure
                adeck_mslp = col[29]
                bdeck_mslp = col[30]

                # Convert the adeck_lon, adeck_lat into grid lon,lat points on the SBU map if they aren't 'NA'
                if 'NA' == adeck_lat or 'NA' == adeck_lon:
                    continue

                grid_lon, grid_lat = lonlat2grid(adeck_lon, adeck_lat)

                cyc_column_elements = [cyclone_number, ' ', fcst_lead_hh, ' ', grid_lon, ' ', grid_lat, ' ',
                                       adeck_mslp]
                model_column_elements = [fcst_lead_hh, ' ', cyclone_number, ' ', cyclone_number, ' ']
                cyc_columns = '   '.join(cyc_column_elements)
                model_columns = '   '.join(model_column_elements)

                # If any other columns of interest contains 'NA', skip to the next line.
                if 'NA' in cyc_columns or 'NA' in model_columns or bdeck_mslp == 'NA':
                    continue

                # Now that we don't have any 'NA' values, we can calculate the center pressure bias and
                # append that to the model_columns string.
                center_pressure_bias = int(adeck_mslp) - int(bdeck_mslp)
                logger.debug("\nReading from file:{},cyclone num:{},init_time:{}, fcst_lead:{}, lon:{}, lat:{},"
                             " AMSLP:{}, BMSLP:{}, Bias {}".format(tc, cyclone_number, init_time, fcst_lead_hh,
                             adeck_lon, adeck_lat, adeck_mslp, bdeck_mslp, center_pressure_bias))
                model_columns = model_columns + ' ' + str(center_pressure_bias)

                # Open each file, retrieve data, write data, then close files.
                # Use a dictionary to keep track of the filename (full path) to its associated date.
                cyc_dict = update_dictionary(cyc_dict, cur_date, cyc_filename)
                model_dict = update_dictionary(model_dict, cur_date, model_filename)
                logger.info("Writing to corresponding cyc_new.dat and model.dat files for {}".format(cur_date))
                logger.debug("Day: {},Cyc column: {}".format(cur_date, cyc_columns)) 
                try:
                    with open(cyc_filename, 'a') as cyc_file:
                        cyc_file.write(cyc_columns)
                        cyc_file.write("\n")
                    with open(model_filename, 'a') as model_file:
                        model_file.write(model_columns)
                        model_file.write("\n")
                    logger.debug("Day: {},Model column: {}".format(cur_date, model_columns))
                except IOError as e:
                    logger.error("ERROR: Couldn't open or write to output file")

            logger.info("INFO Finished creating output for " + cur_tc_file.name + ", on to generating counts...")

    post_process(base_cyclone_relative_dir)
    logger.info("Finished")


def get_date(some_time):
    """ Extract the date from the specified time (ie. valid time, init time)"""
    match = re.match(r'([0-9]{8})_[0-9]{6}', some_time)
    cur_date = match.group(1)
    return cur_date


def update_dictionary(cur_dict, cur_key, cur_file):
    """ Update the dictionary with a new key-value
        pair if the key doesn't already exist 
    """

    if cur_key not in cur_dict:
        logger.debug("Adding new key {} and value: {} to dictionary".format(cur_key, cur_file))
        cur_dict[cur_key] = cur_file
    return cur_dict


def lonlat2grid(in_lon, in_lat):
    """ Convert lon,lat to grid points using SBU provided algorithm (Xinxia Song)
        Returns a tuple of the grid lon and grid lat"""

    # Convert input lon and lat to floats
    # Since SBU algorithm doesn't use the convention of negative lon for west of the prime meridian, make
    # necessary lon conversion (eg -179.5 is 179.5W, converted to 180.5 in SBU's convention)
    west_lon = p.getfloat('config','SBU_WEST_MOST_LON')
    northmost_lat = p.getfloat('config','SBU_NORTHERN_MOST_LAT')

    if west_lon < 0:
        westmost_lon = 360. - abs(west_lon)
    else:
        westmost_lon = west_lon

    logger.debug('westmost lon: {}'.format(str(westmost_lon)))
    logger.debug('northmost lat: {}'.format(str(northmost_lat)))

    numerical_lon = float(in_lon)
    lat = float(in_lat)


    if numerical_lon < 0:
        lon = 360. - abs(numerical_lon)
        logger.debug('lon adjusted for different convention: {}'.format(str(lon)))
    else:
        lon = numerical_lon



    # Resolution
    dlon = p.getfloat('config','SBU_DLON')
    dlat = p.getfloat('config','SBU_DLAT')

    # Get the fractional portion of the lon and lat (ie value to right of decimal point).
    fractional_lon = lon % 1
    fractional_lat = lat % 1

    # Get the whole (integer) value of the lon and lat
    whole_lon = lon - fractional_lon
    whole_lat = lat - fractional_lat

    # Determine an adjustment factor to add so we round the original lon and lat consistently
    lon_round_factor = get_rounding_factor(float(fractional_lon))
    lat_round_factor = get_rounding_factor(float(fractional_lat))

    adj_lon = whole_lon + lon_round_factor
    adj_lat = whole_lat + lat_round_factor

    logger.debug("rounded lon: {}".format(str(adj_lon)))
    logger.debug("rounded lat: {}".format(str(adj_lat)))


    # Convert to grid map lon,lat
    # NOTE: because we assign longitudes west of the Prime Meridian with negative value,
    # the grid_lon formula is 1 + (westmost_lon - adj_lon)/dlon rather than
    # 1 + (adj_lon - westmost_lon)/dlon
    grid_lon = 1 + (adj_lon - westmost_lon)/dlon
    grid_lat = 1 + (northmost_lat - adj_lat)/dlat

    return str(grid_lon), str(grid_lat)


def get_rounding_factor(fractional_value):
    """ Returns 0.5, 0, or 1 based on where the fractional value lies within a defined range"""
    if fractional_value > 0.25 and fractional_value < 0.75:
            logger.debug("decimal value {}".format(str(0.5)))
            return 0.5
    elif fractional_value <= 0.25:
        logger.debug("decimal value {}".format(str(0.0)))
        return 0.0
    elif fractional_value >= 0.75:
        logger.debug("decimal value {}".format(str(1.0)))
        return 1.0


def get_counts(model_cyc_filename):
    """ Determine the number of lines in the specified file and return the count"""

    # Create command for using 'wc -l'
    #cmd = 'wc -l ' + model_cyc_filename
    #result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    #cmd = batchexe('sh')['-c','wc -l '+model_cyc_filename]
    cmd = batchexe('wc')['-l',model_cyc_filename]
    result = runstr(cmd)  #runstr, executes program, captures its stdout.

    # Retrieve only the numerical portion of the result from 'wc -l'
    count_str = re.match(r'([0-9]+).*', result)
    if count_str:
        count = count_str.group(1)
    else:
        logger.error('WARNING: Cannot get count for file ' + model_cyc_filename)

    logger.debug("DEBUG model/cyc filename " + model_cyc_filename + " = " + count)
    return count

   # Using Python generators sometimes give egregiously erroneous counts
   #  with open(model_cyc_filename) as mcf:
   #     num_model_cyc_lines = sum(1 for line in mcf)
   #     print("Input file {} = {}".format(model_cyc_filename, num_model_cyc_lines))
   # return num_model_cyc_lines


def post_process(fulldir):
    # Iterate over all the created directories and determine the number of lines in each output file and
    # create the mcount.dat (for the number of lines in the model-test.dat file) and the cyc-count.dat file
    # (for the number of lines in the cyc-new-test.dat file).

    # Get a list of the full file paths for all the files
    model_dat_files = util.get_files(fulldir, "model-test.dat", logger)
    cyc_dat_files = util.get_files(fulldir, "cyc-new-test.dat", logger)

    for model_dat_file in model_dat_files:
        mcount = get_counts(model_dat_file)
        mpath = get_path_from_full_filename(model_dat_file)

        # Create the mcount.dat file in the correct directory
        #  (i.e. the directory corresponding to this model-test.dat file's date).
        mcount_file = os.path.join(mpath, 'mcount.dat')

        try:
            with open(mcount_file, 'w') as mc:
                mc.write(str(mcount))
                mc.write('\n')
        except IOError as ioe:
            logger.error("ERROR: cannot open or write to " + mcount_file)

    for cyc_dat_file in cyc_dat_files:
        cyc_count = get_counts(cyc_dat_file)
        cpath = get_path_from_full_filename(cyc_dat_file)

        # Create the cyc-count.dat file in the correct directory
        #  (i.e. the directory corresponding to this cyc-new-test.dat file's date).
        cyc_count_file = os.path.join(cpath, 'cyc-count.dat')

        try:
            with open(cyc_count_file, 'w') as cc:
                cc.write(str(cyc_count))
                cc.write('\n')
        except IOError as ioe:
            logger.error("ERROR: cannot open or write to " + cyc_count_file)


def get_path_from_full_filename(fname):
    """ Extract the path from a full '.dat' filename"""
    match = re.match(r'(.*)/.*.dat', fname)
    if match:
        return match.group(1)

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
#        main()
        produtil.log.postmsg('tc2cyclone_relative completed')
    except Exception as e:
        produtil.log.jlogger.critical(
            'tc2cyclone_relative failed: %s'%(str(e),),exc_info=True)
        sys.exit(2)

    # For testing the lon lat grid conversion logic
    lon = -179.5
    lat = 1.5
    adj_lon, adj_lat = lonlat2grid(lon, lat)
    print("adj lon= {} adj lat = {}".format(str(adj_lon), str(adj_lat)))
