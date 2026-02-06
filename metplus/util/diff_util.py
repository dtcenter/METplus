#! /usr/bin/env python3

import sys
import os
import traceback
from typing import Any

import netCDF4
import filecmp
import csv
import re
from math import log10, isclose
from PIL import Image, ImageChops
from pandas import isnull
from numpy.ma import is_masked
from numpy.ma import count_masked

###
# Settings that are commonly overridden
###

# keywords (strings) to search and skip diff tests if found in file path
# override this to skip files that match any of the keywords
SKIP_KEYWORDS = [
]

if os.environ.get('METPLUS_DIFF_SKIP_KEYWORDS'):
    skip_keywords = [item.strip() for item in os.environ['METPLUS_DIFF_SKIP_KEYWORDS'].split(',')]
    SKIP_KEYWORDS.extend(skip_keywords)

# dictionary where key is a keyword to search (e.g. use case name)
# and the value is the rounding precision to use for files that
# match the keyword
# override this to change the rounding precision for files that match the keyword
ROUNDING_OVERRIDES = {
}

# file extensions to skip
# these will be reported as a successful diff test
# override this to skip files that have any of the extensions
SKIP_EXTENSIONS = [
    '.zip',
    '.gif',
    '.ix',
    '.log',
]

###
# Settings common to all uses of this script
###

# file extensions for supported image file types
IMAGE_EXTENSIONS = [
    '.jpg',
    '.jpeg',
    '.png',
]

# file extensions used to determine if a file is a NetCDF file
NETCDF_EXTENSIONS = [
    '.nc',
    '.cdf',
    '.nc4',
]

# file extensions used to determine if a file is a PDF file
PDF_EXTENSIONS = [
    '.pdf',
]

# file extensions used to determine if a file is a CSV file
CSV_EXTENSIONS = [
    '.csv',
]

# file extensions that are not currently supported by the diff utility
# these will be flagged as differences so the reviewer knows to examine
# the files manually
UNSUPPORTED_EXTENSIONS = [
]



###
# Rounding Constants
###

# number of decimal places to use for comparing floats by default
DEFAULT_ROUNDING_PRECISION = 6

# number of decision places to accept float differences
# Note: Completing METplus issue #1873 could allow this to be set to 6
rounding_precision = DEFAULT_ROUNDING_PRECISION

# set tolerance for zero values
IS_ZERO_TOL = 1.0e-10

# number of significant figures to use for comparing floats
SIG_FIG = 7


def get_file_type(filepath):
    _, file_extension = os.path.splitext(filepath)

    if file_extension in CSV_EXTENSIONS:
        return 'csv'

    if file_extension in IMAGE_EXTENSIONS:
        return 'image'

    # if extension is .nc, then assume NetCDF file
    if file_extension in NETCDF_EXTENSIONS:
        return 'netcdf'

    # if the file can be read as a netCDF4.Dataset
    # assume it is a NetCDF file
    try:
        netCDF4.Dataset(filepath)
        return 'netcdf'
    except OSError:
        pass

    if file_extension in SKIP_EXTENSIONS:
        return f'skip {file_extension}'

    if file_extension in PDF_EXTENSIONS:
        return 'pdf'

    if file_extension in UNSUPPORTED_EXTENSIONS:
        return f'unsupported {file_extension}'

    return 'unknown'


def dirs_are_equal(dir_a, dir_b, debug=False, save_diff=False):
    if compare_dir(dir_a, dir_b, debug=debug, save_diff=save_diff):
        return False
    return True


