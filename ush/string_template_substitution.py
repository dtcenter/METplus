#!/usr/bin/env python

"""

Program Name: string_template_substitution.py
Contact(s): Julie Prestopnik, NCAR RAL DTC, jpresto@ucar.edu
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
import time
import calendar
import math
import sys

import time_util

TEMPLATE_IDENTIFIER_BEGIN = "{"
TEMPLATE_IDENTIFIER_END = "}"

FORMATTING_DELIMITER = "?"
FORMATTING_VALUE_DELIMITER = "="
FORMAT_STRING = "fmt"

SHIFT_STRING = "shift"
TRUNCATE_STRING = "truncate"

# These three were added in response to the tropical cyclone use case
DATE_STRING = "date"
REGION_STRING = "region"
CYCLONE_STRING = "cyclone"
MISC_STRING = "misc"

VALID_STRING = "valid"
LEAD_STRING = "lead"
INIT_STRING = "init"
DA_INIT_STRING = "da_init"
OFFSET_STRING = "offset"

GLOBAL_LOGGER = None

length_dict = { '%Y': 4,
                '%m' : 2,
                '%d' : 2,
                '%H' : 2,
                '%M' : 2,
                '%S' : 2,
                '%j' : 3}

def multiple_replace(dict, text):
    """ Replace in 'text' all occurrences of any key in the
    given dictionary by its corresponding value.  Returns the new string. """

    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    j = "".join(map(re.escape, dict.keys()))
    # print "regex from dictionary keys: {}".format(j)

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)


class StringSub:
    """
    log - log object
    tmpl_str - template string to populate
    kwargs - dictionary containing values for each template key

    This class provides functionality for substituting values for
    string templates.

    Possible keys for vals:
       init - must be in YYYYmmddHH[MMSS] format
       valid - must be in YYYYmmddHH[MMSS] format
       lead - must be in HH[MMSS] format
       level - must be in HH[MMSS] format
       model - the name of the model
       domain - the domain number (01, 02, etc.) read in as a string
       cycle - the cycle hour in HH format (00, 03, 06, etc.)
       offset_hour - the offset hour in HH format to add
                     to the init + cycl time:
                      (YYYYMMDD + hh) + offset
                     Indicate a negative offset by using a '-' sign
                     in the
       date - the YYYYMM date
       region - the two-character (upper or lower case) region/basin designation
       cyclone - a two-digit annual cyclone number (if ATCF_by_pairs) or four-digit cyclone number (leading zeros)
       misc - any string



    See the description of doStringSub for further details.
    """

    def __init__(self, log, tmpl, **kwargs):

        self.logger = log
        self.tmpl = tmpl
        self.kwargs = kwargs
        self.shift_seconds = 0
        self.truncate_seconds = 0

        if self.kwargs is not None:
            for key, value in kwargs.iteritems():
                # print("%s == %s" % (key, value))
                setattr(self, key, value)


    def getSecondsFromTemplate(self, split_item):
        shift_split_string = \
            split_item.split(FORMATTING_VALUE_DELIMITER)

        if len(shift_split_string) != 2:
            return

        seconds = shift_split_string[1]
        return int(seconds)


    def roundTimeDown(self, obj):
        if self.truncate_seconds == 0:
            return obj

        trunc = self.truncate_seconds
        seconds = (obj.replace(tzinfo=None) - obj.min).seconds
        rounding = seconds // trunc * trunc
        new_obj  = obj + datetime.timedelta(0, rounding-seconds,
                                            -obj.microsecond)
        return new_obj


    def format_one_time_item(self, item, t, c):
        count = item.count(c)
        if count > 0:
            rest = ''
            # get precision from number (%3H)
            res = re.match("^\.*(\d+)"+c+"(.*)", item)
            if res:
                padding = int(res.group(1))
                rest = res.group(2)
            else:
                padding = count
                res = re.match("^"+c+"+(.*)", item)
                if rest:
                    rest = res.group(1)

            # add formatted time
            return str(t).zfill(padding)+rest

        # return empty string if no match
        return ''


    def format_hms(self, fmt, obj):
        out_str = ''
        # split time into hours, mins, and secs
        hours = obj / 3600
        minutes = (obj % 3600) / 60
        seconds = (obj % 3600) % 60

        # parse format
        fmt_split = fmt.split('%')
        for item in fmt_split:
            out_str += self.format_one_time_item(item, hours, 'H')
            out_str += self.format_one_time_item(item, minutes, 'M')
            out_str += self.format_one_time_item(item, seconds, 'S')
            out_str += self.format_one_time_item(item, obj, 's')

        return out_str


    def handleFormatDelimiter(self, split_string, idx, match, replacement_dict):
        # TODO: how to handle %M vs. %H%M, all minutes if just M?
        # Check for formatting/length request by splitting on
        # FORMATTING_VALUE_DELIMITER
        # split_string[1] holds the formatting/length
        # information (e.g. "fmt=%Y%m%d", "len=3")
        format_split_string = \
            split_string[idx].split(FORMATTING_VALUE_DELIMITER)

        # Add back the template identifiers to the
        # matched string to replace and add the
        # key, value pair to the dictionary
        string_to_replace = TEMPLATE_IDENTIFIER_BEGIN \
                            + match + \
                            TEMPLATE_IDENTIFIER_END

        # Check for requested FORMAT_STRING
        # format_split_string[0] holds the formatting/length
        # value delimiter (e.g. "fmt", "len")
        if format_split_string[0] == FORMAT_STRING:
            obj = self.kwargs.get(split_string[0], None)

            fmt = format_split_string[idx]
            # if input is datetime object, format appropriately
            if isinstance(obj, datetime.datetime):
                # shift date time if set
                obj = obj + datetime.timedelta(seconds=self.shift_seconds)

                # truncate date time if set
                obj = self.roundTimeDown(obj)

                return obj.strftime(fmt)
            # if input is integer, format with H, M, and S
            elif isinstance(obj, int):
                obj += self.shift_seconds
                return self.format_hms(fmt, obj)
            # if string, format if possible
            elif isinstance(obj, str) and fmt == '%s':
                return '{}'.format(obj)
            else:
                self.logger.error('Could not format item {} with format {}'.format(obj, fmt))
                exit(1)


    def doStringSub(self):

        """Populates the specified template with information from the
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

        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # The . matches any single character except newline, and the
        # following + matches 1 or more occurrence of preceding expression.
        # The ? after the .+ makes it a lazy match so that it stops
        # after the first "}" instead of continuing to match as many
        # characters as possible

        # findall searches through the string and finds all non-overlapping
        # matches and returns the group
        # match_list is a list with the contents being the data between the
        # curly braces
        match_list = re.findall('\{(.+?)\}', self.tmpl)

        # finditer gets the start and end indices
        # Iterate over each match to get the starting and ending indices
        matches = re.finditer('\{(.+?)\}', self.tmpl)
        match_start_end_list = []
        for match in matches:
            match_start_end_list.append((match.start(), match.end()))

        if len(match_list) == 0:
            return self.tmpl

        if len(match_list) != len(match_start_end_list):
            # Log and exit
            self.logger.error("match_list and match_start_end_list should " +
                              "have the same length for template: " +
                              self.tmpl)
            exit(0)

        # A dictionary that will contain the string to replace (key)
        # and the string to replace it with (value)
        replacement_dict = {}

        # Search for the FORMATTING_DELIMITER within the first string
        for index, match in enumerate(match_list):

            string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match + \
                                TEMPLATE_IDENTIFIER_END
            split_string = match.split(FORMATTING_DELIMITER)

            # valid, init, lead, etc.
            # print split_string[0]
            # value e.g. 2016012606, 3
            # print (self.kwargs).get(split_string[0], None)

            # split_string[0] holds the key (e.g. "init", "valid", etc)
            if split_string[0] not in self.kwargs.keys():
                # Log and continue
                self.logger.error("The key " + split_string[0] +
                                  " was not passed to StringSub " +
                                  " for template: " + self.tmpl)
                exit(1)

            # if shift is set, get that value before handling formatting
            for split_item in split_string:
                if split_item.startswith(SHIFT_STRING):
                    self.shift_seconds = self.getSecondsFromTemplate(split_item)

            # if truncate is set, get that value before handling formatting
            for split_item in split_string:
                if split_item.startswith(TRUNCATE_STRING):
                    self.truncate_seconds = self.getSecondsFromTemplate(split_item)

            # format times appropriately and add to replacement_dict
            formatted = False
            for idx, split_item in enumerate(split_string):
                if split_item.startswith(FORMAT_STRING):
                    replacement_dict[string_to_replace] = \
                        self.handleFormatDelimiter(split_string, idx,
                                                   match, replacement_dict)
                    formatted = True

            # No formatting or length is requested
            if not formatted:
                # Add back the template identifiers to the matched
                # string to replace and add the key, value pair to the
                # dictionary
                replacement_dict[string_to_replace] = \
                    self.kwargs.get(split_string[0], None)

            # reset shift seconds so it doesn't apply to next match
            self.shift_seconds = 0
            self.truncate_seconds = 0

        # Replace regex with properly formatted information
        self.tmpl = multiple_replace(replacement_dict, self.tmpl)
        return self.tmpl


    def create_cyclone_regex(self):
        """! Create the regex that describes the tropical cyclone string.
             Similar logic to doStringSub() except
             replace the date, region, and cyclone with the appropriate regex.

        """
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # The . matches any single character except newline, and the
        # following + matches 1 or more occurrence of preceding expression.
        # The ? after the .+ makes it a lazy match so that it stops
        # after the first "}" instead of continuing to match as many
        # characters as possible

        # findall searches through the string and finds all non-overlapping
        # matches and returns the group
        # match_list is a list with the contents being the data between the
        # curly braces
        match_list = re.findall('\{(.+?)\}', self.tmpl)

        # finditer gets the start and end indices
        # Iterate over each match to get the starting and ending indices
        matches = re.finditer('\{(.+?)\}', self.tmpl)
        match_start_end_list = []
        for match in matches:
            match_start_end_list.append((match.start(), match.end()))

        if match_list == 0:
            # Log and exit
            self.logger.error("ERROR |  [" + cur_filename + ":" +
                              cur_function + "] | " +
                              "No matches found for template: " +
                              self.tmpl)
            exit(0)
        elif len(match_list) != len(match_start_end_list):
            # Log and exit
            self.logger.error("ERROR |  [" + cur_filename + ":" +
                              cur_function + "] | " +
                              "match_list and match_start_end_list should " +
                              "have the same length for template: " +
                              self.tmpl)
            exit(0)
        else:
            # No times to compute, create the regex expressions that describe
            # the date (YYYY, YYYYMM, YYYYMMMDD, or YYYYMMDDhh),  region,
            # cyclone, and misc portions of the
            # filename template.
            if (
                    DATE_STRING in self.kwargs or
                    (DATE_STRING in self.kwargs and INIT_STRING in self.kwargs)

            ):
                self.kwargs[DATE_STRING] = self.date
            # Date and cyclone only
            elif (
                    DATE_STRING in self.kwargs and
                    CYCLONE_STRING in self.kwargs):
                self.kwargs[DATE_STRING] = self.date
                self.kwargs[CYCLONE_STRING] = self.cyclone

            # Date and region only
            elif (
                    DATE_STRING in self.kwargs and
                    REGION_STRING in self.kwargs
            ):

                self.kwargs[DATE_STRING] = self.date
                self.kwargs[REGION_STRING] = self.region

            # Date, region, and cyclone
            elif (
                    DATE_STRING in self.kwargs and
                    REGION_STRING in self.kwargs and
                    CYCLONE_STRING in self.kwargs
            ):
                self.kwargs[DATE_STRING] = self.date
                self.kwargs[REGION_STRING] = self.region
                self.kwargs[CYCLONE_STRING] = self.cyclone

            # Finally, check for misc string, which can occur with any
            # combination of the above
            if MISC_STRING in self.kwargs:
                self.kwargs[MISC_STRING] = self.misc

            # A dictionary that will contain the string to replace (key)
            # and the string to replace it with (value)
            replacement_dict = {}

            # Search for the FORMATTING_DELIMITER within the first string
            for index, match in enumerate(match_list):
                split_string = match.split(FORMATTING_DELIMITER)

                # valid, init, lead, etc.
                # print split_string[0]
                # value e.g. 2016012606, 3
                # print (self.kwargs).get(split_string[0], None)

                # Formatting is requested or length is requested
                if len(split_string) == 2:

                    # split_string[0] holds the key (e.g. "cyclone",
                    # "region", etc)
                    if split_string[0] not in self.kwargs.keys():
                        # Log and continue
                        self.logger.error("ERROR |  [" + cur_filename +
                                          ":" + cur_function + "] | " +
                                          "The key " + split_string[0] +
                                          " does not exist for template: " +
                                          self.tmpl)

                    # Key is in the dictionary
                    else:
                        # Check for formatting/length request by splitting on
                        # FORMATTING_VALUE_DELIMITER
                        # split_string[1] holds the formatting/length
                        # information (e.g. "fmt=%Y%m%d", "len=3")
                        format_split_string = \
                            split_string[1].split(FORMATTING_VALUE_DELIMITER)
                        # Check for requested FORMAT_STRING
                        # format_split_string[0] holds the formatting/length
                        # value delimiter (e.g. "fmt", "len")
                        if format_split_string[0] == FORMAT_STRING:
                            if split_string[0] == DATE_STRING:
                                value = "([0-9]{4,10})"
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN\
                                                    + match +\
                                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == REGION_STRING:
                                value = "([a-zA-Z]{2})"
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN\
                                                    + match +\
                                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == CYCLONE_STRING:
                                value = "([0-9]{2,3})"
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN \
                                                    + match + \
                                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == MISC_STRING:
                                value = "([a-zA-Z0-9-_.]+)"
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN\
                                                    + match + \
                                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value

                # No formatting or length is requested
                elif len(split_string) == 1:

                    # Add back the template identifiers to the matched
                    # string to replace and add the key, value pair to the
                    # dictionary
                    string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match + \
                                        TEMPLATE_IDENTIFIER_END
                    replacement_dict[string_to_replace] = \
                        self.kwargs.get(split_string[0], None)

            # Replace regex with properly formatted information
            temp_str = multiple_replace(replacement_dict, self.tmpl)
            self.tmpl = temp_str
            return self.tmpl
    

