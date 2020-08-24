"""

Program Name: string_template_substitution.py
Contact(s): Julie Prestopnik, NCAR RAL DTC, jpresto@ucar.edu, George McCabe
Abstract: Supporting functions for parsing and creating filename templates
History Log:  Initial version for METPlus
Usage: Usually imported in other Python code for individual function calls
Parameters: Varies
Input Files: None
Output Files: None
Condition codes: Varies

"""

import re
import datetime
from dateutil.relativedelta import relativedelta

from . import time_util

TEMPLATE_IDENTIFIER_BEGIN = "{"
TEMPLATE_IDENTIFIER_END = "}"

FORMATTING_DELIMITER = "?"
FORMATTING_VALUE_DELIMITER = "="
FORMAT_STRING = "fmt"

SHIFT_STRING = "shift"
TRUNCATE_STRING = "truncate"

VALID_STRING = "valid"
LEAD_STRING = "lead"
INIT_STRING = "init"
DA_INIT_STRING = "da_init"
OFFSET_STRING = "offset"

LENGTH_DICT = {'Y': 4,
               'm': 2,
               'd': 2,
               'H': 2,
               'M': 2,
               'S': 2,
               'j': 3,
               'y': 2,
               'b': 3,
               }


def multiple_replace(replace_dict, text):
    """Helper function for do_string_sub. Replace in 'text' all occurrences of any key in the
    given dictionary by its corresponding value.  Returns the new string. """

    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, replace_dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: replace_dict[mo.string[mo.start():mo.end()]], text)

def get_tags(template):
    """!Parse template and pull out all wildcard characters (* or ?) and all
        tags, i.e. {init?fmt=%H}. Used to pull out information from a template that
        contains wildcards and add that information when filled out another template
        Returns a list of wildcards and tag names found, i.e. [ '*', 'init', 'lead']
    """
    i = 0
    template_len = len(template)
    tags = []
    # loop through template looking for wildcard characters or tags: {init?fmt=%H}
    while i < template_len:
        if template[i] == TEMPLATE_IDENTIFIER_BEGIN:
            end_i = template.find(TEMPLATE_IDENTIFIER_END, i)
            tag = template[i+1:end_i]
            identifier = tag.split('?')[0]
            tags.append(identifier)
            i = end_i
        elif template[i] == '*' or template[i] == '?':
            tags.append(template[i])

        i += 1
    return tags

def format_one_time_item(item, time_str, unit):
    """!Helper function for do_string_sub. Determine precision of time offset value and format
        Args:
         @param item format to substitute, i.e. 3M or H
         @param time_str time value that precision will be applied, i.e. 60
         @param unit currently being processed, i.e. M or H or S
        Returns: Padded value or empty string if unit is not found in item
    """
    count = item.count(unit)
    if count > 0:
        rest = ''
        # get precision from number (%3H)
        res = re.match(r"^\.*(\d+)"+unit+"(.*)", item)
        if res:
            padding = int(res.group(1))
            rest = res.group(2)
        else:
            padding = count
            res = re.match("^"+unit+"+(.*)", item)
            if res:
                rest = res.group(1)
                if unit != 's':
                    padding = max(2, count)

        # add formatted time
        return str(time_str).zfill(padding)+rest

    # return empty string if no match
    return ''

def format_hms(fmt, obj):
    """!Helper function for do_string_sub. For time offset values, get hour, minute, and
        second values to format as necessary
        Args:
            @param fmt format to substitute, i.e. %3H or %2M or %S
            @param obj time value in seconds to format, i.e. 3600
        Returns: Formatted time value
    """
    out_str = ''
    fmt_split = fmt.split('%')[1:]
    # split time into days, hours, mins, and secs
    # time should be relative to the next highest unit if higher units are specified
    # i.e. 90 minutes %M => 90, but %H%M => 0130
    days = obj // 86400
    hours = obj // 3600
    minutes = obj  // 60
    seconds = obj

    # if days are specified, change hours, minutes, and seconds to relative
    if True in ['d' in x for x in fmt_split]:
        hours = (obj % 86400) // 3600
        minutes = (obj % 3600) // 60
        seconds = (obj % 3600) % 60

    # if hours are specified, change minutes and seconds to relative
    if True in ['H' in x for x in fmt_split]:
        minutes = (obj % 3600) // 60
        seconds = (obj % 3600) % 60

    # if minutes are specified, change seconds to relative
    if True in ['M' in x for x in fmt_split]:
        seconds = (obj % 3600) % 60

    # parse format
    for item in fmt_split:
        out_str += format_one_time_item(item, hours, 'H')
        out_str += format_one_time_item(item, minutes, 'M')
        out_str += format_one_time_item(item, seconds, 'S')
        out_str += format_one_time_item(item, obj, 's')
        out_str += format_one_time_item(item, days, 'd')

    return out_str

