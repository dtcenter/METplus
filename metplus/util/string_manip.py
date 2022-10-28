"""
Program Name: string_manip.py
Contact(s): George McCabe
Description: METplus utility to handle string manipulation
"""

import re
from csv import reader

from .constants import VALID_COMPARISONS


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
