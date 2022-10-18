import os
import netCDF4
import filecmp
import csv
from PIL import Image, ImageChops
import numpy

IMAGE_EXTENSIONS = [
    '.jpg',
    '.jpeg',
]

NETCDF_EXTENSIONS = [
    '.nc',
    '.cdf',
]

SKIP_EXTENSIONS = [
    '.zip',
    '.png',
    '.gif',
    '.ix',
]

PDF_EXTENSIONS = [
    '.pdf',
]

CSV_EXTENSIONS = [
    '.csv',
]

UNSUPPORTED_EXTENSIONS = [
]

# number of decision places to accept float differences
# Note: Completing METplus issue #1873 could allow this to be set to 6
ROUNDING_PRECISION = 5

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
    except:
        pass

    if file_extension in SKIP_EXTENSIONS:
        return f'skip {file_extension}'

    if file_extension in PDF_EXTENSIONS:
        return 'pdf'

    if file_extension in UNSUPPORTED_EXTENSIONS:
        return f'unsupported{file_extension}'

    return 'unknown'


def compare_dir(dir_a, dir_b, debug=False, save_diff=False):
    # if input are files and not directories, compare them 
    if os.path.isfile(dir_a):
        result = compare_files(dir_a, dir_b, debug=debug, save_diff=save_diff)
        if result is None or result is True:
            return []

        return [result]

    diff_files = []
    for root, _, files in os.walk(dir_a):
        # skip logs directories
        if root.endswith('logs'):
            continue

        for filename in files:
            filepath_a = os.path.join(root, filename)

            # skip directories
            if not os.path.isfile(filepath_a):
                continue

            # skip final conf file
            if 'metplus_final.conf' in os.path.basename(filepath_a):
                continue

            filepath_b = filepath_a.replace(dir_a, dir_b)
            print("\n# # # # # # # # # # # # # # # # # # # # # # # # # # "
                  "# # # #\n")
            rel_path = filepath_a.replace(f'{dir_a}/', '')
            print(f"COMPARING {rel_path}")
            result = compare_files(filepath_a,
                                   filepath_b,
                                   debug=debug,
                                   dir_a=dir_a,
                                   dir_b=dir_b,
                                   save_diff=save_diff)

            # no differences of skipped
            if result is None or result is True:
                continue

            diff_files.append(result)

    # loop through dir_b and report if any files are not found in dir_a
    for root, _, files in os.walk(dir_b):
        # skip logs directories
        if root.endswith('logs'):
            continue

        for filename in files:
            filepath_b = os.path.join(root, filename)

            # skip final conf file
            if 'metplus_final.conf' in os.path.basename(filepath_b):
                continue

            filepath_a = filepath_b.replace(dir_b, dir_a)
            if not os.path.exists(filepath_a):
                # check if missing file is actually diff file that was generated
                diff_list = [item[3] for item in diff_files]
                if filepath_b in diff_list:
                    continue
                print(f"ERROR: File does not exist: {filepath_a}")
                diff_files.append(('', filepath_b, 'file not found (new output)', ''))

    print("\n\n**************************************************\nSummary:\n")
    if diff_files:
        print("\nERROR: Some differences were found")
        for filepath_a, filepath_b, reason, diff_file in diff_files:
            print(f"{reason}\n  A:{filepath_a}\n  B:{filepath_b}")
            if diff_file:
                print(f"Difference file: {diff_file}")
            print()
    else:
        print("\nNo differences found in any files")

    print("Finished comparing directories\n"
          "**************************************************\n\n")
    return diff_files


