"""
Program Name: system_manip.py
Contact(s): George McCabe
Description: METplus utility to handle OS/system calls
"""

import os
import re
from pathlib import Path
import getpass
import gzip
import bz2
import zipfile
import struct

from .constants import PYTHON_EMBEDDING_TYPES, COMPRESSION_EXTENSIONS


def mkdir_p(path):
    """!
       From stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
       Creates the entire directory path if it doesn't exist (including any
       required intermediate directories).
       Args:
           @param path : The full directory path to be created
       Returns
           None: Creates the full directory path if it doesn't exist,
                 does nothing otherwise.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_user_info():
    """! Get user information from OS. Note that some OS cannot obtain user ID
    and some cannot obtain username.
    @returns username(uid) if both username and user ID can be read,
     username if only username can be read, uid if only user ID can be read,
     or an empty string if neither can be read.
    """
    try:
        username = getpass.getuser()
    except OSError:
        username = None

    try:
        uid = os.getuid()
    except AttributeError:
        uid = None

    if username and uid:
        return f'{username}({uid})'

    if username:
        return username

    if uid:
        return uid

    return ''


def write_list_to_file(filename, output_list):
    with open(filename, 'w+') as f:
        for line in output_list:
            f.write(f"{line}\n")


def get_storms(filter_filename, id_only=False, sort_column='STORM_ID'):
    """! Get each storm as identified by a column in the input file.
         Create dictionary storm ID as the key and a list of lines for that
         storm as the value.

         @param filter_filename name of tcst file to read and extract storm id
         @param sort_column column to use to sort and group storms. Default
          value is STORM_ID
         @returns 2 item tuple - 1)dictionary where key is storm ID and value
          is list of relevant lines from tcst file, 2) header line from tcst
           file. Item with key 'header' contains the header of the tcst file
    """
    # Initialize a set because we want unique storm ids.
    storm_id_list = set()

    try:
        with open(filter_filename, "r") as file_handle:
            header, *lines = file_handle.readlines()

        storm_id_column = header.split().index(sort_column)
        for line in lines:
            storm_id_list.add(line.split()[storm_id_column])
    except (ValueError, FileNotFoundError):
        if id_only:
            return []
        return {}

    # sort the unique storm ids, copy the original
    # set by using sorted rather than sort.
    sorted_storms = sorted(storm_id_list)
    if id_only:
        return sorted_storms

    if not sorted_storms:
        return {}

    storm_dict = {'header': header}
    # for each storm, get all lines for that storm
    for storm in sorted_storms:
        storm_dict[storm] = [line for line in lines if storm in line]

    return storm_dict


def prune_empty(output_dir, logger):
    """! Start from the output_dir, and recursively check
        all directories and files.  If there are any empty
        files or directories, delete/remove them so they
        don't cause performance degradation or errors
        when performing subsequent tasks.

        @param output_dir The directory from which searching should begin.
        @param logger The logger to which all logging is directed.
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


def get_files(filedir, filename_regex, logger=None):
    """! Get all the files (with a particular naming format) by walking
        through the directories.

      @param filedir The topmost directory from which the search begins.
      @param filename_regex The regular expression that defines the naming
       format of the files of interest.
      @returns list of filenames (with full filepath)
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


def netcdf_has_var(file_path, name, level):
    """! Check if name is a variable in the NetCDF file. If not, check if
         {name}_{level} (with level prefix letter removed, i.e. 06 from A06)
          If the file is not a NetCDF file, OSError occurs.
          If the MET_version attribute doesn't exist, AttributeError occurs.
          If the netCDF4 package is not available, ImportError should occur.
          All of these situations result in the file being considered not
          a MET-generated NetCDF file. (CURRENTLY UNUSED)

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


def is_met_netcdf(file_path):
    """! Check if a file is a MET-generated NetCDF file.
          If the file is not a NetCDF file, OSError occurs.
          If the MET_version attribute doesn't exist, AttributeError occurs.
          If the netCDF4 package is not available, ImportError should occur.
          All of these situations result in the file being considered not
          a MET-generated NetCDF file (CURRENTLY NOT USED)

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


def get_filetype(filepath, logger=None):
    """!This function determines if the filepath is a NETCDF or GRIB file
       based on the first eight bytes of the file.
       It returns the string GRIB, NETCDF, or a None object.

       Note: If it is NOT determined to ba a NETCDF file,
       it returns GRIB, regardless.
       Unless there is an IOError exception, such as filepath refers
       to a non-existent file or filepath is only a directory, than
       None is returned, without a system exit. (CURRENTLY NOT USED)

       @param filepath:  path/to/filename
       @param logger the logger, optional
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