def set_output_dict_from_time_info(time_dict, output_dict, key):
    """!Create datetime object from time data,
        get month and day from julian date if applicable"""
    # if 2 digit year is set, get full year
    if time_dict['Y'] == -1 and time_dict['y'] != -1:
        time_dict['Y'] = int(datetime.datetime.strptime(str(time_dict['y']), '%y').strftime('%Y'))

    # if month as 3 letter string is set, get month number
    if time_dict['m'] == -1 and time_dict['b'] != -1:
        time_dict['m'] = int(datetime.datetime.strptime(str(time_dict['b']), '%b').strftime('%m'))

    if time_dict['Y'] != -1 and time_dict['j'] != -1:
        date_t = datetime.datetime.strptime(str(time_dict['Y'])+'_'+str(time_dict['j']),
                                            '%Y_%j')
        time_dict['m'] = int(date_t.strftime('%m'))
        time_dict['d'] = int(date_t.strftime('%d'))

    if time_dict['Y'] != -1 and time_dict['m'] != -1 and time_dict['d'] != -1:
        output_dict[key] = datetime.datetime(time_dict['Y'],
                                             time_dict['m'],
                                             time_dict['d'],
                                             time_dict['H'],
                                             time_dict['M'])

def add_to_dict(match, match_dict, filepath, new_len):
    """!Add extracted information to match dictionary
        Args:
            @param match key for match dictionary containing tag name and units
                   i.e. 'init+H' or 'lead+S'
            @param match_dict dictionary of info extracted from filename
            @param filepath rest of filename string to be parsed
            @param new_len length of filepath to extract
        Returns: True if info was added to dictionary or it already exists and
                 matched newly parsed info, False if info could not be extracted or
                 if info differed from info already in match dictionary
    """
    # if the time info being extracted is not a number, do not add to dict
    if not filepath[0:new_len].isdigit():
        return False

    # if match is not already in match dictionary, add it
    # if it exists and is different than what is attempted to be stored
    #  return False
    if match not in match_dict.keys():
        match_dict[match] = filepath[0:new_len]
    elif match_dict[match].zfill(new_len) != filepath[0:new_len]:
        return False

    # item was added or already existed in match dictionary
    return True

def get_seconds_from_template(split_string, element_name, kwargs):
    """!Get seconds value from tag that contains a shift or truncate item
         Args:
             @param split_string list of key/value from string sub tag to evalute, i.e. shift=-1H
             @param element_name information to extract, i.e. shift or truncate
             @returns integer number of seconds that correspond to the item, i.e. -3600
     """
    # if shift is set, get that value before handling formatting
    for split_item in split_string:
        if split_item.startswith(element_name):

            shift_split_string = split_item.split(FORMATTING_VALUE_DELIMITER)

            if len(shift_split_string) != 2:
                return None

            valid_time = kwargs.get('valid',
                                    kwargs.get('now',
                                               None))

            seconds = shift_split_string[1]
            return int(time_util.get_seconds_from_string(seconds,
                                                         default_unit='S',
                                                         valid_time=valid_time))

    # if not found, return 0
    return 0

def round_time_down(obj, truncate_seconds):
    """!If template value needs to be truncated, round the value down
        to the given truncate interval"""
    if truncate_seconds == 0:
        return obj

    trunc = truncate_seconds
    seconds = (obj.replace(tzinfo=None) - obj.min).seconds
    rounding = seconds // trunc * trunc
    new_obj = obj + datetime.timedelta(0, rounding-seconds,
                                       -obj.microsecond)
    return new_obj