def compare_files(filepath_a, filepath_b, debug=False, dir_a=None, dir_b=None,
                  save_diff=False):
    # dir_a and dir_b are only needed if comparing file lists that need those
    # directories to substitute when comparing because files in the list will
    # have different paths
    print(f"file_A: {filepath_a}")
    print(f"file_B: {filepath_b}\n")

    # if file does not exist in dir_b, report difference
    if not os.path.exists(filepath_b):
        if debug:
            print(f"ERROR: File does not exist: {filepath_b}")
        return filepath_a, '', 'file not found (in truth but missing now)', ''

    file_type = get_file_type(filepath_a)
    if file_type.startswith('skip'):
        print(f"Skipping {file_type.split(' ')[1]} file")
        return None

    if file_type.startswith('unsupported'):
        print(f"Unsupported file type encountered: {file_type.split('.')[1]}")
        return filepath_a, filepath_b, file_type, ''

    if file_type == 'csv':
        print('Comparing CSV')
        if not compare_csv_files(filepath_a, filepath_b):
            print(f'ERROR: CSV file differs: {filepath_b}')
            return filepath_a, filepath_b, 'CSV diff', ''

        print("No differences in CSV files")
        return True

    if file_type == 'netcdf':
        print("Comparing NetCDF")
        if not nc_is_equal(filepath_a, filepath_b):
            return filepath_a, filepath_b, 'NetCDF diff', ''

        print("No differences in NetCDF files")
        return True

    if file_type == 'pdf':
        print("Comparing PDF as images")
        diff_file = compare_pdf_as_images(filepath_a, filepath_b,
                                          save_diff=save_diff)
        if diff_file is True:
            print("No differences in PDF files")
            return True

        if diff_file is False:
            diff_file = ''

        return filepath_a, filepath_b, 'PDF diff', diff_file

    if file_type == 'image':
        print("Comparing images")
        diff_file = compare_image_files(filepath_a, filepath_b,
                                        save_diff=save_diff)
        if diff_file is True:
            print("No differences in image files")
            return True

        if diff_file is False:
            diff_file = ''

        return filepath_a, filepath_b, 'Image diff', diff_file

    # if not any of the above types, use diff to compare
    print("Comparing text files")
    if not filecmp.cmp(filepath_a, filepath_b):
        # if files differ, open files and handle expected diffs
        if not compare_txt_files(filepath_a, filepath_b, dir_a, dir_b):
            print(f"ERROR: File differs: {filepath_b}")
            return filepath_a, filepath_b, 'Text diff', ''

        print("No differences in text files")
        return True
    else:
        print("No differences in text files")

    return True


def compare_pdf_as_images(filepath_a, filepath_b, save_diff=False):
    try:
        from pdf2image import convert_from_path
    except ModuleNotFoundError:
        print("Cannot compare PDF files without pdf2image Python package")
        return False

    images_a = convert_from_path(filepath_a)
    images_b = convert_from_path(filepath_b)
    for image_a, image_b in zip(images_a, images_b):
        image_diff = compare_images(image_a, image_b)

        # no differences if None, so continue to next image from PDF
        if image_diff is None:
            continue

        # if skipping save diff files, return False b/c there are differences
        if not save_diff:
            return False

        # create difference image and return the path
        return save_diff_file(image_diff, filepath_b)

    return True


def compare_image_files(filepath_a, filepath_b, save_diff=False):
    image_a = Image.open(filepath_a)
    image_b = Image.open(filepath_b)
    image_diff = compare_images(image_a, image_b)
    if image_diff is None:
        return True

    if not save_diff:
        return False

    return save_diff_file(image_diff, filepath_b)


def compare_images(image_a, image_b):
    """! Compare pillow image objects. Returns difference image object if there
    are differences or None if not.
    """
    diff_count = 0
    image_diff = ImageChops.difference(image_a, image_b)
    nx, ny = image_diff.size
    for x in range(0, int(nx)):
        for y in range(0, int(ny)):
            pixel = image_diff.getpixel((x, y))
            if pixel != 0 and pixel != (0, 0, 0, 0) and pixel != (0, 0, 0):
                print(f"Difference pixel: {pixel}")
                diff_count += 1
    if diff_count:
        print(f"ERROR: Found {diff_count} differences between images")
        return image_diff
    return None


def save_diff_file(image_diff, filepath_b):
    rel_path, file_extension = os.path.splitext(filepath_b)
    diff_file = f'{rel_path}_diff.png'
    print(f"Saving diff file: {diff_file}")
    image_diff.save(diff_file, "PNG")
    return diff_file


