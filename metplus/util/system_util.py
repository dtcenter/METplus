"""
Program Name: system_util.py
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
import urllib.request
import urllib.error
import urllib.parse
from urllib.request import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener

from .constants import PYTHON_EMBEDDING_TYPES, COMPRESSION_EXTENSIONS


def mkdir_p(path):
    """!From stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
       Creates the entire directory path if it doesn't exist (including any
       required intermediate directories).

       @param path The full directory path to be created
       @returns None: Creates the full directory path if it doesn't exist
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


def get_files(filedir, filename_regex):
    """! Get all the files (with a particular naming format) by walking
        through the directories. Note this uses re.match and will only
        find matches at the beginning of the file name.

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


def _preprocess_passthrough(filename, data_type, allow_dir):
    """!Check if filename should be returned without trying to decompress data.
    Helper function for preprocess_file.
    This is typically due to the filename being related to Python Embedding,
    either:
     A Python Embedding keyword (alone or at the end of a path, e.g.
      /some/path/PYTHON_NUMPY),
     The name starts with a Python Embedding type, e.g.
      PYTHON_NUMPY=/some/path/script.py /some/path/file.nc,
      The data type (*_INPUT_DATATYPE) contains the keyword PYTHON, or
     The filename contains multiple strings separated by spaces and the first
     string is a Python script ending in .py.
     If the filename contains multiple strings, add quotation marks around it
     before returning.

    @param filename string to process
    @param data_type string defining the type of data or None
    @param allow_dir boolean If True, return the directory
    @returns string of filename or None if preprocess_file should check if the
    file should be decompressed.
    """
    if allow_dir and os.path.isdir(filename):
        return filename

    # if using python embedding for input, return the keyword
    if os.path.basename(filename) in PYTHON_EMBEDDING_TYPES:
        return os.path.basename(filename)

    out_filename = None

    # if filename starts with a python embedding type, return the full value
    for py_embed_type in PYTHON_EMBEDDING_TYPES:
        if filename.startswith(py_embed_type):
            out_filename = filename

    # if _INPUT_DATATYPE value contains PYTHON, return the full value
    if data_type is not None and 'PYTHON' in data_type:
        out_filename = filename

    if filename.split()[0].endswith('.py'):
        out_filename = filename

    if out_filename is None:
        return None

    # add quotation marks if string contains spaces
    if len(out_filename.split()) > 1:
        return f'"{filename}"'
    return filename


def _check_and_decompress(filename, stage_dir, config):
    """!Check if file path contains extension that implies it is compressed.
    Decompress file if necessary.
    Supported compression extensions are gz, bz2, and zip.
    The full path of filename is duplicated under stage_dir.

    @param filename path to file to check
    @param stage_dir staging directory to decompress files into
    @param config METplusConfig object used for logging
    """
    # if file exists in the staging area, return that path
    staged_filename = stage_dir + filename
    if os.path.isfile(staged_filename):
        return staged_filename

    # Create staging area directory only if file has compression extension
    if any([os.path.isfile(f'{filename}{ext}') for ext in COMPRESSION_EXTENSIONS]):
        mkdir_p(os.path.dirname(staged_filename))
    else:
        return None

    # uncompress gz, bz2, or zip file
    if os.path.isfile(f"{filename}.gz"):
        config.logger.debug(f"Decompressing gz file to {staged_filename}")
        with gzip.open(f"{filename}.gz", 'rb') as infile:
            with open(staged_filename, 'wb') as outfile:
                outfile.write(infile.read())
                infile.close()
                outfile.close()
                return staged_filename

    elif os.path.isfile(f"{filename}.bz2"):
        config.logger.debug(f"Decompressing bz2 file to {staged_filename}")
        with open(f"{filename}.bz2", 'rb') as infile:
            with open(staged_filename, 'wb') as outfile:
                outfile.write(bz2.decompress(infile.read()))
                infile.close()
                outfile.close()
                return staged_filename

    elif os.path.isfile(f"{filename}.zip"):
        config.logger.debug(f"Decompressing zip file to {staged_filename}")
        with zipfile.ZipFile(f"{filename}.zip") as z:
            with open(staged_filename, 'wb') as f:
                f.write(z.read(os.path.basename(filename)))
                return staged_filename

    return None


def _process_gempak_file(filename, stage_dir, config):
    """!Run GempakToCFWrapper on GEMPAK file to convert it to NetCDF.
    Assumes either filename ends with .grd extension or file type has been
    specified as GEMPAK.

    @param filename path to file to process
    @param stage_dir staging directory to write NetCDF output
    @param config METplusConfig object
    @returns path to staged NetCDF output file or None if conversion failed
    """
    if filename.endswith('.grd'):
        stage_file = stage_dir + filename[:-3] + "nc"
    else:
        stage_file = stage_dir + filename + ".nc"
    if os.path.isfile(stage_file):
        return stage_file
    # if it does not exist, run GempakToCF and return staged nc file
    # Create staging area if it does not exist
    mkdir_p(os.path.dirname(stage_file))

    # only import GempakToCF if needed
    from ..wrappers import GempakToCFWrapper

    run_g2c = GempakToCFWrapper(config)
    run_g2c.infiles.append(filename)
    run_g2c.set_output_path(stage_file)
    cmd = run_g2c.get_command()
    if cmd is None:
        config.logger.error("GempakToCF could not generate command")
        return None
    config.logger.debug("Converting Gempak file into {}".format(stage_file))
    run_g2c.build()
    return stage_file


def preprocess_file(filename, data_type, config, allow_dir=False):
    """Check file path to determine if it needs to be preprocessed, e.g.
    decompress or convert GEMPAK to NetCDF.

    @param filename Path to file without zip extensions
    @param data_type str of data_type for filename
    @param config METplusConfig object
    @param allow_dir (optional) bool to allow 'filename' to be a directory.
     Default is False.
    @returns Path to staged unzipped file or original file if already unzipped
    """
    if not filename:
        return None

    # check if preprocessing should be skipped and return string if so
    pass_filename = _preprocess_passthrough(filename, data_type, allow_dir)
    if pass_filename is not None:
        return pass_filename

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
            return _process_gempak_file(filename, stage_dir, config)

        return filename

    # nc file requested and the Gempak equivalent exists
    if os.path.isfile(filename[:-2]+'grd'):
        return preprocess_file(filename[:-2]+'grd', data_type, config)

    staged_path = _check_and_decompress(filename, stage_dir, config)
    if staged_path is not None:
        return staged_path

    # if input doesn't need to exist, return filename
    if not config.getbool('config', 'INPUT_MUST_EXIST', True):
        return filename

    return None


def traverse_dir(data_dir, get_dirs=False):
    """!Generator used to navigate through and yield full path to all files or
    directories under data_dir.

    @param data_dir directory to traverse
    @param get_dirs If True, get all directories under data_dir. If False, get
    all files under data_dir. Defaults to False (files).
    """
    for dir_path, dirs, all_files in os.walk(data_dir, followlinks=True):
        if get_dirs:
            items = sorted(dirs)
        else:
            items = sorted(all_files)

        for dir_name in items:
            yield os.path.join(dir_path, dir_name)


def download_file_http(url, output_path, username=None, password=None, chunk_size=8192):
    """!Download a file from HTTP URL with optional authentication.

    @param url: The HTTP/HTTPS URL to download from
    @param output_path: Local file path where the downloaded file will be saved
    @param username: Optional username for HTTP basic authentication
    @param password: Optional password for HTTP basic authentication
    @param chunk_size: Size of chunks to download at a time (default: 8192 bytes)
    @returns: Dict with 'success': bool, 'file_size': int, 'error': str (if failed)
    @raises: urllib.error.URLError, urllib.error.HTTPError for network issues
    """
    result = {'success': False, 'file_size': 0, 'error': ''}

    try:
        # Create directory if it doesn't exist
        mkdir_p(os.path.dirname(output_path))

        # Set up authentication if credentials provided
        if username is not None and password is not None:
            # Create password manager
            password_mgr = HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, url, username, password)

            # Create authentication handler
            auth_handler = HTTPBasicAuthHandler(password_mgr)

            # Build opener with authentication
            opener = build_opener(auth_handler)
            urllib.request.install_opener(opener)

        # Create request
        request = urllib.request.Request(url)

        # Add user agent to avoid being blocked by some servers
        request.add_header('User-Agent', 'Python-urllib/3.x')

        # Open URL and download
        with urllib.request.urlopen(request) as response:
            # Get file size if available
            content_length = response.headers.get('Content-Length')
            total_size = int(content_length) if content_length else None
            if not total_size:
                result['error'] = "File size is 0 or Content-Length header not found in response"
                return result

            # Download file in chunks
            with open(output_path, 'wb') as output_file:
                downloaded = 0
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    output_file.write(chunk)
                    downloaded += len(chunk)

        result['success'] = True
        result['file_size'] = downloaded
        return result

    except urllib.error.HTTPError as e:
        error_msg = f"HTTP Error {e.code}: {e.reason}"
        result['error'] = error_msg
        return result

    except urllib.error.URLError as e:
        error_msg = f"URL Error: {e.reason}"
        result['error'] = error_msg
        return result

    except IOError as e:
        error_msg = f"IO Error: {e}"
        result['error'] = error_msg
        return result

    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        result['error'] = error_msg
        return result