def compare_dir(dir_a, dir_b, debug=False, save_diff=False):
    n_files_skipped = 0

    # if inputs are files and not directories, compare them
    if os.path.isfile(dir_a):
        result = compare_files(dir_a, dir_b, debug=True, save_diff=save_diff)
        if result is None or result is True:
            return []

        return [result]

    _print_if_debug("::group::Full diff results:", debug)

    diff_files = []
    n_files_compared = 0
    print(f"Comparing files under\n  {dir_a}\n  {dir_b}")
    for filepath_a in _get_files(dir_a):
        filepath_b = filepath_a.replace(dir_a, dir_b)
        rel_path = filepath_a.replace(f'{dir_a}/', '')
        _print_if_debug(f"\n# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #\nCOMPARING {rel_path}", debug)
        if not debug:
            # when debug output is off, print a dot for every file processed to show progress
            print('.', end='', flush=True)

        try:
            result = compare_files(filepath_a, filepath_b, debug=debug,
                                   dir_a=dir_a, dir_b=dir_b, save_diff=save_diff)
            n_files_compared += 1
        except Exception as err:
            msg = f"ERROR: Exception occurred in diff logic: {err}\n{traceback.format_exc()}"
            _print_if_debug(msg, debug)
            result = filepath_a, filepath_b, 'Exception in diff logic', '', msg

        # no differences or skipped
        if result is None:
            n_files_skipped += 1
            continue

        if result is True:
            continue

        diff_files.append(result)

    # loop through dir_b and report if any files are not found in dir_a
    n_files_compared += _check_for_new_output(debug, diff_files, dir_a, dir_b)

    _print_if_debug("::endgroup::", debug)
    _print_dir_summary(diff_files)

    print(f"\n\nNumber of files compared = {n_files_compared}")
    print(f"Number of files skipped = {n_files_skipped}")
    if diff_files:
        print(f"ERROR: Differences were found with {len(diff_files)} files")
    else:
        print("SUCCESS: No differences found in any files")

    return diff_files


def _check_for_new_output(debug: bool, diff_files: list[Any], dir_a, dir_b) -> int:
    new_files_compared = 0
    for filepath_b in _get_files(dir_b):
        filepath_a = filepath_b.replace(dir_b, dir_a)
        if os.path.exists(filepath_a):
            continue
        # check if missing file is actually diff file that was generated
        diff_list = [item[3] for item in diff_files]
        if filepath_b in diff_list:
            continue
        msg = f"ERROR: File does not exist: {filepath_a}"
        _print_if_debug(msg, debug)
        diff_files.append(('', filepath_b, 'file not found (new output)', '', msg))
        new_files_compared += 1
    return new_files_compared


def _get_files(search_dir):
    """!Generator to get all files in a directory.
    Skips directories that end with 'logs' and files named metplus_final.conf

    @param search_dir directory to search recursively
    """
    for root, _, files in os.walk(search_dir):
        # skip logs directories
        if root.endswith('logs'):
            continue

        for filename in files:
            filepath = os.path.join(root, filename)

            # skip directories
            if not os.path.isfile(filepath):
                continue

            # skip final conf file
            if 'metplus_final.conf' in os.path.basename(filepath):
                continue

            yield filepath


def _print_dir_summary(diff_files):
    print("\n\n**************************************************\nERROR SUMMARY:\n")

    if diff_files:
        print(f"::error::{len(diff_files)} files with differences were found")
    else:
        print("No differences found in any files")

    for filepath_a, filepath_b, reason, diff_file, details in diff_files:
        print(f"{reason}\n  A: {filepath_a}\n  B: {filepath_b}")
        if diff_file:
            print(f"Difference file: {diff_file}")
        if details:
            print(details)
        print()

    print("\n\n**************************************************\nDiff Summary:\n")
    for filepath_a, filepath_b, reason, diff_file, details in diff_files:
        print(f"{reason}\n  A: {filepath_a}\n  B: {filepath_b}")
        print()

    print("\nFinished comparing directories\n"
          "**************************************************\n\n")


