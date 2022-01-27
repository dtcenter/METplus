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

    # FIRST remove surrounding comma, and spaces, form the string.
    list_str = list_str.strip(';[] ').strip().strip(',').strip()

    # remove space around commas
    list_str = re.sub(r'\s*,\s*', ',', list_str)

    # option to not evaluate begin_end_incr
    if expand_begin_end_incr:
        list_str = _handle_begin_end_incr(list_str)

    # use csv reader to divide comma list while preserving strings with comma
    # convert the csv reader to a list and get first item
    # (which is the whole list)
    item_list = list(reader([list_str], escapechar='\\'))[0]

    #item_list = _fix_list(item_list)

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
    item_list = _fix_list_helper(item_list, '(')
    item_list = _fix_list_helper(item_list, '[')
    return item_list

def _fix_list_helper(item_list, type):
    if type == '(':
        close_regex = r"[^(]+\).*"
        open_regex = r".*\([^)]*$"
    elif type == '[':
        close_regex = r"[^\[]+\].*"
        open_regex = r".*\[[^\]]*$"
    elif type == '{':
        close_regex = r"[^\{]+\}.*"
        open_regex = r".*\{[^\}]*$"
    else:
        return item_list

    # combine items that had a comma between ()s or []s
    fixed_list = []
    incomplete_item = None
    found_close = False
    for index, item in enumerate(item_list):
        # if we have found an item that ends with ( but
        if incomplete_item:
            # check if item has ) before (
            match = re.match(close_regex, item)
            if match:
                # add rest of text, add it to output list,
                # then reset incomplete_item
                incomplete_item += ',' + item
                found_close = True
            else:
                # if not ) before (, add text and continue
                incomplete_item += ',' + item

        match = re.match(open_regex, item)
        # if we find ( without ) after it
        if match:
            # if we are still putting together an item,
            # append comma and new item
            if incomplete_item:
                if not found_close:
                    incomplete_item += ',' + item
            # if not, start new incomplete item to put together
            else:
                incomplete_item = item

            found_close = False
        # if we don't find ( without )
        else:
            # if we are putting together item, we can add to the
            # output list and reset incomplete_item
            if incomplete_item:
                if found_close:
                    fixed_list.append(incomplete_item)
                    incomplete_item = None
            # if we are not within brackets and we found no brackets,
            # add item to output list
            else:
                fixed_list.append(item)

    return fixed_list
