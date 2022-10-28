import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
import re
import gzip
import bz2
import zipfile
import struct

from dateutil.relativedelta import relativedelta

from .string_manip import getlist, getlistint
from .system_util import mkdir_p
from . import time_util as time_util
from .string_template_substitution import do_string_sub
from .string_template_substitution import parse_template
from .time_looping import time_generator


"""!@namespace met_util
 @brief Provides  Utility functions for METplus.
"""

from .constants import *


def loop_over_times_and_call(config, processes, custom=None):
    """! Loop over all run times and call wrappers listed in config

    @param config METplusConfig object
    @param processes list of CommandBuilder subclass objects (Wrappers) to call
    @param custom (optional) custom loop string value
    @returns list of tuples with all commands run and the environment variables
    that were set for each
    """
    # keep track of commands that were run
    all_commands = []
    for time_input in time_generator(config):
        if not isinstance(processes, list):
            processes = [processes]

        for process in processes:
            # if time could not be read, increment errors for each process
            if time_input is None:
                process.errors += 1
                continue

            log_runtime_banner(config, time_input, process)
            add_to_time_input(time_input,
                              instance=process.instance,
                              custom=custom)

            process.clear()
            process.run_at_time(time_input)
            if process.all_commands:
                all_commands.extend(process.all_commands)
            process.all_commands.clear()

    return all_commands

def log_runtime_banner(config, time_input, process):
    loop_by = time_input['loop_by']
    run_time = time_input[loop_by].strftime("%Y-%m-%d %H:%M")

    process_name = process.__class__.__name__
    if process.instance:
        process_name = f"{process_name}({process.instance})"

    config.logger.info("****************************************")
    config.logger.info(f"* Running METplus {process_name}")
    config.logger.info(f"*  at {loop_by} time: {run_time}")
    config.logger.info("****************************************")

def add_to_time_input(time_input, clock_time=None, instance=None, custom=None):
    if clock_time:
        clock_dt = datetime.strptime(clock_time, '%Y%m%d%H%M%S')
        time_input['now'] = clock_dt

    # if instance is set, use that value, otherwise use empty string
    time_input['instance'] = instance if instance else ''

    # if custom is specified, set it
    # otherwise leave it unset so it can be set within the wrapper
    if custom:
        time_input['custom'] = custom

def get_lead_sequence(config, input_dict=None, wildcard_if_empty=False):
    """!Get forecast lead list from LEAD_SEQ or compute it from INIT_SEQ.
        Restrict list by LEAD_SEQ_[MIN/MAX] if set. Now returns list of relativedelta objects
        Args:
            @param config METplusConfig object to query config variable values
            @param input_dict time dictionary needed to handle using INIT_SEQ. Must contain
               valid key if processing INIT_SEQ
            @param wildcard_if_empty if no lead sequence was set, return a
             list with '*' if this is True, otherwise return a list with 0
            @returns list of relativedelta objects or a list containing 0 if none are found
    """

    out_leads = []
    lead_min, lead_max, no_max = get_lead_min_max(config)

    # check if LEAD_SEQ, INIT_SEQ, or LEAD_SEQ_<n> are set
    # if more than one is set, report an error and exit
    lead_seq = getlist(config.getstr('config', 'LEAD_SEQ', ''))
    init_seq = getlistint(config.getstr('config', 'INIT_SEQ', ''))
    lead_groups = get_lead_sequence_groups(config)

    if not are_lead_configs_ok(lead_seq,
                               init_seq,
                               lead_groups,
                               config,
                               input_dict,
                               no_max):
        return None

    if lead_seq:
        # return lead sequence if wildcard characters are used
        if lead_seq == ['*']:
            return lead_seq

        out_leads = handle_lead_seq(config,
                                    lead_seq,
                                    lead_min,
                                    lead_max)

    # use INIT_SEQ to build lead list based on the valid time
    elif init_seq:
        out_leads = handle_init_seq(init_seq,
                                    input_dict,
                                    lead_min,
                                    lead_max)
    elif lead_groups:
        out_leads = handle_lead_groups(lead_groups)

    if not out_leads:
        if wildcard_if_empty:
            return ['*']

        return [0]

    return out_leads