def compare_files(filepath_a, filepath_b, debug=False, dir_a=None, dir_b=None,
                  save_diff=False):
    # dir_a and dir_b are only needed if comparing file lists that need those
    # directories to substitute when comparing because files in the list will
    # have different paths
    _print_if_debug(f"file_A: {filepath_a}\nfile_B: {filepath_b}\n", debug)

    if _should_skip_file(filepath_a, filepath_b, debug):
        return None

    msg = set_rounding_precision(filepath_a)
    _print_if_debug(msg, debug)

    # if file does not exist in dir_b, report difference
    if not os.path.exists(filepath_b):
        msg = f"ERROR: File does not exist: {filepath_b}"
        _print_if_debug(msg, debug)
        return filepath_a, '', 'file not found (in truth but missing now)', '', msg

    file_type = get_file_type(filepath_a)
    if file_type.startswith('skip'):
        file_ext = file_type.split(' ')[1]
        _print_if_debug(f"Skipping {file_ext} file" if file_ext else "Skipping file without extension", debug)
        return None

    if file_type.startswith('unsupported'):
        msg = f"Unsupported file type encountered: {file_type.split(' ')[1]}"
        _print_if_debug(msg, debug)
        return filepath_a, filepath_b, file_type, '', msg

    if file_type == 'csv':
        return _handle_csv_files(filepath_a, filepath_b, debug)

    if file_type == 'netcdf':
        return _handle_netcdf_files(filepath_a, filepath_b, debug)

    if file_type == 'pdf':
        return _handle_pdf_files(filepath_a, filepath_b, save_diff, debug)

    if file_type == 'image':
        return _handle_image_files(filepath_a, filepath_b, save_diff, debug)

    # if not any of the above types, use diff to compare
    return _handle_text_files(filepath_a, filepath_b, dir_a, dir_b, debug)

def _print_if_debug(msg, debug_on=True):
    if debug_on:
        print(msg)

def _should_skip_file(filepath_a, filepath_b, debug=False):
    for skip in SKIP_KEYWORDS:
        if skip in filepath_a or skip in filepath_b:
            if debug:
                print(f'WARNING: Skipping diff that contains keyword: {skip}')
            return True
    return False

def set_rounding_precision(filepath):
    global rounding_precision
    for keyword, precision in ROUNDING_OVERRIDES.items():
        if keyword not in filepath:
            continue

        rounding_precision = precision
        return f'Using rounding precision {precision} for {keyword}'

    rounding_precision = DEFAULT_ROUNDING_PRECISION
    return f'Using default rounding precision {DEFAULT_ROUNDING_PRECISION}'


def _handle_csv_files(filepath_a, filepath_b, debug=False):
    if debug:
        print('Comparing CSV')
    success, details = compare_csv_files(filepath_a, filepath_b)
    if not success:
        msg = f'ERROR: CSV file differs: {filepath_b}'
        msg += f'\n{details}'
        if debug:
            print(msg)
        return filepath_a, filepath_b, 'CSV diff', '', msg

    if debug:
        print("No differences in CSV files")
    return True


def _handle_netcdf_files(filepath_a, filepath_b, debug=False):
    if debug:
        print("Comparing NetCDF")
    success, details = nc_is_equal(filepath_a, filepath_b)
    if not success:
        msg = f'ERROR: NetCDF file differs: {filepath_b}'
        msg += f'\n{details}'
        if debug:
            print(msg)
        return filepath_a, filepath_b, 'NetCDF diff', '', msg

    if debug:
        print(f"{details}\nNo differences in NetCDF files")

    return True


def _handle_pdf_files(filepath_a, filepath_b, save_diff, debug=False):
    if debug:
        print("Comparing PDF as images")
    diff_file, details = compare_pdf_as_images(filepath_a, filepath_b, save_diff=save_diff)
    if diff_file is True:
        if debug:
            print("No differences in PDF files")
        return True

    if diff_file is False:
        diff_file = ''

    msg = f"ERROR: PDF file differs: {filepath_b}"
    msg += f'\n{details}'
    if diff_file:
        msg += f"\nSaving diff file {diff_file}"
    if debug:
        print(msg)
    return filepath_a, filepath_b, 'PDF diff', diff_file, msg


def _handle_image_files(filepath_a, filepath_b, save_diff, debug=False):
    if debug:
        print("Comparing images")
    diff_file, details = compare_image_files(filepath_a, filepath_b, save_diff=save_diff)
    if diff_file is True:
        if debug:
            print("No differences in image files")
        return True

    if diff_file is False:
        diff_file = ''

    msg = f"ERROR: image file differs: {filepath_b}\n{details}"
    if diff_file:
        msg += f"\nSaving diff file {diff_file}"
    if debug:
        print(msg)
    return filepath_a, filepath_b, 'Image diff', diff_file, msg


