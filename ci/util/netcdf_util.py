import netCDF4
################################################################################
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
        a_fields = list(nc_a.variables.keys())
        b_fields = list(nc_b.variables.keys())
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
            values_a = var_a[:]
            values_b = var_b[:]
            values_diff = values_a - values_b
            if values_diff.min() != 0.0 or values_diff.max() != 0.0:
                print(f"Field ({field}) values differ\n"
                      f"Min diff: {values_diff.min()}, "
                      f"Max diff: {values_diff.max()}")

                # print indices that are not zero and count of diffs if debug
                if debug:
                    count = 0
                    values_list = [j for sub in values_diff.tolist() for j in sub]
                    for idx, val in enumerate(values_list):
                        if val != 0.0:
                            print(f"{idx}: {val}")
                            count += 1
                    print(f"{count} / {idx+1} points differ")

                is_equal = False

    except KeyError:
        print("ERROR: Field {field} not found")
        return False

    return is_equal