def handle_format_delimiter(split_string, idx, shift_seconds, truncate_seconds, kwargs):
    """!Check for formatting/length request by splitting on
        FORMATTING_VALUE_DELIMITER
        split_string[1]
        Args:
            @param split_string holds the formatting/length
              information (e.g. "fmt=%Y%m%d", "len=3")
            @param idx index in split_string of the format item
        Returns: Formatted string
    """
    format_split_string = \
        split_string[idx].split(FORMATTING_VALUE_DELIMITER)

    # Check for requested FORMAT_STRING
    # format_split_string[0] holds the formatting/length
    # value delimiter (e.g. "fmt", "len")
    if format_split_string[0] == FORMAT_STRING:
        obj = kwargs.get(split_string[0], None)

        fmt = format_split_string[idx]
        # if input is datetime object, format appropriately
        if isinstance(obj, datetime.datetime):
            # shift date time if set
            obj = obj + datetime.timedelta(seconds=shift_seconds)

            # truncate date time if set
            obj = round_time_down(obj, truncate_seconds)
            return obj.strftime(fmt)

        # if input is relativedelta
        if isinstance(obj, relativedelta):
            seconds = time_util.ti_get_seconds_from_relativedelta(obj)
            if seconds is None:
                raise TypeError('Year and month intervals not yet supported in string substitution')

            return format_hms(fmt, seconds)

        # if input is integer, format with H, M, and S
        if isinstance(obj, int):
            obj += shift_seconds
            return format_hms(fmt, obj)

        # if string, format if possible
        if isinstance(obj, str):
            return '{}'.format(obj)

        raise TypeError('Could not format item {} with format {} in {}'
                        .format(obj, fmt, split_string))

    return None

def do_string_sub(tmpl, skip_missing_tags=False, **kwargs):
    """
    log - log object
    tmpl_str - template string to populate
    kwargs - dictionary containing values for each template key

    This class provides functionality for substituting values for
    string templates.

    Possible keys for vals:
       init - datetime object
       valid - datetime object
       lead - must be in seconds
       level - must be in seconds
       model - the name of the model
       domain - the domain number (01, 02, etc.) read in as a string
       cycle - the cycle hour in HH format (00, 03, 06, etc.)
       offset_hour - the offset hour in HH format to add
                     to the init + cycl time:
                      (YYYYMMDD + hh) + offset
                     Indicate a negative offset by using a '-' sign
                     in the
       date - datetime object
       region - the two-character (upper or lower case) region/basin designation
       cyclone - a two-digit annual cyclone number (if ATCF_by_pairs) or
                 four-digit cyclone number (leading zeros)
       misc - any string

    Populates the specified template with information from the
           kwargs dictionary.  The template structure is comprised of
           a fixed string populated with template place-holders inside curly
           braces, for example {tmpl_str}.  The tmpl_str must be present as
           a key in the kwargs dictionary, and the value will replace the
           {tmpl_str} in the returned string.

            In some cases, the template keys can have parameters containing
            formatting information. The format of the template in this case
            is {tmpl_str?parm=val}.  The supported parameters are:

            init, valid:
                fmt - specifies a strftime format for the date/time
                      e.g. %Y%m%d%H%M%S, %Y%m%d%H

              lead, level:
                fmt -  specifies an amount of time in [H]HH[MMSS] format
                       e.g. %HH, %HHH, %HH%MMSS, %HHH%MMSS

              cycle, negative_offset, positive_offset:
                fmt - specifies the cycle and offset hours in HH format. H and
                      HHH format are supported, to anticipate any changes
                      in prepbufr data.

              The following were created to support processing of
              tropical cyclone data:
              cyclone:
                fmt - specifies the annual cyclone number as a string.

              region:
                fmt - a string that specifies the region/basin of cyclone.
                      For ATCF_by_pairs formatted data, this is a 2-character
                      designation:
                      AL|WP|CP|EP|SH|IO|LS lower case designations are
                      observed in filenames.
              date:
                fmt - a string representation of the date format for a
                      subdirectory in which track data resides, or the
                      string representation of the date format in a file.
                      Expected formats: YYYY, YYYYMM, YYYYMMDD, and YYYYMMDDhh
              misc:
                fmt -a string that represents any other miscellaneous feature
                     of the track data, such as experiment name or some other descriptor
    """

    # The . matches any single character except newline, and the
    # following + matches 1 or more occurrence of preceding expression.
    # The ? after the .+ makes it a lazy match so that it stops
    # after the first "}" instead of continuing to match as many
    # characters as possible

    # findall searches through the string and finds all non-overlapping
    # matches and returns the group
    # match_list is a list with the contents being the data between the
    # curly braces
    match_list = re.findall(r'\{(.+?)\}', tmpl)

    # finditer gets the start and end indices
    # Iterate over each match to get the starting and ending indices
    matches = re.finditer(r'\{(.+?)\}', tmpl)
    match_start_end_list = []
    for match in matches:
        match_start_end_list.append((match.start(), match.end()))

    if len(match_list) == 0:
        return tmpl

    if len(match_list) != len(match_start_end_list):
        # Log and exit
        raise TypeError("match_list and match_start_end_list should " +
                        "have the same length for template: " +
                        tmpl)

    return find_and_replace_tags_in_template(match_list, tmpl, kwargs, skip_missing_tags)