def _handle_text_files(filepath_a, filepath_b, dir_a, dir_b, debug=False):
    if debug:
        print("Comparing text files")
    
    if filecmp.cmp(filepath_a, filepath_b, shallow=False):
        if debug:
            print("No differences found from filecmp.cmp")
        return True

    # if files differ, open files and handle expected diffs
    success, details = compare_txt_files(filepath_a, filepath_b, dir_a, dir_b)
    if not success:
        msg = f"ERROR: File differs: {filepath_b}\n{details}"
        if debug:
            print(msg)
        return filepath_a, filepath_b, 'Text diff', '', msg

    if debug:
        print("No differences found from compare_txt_files")
    return True


def compare_pdf_as_images(filepath_a, filepath_b, save_diff=False):
    try:
        from pdf2image import convert_from_path
    except ModuleNotFoundError:
        return False, "Cannot compare PDF files without pdf2image Python package"

    images_a = convert_from_path(filepath_a)
    images_b = convert_from_path(filepath_b)
    for image_a, image_b in zip(images_a, images_b):
        image_diff, details = compare_images(image_a, image_b)

        # no differences if None, so continue to next image from PDF
        if image_diff is None:
            continue

        # if skipping save diff files, return False b/c there are differences
        if not save_diff:
            return False, details

        # create difference image and return the path
        return save_diff_file(image_diff, filepath_b), details

    return True, ''


def compare_image_files(filepath_a, filepath_b, save_diff=False):
    image_a = Image.open(filepath_a)
    image_b = Image.open(filepath_b)
    image_diff, details = compare_images(image_a, image_b)
    if image_diff is None:
        return True, ''

    if not save_diff:
        return False, details

    return save_diff_file(image_diff, filepath_b), details


def compare_images(image_a, image_b):
    """! Compare pillow image objects. Returns difference image object if there
    are differences or None if not.
    """
    details = ''
    diff_count = 0
    image_diff = ImageChops.difference(image_a, image_b)
    nx, ny = image_diff.size
    for x in range(0, int(nx)):
        for y in range(0, int(ny)):
            diff_pixel = image_diff.getpixel((x, y))
            if not _is_zero_pixel(diff_pixel):
                details += f"Difference pixel: {diff_pixel}: {x},{y}\n"
                diff_count += 1
    if diff_count:
        return image_diff, f"ERROR: Found {diff_count} differences between images\n{details.rstrip()}"
    return None, ''


def _is_zero_pixel(pixel, total_threshold=10, pixel_threshold=5):
    """!Check if difference pixel is 0, which means no differences.

    @param pixel pixel value or tuple if multi-layer image
    @param total_threshold change in total of all the pixels that can still be considered not a difference
    @param pixel_threshold change in a single pixel that can still be considered not a difference
    @returns True if all values are 0 or False if any value is non-zero
    """
    if isinstance(pixel, tuple):
        if sum(pixel) > total_threshold:
            return False
        return not any(val > pixel_threshold for val in pixel)

    return pixel <= total_threshold


def save_diff_file(image_diff, filepath_b):
    rel_path, _ = os.path.splitext(filepath_b)
    diff_file = f'{rel_path}_diff.png'
    image_diff.save(diff_file, "PNG")
    return diff_file


def compare_csv_files(filepath_a, filepath_b):
    lines_a = []
    lines_b = []

    with open(filepath_a, 'r') as file_handle:
        lines_a.extend(csv.DictReader(file_handle, delimiter=','))

    with open(filepath_b, 'r') as file_handle:
        lines_b.extend(csv.DictReader(file_handle, delimiter=','))

    # compare header values and number of lines
    success, details = _compare_csv_lengths(lines_a, lines_b)
    if not success:
        return success, details

    # compare each CSV column
    return _compare_csv_columns(lines_a, lines_b)