def are_lead_configs_ok(lead_seq, init_seq, lead_groups,
                        config, input_dict, no_max):
    if lead_groups is None:
        return False

    error_message = ('are both listed in the configuration. '
                     'Only one may be used at a time.')
    if lead_seq:
        if init_seq:
            config.logger.error(f'LEAD_SEQ and INIT_SEQ {error_message}')
            return False

        if lead_groups:
            config.logger.error(f'LEAD_SEQ and LEAD_SEQ_<n> {error_message}')
            return False

    if init_seq and lead_groups:
        config.logger.error(f'INIT_SEQ and LEAD_SEQ_<n> {error_message}')
        return False

    if init_seq:
        # if input dictionary not passed in,
        # cannot compute lead sequence from it, so exit
        if input_dict is None:
            config.logger.error('Cannot run using INIT_SEQ for this wrapper')
            return False

        # if looping by init, fail and exit
        if 'valid' not in input_dict.keys():
            log_msg = ('INIT_SEQ specified while looping by init time.'
                       ' Use LEAD_SEQ or change to loop by valid time')
            config.logger.error(log_msg)
            return False

        # maximum lead must be specified to run with INIT_SEQ
        if no_max:
            config.logger.error('LEAD_SEQ_MAX must be set to use INIT_SEQ')
            return False

    return True

def get_lead_min_max(config):
    # remove any items that are outside of the range specified
    #  by LEAD_SEQ_MIN and LEAD_SEQ_MAX
    # convert min and max to relativedelta objects, then use current time
    # to compare them to each forecast lead
    # this is an approximation because relative time offsets depend on
    # each runtime
    huge_max = '4000Y'
    lead_min_str = config.getstr_nocheck('config', 'LEAD_SEQ_MIN', '0')
    lead_max_str = config.getstr_nocheck('config', 'LEAD_SEQ_MAX', huge_max)
    no_max = lead_max_str == huge_max
    lead_min = time_util.get_relativedelta(lead_min_str, 'H')
    lead_max = time_util.get_relativedelta(lead_max_str, 'H')
    return lead_min, lead_max, no_max

def handle_lead_seq(config, lead_strings, lead_min=None, lead_max=None):
    out_leads = []
    leads = []
    for lead in lead_strings:
        relative_delta = time_util.get_relativedelta(lead, 'H')
        if relative_delta is not None:
            leads.append(relative_delta)
        else:
            config.logger.error(f'Invalid item {lead} in LEAD_SEQ. Exiting.')
            return None

    if lead_min is None and lead_max is None:
        return leads

    # add current time to leads to approximate month and year length
    now_time = datetime.now()
    lead_min_approx = now_time + lead_min
    lead_max_approx = now_time + lead_max
    for lead in leads:
        lead_approx = now_time + lead
        if lead_approx >= lead_min_approx and lead_approx <= lead_max_approx:
            out_leads.append(lead)

    return out_leads

def handle_init_seq(init_seq, input_dict, lead_min, lead_max):
    out_leads = []
    lead_min_hours = time_util.ti_get_hours_from_relativedelta(lead_min)
    lead_max_hours = time_util.ti_get_hours_from_relativedelta(lead_max)

    valid_hr = int(input_dict['valid'].strftime('%H'))
    for init in init_seq:
        if valid_hr >= init:
            current_lead = valid_hr - init
        else:
            current_lead = valid_hr + (24 - init)

        while current_lead <= lead_max_hours:
            if current_lead >= lead_min_hours:
                out_leads.append(relativedelta(hours=current_lead))
            current_lead += 24

    out_leads = sorted(out_leads, key=lambda
        rd: time_util.ti_get_seconds_from_relativedelta(rd,
                                                        input_dict['valid']))
    return out_leads

def handle_lead_groups(lead_groups):
    """! Read groups of forecast leads and create a list with all unique items

         @param lead_group dictionary where the values are lists of forecast
         leads stored as relativedelta objects
         @returns list of forecast leads stored as relativedelta objects
    """
    out_leads = []
    for _, lead_seq in lead_groups.items():
        for lead in lead_seq:
            if lead not in out_leads:
                out_leads.append(lead)

    return out_leads

