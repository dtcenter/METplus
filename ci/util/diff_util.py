import os
import netCDF4
import filecmp
from PIL import Image, ImageChops
import numpy

IMAGE_EXTENSIONS = [
    '.png',
    '.jpg',
    '.jpeg',
]

NETCDF_EXTENSIONS = [
    '.nc',
    '.cdf',
]

SKIP_EXTENSIONS = [
    '.zip',
]

def get_file_type(filepath):
    _, file_extension = os.path.splitext(filepath)
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
        return 'skip'

    return 'unknown'

def compare_dir(dir_a, dir_b, debug=False):
    # if input are files and not directories, compare them
    if os.path.isfile(dir_a):
        result = compare_files(dir_a, dir_b, debug)
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

            # skip metplus_final.conf
            if filepath_a.endswith('metplus_final.conf'):
                continue

            filepath_b = filepath_a.replace(dir_a, dir_b)
            result = compare_files(filepath_a, filepath_b, debug)

            # no differences of skipped
            if result is None or result is True:
                continue

            diff_files.append(result)

    if diff_files:
        print("\nERROR: Some differences were found")
        for filepath_a, filepath_b, reason in diff_files:
            print(f"{reason}\n  {filepath_a}\n  {filepath_b}")
    else:
        print("\nNo differences found in any files")

    return diff_files

def compare_files(filepath_a, filepath_b, debug=False):
    print("\n# # # # # # # # # # # # # # # # # # # # # # # # # # "
          "# # # #\n")
    rel_path = filepath_a.replace(f'{dir_a}/', '')
    print(f"COMPARING {rel_path}")
    print(f"file_A: {filepath_a}")
    print(f"file_B: {filepath_b}\n")

    # if file does not exist in dir_b, report difference
    if not os.path.exists(filepath_b):
        if debug:
            print(f"ERROR: File does not exist: {filepath_b}")
        return (filepath_a, '', 'file not found')

    file_type = get_file_type(filepath_a)
    if file_type == 'skip':
        print(f'Skipping')
        return None

    if file_type == 'netcdf':
        print("Comparing NetCDF")
        if not nc_is_equal(filepath_a, filepath_b):
            return (filepath_a, filepath_b, 'NetCDF diff')

        print("No differences in NetCDF files")
        return True

    if file_type == 'image':
        print("Comparing images")
        if not compare_image_files(filepath_a, filepath_b):
            return (filepath_a, filepath_b, 'Image diff')

        print("No differences in image files")
        return True

    # if not any of the above types, use diff to compare
    print("Comparing text files")
    if not filecmp.cmp(filepath_a, filepath_b):
        # if files differ, open files and handle expected diffs
        if not compare_txt_files(filepath_a, filepath_b, dir_a, dir_b):
            print(f"ERROR: File differs: {filepath_b}")
            return (filepath_a, filepath_b, 'Text diff')

        print("No differences in text files")
        return True
    else:
        print("No differences in text files")

    return True

def compare_image_files(filepath_a, filepath_b):
    diff_count = 0

    image_a = Image.open(filepath_a)
    image_b = Image.open(filepath_b)
    image_diff = ImageChops.difference(image_a, image_b)
    nx, ny = image_diff.size
    for x in range(0, int(nx)):
        for y in range(0, int(ny)):
            pixel = image_diff.getpixel((x, y))
            if pixel != 0 and pixel != (0, 0, 0, 0):
                diff_count += 1
    if diff_count:
        print(f"ERROR: Found {diff_count} differences between images")
        return False
    return True

def compare_txt_files(filepath_a, filepath_b, dir_a, dir_b):
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

    if len(lines_a) != len(lines_b):
        print(f"ERROR: Different number of lines in {filepath_b}")
        print(f" File_A: {len(lines_a)}\n File_B: {len(lines_b)}")
        return False

    all_good = True
    for line_a, line_b in zip(lines_a, lines_b):
        compare_a = line_a
        compare_b = line_b
        # if files are file list files, compare each line after replacing
        # dir_b with dir_a in filepath_b
        if is_file_list:
            compare_b = compare_b.replace(dir_b, dir_a)

        # check for differences
        if compare_a != compare_b:
            # if the diff is in a stat file, ignore the version number
            if is_stat_file:
                cols_a = compare_a.split()[1:]
                cols_b = compare_b.split()[1:]
                for col_a, col_b, label in zip(cols_a, cols_b, header_a):
                    if col_a != col_b:
                        print(f"ERROR: {label} differs: {col_a} vs {col_b}")
                        all_good = False
            else:
                print(f"ERROR: Line in {filepath_b} differs")
                print(f"  A: {compare_a}")
                print(f"  B: {compare_b}")
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
                              f" File_A: {var_a}\n File_B: {var_b}")
                        is_equal = False
                except:
                    print("ERROR: Couldn't diff NetCDF files, need to update diff method")
                    is_equal = False

    except KeyError:
        print(f"ERROR: Field {field} not found")
        return False

    return is_equal