def _compare_csv_lengths(lines_a, lines_b):
    """!Compare length of CSV columns and lines.

    @param lines_a list of CSV lines from file A
    @param lines_b list of CSV lines from file B
    @returns string with error details if diffs are found, or empty string otherwise
    """
    details = ''
    keys_a = lines_a[0].keys()
    keys_b = lines_b[0].keys()
    # compare header columns and report error if they differ
    if len(keys_a) != len(keys_b):
        details += (f'ERROR: Different number of columns in TRUTH ({len(keys_a)}) '
                    f'than in OUTPUT ({len(keys_b)})')
        only_a = [item for item in keys_a if item not in keys_b]
        if only_a:
            details += f'\nColumns only in TRUTH: {",".join(only_a)}'

        only_b = [item for item in keys_b if item not in keys_a]
        if only_b:
            details += f'\nColumns only in OUTPUT: {",".join(only_b)}'
        return False, details

    # compare number of lines and error if they differ
    if len(lines_a) != len(lines_b):
        details += (f'ERROR: Different number of lines in TRUTH ({len(lines_a)}) '
                    f'than in OUTPUT ({len(lines_b)})')
        return False, details

    return True, details


def _compare_csv_columns(lines_a, lines_b):
    """!Compare length of CSV columns and lines.

    @param lines_a list of CSV lines from file A
    @param lines_b list of CSV lines from file B
    @returns string with error details if diffs are found, or empty string otherwise
    """
    details = ''
    keys_a = lines_a[0].keys()
    for num, (line_a, line_b) in enumerate(zip(lines_a, lines_b), start=1):
        for key in keys_a:
            val_a = line_a[key].strip()
            val_b = line_b[key].strip()
            # prevent error if values are diffs are less than
            # rounding_precision decimal places
            # METplus issue #1873 addresses the real problem
            try:
                if _is_equal_rounded(val_a, val_b):
                    continue
                details += (f"ERROR: Line {num} - {key} differs by "
                            f"less than {rounding_precision} decimals: "
                            f"TRUTH = {val_a}, OUTPUT = {val_b}")
            except ValueError:
                # handle values that can't be cast to float
                details += (f"ERROR: Line {num} - {key} differs: "
                            f"TRUTH = {val_a}, OUTPUT = {val_b}")

    return not details, details


def _is_version_string(value):
    """!Check if value is a MET version string, e.g., V12.1.0 or v10.2.1

    @param value string to check
    @returns True if value is a MET version string, False if not
    """
    return re.search(r"^[vV]\d+\.\d+\.\d+$", value)


def _is_equal_rounded(value_a, value_b):
    if value_a == value_b:
        return True
    if not _is_number(value_a) or not _is_number(value_b):
        return False
    if _set_zero(value_a) == _set_zero(value_b):
        return True
    if _round_sig_figs(value_a) == _round_sig_figs(value_b):
        return True
    if _truncate_float(value_a) == _truncate_float(value_b):
        return True
    if _round_float(value_a) == _round_float(value_b):
        return True
    return False


def _is_number(value):
    try:
        # consider masked values to not be a number
        if is_masked(value):
            return False
        float(value)
    except ValueError:
        return False
    return True

def _truncate_float(value):
    factor = 1 / (10 ** rounding_precision)
    return float(value) // factor * factor

def _round_float(value):
    return round(float(value), rounding_precision)

def _set_zero(value):
    if abs(float(value)) < IS_ZERO_TOL:
        # print(f"setting {value} to 0.0")  # DEBUG
        value = 0.0
    return value

def _round_sig_figs(value):
    # divide by 10^val_mag to put its first sig fig before the decimal
    #   and the rest after
    # round to SIG_FIG-1 to retain SIG_FIG digits
    # then multiply by 10^val_mag to revert to its actual magnitude
    try:
        val_mag = log10(abs(float(value))) // 1
        return round(float(value) / 10**val_mag, SIG_FIG-1) * (10**val_mag)
    except ValueError:
        if abs(float(value)) < IS_ZERO_TOL:
            return 0
        raise