def get_lead_sequence_groups(config):
    # output will be a dictionary where the key will be the
    #  label specified and the value will be the list of forecast leads
    lead_seq_dict = {}
    # used in plotting
    all_conf = config.keys('config')
    indices = []
    regex = re.compile(r"LEAD_SEQ_(\d+)")
    for conf in all_conf:
        result = regex.match(conf)
        if result is not None:
            indices.append(result.group(1))

    # loop over all possible variables and add them to list
    for index in indices:
        if config.has_option('config', f"LEAD_SEQ_{index}_LABEL"):
            label = config.getstr('config', f"LEAD_SEQ_{index}_LABEL")
        else:
            log_msg = (f'Need to set LEAD_SEQ_{index}_LABEL to describe '
                       f'LEAD_SEQ_{index}')
            config.logger.error(log_msg)
            return None

        # get forecast list for n
        lead_string_list = getlist(config.getstr('config', f'LEAD_SEQ_{index}'))
        lead_seq = handle_lead_seq(config,
                                   lead_string_list,
                                   lead_min=None,
                                   lead_max=None)
        # add to output dictionary
        lead_seq_dict[label] = lead_seq

    return lead_seq_dict


def get_files(filedir, filename_regex, logger=None):
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
    file_paths = []

    # Walk the tree
    for root, _, files in os.walk(filedir):
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
    return sorted(file_paths)

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

    # Check for empty files.
    for root, dirs, files in os.walk(output_dir):
        # Create a full file path by joining the path
        # and filename.
        for a_file in files:
            a_file = os.path.join(root, a_file)
            if os.stat(a_file).st_size == 0:
                logger.debug("Empty file: " + a_file +
                             "...removing")
                os.remove(a_file)

    # Now check for any empty directories, some
    # may have been created when removing
    # empty files.
    for root, dirs, files in os.walk(output_dir):
        for direc in dirs:
            full_dir = os.path.join(root, direc)
            if not os.listdir(full_dir):
                logger.debug("Empty directory: " + full_dir +
                             "...removing")
                os.rmdir(full_dir)


def shift_time_seconds(time_str, shift):
    """ Adjust time by shift seconds. Format is %Y%m%d%H%M%S
        Args:
            @param time_str: Start time in %Y%m%d%H%M%S
            @param shift: Amount to adjust time in seconds
        Returns:
            New time in format %Y%m%d%H%M%S
    """
    return (datetime.strptime(time_str, "%Y%m%d%H%M%S") +
            timedelta(seconds=shift)).strftime("%Y%m%d%H%M%S")


def sub_var_info(var_info, time_info):
    if not var_info:
        return {}

    out_var_info = {}
    for key, value in var_info.items():
        if isinstance(value, list):
            out_value = []
            for item in value:
                out_value.append(do_string_sub(item,
                                               skip_missing_tags=True,
                                               **time_info))
        else:
            out_value = do_string_sub(value,
                                      skip_missing_tags=True,
                                      **time_info)

        out_var_info[key] = out_value

    return out_var_info

def sub_var_list(var_list, time_info):
    """! Perform string substitution on var list values with time info

        @param var_list list of field info to substitute values into
        @param time_info dictionary containing time information
        @returns var_list with values substituted
    """
    if not var_list:
        return []

    out_var_list = []
    for var_info in var_list:
        out_var_info = sub_var_info(var_info, time_info)
        out_var_list.append(out_var_info)

    return out_var_list

def split_level(level):
    """! If level value starts with a letter, then separate that letter from
     the rest of the string. i.e. 'A03' will be returned as 'A', '03'. If no
     level type letter is found and the level value consists of alpha-numeric
     characters, return an empty string as the level type and the full level
     string as the level value

     @param level input string to parse/split
     @returns tuple of level type and level value
    """
    if not level:
        return '', ''

    match = re.match(r'^([a-zA-Z])(\w+)$', level)
    if match:
        level_type = match.group(1)
        level = match.group(2)
        return level_type, level

    match = re.match(r'^[\w]+$', level)
    if match:
        return '', level

    return '', ''

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

    # if filepath is set to None, return None to avoid crash
    if filepath == None:
        return None

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
            name_cdf = struct.unpack('3s', first_eight_bytes[:3])[0]
            name_hdf = struct.unpack('3s', first_eight_bytes[1:4])[0]
            name_grib = struct.unpack('4s', first_eight_bytes[:4])[0]

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
    # ncdump_exe = config.getexe('NCDUMP')
    #try:
    #    result = subprocess.check_output([ncdump_exe, filepath])

    #except subprocess.CalledProcessError:
    #    return "GRIB"

    #regex = re.search("netcdf", result)
    #if regex is not None:
    #    return "NETCDF"
    #else:
    #    return None

