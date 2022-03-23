"""
Program Name: string_manip.py
Contact(s): George McCabe
Description: METplus utility to handle string manipulation
"""

import re
from csv import reader

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
