"""
Program Name: string_manip.py
Contact(s): George McCabe
Description: METplus utility to handle string manipulation
"""

import sys
import os
import re
from csv import reader
import random
import string
import logging

try:
    from .constants import VALID_COMPARISONS, LOWER_TO_WRAPPER_NAME
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from constants import VALID_COMPARISONS, LOWER_TO_WRAPPER_NAME


def get_wrapper_name(process_name):
    """! Determine name of wrapper from string that may not contain the correct
         capitalization, i.e. Pcp-Combine translates to PCPCombine

         @param process_name string that was listed in the PROCESS_LIST
         @returns name of wrapper (without 'Wrapper' at the end) and None if
          name cannot be determined
    """
    lower_process = (process_name.replace('-', '').replace('_', '')
                     .replace(' ', '').lower())
    if lower_process in LOWER_TO_WRAPPER_NAME.keys():
        return LOWER_TO_WRAPPER_NAME[lower_process]

    return None


def remove_quotes(input_string):
    """!Remove quotes from string"""
    if not input_string:
        return ''

    # strip off double and single quotes
    return input_string.strip('"').strip("'")


def getlist(list_str, expand_begin_end_incr=True):
    """! Returns a list of string elements from a comma
         separated string of values.
         This function MUST also return an empty list [] if s is '' empty.
         This function is meant to handle these possible or similar inputs:
         AND return a clean list with no surrounding spaces or trailing
         commas in the elements.
         '4,4,2,4,2,4,2, ' or '4,4,2,4,2,4,2 ' or
         '4, 4, 4, 4, ' or '4, 4, 4, 4 '
         Note: getstr on an empty variable (EMPTY_VAR = ) in
         a conf file returns '' an empty string.

        @param list_str the string being converted to a list.
        @returns list of strings formatted properly and expanded as needed
    """
    if not list_str:
        return []

    # remove surrounding comma and spaces from the string
    list_str = list_str.strip(', ').strip()

    # remove trailing semi-colon IF found after []s
    if list_str.endswith('];'):
        list_str = list_str.strip('; ').strip()

    # remove [ from start (left) and ] from end (right)
    list_str = list_str.lstrip('[ ').rstrip('] ').strip()

    # remove space around commas
    list_str = re.sub(r'\s*,\s*', ',', list_str)

    # option to not evaluate begin_end_incr
    if expand_begin_end_incr:
        list_str = _handle_begin_end_incr(list_str)

    # use regex split to split list string by commas that are not
    # found within []s or ()s
    item_list = re.split(r',\s*(?![^\[\]]*\]|[^()]*\))', list_str)

    # regex split will still split by commas that are found between
    # quotation marks, so call function to put them back together properly
    item_list = _fix_list(item_list)

    return item_list


def getlistint(list_str):
    """! Get list and convert all values to int

    @param list_str the string being converted to a list.
    @returns list of ints
    """
    list_str = getlist(list_str)
    list_str = [int(i) for i in list_str]
    return list_str


def _handle_begin_end_incr(list_str):
    """! Check for instances of begin_end_incr() in the input string and
     evaluate as needed

     @param list_str string that contains a comma separated list
     @returns string that has list expanded
    """

    matches = _begin_end_incr_findall(list_str)

    for match in matches:
        item_list = _begin_end_incr_evaluate(match)
        if item_list:
            list_str = list_str.replace(match, ','.join(item_list))

    return list_str


def _begin_end_incr_findall(list_str):
    """! Find all instances of begin_end_incr in list string

    @param list_str string that contains a comma separated list
    @returns list of strings that have begin_end_incr() characters
    """
    # remove space around commas (again to make sure)
    # this makes the regex slightly easier because we don't have to include
    # as many \s* instances in the regex string
    list_str = re.sub(r'\s*,\s*', ',', list_str)

    # find begin_end_incr and any text before and after that are not a comma
    # [^,\s]* evaluates to any character that is not a comma or space
    return re.findall(
        r"([^,]*begin_end_incr\(\s*-?\d*,-?\d*,-*\d*,?\d*\s*\)[^,]*)",
        list_str
    )