def preprocess_file(filename, data_type, config, allow_dir=False):
    """ Decompress gzip, bzip, or zip files or convert Gempak files to NetCDF
        Args:
            @param filename: Path to file without zip extensions
            @param config: Config object
        Returns:
            Path to staged unzipped file or original file if already unzipped
    """
    if not filename:
        return None

    if allow_dir and os.path.isdir(filename):
        return filename

    # if using python embedding for input, return the keyword
    if os.path.basename(filename) in PYTHON_EMBEDDING_TYPES:
        return os.path.basename(filename)

    # if filename starts with a python embedding type, return the full value
    for py_embed_type in PYTHON_EMBEDDING_TYPES:
        if filename.startswith(py_embed_type):
            return filename

    # if _INPUT_DATATYPE value contains PYTHON, return the full value
    if data_type is not None and 'PYTHON' in data_type:
        return filename

    stage_dir = config.getdir('STAGING_DIR')

    if os.path.isfile(filename):
        # if filename provided ends with a valid compression extension,
        # remove the extension and call function again so the
        # file will be uncompressed properly. This is done so that
        # the function will handle files passed to it with an
        # extension the same way as files passed
        # without an extension but the compressed equivalent exists
        for ext in COMPRESSION_EXTENSIONS:
            if filename.endswith(ext):
                return preprocess_file(filename[:-len(ext)], data_type, config)
        # if extension is grd (Gempak), then look in staging dir for nc file
        if filename.endswith('.grd') or data_type == "GEMPAK":
            if filename.endswith('.grd'):
                stagefile = stage_dir + filename[:-3]+"nc"
            else:
                stagefile = stage_dir + filename+".nc"
            if os.path.isfile(stagefile):
                return stagefile
            # if it does not exist, run GempakToCF and return staged nc file
            # Create staging area if it does not exist
            mkdir_p(os.path.dirname(stagefile))

            # only import GempakToCF if needed
            from ..wrappers import GempakToCFWrapper

            run_g2c = GempakToCFWrapper(config)
            run_g2c.infiles.append(filename)
            run_g2c.set_output_path(stagefile)
            cmd = run_g2c.get_command()
            if cmd is None:
                config.logger.error("GempakToCF could not generate command")
                return None
            if config.logger:
                config.logger.debug("Converting Gempak file into {}".format(stagefile))
            run_g2c.build()
            return stagefile

        return filename

    # nc file requested and the Gempak equivalent exists
    if os.path.isfile(filename[:-2]+'grd'):
        return preprocess_file(filename[:-2]+'grd', data_type, config)

    # if file exists in the staging area, return that path
    outpath = stage_dir + filename
    if os.path.isfile(outpath):
        return outpath

    # Create staging area directory only if file has compression extension
    if any([os.path.isfile(f'{filename}{ext}')
            for ext in COMPRESSION_EXTENSIONS]):
        mkdir_p(os.path.dirname(outpath))

    # uncompress gz, bz2, or zip file
    if os.path.isfile(filename+".gz"):
        if config.logger:
            config.logger.debug("Uncompressing gz file to {}".format(outpath))
        with gzip.open(filename+".gz", 'rb') as infile:
            with open(outpath, 'wb') as outfile:
                outfile.write(infile.read())
                infile.close()
                outfile.close()
                return outpath
    elif os.path.isfile(filename+".bz2"):
        if config.logger:
            config.logger.debug("Uncompressing bz2 file to {}".format(outpath))
        with open(filename+".bz2", 'rb') as infile:
            with open(outpath, 'wb') as outfile:
                outfile.write(bz2.decompress(infile.read()))
                infile.close()
                outfile.close()
                return outpath
    elif os.path.isfile(filename+".zip"):
        if config.logger:
            config.logger.debug("Uncompressing zip file to {}".format(outpath))
        with zipfile.ZipFile(filename+".zip") as z:
            with open(outpath, 'wb') as f:
                f.write(z.read(os.path.basename(filename)))
                return outpath

    # if input doesn't need to exist, return filename
    if not config.getbool('config', 'INPUT_MUST_EXIST', True):
        return filename

    return None

def template_to_regex(template, time_info):
    in_template = re.sub(r'\.', '\\.', template)
    in_template = re.sub(r'{lead.*?}', '.*', in_template)
    return do_string_sub(in_template,
                         **time_info)