class StringExtract:
    def __init__(self, log, temp, fstr):
        self.logger = log
        self.template = temp
        self.full_str = fstr

        self.validTime = None
        self.initTime = None
        self.leadTime = 0
        self.levelTime = -1

    def add_to_dict(self, match, match_dict, full_str, new_len):
        if not full_str[0:new_len].isdigit():
            return False
        if match not in match_dict.keys():
            match_dict[match] = full_str[0:new_len]
        elif match_dict[match].zfill(new_len) != full_str[0:new_len]:
            return False
#        print("Added {} to dict under {}".format(full_str[0:new_len], match))
        return True

    def get_fmt_info(self, fmt, full_str, match_dict, identifier):
        length = 0
        match_list = re.findall('%[^%]+', fmt)
        for match in match_list:
            new_len = 0
            extra_len = 0
#            print("MATCH {}".format(match))
            # exact match, i.e. %Y
            if match in length_dict.keys():
                # handle lead and level that have 1 digit precision
                new_len = length_dict[match]
                if match == '%H' and identifier == 'lead' or \
                   identifier == 'level':
                    # look forward until non-digit is found
                    new_len = 0
                    while full_str[new_len].isdigit():
                        new_len += 1
#                print("ADD {}".format(new_len))
                length += new_len
                if not self.add_to_dict(identifier+'+'+match[1:], match_dict, full_str, new_len):
                    return -1
            # if match starts with key, find new length, i.e. %Y: or %HH
            elif match[0:2] in length_dict.keys():
                c = match[1]
                x = re.match('%(['+c+']+)(.*)', match)
                if x:
                    new_len = len(x.group(1))
                    if new_len > 1:
#                        print("ADD {} from multi letter".format(len(x.group(1))))
                        length += new_len
                    else:
                        m = match[0:2]
#                        print("ADD {}".format(length_dict[m]))
                        new_len = length_dict[m]
                        length += new_len
                    if not self.add_to_dict(identifier+'+'+c, match_dict, full_str, new_len):
                        return -1

                    if len(x.group(2)) > 0:
#                        print("ADD extra chars {}".format(len(x.group(2))))
                        extra_len = len(x.group(2))
                        length += extra_len
            else:
                # match %2H or %.2H
                x = re.match('%\.*(\d+)(\D)$', match)
                if x:
#                    print("LEN ADDED IS {}".format(x.group(1)))
                    new_len = int(x.group(1))
                    length += new_len
                    if not self.add_to_dict(identifier+'+'+x.group(2)[0], match_dict, full_str, new_len):
                        return -1
                else:
#                    print("Unknown time format: {}".format(match))
                    return -1

            full_str = full_str[new_len+extra_len:]

#        print("TOTAL LEN IS {}\n".format(length))
        return length


    def set_output_dict_from_time_info(self, time_dict, output_dict, key):
        # get month and day from julian date if applicable
        if time_dict['Y'] != -1 and time_dict['j'] != -1:
            dt = datetime.datetime.strptime(str(time_dict['Y'])+'_'+str(time_dict['j']),
                                            '%Y_%j')
            time_dict['m'] = int(dt.strftime('%m'))
            time_dict['d'] = int(dt.strftime('%d'))

        if time_dict['Y'] != -1 and time_dict['m'] != -1 and time_dict['d'] != -1:
            output_dict[key] = datetime.datetime(time_dict['Y'],
                                          time_dict['m'],
                                          time_dict['d'],
                                          time_dict['H'],
                                          time_dict['M'])


    def parseTemplate(self):
        template_len = len(self.template)
        i = 0
        str_i = 0
        match_dict = {}
        valid_shift = 0

        while i < template_len:
            # if a tag is found, split contents and extract time
            if self.template[i] == TEMPLATE_IDENTIFIER_BEGIN:
                end_i = self.template.find(TEMPLATE_IDENTIFIER_END, i)
                tag = self.template[i+1:end_i]
                sections = tag.split('?')
                identifier = sections[0]
                format = ''
                shift = 0
                for section in sections[1:]:
                    items = section.split('=')
                    if items[0] == 'fmt':
                        format = items[1]