def find_and_replace_tags_in_template(match_list, tmpl, kwargs, skip_missing_tags=False):
    """! Loop through tags from template and replace them with the correct time values
         @param match_list list of tags to process
         @param template filename template to substitute values into
         @param kwargs all

    """
    # A dictionary that will contain the string to replace (key)
    # and the string to replace it with (value)
    replacement_dict = {}
    # Search for the FORMATTING_DELIMITER within the first string
    for match in match_list:

        string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match + \
                            TEMPLATE_IDENTIFIER_END
        split_string = match.split(FORMATTING_DELIMITER)

        # valid, init, lead, etc.
        # print split_string[0]
        # value e.g. 2016012606, 3

        # split_string[0] holds the key (e.g. "init", "valid", etc)
        if split_string[0] not in kwargs.keys():
            # if skip_missing_tags is True, leave template tag if key was not found
            if skip_missing_tags:
                continue

            # otherwise log and exit
            raise TypeError("The key " + split_string[0] +
                            " was not passed to do_string_sub " +
                            " for template: " + tmpl)

        # if shift is set, get that value before handling formatting
        shift_seconds = get_seconds_from_template(split_string, SHIFT_STRING, kwargs)

        # if truncate is set, get that value before handling formatting
        truncate_seconds = get_seconds_from_template(split_string, TRUNCATE_STRING, kwargs)

        # format times appropriately and add to replacement_dict
        formatted = False
        for idx, split_item in enumerate(split_string):
            if split_item.startswith(FORMAT_STRING):
                replacement_dict[string_to_replace] = \
                    handle_format_delimiter(split_string,
                                            idx,
                                            shift_seconds,
                                            truncate_seconds,
                                            kwargs)
                formatted = True

        # No formatting or length is requested
        if not formatted:
            # Add back the template identifiers to the matched
            # string to replace and add the key, value pair to the
            # dictionary
            value = kwargs.get(split_string[0], None)
            if isinstance(value, int):
                value = f"{value}S"
            replacement_dict[string_to_replace] = value

    # Replace regex with properly formatted information
    return multiple_replace(replacement_dict, tmpl)

def parse_template(template, filepath, logger=None):
    """!Extract time information from path using the filename template
         Args:
             @param template filename template to use to extract time information
             @param filepath path to examine
             @returns time_info dictionary with time information if successful, None if not"""

    match_dict, valid_shift = populate_match_dict(template, filepath, logger)
    if match_dict is None:
        return None

    # combine common items and get datetime
    output_dict = populate_output_dict(match_dict, valid_shift)

    if not output_dict:
        if logger:
            logger.debug(f"Could not extract enough time information from {filepath}")
        else:
            print(f"DEBUG: Could not extract enough time information from {filepath}")

        return None

    # fill in the rest of the time info dictionary items with ti_calculate
    time_info = time_util.ti_calculate(output_dict)

    return time_info

