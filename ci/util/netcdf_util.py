import os
import netCDF4

def compare_dir(dir_a, dir_b, debug=False):
    all_equal = True
    for root, _, files in os.walk(dir_a):
        for filename in files:
            filepath = os.path.join(root, filename)

            # compare NetCDF data
            if filepath.endswith('nc'):
                filepath2 = filepath.replace(dir_a, dir_b)
                if not os.path.exists(filepath2):
                    if debug:
                        print(f"File does not exist: {filepath2}")
                    all_equal = False
                else:
                    if debug:
                        print(filepath)
                        print(filepath2)
                    if not nc_is_equal(filepath, filepath2):
                        all_equal = False

    return all_equal

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
            print("Field list differs between files\n"
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
                if values_diff.min() != 0.0 or values_diff.max() != 0.0:
                    print(f"Field ({field}) values differ\n"
                          f"Min diff: {values_diff.min()}, "
                          f"Max diff: {values_diff.max()}")
                    is_equal = False
                    # print indices that are not zero and count of diffs if debug
                    if debug:
                        count = 0
                        values_list = [j for sub in values_diff.tolist() for j in sub]
                        for idx, val in enumerate(values_list):
                            if val != 0.0:
                                print(f"{idx}: {val}")
                                count += 1
                        print(f"{count} / {idx+1} points differ")

            except TypeError:
                # handle non-numeric fields
                if any(var_a[:].flatten() != var_b[:].flatten()):
                    print(f"Field ({field}) values (non-numeric) differ\n"
                          f"A: {var_a}, B: {var_b}")
                    is_equal = False

    except KeyError:
        print(f"ERROR: Field {field} not found")
        return False

    return is_equal
