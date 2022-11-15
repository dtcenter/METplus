import re

from .constants import LOWER_TO_WRAPPER_NAME
from .string_manip import getlist


def get_wrapper_name(process_name):
    """! Determine name of wrapper from string that may not contain the correct
         capitalization, i.e. Pcp-Combine translates to PCPCombine

         @param process_name string that was listed in the PROCESS_LIST
         @returns name of wrapper (without 'Wrapper' at the end) and None if
          name cannot be determined
    """
    lower_process = (process_name.replace('-', '')
                         .replace('_', '')
                         .replace(' ', '')
                         .lower())
    if lower_process in LOWER_TO_WRAPPER_NAME.keys():
        return LOWER_TO_WRAPPER_NAME[lower_process]

    return None

def get_process_list(config):
    """!Read process list, Extract instance string if specified inside
     parenthesis. Remove dashes/underscores and change to lower case,
     then map the name to the correct wrapper name

     @param config METplusConfig object to read PROCESS_LIST value
     @returns list of tuple containing process name and instance identifier
     (None if no instance was set)
    """
    # get list of processes
    process_list = getlist(config.getstr('config', 'PROCESS_LIST'))

    out_process_list = []
    # for each item remove dashes, underscores, and cast to lower-case
    for process in process_list:
        # if instance is specified, extract the text inside parenthesis
        match = re.match(r'(.*)\((.*)\)', process)
        if match:
            instance = match.group(2)
            process_name = match.group(1)
        else:
            instance = None
            process_name = process

        wrapper_name = get_wrapper_name(process_name)
        if wrapper_name is None:
            config.logger.warning(f"PROCESS_LIST item {process_name} "
                                  "may be invalid.")
            wrapper_name = process_name

        out_process_list.append((wrapper_name, instance))

    return out_process_list


def get_custom_string_list(config, met_tool):
    var_name = 'CUSTOM_LOOP_LIST'
    custom_loop_list = config.getstr_nocheck('config',
                                             f'{met_tool.upper()}_{var_name}',
                                             config.getstr_nocheck('config',
                                                                   var_name,
                                                                   ''))
    custom_loop_list = getlist(custom_loop_list)
    if not custom_loop_list:
        custom_loop_list.append('')

    return custom_loop_list