def populate_match_dict(template, filepath, logger=None):
    """! Use template to extract time information from filepath, add each value to a dictionary.
         Populates a dictionary with keys that contain tag name + time type, i.e. init+Y,
         valid+M, or lead+S, with string values containing the number extracted from the filepath.
         Also determines the shift amount  for valid time if it was found, i.e.
         {valid?fmt=%Y%m%d?shift=-30}. Valid shift will be 0 if no shift.
         Note: valid time values will not have the shift applied.
         Args:
             @param template filename template to use to find time information, i.e.
                 file.{valid?fmt=%Y%m%d}.ext
             @param filepath path to examine, i.e. file.20190201.ext
             @returns tuple of match dictionary and valid shift value if success, i.e.
                 ({'init+Y': '2019'}, -30)
              Returns (None, None) if could not extract time info
    """
    # get the text before any tags, between tags, and after any tags
    match = re.match(r'([^{]*)({.*})([^}]*)', template)
    if not match:
        # if there were no tags, we can't extract time info, so return None, None
        if logger:
            logger.debug("No tags found (1)")
        return None, None

    # tags to process, including text in between tags
    all_tags = match.group(2)

    # check if text before and after tags matches template and strip off from file path
    filepath = check_pre_text(filepath, match.group(1), logger)
    filepath = check_post_text(filepath, match.group(3), logger)
    if filepath is None:
        return None, None

    return process_match_tags(all_tags, filepath, logger)

def process_match_tags(all_tags, filepath, logger):
    """! Loop through tags and process each.
         @param all_tags string containing all tags with non-tag text removed from
         beginning and end.
         @param filepath path to process
         @param logger optional logger to output error information
         @returns tuple containing dictionary with match information and valid shift
             value if applicable, or (None, None) could not parse information
    """
    match_dict = {}
    valid_shift = 0

    match_tags = re.findall(r'{(.*?)}([^{]*)', all_tags)
    if not match_tags:
        if logger:
            logger.debug("No tags found (2)")
        return None, None

    for match_tag in match_tags:
        tag_content, extra_text = match_tag
        fmt_len, valid_shift = get_format_and_shift(tag_content,
                                                    filepath,
                                                    match_dict,
                                                    valid_shift)

        # if length of formatted text couldn't be determined
        if fmt_len is None:
            if logger:
                logger.debug("Could not determine length of formatted text")
            return None, None

        # if length of formatted text is longer than remaining text in file path
        if fmt_len > len(filepath):
            if logger:
                logger.debug("Length of formatted text is longer than remaining text in file path")
            return None, None

        # strip off length of formatted text from filepath
        filepath = filepath[fmt_len:]

        # check that any extra text matches the filepath
        filepath = check_pre_text(filepath, extra_text, logger)
        if filepath is None:
            return None, None

    return match_dict, valid_shift

def check_pre_text(filepath, pre_text, logger=None):
    """! Check if there is an text before all tags and if they match the template.
         Strip off text from filepath.
         @param filepath path to check
         @param pre_text text before any tags
         @param post_text text after all tags
         @returns file path with pre text removed or None if text does not match template"""

    if filepath is None:
        return None

    # if length of extra text is longer than remaining text in file path
    if len(pre_text) > len(filepath):
        # too much logging output comes from this - if verbose is added, this is a good candidate
#        if logger:
#            logger.debug("Length of pre text is longer than "
#                         "remaining text in file path")
        return None

    # if there is text before any tags, check that the text in the template matches the file path
    if pre_text:
        if pre_text != filepath[0:len(pre_text)]:
            # too much logging output comes from this - if verbose is added, this is a good candidate
#            if logger:
#                logger.debug("Text at beginning of filepath does not match template")
            return None

        # strip off pre text from file path
        filepath = filepath[len(pre_text):]

    return filepath

def check_post_text(filepath, post_text, logger=None):
    """! Check if there is an text after all tags and if they match the template.
         Strip off text from filepath.
         @param filepath path to check
         @param post_text text after all tags
         @returns file path with post text removed or None if text does not match template"""

    if filepath is None:
        return None

    # do the same for text at the end of all tags
    if post_text:
        if post_text != filepath[-len(post_text):]:
            # too much logging output comes from this - if verbose is added, this is a good candidate