def compare_csv_files(filepath_a, filepath_b):
    lines_a = []
    lines_b = []

    with open(filepath_a, 'r') as file_handle:
        csv_read = csv.DictReader(file_handle, delimiter=',')
        for row in csv_read:
            lines_a.append(row)

    with open(filepath_b, 'r') as file_handle:
        csv_read = csv.DictReader(file_handle, delimiter=',')
        for row in csv_read:
            lines_b.append(row)

    keys_a = lines_a[0].keys()
    keys_b = lines_b[0].keys()
    # compare header columns and report error if they differ
    if len(keys_a) != len(keys_b):
        print(f'ERROR: Different number of columns in TRUTH ({len(keys_a)}) '
              f'than in OUTPUT ({len(keys_b)})')
        only_a = [item for item in keys_a if item not in keys_b]
        if only_a:
            print(f'Columns only in TRUTH: {",".join(only_a)}')

        only_b = [item for item in keys_b if item not in keys_a]
        if only_b:
            print(f'Columns only in OUTPUT: {",".join(only_b)}')
        return False

    # compare number of lines and error if they differ
    if len(lines_a) != len(lines_b):
        print(f'ERROR: Different number of lines in TRUTH ({len(lines_a)}) '
              f'than in OUTPUT ({len(lines_b)})')
        return False

    # compare each CSV column
    status = True
    for num, (line_a, line_b) in enumerate(zip(lines_a, lines_b), start=1):
        for key in keys_a:
            val_a = line_a[key]
            val_b = line_b[key]
            if val_a == val_b:
                continue
            # prevent error if values are diffs are less than
            # ROUNDING_PRECISION decimal places
            # METplus issue #1873 addresses the real problem
            try:
                if is_equal_rounded(val_a, val_b):
                    continue
                print(f"ERROR: Line {num} - {key} differs by "
                      f"less than {ROUNDING_PRECISION} decimals: "
                      f"TRUTH = {val_a}, OUTPUT = {val_b}")
                status = False
            except ValueError:
                # handle values that can't be cast to float
                print(f"ERROR: Line {num} - {key} differs: "
                      f"TRUTH = {val_a}, OUTPUT = {val_b}")
                status = False

    return status


def is_equal_rounded(value_a, value_b):
    if _truncate_float(value_a) == _truncate_float(value_b):
        return True
    if _round_float(value_a) == _round_float(value_b):
        return True
    return False


def _truncate_float(value):
    factor = 1 / (10 ** ROUNDING_PRECISION)
    return float(value) // factor * factor


def _round_float(value):
    return round(float(value), ROUNDING_PRECISION)


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
            return True
        else:
            print(f"Empty file: {filepath_b}\n"
                  f"Not empty: {filepath_a}")
            return False
    # filepath_b is not empty but filepath_a is empty
    elif not len(lines_a):
        print(f"Empty file: {filepath_a}\n"
              f"Not empty: {filepath_b}")
        return False

    # check if the files are "file list" files
    # remove file_list first line for comparison
    is_file_list = False
    if lines_a[0] == 'file_list':
        is_file_list = True
        lines_a.pop(0)
    if lines_b[0] == 'file_list':
        is_file_list = True
        lines_b.pop(0)

    if is_file_list:
        print("Comparing file list file")

    # check if file is an output stat file generated by MET
    is_stat_file = lines_a[0].startswith('VERSION')

    # if it is, save the header columns
    if is_stat_file:
        print("Comparing stat file")
        header_a = lines_a.pop(0).split()[1:]
        header_b = lines_b.pop(0).split()[1:]
    else:
        header_a = None
        header_b = None

    if len(lines_a) != len(lines_b):
        print(f"ERROR: Different number of lines in {filepath_b}")
        print(f" File_A: {len(lines_a)}\n File_B: {len(lines_b)}")
        return False

    all_good = diff_text_lines(lines_a,
                               lines_b,
                               dir_a=dir_a,
                               dir_b=dir_b,
                               print_error=False,
                               is_file_list=is_file_list,
                               is_stat_file=is_stat_file,
                               header_a=header_a)

    # if differences found in text file, sort and try again
    if not all_good:
        lines_a.sort()
        lines_b.sort()
        all_good = diff_text_lines(lines_a,
                                   lines_b,
                                   dir_a=dir_a,
                                   dir_b=dir_b,
                                   print_error=True,
                                   is_file_list=is_file_list,
                                   is_stat_file=is_stat_file,
                                   header_a=header_a)

    return all_good


