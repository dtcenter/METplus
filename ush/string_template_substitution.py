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

TEMPLATE_IDENTIFIER_BEGIN = "{"
TEMPLATE_IDENTIFIER_END = "}"

FORMATTING_DELIMITER = "?"
FORMATTING_VALUE_DELIMITER = "="
FORMAT_STRING = "fmt"

SHIFT_STRING = "shift"

VALID_STRING = "valid"
LEAD_STRING = "lead"
INIT_STRING = "init"
LEVEL_STRING = "level"
CYCLE_STRING = "cycle"
OFFSET_STRING = "offset"
# These three were added in response to the tropical cyclone use case
DATE_STRING = "date"
REGION_STRING = "region"
CYCLONE_STRING = "cyclone"
MISC_STRING = "misc"

LEAD_LEVEL_FORMATTING_DELIMITER = "%"
# Use the same formatting delimiter used for level:
CYCLE_OFFSET_FORMATTING_DELIMITER = LEAD_LEVEL_FORMATTING_DELIMITER

SECONDS_PER_HOUR = 3600.
MINUTES_PER_HOUR = 60.
SECONDS_PER_MINUTE = 60.
HOURS_PER_DAY = 24.

TWO_DIGIT_PAD = 2
THREE_DIGIT_PAD = 3