def _begin_end_incr_evaluate(item):
    """! Expand begin_end_incr() items into a list of values

    @param item string containing begin_end_incr() tag with
     possible text before and after
    @returns list of items expanded from begin_end_incr
    """
    match = re.match(
        r"^(.*)begin_end_incr\(\s*(-*\d*),(-*\d*),(-*\d*),?(\d*)\s*\)(.*)$",
        item
    )
    if match:
        before = match.group(1).strip()
        after = match.group(6).strip()
        start = int(match.group(2))
        end = int(match.group(3))
        step = int(match.group(4))
        precision = match.group(5).strip()

        if start <= end:
            int_list = range(start, end+1, step)
        else:
            int_list = range(start, end-1, step)

        out_list = []
        for int_values in int_list:
            out_str = str(int_values)

            if precision:
                out_str = out_str.zfill(int(precision))

            out_list.append(f"{before}{out_str}{after}")

        return out_list

    return None


def _fix_list(item_list):
    """! The logic that calls this function may have incorrectly split up
    a string that contains commas within quotation marks. This function
    looks through the list and finds items that appear to have been split up
    incorrectly and puts them back together properly.

     @param item_list list of items to be corrected
     @returns corrected list
    """
    fixed_list = []
    list_buffer = []
    for item in item_list:
        quote_count = item.count('"')
        if not list_buffer:
            # if there are an even number of quotation marks, add to list
            if quote_count % 2 == 0:
                fixed_list.append(item)
            # otherwise add it to the list buffer
            else:
                list_buffer.append(item)
        else:
            list_buffer.append(item)
            if quote_count == 1:
                fixed_list.append(','.join(list_buffer))
                list_buffer.clear()

    # if there are still items in the buffer, add them to end of list
    if list_buffer:
        fixed_list.append(','.join(list_buffer))

    # remove extra quotation marks around string
    out_list = []
    for item in fixed_list:
        if item[0] == '"' and item[-1] == '"':
            out_list.append(item.strip('"'))
        else:
            out_list.append(item)

    return out_list


def list_to_str(list_of_values, add_quotes=True):
    """! Turn a list of values into a single string

    @param list_of_values list of values, i.e. ['value1', 'value2']
    @param add_quotes if True, add quotation marks around values,
     default is True

    @returns string created from list_of_values with the values separated
      by commas, i.e. '"value1", "value2"'  or 1, 3 if add_quotes is False
    """
    # return empty string if list is empty
    if not list_of_values:
        return ''

    if add_quotes:
        # remove any quotes that are already around items, then add quotes
        values = [remove_quotes(item) for item in list_of_values]
        return '"' + '", "'.join(values) + '"'

    return ', '.join(list_of_values)


def comparison_to_letter_format(expression):
    """! Convert comparison operator to the letter version if it is not already

    @param expression string starting with comparison operator to convert,
     i.e. gt3 or <=5.4
    @returns letter comparison operator, i.e. gt3 or le5.4 or None if invalid
    """
    for symbol_comp, letter_comp in VALID_COMPARISONS.items():
        if letter_comp in expression or symbol_comp in expression:
            return expression.replace(symbol_comp, letter_comp)

    return None


def format_thresh(thresh_str):
    """! Format thresholds for file naming

    @param thresh_str string of the thresholds.
     Can be a comma-separated list, i.e. gt3,<=5.5, ==7

    @returns string of comma-separated list of the threshold(s) with
     letter format, i.e. gt3,le5.5,eq7
    """
    if isinstance(thresh_str, list):
        return format_thresh(','.join(thresh_str))

    formatted_thresh_list = []
    # separate thresholds by comma and strip off whitespace around values
    thresh_list = [thresh.strip() for thresh in thresh_str.split(',')]
    for thresh in thresh_list:
        if not thresh:
            continue

        thresh_letter = comparison_to_letter_format(thresh)
        if thresh_letter:
            formatted_thresh_list.append(thresh_letter)

    return ','.join(formatted_thresh_list)


def is_python_script(name):
    """ Check if field name is a python script by checking if any of the words
     in the string end with .py

     @param name string to check
     @returns True if the name is determined to be a python script command
     """
    if not name:
        return False

    all_items = name.split(' ')
    if any(item.endswith('.py') for item in all_items):
        return True

    return False


def camel_to_underscore(camel):
    """! Change camel case notation to underscore notation, i.e. GridStatWrapper to grid_stat_wrapper
         Multiple capital letters are excluded, i.e. PCPCombineWrapper to pcp_combine_wrapper
         Numerals are also skipped, i.e. ASCII2NCWrapper to ascii2nc_wrapper
         Args:
             @param camel string to convert
             @returns string in underscore notation
    """
    s1 = re.sub(r'([^\d])([A-Z][a-z]+)', r'\1_\2', camel)
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', s1).lower()