def expand_int_string_to_list(int_string):
    """! Expand string into a list of integer values. Items are separated by
    commas. Items that are formatted X-Y will be expanded into each number
    from X to Y inclusive. If the string ends with +, then add a str '+'
    to the end of the list. Used in .github/jobs/get_use_case_commands.py

    @param int_string String containing a comma-separated list of integers
    @returns List of integers and potentially '+' as the last item
    """
    subset_list = []

    # if string ends with +, remove it and add it back at the end
    if int_string.strip().endswith('+'):
        int_string = int_string.strip(' +')
        hasPlus = True
    else:
        hasPlus = False

    # separate into list by comma
    comma_list = int_string.split(',')
    for comma_item in comma_list:
        dash_list = comma_item.split('-')
        # if item contains X-Y, expand it
        if len(dash_list) == 2:
            for i in range(int(dash_list[0].strip()),
                           int(dash_list[1].strip())+1,
                           1):
                subset_list.append(i)
        else:
            subset_list.append(int(comma_item.strip()))

    if hasPlus:
        subset_list.append('+')

    return subset_list

def subset_list(full_list, subset_definition):
    """! Extract subset of items from full_list based on subset_definition
    Used in internal/tests/use_cases/metplus_use_case_suite.py

    @param full_list List of all use cases that were requested
    @param subset_definition Defines how to subset the full list. If None,
    no subsetting occurs. If an integer value, select that index only.
    If a slice object, i.e. slice(2,4,1), pass slice object into list.
    If list, subset full list by integer index values in list. If
    last item in list is '+' then subset list up to 2nd last index, then
    get all items from 2nd last item and above
    """
    if subset_definition is not None:
        subset_list = []

        # if case slice is a list, use only the indices in the list
        if isinstance(subset_definition, list):
            # if last slice value is a plus sign, get rest of items
            # after 2nd last slice value
            if subset_definition[-1] == '+':
                plus_value = subset_definition[-2]
                # add all values before last index before plus
                subset_list.extend([full_list[i]
                                    for i in subset_definition[:-2]])
                # add last index listed + all items above
                subset_list.extend(full_list[plus_value:])
            else:
                # list of integers, so get items based on indices
                subset_list = [full_list[i] for i in subset_definition]
        else:
            subset_list = full_list[subset_definition]
    else:
        subset_list = full_list

    # if only 1 item is left, make it a list before returning
    if not isinstance(subset_list, list):
        subset_list = [subset_list]

    return subset_list

def is_met_netcdf(file_path):
    """! Check if a file is a MET-generated NetCDF file.
          If the file is not a NetCDF file, OSError occurs.
          If the MET_version attribute doesn't exist, AttributeError occurs.
          If the netCDF4 package is not available, ImportError should occur.
          All of these situations result in the file being considered not
          a MET-generated NetCDF file
         Args:
             @param file_path full path to file to check
             @returns True if file is a MET-generated NetCDF file and False if
              it is not or it can't be determined.
    """
    try:
        from netCDF4 import Dataset
        nc_file = Dataset(file_path, 'r')
        getattr(nc_file, 'MET_version')
    except (AttributeError, OSError, ImportError):
        return False

    return True

def netcdf_has_var(file_path, name, level):
    """! Check if name is a variable in the NetCDF file. If not, check if
         {name}_{level} (with level prefix letter removed, i.e. 06 from A06)
          If the file is not a NetCDF file, OSError occurs.
          If the MET_version attribute doesn't exist, AttributeError occurs.
          If the netCDF4 package is not available, ImportError should occur.
          All of these situations result in the file being considered not
          a MET-generated NetCDF file
         Args:
             @param file_path full path to file to check
             @returns True if file is a MET-generated NetCDF file and False if
              it is not or it can't be determined.
    """
    try:
        from netCDF4 import Dataset

        nc_file = Dataset(file_path, 'r')
        variables = nc_file.variables.keys()

        # if name is a variable, return that name
        if name in variables:
            return name


        # if name_level is a variable, return that
        name_underscore_level = f"{name}_{split_level(level)[1]}"
        if name_underscore_level in variables:
            return name_underscore_level

        # requested variable name is not found in file
        return None

    except (AttributeError, OSError, ImportError):
        return False

def generate_tmp_filename():
    import random
    import string
    random_string = ''.join(random.choice(string.ascii_letters)
                            for i in range(10))
    return f"metplus_tmp_{random_string}"

def format_level(level):
    """! Format level string to prevent NetCDF level values from creating
         filenames and field names with bad characters. Replaces '*' with 'all'
         and ',' with '_'

        @param level string of level to format
        @returns formatted string
    """
    return level.replace('*', 'all').replace(',', '_')