#            if logger:
#                logger.debug("Text at end of filepath does not match template")
            return None

        # strip off post text from file path
        filepath = filepath[0:-len(post_text)]

    return filepath

def get_format_and_shift(tag_content, filepath, match_dict, valid_shift):
    """! Extract format and shift information from tag. Raises TypeError if shift keyword
         is applied to a tag other than valid or if 2 different shift values are found
         Args:
             @param tag_content text inside a tag, i.e. valid?fmt=%Y%m%d?shift=30
             @param filepath rest of filepath to process, i.e. 20190201.ext
             @param match_dict dictionary to add time info
             @param valid_shift current numbers of seconds to shift valid time
             @returns tuple of the length of the formatted time info (i.e. 8 for %Y%m%d) and
                 valid shift value
    """
    fmt_len = 0

    # identifier is time type, i.e. valid, init, lead, etc.
    # sections is a list of key=values, i.e. fmt=%Y or shift=30
    identifier, *sections = tag_content.split('?')

    for section in sections:
        element_name, element_value = section.split('=')
        if element_name == FORMAT_STRING:
            fmt_len = get_fmt_info(element_value, filepath,
                                   match_dict, identifier)
            if fmt_len is None:
                return None, None
            # extract string that corresponds to format
        elif element_name == SHIFT_STRING:
            # don't allow shift on any identifier except valid
            if identifier != VALID_STRING:
                msg = 'Cannot apply a shift to template ' + \
                      'item {} when processing inexact '.format(identifier) + \
                      'times. Only {} is accepted'.format(VALID_STRING)
                raise TypeError(msg)

            # convert time string (i.e. 3600S, 60M, 1H, etc.) to seconds
            shift = int(time_util.get_seconds_from_string(element_value, default_unit='S'))

            # if shift has been set before (other than 0) and
            # this shift differs, raise exception
            if valid_shift not in (0, shift):
                raise TypeError('Found multiple shifts for valid time' +
                                '{} differs from {}'
                                .format(shift, valid_shift))

            # save valid shift to apply to valid time later
            valid_shift = shift

    return fmt_len, valid_shift

def get_fmt_info(fmt, filepath, match_dict, identifier):
    """!Helper function for parse_template. Reads format information from tag and
        populates dictionary with extracted values.
        Args:
            @param fmt formatting values from template tag, i.e. %Y%m%d
            @param filepath rest of text from filename that can be parsed
            @param match_dict dictionary of extracted information. Key is made up
                   of the identifier and the format tag, i.e. init_H or valid_M.
                   Value is the extracted information, i.e. 19870201
            @param identifier tag name, i.e. 'init' or 'lead'
            @returns Number of characters processed from the filename if success,
                 -1 if failed to parse all format items in template tag"""
    length = 0
    # find all items that start with %, i.e. %Y or %3H, %10S, or %.2d
    # group 1 is optional number, i.e. 3 in %3H or 2 in %.2d
    # group 2 is letters with extra characters at the end,
    #  i.e. HH in %HH or S: in %10S:
    match_list = re.findall(r'%\.?(\d*)([^%]+)', fmt)
    for match in match_list:
        # letter identifier for time - may be duplicate letters
        # i.e. H in %3H or HHH in %HHH or H: in %H: (can have trailing characters)
        time_letter = match[1][0]

        # optional number for specifying zero padding, i.e. 3 in %3H
        time_number = match[0]

        # if first letter is not found in time identifier length dictionary
        if time_letter not in LENGTH_DICT.keys():
            return None

        # get length of time type
        new_len = LENGTH_DICT.get(time_letter)

        # find how many times the first letter is found in the time letters
        # i.e. HHH: should be 3
        match_len = re.match(r'([' + time_letter + ']+)(.*)', match[1])
        if not match_len:
            return None

        # if there are multiple letters, update length if it is more than
        # the standard length for that time type
        time_letter_count = len(match_len.group(1))
        extra_len = len(match_len.group(2))
        if time_letter_count > 1:
            # if multiple letters and a number is specifed, i.e. 3HH, then fail
            if time_number:
                return None

            new_len = time_letter_count

        # if number was provided and it is different than the
        # standard length use that number instead
        elif time_number and int(time_number) != new_len:
            new_len = int(time_number)

        # if lead or level hours are found
        if (match[1] == 'H' and
                (identifier in ('lead', 'level'))):
            # look forward until non-digit is found
            new_len = 0
            while new_len < len(filepath) and filepath[new_len].isdigit():
                new_len += 1

        # add the length specified plus any additional characters
        length += new_len + extra_len

        if not add_to_dict(identifier + '+' + time_letter,
                           match_dict,
                           filepath,
                           new_len):
            return None

        filepath = filepath[new_len+extra_len:]

    return length

