#!/usr/bin/env python3


import os
import time
import logging
import yaml
from METdbLoad.ush.read_data_files import ReadDataFiles
from METdbLoad.ush.read_load_xml  import XmlLoadFile
from METreformat.write_stat_ascii import WriteStatAscii
import metcalcpy.util.read_env_vars_in_config as readconfig


logger = logging.getLogger(__name__)

def main():

    # Read in the YAML configuration file.  Environment variables in
    # the configuration file are supported.
    try:
        input_config_file = os.getenv("YAML_CONFIG_NAME", "reformat_ecnt.yaml")
        parms = readconfig.parse_config(input_config_file)
        logging.info(parms)
    except yaml.YAMLError as exc:
        logging.error(exc)


    # Replacing the need for an XML specification file, pass in the XMLLoadFile and
    # ReadDataFile parameters
    rdf_obj: ReadDataFiles = ReadDataFiles()
    xml_loadfile_obj: XmlLoadFile = XmlLoadFile(None)

    # Retrieve all the filenames in the data_dir specified in the YAML config file
    load_files = xml_loadfile_obj.filenames_from_template(parms['input_data_dir'],
                                                          {})

    flags = xml_loadfile_obj.flags
    line_types = xml_loadfile_obj.line_types
    beg_read_data = time.perf_counter()
    rdf_obj.read_data(flags, load_files, line_types)
    end_read_data = time.perf_counter()
    time_to_read = end_read_data - beg_read_data
    logger.info("Time to read input .stat data files using METdbLoad: {time_to_read}")
    file_df = rdf_obj.stat_data

    # Check if the output file already exists, if so, delete it to avoid
    # appending output from subsequent runs into the same file.
    existing_output_file = os.path.join(parms['output_dir'], parms['output_filename'])
    logger.info("Checking if {existing_output_file}  already exists")
    if os.path.exists(existing_output_file):
        logger.info("Removing existing output file {existing_output_file}")
        os.remove(existing_output_file)

    # Write stat file in ASCII format
    stat_lines_obj: WriteStatAscii = WriteStatAscii(parms)
    # stat_lines_obj.write_stat_ascii(file_df, parms, logger)
    stat_lines_obj.write_stat_ascii(file_df, parms)


if __name__ == "__main__":
    main()
