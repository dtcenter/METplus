"""
Program Name: field_util.py
Contact(s): George McCabe <mccabe@ucar.edu>
Description: METplus utility to handle MET config dictionaries with field info
"""

from . import get_threshold_via_regex, is_python_script, remove_quotes

def field_read_prob_info(config, c_dict, data_types, app_name):
    """! Read probabilistic variables for each field data type from the config
         object and sets values in the c_dict as appropriate.

        @param config METplusConfig object to read
        @param c_dict dictionary to set values
        @param data_types list of field types to check, i.e. FCST, OBS
        @param app_name name of tool used to read wrapper-specific configs
    """
    for data_type in data_types:
        # check both wrapper-specific variable and generic variable
        config_names = [
            f'{data_type}_{app_name.upper()}_IS_PROB',
            f'{data_type}_IS_PROB',
        ]
        name = config.get_mp_config_name(config_names)

        is_prob = config.getbool('config', name) if name else False
        c_dict[f'{data_type}_IS_PROB'] = is_prob

        # if field type is probabilistic, check if prob info is in GRIB PDS
        if not is_prob:
            continue

        config_names = [
            f'{data_type}_{app_name.upper()}_PROB_IN_GRIB_PDS',
            f'{data_type}_PROB_IN_GRIB_PDS',
        ]
        name = config.get_mp_config_name(config_names)
        prob_in_pds = config.getbool('config', name) if name else False
        c_dict[f'{data_type}_PROB_IN_GRIB_PDS'] = prob_in_pds


def get_field_info(c_dict, data_type='', v_name='', v_level='', v_thresh=None,
                   v_extra='', add_curly_braces=True):
    """! Format field information into format expected by MET config file

         @param c_dict config dictionary to read values
         @param v_level level of data to extract
         @param v_thresh threshold value to use in comparison
         @param v_name name of field to process
         @param v_extra additional field information to add if available
         @param data_type type of data to find i.e. FCST or OBS
         @param add_curly_braces if True, add curly braces around each
          field info string. If False, add single quotes around each
          field info string (defaults to True)
         @rtype string
         @return Returns a list of formatted field information or a string
          containing an error message if something went wrong
    """
    # if thresholds are set
    if v_thresh:
        # if neither fcst or obs are probabilistic,
        # pass in all thresholds as a comma-separated list for 1 field info
        if (not c_dict.get('FCST_IS_PROB', False) and
                not c_dict.get('OBS_IS_PROB', False)):
            thresholds = [','.join(v_thresh)]
        else:
            thresholds = v_thresh
    # if no thresholds are specified, fail if prob field is in grib PDS
    elif (c_dict.get(f'{data_type}_IS_PROB', False) and
          c_dict.get(f'{data_type}_PROB_IN_GRIB_PDS', False) and
          not is_python_script(v_name)):
        return 'No threshold was specified for probabilistic GRIB data'
    else:
        thresholds = [None]

    # list to hold field information
    fields = []

    for thresh in thresholds:
        if (c_dict.get(f'{data_type}_PROB_IN_GRIB_PDS', False) and
                not is_python_script(v_name)):
            field = _handle_grib_pds_field_info(v_name, v_level, thresh)
        else:
            # add field name
            field = f'name="{v_name}";'

            if v_level:
                field += f' level="{remove_quotes(v_level)}";'

            if c_dict.get(f'{data_type}_IS_PROB', False):
                field += " prob=TRUE;"

        # handle cat_thresh
        if c_dict.get(f'{data_type}_IS_PROB', False):
            # add probabilistic cat thresh if different from default ==0.1
            cat_thresh = c_dict.get(f'{data_type}_PROB_THRESH')
        else:
            cat_thresh = thresh

        if cat_thresh:
            field += f" cat_thresh=[ {cat_thresh} ];"

        # handle extra options if set
        if v_extra:
            extra = v_extra.strip()
            # if trailing semi-colon is not found, add it
            if not extra.endswith(';'):
                extra = f"{extra};"
            field += f' {extra}'

        # add curly braces around field info if requested
        # otherwise add single quotes around field info
        field = f'{{ {field} }}' if add_curly_braces else f"'{field}'"

        # add field info string to list of fields
        fields.append(field)

    # return list of strings in field dictionary format
    return fields


def _handle_grib_pds_field_info(v_name, v_level, thresh):
    """! Format field string to read probabilistic data from the PDS of a GRIB
     file. Thresholds are formatted using thresh_lo and thresh_hi syntax.

        @param v_name name of field to read
        @param v_level level of field to read
        @param thresh threshold value to format if set
        @returns formatted field string
    """

    field = f'name="PROB"; level="{v_level}"; prob={{ name="{v_name}";'

    if thresh:
        thresh_tuple_list = get_threshold_via_regex(thresh)
        for comparison, number in thresh_tuple_list:
            # skip adding thresh_lo or thresh_hi if comparison is NA
            if comparison == 'NA':
                continue

            if comparison in ["gt", "ge", ">", ">=", "==", "eq"]:
                field = f"{field} thresh_lo={number};"
            if comparison in ["lt", "le", "<", "<=", "==", "eq"]:
                field = f"{field} thresh_hi={number};"

    # add closing curly brace for prob=
    return f'{field} }}'