def get_threshold_via_regex(thresh_string):
    """!Ensure thresh values start with >,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le and then a number
        Optionally can have multiple comparison/number pairs separated with && or ||.
        Args:
            @param thresh_string: String to examine, i.e. <=3.4
        Returns:
            None if string does not match any valid comparison operators or does
              not contain a number afterwards
            regex match object with comparison operator in group 1 and
            number in group 2 if valid
    """

    comparison_number_list = []
    # split thresh string by || or &&
    thresh_split = re.split(r'\|\||&&', thresh_string)
    # check each threshold for validity
    for thresh in thresh_split:
        found_match = False
        for comp in list(VALID_COMPARISONS)+list(VALID_COMPARISONS.values()):
            # if valid, add to list of tuples
            # must be one of the valid comparison operators followed by
            # at least 1 digit or NA
            if thresh == 'NA':
                comparison_number_list.append((thresh, ''))
                found_match = True
                break

            match = re.match(r'^('+comp+r')(.*\d.*)$', thresh)
            if match:
                comparison = match.group(1)
                number = match.group(2)
                # try to convert to float if it can, but allow string
                try:
                    number = float(number)
                except ValueError:
                    pass

                comparison_number_list.append((comparison, number))
                found_match = True
                break

        # if no match was found for the item, return None
        if not found_match:
            return None

    if not comparison_number_list:
        return None

    return comparison_number_list


def validate_thresholds(thresh_list):
    """ Checks list of thresholds to ensure all of them have the correct format
        Should be a comparison operator with number pair combined with || or &&
        i.e. gt4 or >3&&<5 or gt3||lt1
        Args:
            @param thresh_list list of strings to check
        Returns:
            True if all items in the list are valid format, False if not
    """
    valid = True
    for thresh in thresh_list:
        match = get_threshold_via_regex(thresh)
        if match is None:
            valid = False

    if valid is False:
        print("ERROR: Threshold values must use >,>=,==,!=,<,<=,gt,ge,eq,ne,lt, or le with a number, "
              "optionally combined with && or ||")
        return False
    return True


def round_0p5(val):
    """! Round to the nearest point five (ie 3.3 rounds to 3.5, 3.1
       rounds to 3.0) Take the input value, multiply by two, round to integer
       (no decimal places) then divide by two.  Expect any input value of n.0,
       n.1, or n.2 to round down to n.0, and any input value of n.5, n.6 or
       n.7 to round to n.5. Finally, any input value of n.8 or n.9 will
       round to (n+1).0

      @param val :  The number to be rounded to the nearest .5
    @returns n.0, n.5, or (n+1).0 value as a result of rounding
    """
    return round(val * 2) / 2


def generate_tmp_filename():
    random_string = ''.join(random.choice(string.ascii_letters)
                            for i in range(10))
    return f"metplus_tmp_{random_string}"


def template_to_regex(template):
    in_template = re.sub(r'\.', '\\.', template)
    return re.sub(r'{lead.*?}', '.*', in_template)


def split_level(level):
    """! If level value starts with a letter, then separate that letter from
     the rest of the string. i.e. 'A03' will be returned as 'A', '03'. If no
     level type letter is found and the level value consists of alpha-numeric
     characters, return an empty string as the level type and the full level
     string as the level value

     @param level input string to parse/split
     @returns tuple of level type and level value
    """
    if not level:
        return '', ''

    match = re.match(r'^([a-zA-Z])(\w+)$', level)
    if match:
        level_type = match.group(1)
        level = match.group(2)
        return level_type, level

    match = re.match(r'^[\w]+$', level)
    if match:
        return '', level

    return '', ''


def format_level(level):
    """! Format level string to prevent NetCDF level values from creating
         filenames and field names with bad characters. Replaces '*' with 'all'
         and ',' with '_'

        @param level string of level to format
        @returns formatted string
    """
    return level.replace('*', 'all').replace(',', '_')