#                        print("Format for {} is {}".format(identifier, format))
                        fmt_len = self.get_fmt_info(format, self.full_str[str_i:],
                                               match_dict, identifier)
                        if fmt_len == -1:
                            return None
                        # extract string that corresponds to format
                    if items[0] == SHIFT_STRING:
                        shift = int(items[1])
#                        self.logger.warning("Shift for {} is {}. Shift not yet supported".format(identifier, shift))
                        # don't allow shift on any identifier except valid
                        if identifier != VALID_STRING:
                            self.logger.error('Cannot apply a shift to template ' +
                                              'item {} when processing inexact ' +
                                              'times. Only {} is accepted'
                                              .format(identifier, VALID_STRING))
                            exit(1)

                        # if shift has been set before (other than 0) and
                        # this shift differs, report error and exit
                        if valid_shift != 0 and shift != valid_shift:
                            self.logger.error('Found multiple shifts for valid time' +
                                              '{} differs from {}'
                                              .format(shift, valid_shift))
                            exit(1)

                        # save valid shift to apply to valid time later
                        valid_shift = shift

                    # check if duplicate formatters are found
                i = end_i + 1
                str_i += fmt_len
            else:
                i += 1
                str_i += 1

        # combine common items and get datetime
        output_dict = {}

        valid = {}
        init = {}
        da_init = {}
        lead = {}
        offset = {}

        valid['Y'] = -1
        valid['m'] = -1
        valid['d'] = -1
        valid['j'] = -1
        valid['H'] = 0
        valid['M'] = 0

        init['Y'] = -1
        init['m'] = -1
        init['d'] = -1
        init['j'] = -1
        init['H'] = 0
        init['M'] = 0

        da_init['Y'] = -1
        da_init['m'] = -1
        da_init['d'] = -1
        da_init['j'] = -1
        da_init['H'] = 0
        da_init['M'] = 0

        lead['H'] = 0
        lead['M'] = 0
        lead['S'] = 0

        offset['H'] = 0