GLOBAL_LOGGER = None


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

        if self.kwargs is not None:
            for key, value in kwargs.iteritems():
                # print("%s == %s" % (key, value))
                setattr(self, key, value)


    def getShiftTime(self, split_item):
        shift_split_string = \
            split_item.split(FORMATTING_VALUE_DELIMITER)

        if len(shift_split_string) != 2:
            return

        shift_seconds = shift_split_string[1]
        self.shift_seconds = int(shift_seconds)


    def format_one_time_item(self, item, t, c):
        count = item.count(c)
        if count > 0:
            rest = ''
            # get precision
            res = re.match("^\.(\d+)"+c+"(.*)", item)
            if res:
                padding = int(res.group(1))
                rest = res.group(2)
            else:
                res = re.match("^(\d+)"+c+"(.*)", item)
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

            # shift if set, get that value before handling formatting
            for split_item in split_string:
                if split_item.startswith(SHIFT_STRING):
                    self.getShiftTime(split_item)

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

        # Replace regex with properly formatted information
        self.tmpl = multiple_replace(replacement_dict, self.tmpl)
        return self.tmpl

    # TODO: Remove this after wrapper refactor
    def create_grid2obs_regex(self):
        """! Create the regex that describes a grid to obs filename based on
             what is defined in the config file's filename template section.
             Similar logic to doStringSub() except
             replace the date, cycle, lead, and offset with the appropriate
             regex.

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
            self.logger.error("No matches found for template: " +
                              self.tmpl)
            exit(0)
        elif len(match_list) != len(match_start_end_list):
            # Log and exit
            self.logger.error("match_list and match_start_end_list should " +
                              "have the same length for template: " +
                              self.tmpl)
            exit(0)
        else:
            # No times to compute, create the regex expressions that describe
            # the date (YYYY, YYYYMM, YYYYMMMDD, or YYYYMMDDhh),  cycle, lead
            # and offset portions of the filename template (as applicable).
            if VALID_STRING in self.kwargs:
                self.kwargs[VALID_STRING] = self.valid
            # Cycle only
            elif CYCLE_STRING in self.kwargs:
                self.kwargs[CYCLE_STRING] = self.cycle

            # Valid and cycle only
            elif (VALID_STRING in self.kwargs and
                  CYCLE_STRING in self.kwargs):

                self.kwargs[VALID_STRING] = self.valid
                self.kwargs[CYCLE_STRING] = self.cycle

            # Cycle and lead
            elif (CYCLE_STRING in self.kwargs and
                  LEAD_STRING in self.kwargs):
                self.kwargs[CYCLE_STRING] = self.cycle
                self.kwargs[LEAD_STRING] = self.lead
            # Cycle and offset
            elif (CYCLE_STRING in self.kwargs and
                  OFFSET_STRING in self.kwargs):
                self.kwargs[CYCLE_STRING] = self.date
                self.kwargs[OFFSET_STRING] = self.region
            # Valid and lead
            elif (VALID_STRING in self.kwargs and
                  LEAD_STRING in self.kwargs):
                self.kwargs[VALID_STRING] = self.valid
                self.kwargs[LEAD_STRING] = self.lead
            # init and lead
            # This combination hasn't been observed, but including it
            # in the event it is needed.
            elif (INIT_STRING in self.kwargs and
                  LEAD_STRING in self.kwargs):
                self.kwargs[INIT_STRING] = self.init
                self.kwargs[LEAD_STRING] = self.lead

            # Cycle, lead, and offset
            elif (CYCLE_STRING in self.kwargs and
                  LEAD_STRING in self.kwargs and
                  OFFSET_STRING in self.kwargs):
                self.kwargs[CYCLE_STRING] = self.cycle
                self.kwargs[LEAD_STRING] = self.lead
                self.kwargs[OFFSET_STRING] = self.offset

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

                    # split_string[0] holds the key (e.g. "cycle",
                    # "offset", etc)
                    if split_string[0] not in self.kwargs.keys():
                        # Log and continue
                        self.logger.error("The key " + split_string[0] +
                                          " does not exist for the template: " +
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
                            if split_string[0] == VALID_STRING:
                                value = "([0-9]{10})"
                                string_to_replace = \
                                    TEMPLATE_IDENTIFIER_BEGIN + match + \
                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == INIT_STRING:
                                value = "([0-9]{8})"
                                string_to_replace = \
                                    TEMPLATE_IDENTIFIER_BEGIN + match + \
                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == CYCLE_STRING:
                                value = "([0-9]{2,3})"
                                string_to_replace = \
                                    TEMPLATE_IDENTIFIER_BEGIN + match + \
                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == LEAD_STRING:
                                value = "([0-9]{1,3})"
                                string_to_replace = \
                                    TEMPLATE_IDENTIFIER_BEGIN + match + \
                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == OFFSET_STRING:
                                value = "([0-9]{2,3})"
                                string_to_replace = \
                                    TEMPLATE_IDENTIFIER_BEGIN + match + \
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

            # Add the $ to the end of the filename to
            # ensure that no other files with unorthodox extensions
            #  (e.g. file1.grb2.idx) are matched, thereby improving performance.
            self.tmpl = temp_str + "$"
            return self.tmpl



class StringExtract:
    def __init__(self, log, temp, fstr):
        self.logger = log
        self.temp = temp
        self.fstr = fstr

        self.validTime = None
        self.initTime = None
        self.leadTime = 0
        self.levelTime = -1

    def getValidTime(self, fmt):
        if self.validTime is None:
            if self.initTime is None:
                return ""
            return (self.initTime +
                    datetime.timedelta(seconds=self.leadTime)).strftime(fmt)

        return self.validTime.strftime(fmt)

    def getInitTime(self, fmt):
        if self.initTime is None:
            if self.validTime is None:
                return ""
            return (self.validTime -
                    datetime.timedelta(seconds=self.leadTime)).strftime(fmt)
        return self.initTime.strftime(fmt)

    @property
    def leadHour(self):
        if self.leadTime == -1:
            return -1
        return self.leadTime / 3600

    @property
    def levelHour(self):
        if self.levelTime == -1:
            return -1
        return self.levelTime / 3600

    def parseTemplate(self):
        tempLen = len(self.temp)
        i = 0
        idx = 0
        yIdx = -1
        mIdx = -1
        dIdx = -1
        hIdx = -1
        minIdx = -1
        lead = -1
        level = -1

        validYear = -1
        validMonth = -1
        validDay = -1
        validHour = 0
        validMin = 0

        initYear = -1
        initMonth = -1
        initDay = -1
        initHour = 0
        initMin = 0

        inValid = False
        inLevel = False
        inLead = False
        inInit = False

        fmt_len = len(FORMATTING_DELIMITER + \
                      FORMATTING_VALUE_DELIMITER + \
                      FORMAT_STRING)

        while i < tempLen:
            if self.temp[i] == TEMPLATE_IDENTIFIER_BEGIN:
                # increment past TEMPLATE_IDENTIFIER_BEGIN
                i += 1
                # TODO: change 9 and 8 to len(VALID_STRING) + len(?fmt=)
                if self.temp[
                   i:i + len(VALID_STRING) + fmt_len] == VALID_STRING + "?fmt=":
                    inValid = True
                    i += len(VALID_STRING) + fmt_len - 1
                if self.temp[
                   i:i + len(LEVEL_STRING) + fmt_len] == LEVEL_STRING + "?fmt=":
                    inLevel = True
                    i += len(LEVEL_STRING) + fmt_len - 1
                if self.temp[
                   i:i + len(INIT_STRING) + fmt_len] == INIT_STRING + "?fmt=":
                    inInit = True
                    i += len(INIT_STRING) + fmt_len - 1
                if self.temp[
                   i:i + len(LEAD_STRING) + fmt_len] == LEAD_STRING + "?fmt=":
                    inLead = True
                    i += len(LEAD_STRING) + fmt_len - 1
            elif self.temp[i] == TEMPLATE_IDENTIFIER_END:
                if inValid:
                    if yIdx != -1:
                        if self.fstr[yIdx:yIdx+4].isdigit():
                            validYear = int(self.fstr[yIdx:yIdx+4])
                        else:
                            return False
                    if mIdx != -1:
                        if self.fstr[mIdx:mIdx+2].isdigit():
                            validMonth = int(self.fstr[mIdx:mIdx+2])
                        else:
                            return False
                    if dIdx != -1:
                        if self.fstr[dIdx:dIdx+2].isdigit():
                            validDay = int(self.fstr[dIdx:dIdx+2])
                        else:
                            return False
                    if hIdx != -1:
                        if self.fstr[hIdx:hIdx+2].isdigit():
                            validHour = int(self.fstr[hIdx:hIdx + 2])
                        else:
                            return False
                    if minIdx != -1:
                        if self.fstr[minIdx:minIdx+2].isdigit():
                            validMin = int(self.fstr[minIdx:minIdx + 2])
                        else:
                            return False

                    yIdx = -1
                    mIdx = -1
                    dIdx = -1
                    hIdx = -1
                    minIdx = -1
                    inValid = False

                if inInit:
                    if yIdx != -1:
                        if self.fstr[yIdx:yIdx+4].isdigit():
                            initYear = int(self.fstr[yIdx:yIdx + 4])
                        else:
                            return False
                    if mIdx != -1:
                        if self.fstr[mIdx:mIdx+2].isdigit():
                            initMonth = int(self.fstr[mIdx:mIdx + 2])
                        else:
                            return False
                    if dIdx != -1:
                        if self.fstr[dIdx:dIdx+2].isdigit():
                            initDay = int(self.fstr[dIdx:dIdx + 2])
                        else:
                            return False
                    if hIdx != -1:
                        if self.fstr[hIdx:hIdx+2].isdigit():
                            initHour = int(self.fstr[hIdx:hIdx + 2])
                        else:
                            return False
                    if minIdx != -1:
                        if self.fstr[minIdx:minIdx+2].isdigit():
                            initMin = int(self.fstr[minIdx:minIdx + 2])
                        else:
                            return False

                    yIdx = -1
                    mIdx = -1
                    dIdx = -1
                    hIdx = -1
                    minIdx = -1
                    inInit = False

                elif inLevel:
                    if level == -1 or level == None or not level.isdigit():
                        return False
                    self.levelTime = int(level) * SECONDS_PER_HOUR
                    level = -1
                    inLevel = False

                elif inLead:
                    if lead == -1 or lead == None or not lead.isdigit():
                        return False
                    self.leadTime = int(lead) * SECONDS_PER_HOUR
                    lead = -1
                    inLead = False

            elif inValid or inInit:
                if idx > len(self.fstr):
                    return False
                if self.temp[i:i + 2] == "%Y":
                    yIdx = idx
                    idx += 4
                    i += 1
                elif self.temp[i:i + 2] == "%m":
                    mIdx = idx
                    idx += 2
                    i += 1
                elif self.temp[i:i + 2] == "%d":
                    dIdx = idx
                    idx += 2
                    i += 1
                elif self.temp[i:i + 2] == "%H":
                    hIdx = idx
                    idx += 2
                    i += 1
                elif self.temp[i:i + 2] == "%M":
                    minIdx = idx
                    idx += 2
                    i += 1
            elif inLevel:
                if self.temp[i:i + 4] == "%HHH":
                    level = self.fstr[idx:idx + 3]
                    idx += 3
                    i += 3
                elif self.temp[i:i + 3] == "%HH":
                    level = self.fstr[idx:idx + 2]
                    idx += 2
                    i += 2
            elif inLead:
                if self.temp[i:i + 4] == "%HHH":
                    lead = self.fstr[idx:idx + 3]
                    idx += 3
                    i += 3
                elif self.temp[i:i + 3] == "%HH":
                    lead = self.fstr[idx:idx + 2]
                    idx += 2
                    i += 2
                elif re.match("%\..*H", self.temp[i:i+4]):
                    padding = int(re.match("%\.(.*)H", self.temp[i:i+4]).group(1))
                    lead = self.fstr[idx:idx + padding]
                    idx += padding
                    i += padding
                elif self.temp[i:i + 2] == "%H":
                    # check for digit until non-digit comes up
                    lead = ""
                    while self.fstr[idx].isdigit():
                        lead += self.fstr[idx]
                        idx += 1

                    i += 1
                    if lead == "":
                        lead = -1
                        return False
            else:
                idx += 1
            # increment past TEMPLATE_IDENTIFIER_END
            i += 1

        if validYear != -1 and validMonth != -1 and validDay != -1:
            self.validTime = \
                datetime.datetime(validYear,
                                  validMonth,
                                  validDay,
                                  validHour,
                                  validMin)

        if initYear != -1 and initMonth != -1 and initDay != -1:
            self.initTime = \
                datetime.datetime(initYear,
                                  initMonth,
                                  initDay,
                                  initHour,
                                  initMin)
        # TODO: Check if success? Or wrap getValid/InitTime with == None check?
        return True