def compare_txt_files(filepath_a, filepath_b, dir_a=None, dir_b=None):
    with open(filepath_a, 'r') as file_handle:
        lines_a = file_handle.read().splitlines()

    with open(filepath_b, 'r') as file_handle:
        lines_b = file_handle.read().splitlines()

    # handle if either file (or both) is empty
    # filepath_b is empty
    if not len(lines_b):
        # filepath_a is also empty
        if not len(lines_a):
            print("Both text files are empty, so they are equal")
            return True, ''
        return False, f"Empty file: {filepath_b}\nNot empty: {filepath_a}"
    # filepath_b is not empty but filepath_a is empty
    elif not len(lines_a):
        return False, f"Empty file: {filepath_a}\nNot empty: {filepath_b}"

    # check if the files are "file list" files
    # remove file_list first line for comparison
    _handle_file_list_files(lines_a, lines_b)

    # check if file is a METplus data file
    # - MET stat header lines starting with 'VERSION'
    # - METdataio header lines starting with 'Idx'
    # - MET stat data lines with 'VX.Y.Z' in the first column
    # - METdataio data lines with 'VX.Y.Z' in the second column
    has_header   = lines_a[0].startswith('VERSION') or lines_a[0].startswith('Idx')
    is_stat_file = has_header or any(_is_version_string(value) for value in lines_a[0].split()[0:2])

    # process data files
    header_a = None
    if is_stat_file:
        print("Comparing stat files")
        # check header lines
        if has_header:
            header_a = lines_a.pop(0).split()
            header_b = lines_b.pop(0).split()
            if len(header_a) != len(header_b):
                return False, f'ERROR: Different number of header columns\n A: {header_a}\n B: {header_b}'

    if len(lines_a) != len(lines_b):
        return False, (f"ERROR: Different number of lines in {filepath_b}\n"
                       f" File_A: {len(lines_a)}\n File_B: {len(lines_b)}")

    success, _ = diff_text_lines(lines_a, lines_b, dir_a=dir_a, dir_b=dir_b,
                                 is_stat_file=is_stat_file, header=header_a)
    if success:
        return True, ''

    # if differences found in text file, sort and try again
    orig_lines_a = lines_a.copy()
    orig_lines_b = lines_b.copy()
    lines_a.sort()
    lines_b.sort()
    success, _ = diff_text_lines(lines_a, lines_b, dir_a=dir_a, dir_b=dir_b,
                                 is_stat_file=is_stat_file, header=header_a)
    if success:
        return True, ''

    # if differences persist, print the original, unsorted differences
    return diff_text_lines(orig_lines_a, orig_lines_b, dir_a=dir_a, dir_b=dir_b,
                           is_stat_file=is_stat_file, header=header_a)


def _handle_file_list_files(lines_a, lines_b):
    """!Check if the files are "file list" files.
    Remove the first line that contains the string "file_list" for comparison.
    """
    is_file_list = False
    if lines_a[0] == 'file_list':
        is_file_list = True
        lines_a.pop(0)
    if lines_b[0] == 'file_list':
        is_file_list = True
        lines_b.pop(0)

    if is_file_list:
        print("Comparing file list file")

    return is_file_list


def diff_text_lines(lines_a, lines_b, dir_a=None, dir_b=None,
                    is_stat_file=False, header=None):
    all_good = True
    details = ''
    for line_a, line_b in zip(lines_a, lines_b):
        compare_a = line_a
        compare_b = line_b

        # initial check to skip lines without diffs
        if compare_a == compare_b:
            continue

        # skip FILTER and JOB_LIST lines due to expected filepath diffs
        if compare_a.startswith(('FILTER', 'JOB_LIST')):
            continue

        # try replacing dir_b with dir_a in line_b 
        # for cases where diff is due to filepath
        try:
            compare_b = compare_b.replace(dir_b, dir_a)
        except TypeError:       # don't error if missing dir_a or dir_b
            pass

        # check for differences
        if compare_a == compare_b:
            continue

        # if the diff is in a stat file, ignore the version number
        if is_stat_file:
            success, message = _diff_stat_line(compare_a, compare_b, header=header)
            if not success:
                all_good = False
                details += f"\n{message}"
            continue

        details += f"\nERROR: Line differs\n A: {compare_a}\n B: {compare_b}"
        all_good = False

    return all_good, details.lstrip()