#        offset['M'] = 0
#        offset['S'] = 0

        for key, value in match_dict.iteritems():
            if key.startswith(VALID_STRING):
                valid[key.split('+')[1]] = int(value)

        self.set_output_dict_from_time_info(valid, output_dict, 'valid')

        # shift valid time if applicable
        if valid_shift != 0:
            output_dict['valid'] -= datetime.timedelta(seconds=valid_shift)


        for key, value in match_dict.iteritems():
            if key.startswith(INIT_STRING):
                init[key.split('+')[1]] = int(value)

        self.set_output_dict_from_time_info(init, output_dict, 'init')


        for key, value in match_dict.iteritems():
            if key.startswith(DA_INIT_STRING):
                da_init[key.split('+')[1]] = int(value)

        self.set_output_dict_from_time_info(da_init, output_dict, 'da_init')


        for key, value in match_dict.iteritems():
            if key.startswith(LEAD_STRING):
                lead[key.split('+')[1]] = int(value)

        lead_seconds = lead['H'] * 3600 + lead['M'] * 60 + lead['S']
        output_dict['lead'] = lead_seconds

        for key, value in match_dict.iteritems():
            if key.startswith(OFFSET_STRING):
                offset[key.split('+')[1]] = int(value)

        output_dict['offset'] = offset['H']

        time_info = time_util.ti_calculate(output_dict)
#        print(time_info)
        return time_info