def expand_int_string_to_list(int_string):
    """! Expand string into a list of integer values. Items are separated by
    commas. Items that are formatted X-Y will be expanded into each number
    from X to Y inclusive. If the string ends with +, then add a str '+'
    to the end of the list. Used in .github/jobs/get_use_case_commands.py

    @param int_string String containing a comma-separated list of integers
    @returns List of integers and potentially '+' as the last item
    """
    subset_list = []

    # if string ends with +, remove it and add it back at the end
    if int_string.strip().endswith('+'):
        int_string = int_string.strip(' +')
        hasPlus = True
    else:
        hasPlus = False

    # separate into list by comma
    comma_list = int_string.split(',')
    for comma_item in comma_list:
        dash_list = comma_item.split('-')
        # if item contains X-Y, expand it
        if len(dash_list) == 2:
            for i in range(int(dash_list[0].strip()),
                           int(dash_list[1].strip())+1,
                           1):
                subset_list.append(i)
        else:
            subset_list.append(int(comma_item.strip()))

    if hasPlus:
        subset_list.append('+')

    return subset_list


def subset_list(full_list, subset_definition):
    """! Extract subset of items from full_list based on subset_definition
    Used in internal/tests/use_cases/metplus_use_case_suite.py

    @param full_list List of all use cases that were requested
    @param subset_definition Defines how to subset the full list. If None,
    no subsetting occurs. If an integer value, select that index only.
    If a slice object, i.e. slice(2,4,1), pass slice object into list.
    If list, subset full list by integer index values in list. If
    last item in list is '+' then subset list up to 2nd last index, then
    get all items from 2nd last item and above
    """
    if subset_definition is not None:
        subset_list = []

        # if case slice is a list, use only the indices in the list
        if isinstance(subset_definition, list):
            # if last slice value is a plus sign, get rest of items
            # after 2nd last slice value
            if subset_definition[-1] == '+':
                plus_value = subset_definition[-2]
                # add all values before last index before plus
                subset_list.extend([full_list[i]
                                    for i in subset_definition[:-2]])
                # add last index listed + all items above
                subset_list.extend(full_list[plus_value:])
            else:
                # list of integers, so get items based on indices
                subset_list = [full_list[i] for i in subset_definition]
        else:
            subset_list = full_list[subset_definition]
    else:
        subset_list = full_list

    # if only 1 item is left, make it a list before returning
    if not isinstance(subset_list, list):
        subset_list = [subset_list]

    return subset_list


def find_indices_in_config_section(regex, config, sec='config',
                                   index_index=1, id_index=None):
    """! Use regular expression to get all config variables that match and
    are set in the user's configuration. This is used to handle config
    variables that have multiple indices, i.e. FCST_VAR1_NAME, FCST_VAR2_NAME,
    etc.

    @param regex regular expression to use to find variables
    @param config METplusConfig object to search
    @param sec (optional) config file section to search. Defaults to config
    @param index_index 1 based number that is the regex match index for the
     index number (default is 1)
    @param id_index 1 based number that is the regex match index for the
     identifier. Defaults to None which does not extract an identifier
    @returns dictionary where keys are the index number and the value is a
     list of identifiers (if id_index=None) or a list containing None
    """
    # regex expression must have 2 () items and the 2nd item must be the index
    all_conf = config.keys(sec)
    indices = {}
    regex = re.compile(regex)
    for conf in all_conf:
        result = regex.match(conf)
        if result is None:
            continue

        index = result.group(index_index)
        if id_index:
            identifier = result.group(id_index)
        else:
            identifier = None

        if index not in indices:
            indices[index] = [identifier]
        else:
            indices[index].append(identifier)

    return indices


def get_logfile_info(config):
    """!Get path to log file from LOG_METPLUS config variable or return a
    useful message if it is not set to instruct users how to set it.

    @param config METplusConfig object to read LOG_METPLUS from
    @returns path to log file or message if unset
    """
    log_file = config.getstr('config', 'LOG_METPLUS', '')
    return log_file if log_file else 'Set LOG_METPLUS to write logs to a file'


def log_terminal_includes_info(config):
    """!Check LOG_LEVEL_TERMINAL to see if it is set to a logging level that
    includes INFO output. Check [runtime] section if not found in [config]
    because the variable is moved at the end of the run.

    @param config METplusConfig object to query
    @returns True if log level is set to include INFO messages. False if not.
    """
    log_terminal_level = logging.getLevelName(
        config.getstr('config', 'LOG_LEVEL_TERMINAL',
                      config.getstr('runtime', 'LOG_LEVEL_TERMINAL'))
    )
    return log_terminal_level <= logging.INFO