def _diff_stat_line(compare_a, compare_b, header=None):
    """Compare values in .stat file. Ignore first column which contains MET
    version number

    @param compare_a list of values in line A
    @param compare_b list of values in line B
    @param header list of header values in file A excluding MET version
    """
    cols_a = compare_a.split()
    cols_b = compare_b.split()

    # error message to print if a diff is found
    message = f"ERROR: Stat line differs\n A: {compare_a}\n B: {compare_b}\n\n"

    # error if different number of columns are found
    if len(cols_a) != len(cols_b):
        message += '\nDifferent number of columns'
        return False, message

    all_good = True
    for index, (col_a, col_b) in enumerate(zip(cols_a, cols_b)):
        if _is_version_string(col_a) and _is_version_string(col_b):
            continue
        if _is_equal_rounded(col_a, col_b):
            continue
        all_good = False
        label = f'column {index+1}' if not header or index >= len(header) else header[index]
        message += f"  Diff in {label}:\n    A: {col_a}\n    B: {col_b}\n"

    if all_good:
        message = ''
    return all_good, message


def nc_is_equal(file_a, file_b, fields=None):
    """! Check if two NetCDF files have the same data

    @param file_a first file to compare
    @param file_b second file to compare
    @param fields (Optional) list of fields to compare. If unset, compare all
    @returns True if all values in fields are equivalent, False if not
    """
    nc_a = netCDF4.Dataset(file_a)
    nc_b = netCDF4.Dataset(file_b)

    # keep track of any differences that are found
    is_equal = True
    details = ''

    # if no fields are specified, get all of them
    if fields:
        field_list = [fields] if not isinstance(fields, list) else fields
    else:
        a_fields = sorted(nc_a.variables.keys())
        b_fields = sorted(nc_b.variables.keys())
        # fail if any fields exist in 1 file and not the other
        if a_fields != b_fields:
            details += ("ERROR: Field list differs between files\n"
                        f" File_A: {a_fields}\n File_B:{b_fields}\n"
                        f"Using File_A fields.")
            is_equal = False

        field_list = a_fields

    # loop through fields, keeping track of any differences
    for field in field_list:
        success, more_details = _nc_fields_are_equal(field, nc_a, nc_b)
        if not success:
            is_equal = False
        details += f"\n{more_details}"

    return is_equal, details


def _nc_fields_are_equal(field, nc_a, nc_b):
    """!Compare same field from 2 NetCDF files.

    @param field name of field to compare
    @param nc_a first netCDF4.Dataset
    @param nc_b first netCDF4.Dataset
    @returns True is fields are equal, False if fields are not equal or if
    field is not found in one of the files
    """
    try:
        var_a = nc_a.variables[field]
        var_b = nc_b.variables[field]
    except KeyError:
        return False, f"ERROR: Field {field} not found"

    msg = f"Field: {field}\nVar_A:{var_a}\nVar_B:{var_b}"
    if len(var_a) > 0:
      msg += f"\nInstance type: {type(var_a[0])}"

    values_a = var_a[:]
    values_b = var_b[:]

    # check for same amount of masked data
    if count_masked(values_a) != count_masked(values_b):
        msg += f"\nERROR: Field {field} has differing number of missing data values"
        return False, msg

    # compute diffs
    try:
        values_diff = values_a - values_b
    except TypeError:
        # handle non-numeric fields
        success, details = _all_values_are_equal(var_a, var_b)
        if not success:
            details += (f"\nERROR: Field ({field}) values (non-numeric) differ\n"
                        f" File_A: {var_a[:]}\n File_B: {var_b[:]}")
            msg += f"\n{details}"
            return False, msg
        return True, msg
    except ValueError:
        # check if shapes are not equal
        if values_a.shape != values_b.shape:
            msg += f"\nERROR: Field {field} values don't have the same shape"
            return False, msg
        raise

    # Check for NaN values and empty arrays first
    diff_result = _check_values_diff(values_diff, field, var_a, var_b)
    msg += f"\n{diff_result[1]}"
    if diff_result[0] is not None:
        return diff_result[0], msg

    # if this fails, compare all values, applying the same rounding logic
    # used for other file types
    success, details = _all_values_are_equal(var_a, var_b)
    if success:
        return True, msg

    details += (f"\nERROR: Field ({field}) values differ\n"
                f"Min diff: {values_diff.min()}, "
                f"Max diff: {values_diff.max()}")

    # print indices that are not zero and count of diffs
    details += f"\n{_print_nc_field_diff_summary(values_diff)}"

    msg += f"\n{details}"
    return False, msg


