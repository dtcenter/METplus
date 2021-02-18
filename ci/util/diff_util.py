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
    all_equal = True
    diff_files = []
    for root, _, files in os.walk(dir_a):
        # skip logs directories
        if root.endswith('logs'):
            continue

        for filename in files:
            filepath = os.path.join(root, filename)

            # skip directories
            if not os.path.isfile(filepath):
                continue

            # skip metplus_final.conf
            if filepath.endswith('metplus_final.conf'):
                continue

            filepath2 = filepath.replace(dir_a, dir_b)
            if debug:
                print("\n# # # # # # # # # # # # # # # # # # # # # # # # # # "
                      "# # # #\n")
                rel_path = filepath.replace(f'{dir_a}/', '')
                print(f"COMPARING {rel_path}")
                print(f"file1: {filepath}")
                print(f"file2: {filepath2}\n")

            # if file does not exist in dir_b, report difference
            if not os.path.exists(filepath2):
                if debug:
                    print(f"ERROR: File does not exist: {filepath2}")
                all_equal = False
                diff_files.append((filepath, '', 'file not found'))
                continue

            file_type = get_file_type(filepath)
            if file_type == 'skip':
                print(f'Skipping')
                continue

            if file_type == 'netcdf':
                print("Comparing NetCDF")
                if not nc_is_equal(filepath, filepath2):
                    all_equal = False
                    diff_files.append((filepath, filepath2, 'NetCDF diff'))
                else:
                    print("No differences in NetCDF files")
                continue

            if file_type == 'image':
                print("Comparing images")
                if not compare_image_files(filepath, filepath2):
                    all_equal = False
                    diff_files.append((filepath, filepath2, 'Image diff'))
                else:
                    print("No differences in image files")
                continue

            # if not any of the above types, use diff to compare
            print("Comparing text files")
            if not filecmp.cmp(filepath, filepath2):
                # if files differ, open files and handle expected diffs
                if not compare_txt_files(filepath, filepath2, dir_a, dir_b):
                    print(f"ERROR: File differs: {filepath2}")
                    all_equal = False
                    diff_files.append((filepath, filepath2, 'Text diff'))
                else:
                    print("No differences in text files")
            else:
                print("No differences in text files")

    if not all_equal:
        print("ERROR: Some differences were found")
        for filepath_a, filepath_b, reason in diff_files:
            print(f"{reason}\n  {filepath_a}\n  {filepath_b}")
    else:
        print("No differences found in any files")

    return all_equal

def compare_image_files(filepath, filepath2):
    diff_count = 0

    image_a = Image.open(filepath)
    image_b = Image.open(filepath2)
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

def compare_txt_files(filepath, filepath2, dir_a, dir_b):
    with open(filepath, 'r') as file_handle:
        lines_a = file_handle.read().splitlines()

    with open(filepath2, 'r') as file_handle:
        lines_b = file_handle.read().splitlines()

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
        print(f"ERROR: Different number of lines in {filepath2}")
        print(f"A: {len(lines_a)}, B: {len(lines_b)}")
        return False

    for line_a, line_b in zip(lines_a, lines_b):
        compare_a = line_a
        compare_b = line_b
        # if files are file list files, compare each line after replacing
        # dir_b with dir_a in filepath2
        if is_file_list:
            compare_b = compare_b.replace(dir_b, dir_a)

        # check for differences
        all_good = True
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
                print(f"ERROR: Line in {filepath2} differs")
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
                  f"A: {a_fields}\nB:{b_fields}\n"
                  f"Using A fields.")

        field_list = a_fields

    # loop through fields, keeping track of any differences
    is_equal = True
    try:
        for field in field_list:
            var_a = nc_a.variables[field]
            var_b = nc_b.variables[field]

            if debug:
                print(f"Field: {field}")
                print(f"Var_a:{var_a}\nVar_b:{var_b}")
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

            except TypeError:
                # handle non-numeric fields
                if any(var_a[:].flatten() != var_b[:].flatten()):
                    print(f"ERROR: Field ({field}) values (non-numeric) "
                          "differ\n"
                          f"A: {var_a}, B: {var_b}")
                    is_equal = False

    except KeyError:
        print(f"ERROR: Field {field} not found")
        return False

    return is_equal