def populate_output_dict(match_dict, valid_shift):
    """! Get all time values in match dictionary to add to the output dictionary
          Args:
              @param match_dict dictionary containing matches found with keys named
              @param valid_shift number of seconds to shift the valid time
              @returns output dictionary containing the extracted time information
    """
    output_dict = {}

    for time_type in [VALID_STRING, INIT_STRING, DA_INIT_STRING]:
        if time_type == VALID_STRING:
            time_shift = valid_shift
        else:
            time_shift = 0

        add_date_matches_to_output_dict(match_dict, output_dict, time_type, time_shift)

    add_lead_matches_to_output_dict(match_dict, output_dict)
    add_offset_matches_to_output_dict(match_dict, output_dict)

    extracted_time_info = False
    for time_type in [VALID_STRING, INIT_STRING, DA_INIT_STRING]:
        if time_type in output_dict:
            extracted_time_info = True

    if extracted_time_info:
        return output_dict

    return None

def add_date_matches_to_output_dict(match_dict, output_dict, time_type, valid_shift=0):
    """! Look for time values in match dictionary add combine the values to add to the
         output dictionary. Apply shift value for valid time only.
         Args:
             @param match_dict dictionary containing matches found with keys named
                 'valid+Y','init+m', 'da_init+d', etc. and values are the number of
                  years, months, hours, etc.
             @param output_dict time dictionary to set valid, init, or da_init
             @param time_type type of time item to process. Valid options are:
                 VALID_STRING, INIT_STRING, or DA_INIT_STRING
             @param valid_shift amount of time (in seconds) to shift the valid time
                 Not applicable for any time type besides valid
    """
    time_values = {
        'Y': -1,
        'y': -1,
        'm': -1,
        'd': -1,
        'j': -1,
        'H': 0,
        'M': 0,
        'b': -1,
    }

    for key, value in match_dict.items():
        if key.startswith(time_type):
            time_values[key.split('+')[1]] = int(value)

    set_output_dict_from_time_info(time_values, output_dict, time_type)

    # shift valid time if applicable
    if valid_shift:
        output_dict[time_type] -= datetime.timedelta(seconds=valid_shift)

def add_lead_matches_to_output_dict(match_dict, output_dict):
    """! Look for forecast lead values in match dictionary add combine the values
         to add to the output dictionary
         Args:
             @param match_dict dictionary containing matches found with keys named
                 'lead+H','lead+M', or 'lead+S' and values are the number of hours,
                  minutes, or seconds in the forecast lead
             @param output_dict time dictionary to set lead
    """
    lead = {
        'H': 0,
        'M': 0,
        'S': 0,
    }

    for key, value in match_dict.items():
        if key.startswith(LEAD_STRING):
            lead[key.split('+')[1]] = int(value)

    lead_seconds = lead['H'] * 3600 + lead['M'] * 60 + lead['S']
    output_dict['lead'] = lead_seconds

def add_offset_matches_to_output_dict(match_dict, output_dict):
    """! Look for offset value in match dictionary and add the value to the
         output dictionary
         Args:
             @param match_dict dictionary containing matches found with keys named
                 'offset+H' (only hours are supported for offset) and value is number
                 of hours in the offset
             @param output_dict time dictionary to set offset_hours
    """
    offset = 0

    for key, value in match_dict.items():
        if key.startswith(OFFSET_STRING):
            offset = int(value)

    output_dict['offset_hours'] = offset
