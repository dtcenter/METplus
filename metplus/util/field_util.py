"""
Program Name: field_util.py
Contact(s): George McCabe <mccabe@ucar.edu>
Description: METplus utility to handle MET config dictionaries with field info
"""


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