def diff_text_lines(lines_a, lines_b,
                    dir_a=None, dir_b=None,
                    print_error=False,
                    is_file_list=False, is_stat_file=False,
                    header_a=None):
    all_good = True
    for line_a, line_b in zip(lines_a, lines_b):
        compare_a = line_a
        compare_b = line_b
        # if files are file list files, compare each line after replacing
        # dir_b with dir_a in filepath_b
        if is_file_list and dir_a and dir_b:
            compare_b = compare_b.replace(dir_b, dir_a)

        # check for differences
        if compare_a != compare_b:
            # if the diff is in a stat file, ignore the version number
            if is_stat_file:
                cols_a = compare_a.split()[1:]
                cols_b = compare_b.split()[1:]
                for col_a, col_b, label in zip(cols_a, cols_b, header_a):
                    if col_a != col_b:
                        if print_error:
                            print(f"ERROR: {label} differs:\n"
                                  f" A: {col_a}\n B: {col_b}")
                        all_good = False
            else:
                if print_error:
                    print(f"ERROR: Line differs\n"
                          f" A: {compare_a}\n B: {compare_b}")
                all_good = False

    return all_good


def nc_is_equal(file_a, file_b, fields=None, debug=False):
    """! Check if two NetCDF files have the same data
         @param file_a first file to compare
         @param file_b second file to compare
         @param fields (Optional) list of fields to compare. If unset, compare
          all fields
         @returns True if all values in fields are equivalent, False if not
    """
    nc_a = netCDF4.Dataset(file_a)
    nc_b = netCDF4.Dataset(file_b)

    # if no fields are specified, get all of them
    if fields:
        if not isinstance(fields, list):
            field_list = [fields]
        else:
            field_list = fields
    else:
        a_fields = sorted(nc_a.variables.keys())
        b_fields = sorted(nc_b.variables.keys())
        if a_fields != b_fields:
            print("ERROR: Field list differs between files\n"
                  f" File_A: {a_fields}\n File_B:{b_fields}\n"
                  f"Using File_A fields.")

        field_list = a_fields

    # loop through fields, keeping track of any differences
    is_equal = True
    try:
        for field in field_list:
            var_a = nc_a.variables[field]
            var_b = nc_b.variables[field]

            if debug:
                print(f"Field: {field}")
                print(f"Var_A:{var_a}\nVar_B:{var_b}")
                print(f"Instance type: {type(var_a[0])}")
            try:
                values_a = var_a[:]
                values_b = var_b[:]
                values_diff = values_a - values_b
                if (numpy.isnan(values_diff.min()) and
                        numpy.isnan(values_diff.max())):
                    print(f"WARNING: Variable {field} contains NaN values. "
                          "Cannot perform comparison.")
                elif values_diff.min() != 0.0 or values_diff.max() != 0.0:
                    print(f"ERROR: Field ({field}) values differ\n"
                          f"Min diff: {values_diff.min()}, "
                          f"Max diff: {values_diff.max()}")
                    is_equal = False
                    # print indices that are not zero and count of diffs
                    if debug:
                        count = 0
                        values_list = [j for sub in values_diff.tolist()
                                       for j in sub]
                        for idx, val in enumerate(values_list):
                            if val != 0.0:
                                print(f"{idx}: {val}")
                                count += 1
                        print(f"{count} / {idx+1} points differ")

            except:
                # handle non-numeric fields
                try:
                    if any(var_a[:].flatten() != var_b[:].flatten()):
                        print(f"ERROR: Field ({field}) values (non-numeric) "
                              "differ\n"
                              f" File_A: {var_a[:]}\n File_B: {var_b[:]}")
                        is_equal = False
                except:
                    print("ERROR: Couldn't diff NetCDF files, need to update diff method")
                    is_equal = False

    except KeyError:
        print(f"ERROR: Field {field} not found")
        return False

    return is_equal


if __name__ == '__main__':
    dir_a = sys.argv[1]
    dir_b = sys.argv[2]
    if len(sys.argv) > 3:
        save_diff = True
    compare_dir(dir_a, dir_b, debug=True, save_diff=save_diff)