def _check_values_diff(values_diff, field, var_a, var_b):
    """Check for NaN values and empty arrays in NetCDF field comparison.

    @param values_diff numpy array of differences between var_a and var_b
    @param field name of the field being compared
    @param var_a first netCDF variable
    @param var_b second netCDF variable
    @returns (True, '') if values are equal, (False, error_details) if they differ, None if normal comparison should continue
    """
    # if any NaN values in either data set, min and max of diff will be NaN
    # compare each value
    details = ''
    try:
        if isnull(values_diff.min()) and isnull(values_diff.max()):
            details = f"Variable {field} contains NaN. Comparing each value..."
            success, more_details = _all_values_are_equal(var_a, var_b)
            if not success:
                details += f'\n{more_details}\nERROR: Some values differ in {field}'
                return False, details
            return True, details
    except ValueError:
        # handle error due to zero-size array
        if values_diff.size == 0:
            return True, details
        raise

    # consider all values equal if min and max diff are 0
    if not values_diff.min() and not values_diff.max():
        return True, details

    # Return None to indicate normal comparison should continue
    return None, details


def _print_nc_field_diff_summary(values_diff):
    """!Print summary of NetCDF fields that differ. Prints the index of each
    point that differs with the numeric difference between the points.
    Also print number of points that differ and the total number of points.

    @param values_diff numpy array (possibly 2D) of differences
    """
    diff_values = ''
    count = 0
    values_list = values_diff.flatten().tolist()
    idx = -1
    for idx, val in enumerate(values_list):
        if not isclose(val, 0.0, rel_tol=1e-09, abs_tol=1e-09):
            diff_values += f"{idx}: {val}\n"
            count += 1
    return f"{diff_values}{count} / {idx + 1} points differ"


def _all_values_are_equal(var_a, var_b):
    """!Compare each value to find differences. Handles case if both values
    are NaN.

    @param var_a Numpy array
    @param var_b Numpy array
    @returns (True, '') if all values are equal, (False, error_details) otherwise
    """
    # if the values are stored as a string, compare them with ==
    if isinstance(var_a[:], str) or isinstance(var_b[:], str):
        return var_a[:] == var_b[:], ''

    # flatten the numpy.ndarray and compare each value
    for val_a, val_b in zip(var_a[:].flatten(), var_b[:].flatten()):
        # continue to next value if both values are NaN
        if (isnull(val_a) and isnull(val_b)) or (is_masked(val_a) and is_masked(val_b)):
            continue
        if not _is_equal_rounded(val_a, val_b):
            return False, f'val_a: {val_a}, val_b: {val_b}'
    return True, ''


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('ERROR: Must supply 2 directories to compare as arguments')
        sys.exit(1)

    dir_a = sys.argv[1]
    dir_b = sys.argv[2]
    debug = any('debug' in arg for arg in sys.argv[1:])
    save_diff = any('save_diff' in arg for arg in sys.argv[1:])

    if debug:
        print("Debugging is turned on with --debug argument")
    else:
        print("Debugging is turned off. Add --debug argument to view details of comparisons with no differences")

    if save_diff:
        print("Saving diff files with --save_diff argument")
    else:
        print("Not saving diff files. Add --save_diff argument to save diff files for files with differences")

    # if any files were flagged, exit non-zero
    if compare_dir(dir_a, dir_b, debug=debug, save_diff=save_diff):
        sys.exit(2)
