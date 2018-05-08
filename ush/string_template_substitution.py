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


def date_str_to_datetime_obj(str):
    """Convert year month day string to a datetime object.
    Works with YYYYMMDDHHMMSS, YYYYMMDDHHMM, YYYYMMDDHH, YYYYMMDD, YYYYMM"""

    length = len(str)
    if length == 14:
        return datetime.datetime(int(str[:4]), int(str[4:6]),
                                 int(str[6:8]), int(str[8:10]),
                                 int(str[10:12]), int(str[12:14]), 0, None)
    elif length == 6:
        return datetime.datetime(int(str[:4]), int(str[4:6]), 0, 0, 0, 0, 0, None)
    elif length == 8:
        return datetime.datetime(int(str[:4]), int(str[4:6]),
                                 int(str[6:8]), 0, 0, 0, 0, None)
    elif length == 10:
        return datetime.datetime(int(str[:4]), int(str[4:6]),
                                 int(str[6:8]), int(str[8:10]),
                                 0, 0, 0, None)
    elif length == 12:
        return datetime.datetime(int(str[:4]), int(str[4:6]),
                                 int(str[6:8]), int(str[8:10]),
                                 int(str[10:12]), 0, 0, None)


def multiple_replace(dict, text):
    """ Replace in 'text' all occurrences of any key in the
    given dictionary by its corresponding value.  Returns the new string. """

    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    j = "".join(map(re.escape, dict.keys()))
    # print "regex from dictionary keys: {}".format(j)

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)


def get_lead_level_time_seconds(logger, time_string):
    """ Returns the number of seconds for the time string in the format
        [H]HH[MMSS]"""

    # Used for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # HH
    if len(time_string) == 2:
        return (int(time_string) * SECONDS_PER_HOUR)
    # HHH
    elif len(time_string) == 3:
        return (int(time_string) * SECONDS_PER_HOUR)
    # HHMM
    elif len(time_string) == 4:
        return ((int(time_string[0:2]) * SECONDS_PER_HOUR) +
                (int(time_string[2:4]) * MINUTES_PER_HOUR))
    # HHHMM
    elif len(time_string) == 5:
        return ((int(time_string[0:3]) * SECONDS_PER_HOUR) +
                (int(time_string[3:5]) * MINUTES_PER_HOUR))
    # HHMMSS
    elif len(time_string) == 6:
        return ((int(time_string[0:2]) * SECONDS_PER_HOUR) +
                (int(time_string[2:4]) * MINUTES_PER_HOUR) +
                int(time_string[4:6]))
    # HHHMMSS
    elif len(time_string) == 7:
        return ((int(time_string[0:3]) * SECONDS_PER_HOUR) +
                (int(time_string[3:5]) * MINUTES_PER_HOUR) +
                int(time_string[5:7]))
    else:
        logger.error("ERROR | [" + cur_filename + ":" + cur_function +
                     "] | " + "The time string " + time_string +
                     " must be in the format [H]HH[MMSS], where a two digit " +
                     "hour is required.  Providing a three digit hour, two " +
                     "digit minutes and a two digit seconds are optional.")
        exit(0)


def get_time_in_hours(logger, time_string):
    """! Returns the number of hours for the time string in the format
         H, HH or HHH"""

    # Used for logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # H, HH or HHH
    if len(time_string) == 1:
        return int(time_string)
    elif len(time_string) == 2:
        return int(time_string)
    elif len(time_string) == 3:
        return int(time_string)
    else:
        logger.error("ERROR | [" + cur_filename + ":" + cur_function +
                     "] | " + "The time string " + time_string +
                     " must be in the format H, HH or HHH where a one-, two-"
                     " or three-digit" +
                     " hour is required.")
        exit(0)


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
       cyclone - a two-digit annual cyclone number (if ATCF) or four-digit cyclone number (leading zeros)
       misc - any string



    See the description of doStringSub for further details.
    """

    def __init__(self, log, tmpl, **kwargs):

        self.logger = log
        self.tmpl = tmpl
        self.kwargs = kwargs

        if self.kwargs is not None:
            for key, value in kwargs.iteritems():
                # print("%s == %s" % (key, value))
                setattr(self, key, value)

        self.lead_time_seconds = 0
        self.level_time_seconds = 0
        self.negative_lead = False
        self.negative_level = False
        self.cycle_hours = 0
        self.offset_hour = 0

        if LEAD_STRING in self.kwargs:
            self.lead_time_seconds = \
                get_lead_level_time_seconds(self.logger,
                                            self.kwargs.get(LEAD_STRING,
                                                            None))
        if LEVEL_STRING in self.kwargs:
            self.level_time_seconds = \
                get_lead_level_time_seconds(self.logger,
                                            self.kwargs.get(LEVEL_STRING,
                                                            None))
        if CYCLE_STRING in self.kwargs:
            self.cycle_time_hours = \
                get_time_in_hours(self.logger,
                                  self.kwargs.get(CYCLE_STRING, None))

        if OFFSET_STRING in self.kwargs:
            self.offset_hour = \
                get_time_in_hours(self.logger,
                                  self.kwargs.get(OFFSET_STRING, None))

        if DATE_STRING in self.kwargs:
            self.date = self.kwargs.get(DATE_STRING, None)

        if CYCLONE_STRING in self.kwargs:
            self.cyclone = str(self.kwargs.get(CYCLONE_STRING, None))

        if REGION_STRING in self.kwargs:
            self.region = str(self.kwargs.get(REGION_STRING, None))

        if MISC_STRING in self.kwargs:
            self.misc = str(self.kwargs.get(MISC_STRING, None))

    def dateCalcInit(self):
        """ Calculate the init time from the valid and lead time  """
        # Used for logging
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # Get the unix time for the valid time
        if len(self.kwargs.get(VALID_STRING, None)) == 10:
            valid_time_tuple = \
                time.strptime(self.kwargs.get(VALID_STRING, None), "%Y%m%d%H")
        elif len(self.kwargs.get(VALID_STRING, None)) == 12:
            valid_time_tuple = \
                time.strptime(self.kwargs.get(VALID_STRING, None),
                              "%Y%m%d%H%M")
        elif len(self.kwargs.get(VALID_STRING, None)) == 14:
            valid_time_tuple = \
                time.strptime(self.kwargs.get(VALID_STRING, None),
                              "%Y%m%d%H%M%S")
        else:
            self.logger.error("ERROR | [" + cur_filename + ":" +
                              cur_function + "] | " + "The valid time " +
                              self.kwargs.get(VALID_STRING, None) +
                              " must be in the format YYYYmmddHH[MMSS].")
            exit(0)

        valid_unix_time = calendar.timegm(valid_time_tuple)

        # Get the number of seconds for the lead time
        self.lead_time_seconds = \
            get_lead_level_time_seconds(self.logger,
                                        self.kwargs.get(LEAD_STRING, None))

        init_unix_time = valid_unix_time - self.lead_time_seconds
        init_time = time.strftime("%Y%m%d%H%M%S", time.gmtime(init_unix_time))

        return init_time

    def dateCalcValid(self):

        """ Calculate the valid time from the init and lead time """

        # Used for logging
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # Get the unix time for the init time
        if len(self.kwargs.get(INIT_STRING, None)) == 10:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None), "%Y%m%d%H")
        elif len(self.kwargs.get(INIT_STRING, None)) == 12:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None), "%Y%m%d%H%M")
        elif len(self.kwargs.get(INIT_STRING, None)) == 14:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None),
                              "%Y%m%d%H%M%S")
        else:
            self.logger.error("ERROR | [" + cur_filename + ":" +
                              cur_function + "] | " + "The init time " +
                              self.kwargs.get(INIT_STRING, None) +
                              " must be in the format YYYYmmddHH[MMSS].")
            exit(0)

        init_unix_time = calendar.timegm(init_time_tuple)

        # Get the number of seconds for the lead time
        self.lead_time_seconds = \
            get_lead_level_time_seconds(self.logger,
                                        self.kwargs.get(LEAD_STRING, None))

        valid_unix_time = init_unix_time + self.lead_time_seconds
        valid_time = time.strftime("%Y%m%d%H%M%S",
                                   time.gmtime(valid_unix_time))

        return valid_time

    def calc_valid_for_prepbufr(self):
        """! Calculates the valid time from the init time, cycle hour, and
             negative or positive offset hour.

             Returns:
                 valid_time - the calculated valid time

        """
        # Used for logging
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # For GDAS and other prepbufr files that do not make use
        # of the cycle hour and offset hour
        cycle_and_offset_difference_in_secs = 0

        # Get the unix time for the init time
        if len(self.kwargs.get(INIT_STRING, None)) == 8:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None), "%Y%m%d")
        elif len(self.kwargs.get(INIT_STRING, None)) == 10:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None), "%Y%m%d%H")
        elif len(self.kwargs.get(INIT_STRING, None)) == 12:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None), "%Y%m%d%H%M")
        elif len(self.kwargs.get(INIT_STRING, None)) == 14:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None),
                              "%Y%m%d%H%M%S")
        else:
            self.logger.error("ERROR | [" + cur_filename + ":" +
                              cur_function + "] | " + "The init time " +
                              self.kwargs.get(INIT_STRING, None) +
                              " must be in the format YYYYmmddHH[MMSS].")
            exit(0)

        init_unix_time = calendar.timegm(init_time_tuple)

        # Get the difference between the cycle hour and offset hour and convert
        # result to seconds.
        if self.offset_hour:
            cycle_and_offset_difference_in_secs = \
                (self.cycle_time_hours - self.offset_hour) * SECONDS_PER_HOUR

        # valid time is the sum of the init time and difference between
        # the cycle and offset.
        valid_unix_time = init_unix_time + cycle_and_offset_difference_in_secs

        # Convert valid_unix_time to the specified format.
        valid_time = time.strftime("%Y%m%d%H%M%S",
                                   time.gmtime(valid_unix_time))

        return valid_time

    def dateCalcLead(self):

        """ Calculate the lead time from the init and valid time """

        # Used for logging
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # Get the unix time for the init time
        if len(self.kwargs.get(INIT_STRING, None)) == 10:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None),
                              "%Y%m%d%H")
        elif len(self.kwargs.get(INIT_STRING, None)) == 12:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None),
                              "%Y%m%d%H%M")
        elif len(self.kwargs.get(INIT_STRING, None)) == 14:
            init_time_tuple = \
                time.strptime(self.kwargs.get(INIT_STRING, None),
                              "%Y%m%d%H%M%S")
        else:
            self.logger.error("ERROR | [" + cur_filename + ":" +
                              cur_function + "] | " + "The init time " +
                              self.kwargs.get(INIT_STRING, None) +
                              " must be in the format YYYYmmddHH[MMSS].")
            exit(0)
        init_unix_time = calendar.timegm(init_time_tuple)

        # Get the unix time for the valid time
        if len(self.kwarg).get(VALID_STRING, None) == 10:
            valid_time_tuple = \
                time.strptime(self.kwargs.get(VALID_STRING, None),
                              "%Y%m%d%H")
        elif len(self.kwargs.get(VALID_STRING, None)) == 12:
            valid_time_tuple = \
                time.strptime(self.kwargs.get(VALID_STRING, None),
                              "%Y%m%d%H%M")
        elif len(self.kwargs.get(VALID_STRING, None)) == 14:
            valid_time_tuple = \
                time.strptime(self.kwargs.get(VALID_STRING, None),
                              "%Y%m%d%H%M%S")
        else:
            self.logger.error("ERROR | [" + cur_filename + ":" +
                              cur_function + "] | " + "The valid time " +
                              self.kwargs.get(VALID_STRING, None) +
                              " must be in the format YYYYmmddHH[MMSS].")
            exit(0)
        valid_unix_time = calendar.timegm(valid_time_tuple)

        # Determine if the init time is greater than the lead time,
        # if so lead time should be negative
        negative_lead_flag = 0
        if valid_unix_time > init_unix_time:
            self.lead_time_seconds = valid_unix_time - init_unix_time
        else:
            self.lead_time_seconds = init_unix_time - valid_unix_time
            negative_lead_flag = 1
            self.negative_lead = True
        lead_seconds_str = \
            str(datetime.timedelta(seconds=self.lead_time_second))

        # There are no days, but only HH:MM:SS information
        if len(lead_seconds_str) <= 8:
            HH, MM, SS = lead_seconds_str.split(":")
            lead_time = HH.zfill(TWO_DIGIT_PAD) + MM + SS
        # There are days in addition to HH:MM:SS information
        elif len(lead_seconds_str) > 8:
            # e.g. '4 days, 23:35:00' split on comma and get first value
            lead_seconds_str_split_comma = lead_seconds_str.split(",")
            # e.g. '4 days' split on space and get first value
            lead_seconds_str_split_space = \
                lead_seconds_str_split_comma[0].split(" ")
            # Convert the number of days to hours
            days_to_hours = int(lead_seconds_str_split_space[0]) * 24
            # Get string values for the hours, minutes, seconds
            HH, MM, SS = lead_seconds_str.split(":")
            # e.g. '4 days, 23' split on comma and get second value
            HH_split = HH.split(", ")
            # Convert the hours string to an integer and
            # add to the days in hours
            HH = int(HH_split[1])
            total_hours = days_to_hours + int(HH)
            # Put together the lead_time string in the format [H]HH[MMSS]
            lead_time = str(total_hours) + MM + SS
        # If the init time was greater than the valid time,
        # the lead time should be negative
        if negative_lead_flag == 1:
            lead_time = "-" + lead_time

        return lead_time

    def format_lead_level(self, parm_type, format_string):

        """ Formats the lead or level in the requested format """

        # Used for logging
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        formatted_time_string = ""
        time_seconds = 0
        negative_flag = False

        if parm_type == LEAD_STRING:
            time_seconds = self.lead_time_seconds
            negative_flag = self.negative_lead
        elif parm_type == LEVEL_STRING:
            time_seconds = self.level_time_seconds
            negative_flag = self.negative_level
        else:
            # Log and exit
            self.logger.error("ERROR | [" + cur_filename + ":" +
                              cur_function + "] | Invalid parm_type of " +
                              parm_type + ".  Acceptable parm types are: " +
                              LEAD_STRING + " and " + LEVEL_STRING + ".")
            exit(0)

        hours_value = math.floor(time_seconds / SECONDS_PER_HOUR)
        time_seconds = time_seconds - (hours_value * SECONDS_PER_HOUR)
        minutes_value = math.floor(time_seconds / MINUTES_PER_HOUR)
        time_seconds = time_seconds - (minutes_value * MINUTES_PER_HOUR)
        seconds_value = time_seconds

        hours_value_str = str(int(hours_value))
        minutes_value_str = str(int(minutes_value))
        seconds_value_str = str(int(seconds_value))

        format_string_split = \
            format_string.split(LEAD_LEVEL_FORMATTING_DELIMITER)

        # Minutes and seconds should be included (Empty, HH or HHH, MMSS)
        if len(format_string_split) == 3:
            MM = minutes_value_str.zfill(TWO_DIGIT_PAD)
            SS = seconds_value_str.zfill(TWO_DIGIT_PAD)
            MMSS = MM + SS
            if format_string_split[1] == 'HH':
                hours = hours_value_str.zfill(TWO_DIGIT_PAD)
                if len(hours) == 3:
                    self.logger.warn("WARN | [" + cur_filename + ":" +
                                     cur_function + "] | " +
                                     "The requested format for hours was " +
                                     format_string_split[1] +
                                     " but the hours given are " + hours +
                                     ". Returning a three digit hour.")

            elif format_string_split[1] == 'HHH':
                hours = hours_value_str.zfill(THREE_DIGIT_PAD)
            else:
                self.logger.error("ERROR | [" + cur_filename + ":" +
                                  cur_function + "] | " + "The time must " +
                                  "be in the format [H]HH[MMSS], where a " +
                                  "two digit hour is required.  Providing a " +
                                  "one-,two-, or three-digit "
                                  "day, two-digit "
                                  "minute and a" +
                                  " two-digit second are optional.")
                exit(0)

            formatted_time_string = hours + MMSS

        # Only hours should be included (Empty, HH or HHH)
        elif len(format_string_split) == 2:
            if format_string_split[1] == 'HH':
                hours = hours_value_str.zfill(TWO_DIGIT_PAD)
                if len(hours) == 3:
                    self.logger.warn("WARN | [" + cur_filename + ":" +
                                     cur_function + "] | " +
                                     "The requested format for hours was " +
                                     format_string_split[1] +
                                     " but the hours given are " + hours +
                                     ". Returning a three digit hour.")
            elif format_string_split[1] == 'HHH':
                hours = hours_value_str.zfill(THREE_DIGIT_PAD)
            else:
                self.logger.error("ERROR | [" + cur_filename + ":" +
                                  cur_function + "] | " +
                                  "The time must be in the format " +
                                  "[H]HH[MMSS], where a two digit hour is " +
                                  "required.  Providing a three digit hour, " +
                                  "two digit minutes and a two digit seconds" +
                                  " are optional.")
                exit(0)

            formatted_time_string = hours

        else:
            self.logger.error("ERROR | [" + cur_filename + ":" +
                              cur_function + "] | " + "The time must be in " +
                              "the format [H]HH[MMSS], where a two digit " +
                              "hour is required.  Providing a three digit " +
                              "hour, two digit minutes and a two digit " +
                              "seconds are optional.")
            exit(0)

        if negative_flag:
            formatted_time_string = "-" + formatted_time_string

        return formatted_time_string

    def format_cycle_offset(self, parm_type, format_string):
        """! Formats the cycle or offset time in the requested format.
             The cycle and offset units are in seconds, the smallest unit of
             time which is supported by MET/METplus. The output formats
             supported are: day hour minutes seconds (dHMS), day hour
             minutes (dHM), hour minutes seconds (HMS), day hour (dH),
             hour minutes (HM), and hour (H).  Minutes and seconds are in
             two-digit format and days and hours can be either two- or
             three-digit.

             Args:
                 parm_type    -  either cycle or offset
                 format_string -  the string whose format should be emulated
                                  i.e. the template

             Returns:
                 formatted_time_string - the time string in the requested
                 format
        """
        # Used for logging
        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        formatted_time_string = ""
        if parm_type == CYCLE_STRING:
            time_hours = self.cycle_time_hours
        elif parm_type == OFFSET_STRING:
            time_hours = self.offset_hour
        else:
            # Log and exit
            self.logger.error("ERROR | [" + cur_filename + ":" +
                              cur_function + "] | Invalid parm_type of " +
                              parm_type + ".  Acceptable parm types are: " +
                              CYCLE_STRING + " and " + OFFSET_STRING + ".")
            exit(0)

        #
        # Break down the cycle/offset time into number of whole numbers
        # of days, hours, minutes and seconds.
        #

        # DAYS
        # Determine the whole number of days. The difference between the
        # cycle/offset's whole number of days and the original cycle/offset
        # value is used to calculate the whole number of hours.
        time_days = time_hours / HOURS_PER_DAY
        whole_number_of_days = math.floor(time_days)
        remaining_time_in_hours = \
            (time_days - whole_number_of_days) * HOURS_PER_DAY

        # HOURS
        # Determine the whole number of hours. Following the same logic
        # employed above.
        whole_number_of_hours = math.floor(remaining_time_in_hours)
        remaining_time_in_seconds = \
            (remaining_time_in_hours - whole_number_of_hours) * \
            SECONDS_PER_HOUR

        # MINUTES and SECONDS
        # Get the whole number of minutes. The difference between the
        # remaining_time_minutes and the whole number of minutes is then
        # used to calculate the number of seconds (i.e. what is left over).
        whole_number_of_minutes = \
            math.floor(remaining_time_in_seconds / SECONDS_PER_MINUTE)
        remaining_seconds = \
            remaining_time_in_seconds - \
            (whole_number_of_minutes * SECONDS_PER_MINUTE)

        # What's left is the number of seconds
        seconds_value = remaining_seconds

        days_value_str = str(int(whole_number_of_days))
        hours_value_str = str(int(whole_number_of_hours))
        minutes_value_str = str(int(whole_number_of_minutes))
        seconds_value_str = str(int(seconds_value))
        # print("days: {} hours: {} minutes: {}".format(days_value_str,
        #                                               hours_value_str,
        #                                               minutes_value_str))

        format_string_split = \
            format_string.split(CYCLE_OFFSET_FORMATTING_DELIMITER)

        # Two- and three-digits for days and hours, minutes and seconds
        # will always be tw0-digit values, unless otherwise specified.
        days_two_digit = days_value_str.zfill(TWO_DIGIT_PAD)
        days_three_digit = days_value_str.zfill(THREE_DIGIT_PAD)
        hours_two_digit = hours_value_str.zfill(TWO_DIGIT_PAD)
        hours_three_digit = hours_value_str.zfill(THREE_DIGIT_PAD)
        MM = minutes_value_str.zfill(TWO_DIGIT_PAD)
        SS = seconds_value_str.zfill(TWO_DIGIT_PAD)
        MMSS = MM + SS

        # Days, hours, minutes and seconds (dHMS)
        if len(format_string_split) == 5:
            if format_string_split[1] == 'dd':
                days = days_two_digit
            elif format_string_split[1] == 'ddd':
                days = days_three_digit
            else:
                self.logger.error(
                        "ERROR | [" + cur_filename + ":" + cur_function + "] | "
                        + "The number of days must be in the format dd where a "
                          "two digit day is required. An  optional 3-digit "
                          "number is also supported.")
                exit(0)

            if format_string_split[2] == 'HH':
                hours = hours_two_digit
            elif format_string_split[2] == 'HHH':
                hours = hours_three_digit

            formatted_time_string = days + '_' + hours + '_' + MM + '_' + SS

        # Days-hours-minutes (dHM) or hours-minutes-seconds (HMS)
        elif len(format_string_split) == 4:
            # Days Hours Minutes (dHM)
            day_flag = False

            # The first formatting element determines whether this is a
            # day-hour-minute (dHM) or hour-minute-second (HMS) format

            # Day Hour Minute
            if format_string_split[1] == 'dd':
                day_flag = True
                days = days_two_digit
            elif format_string_split[1] == 'ddd':
                day_flag = True
                days = days_three_digit

            # Hour Minute Seconds
            elif format_string_split[1] == 'HH':
                hours = hours_two_digit
            elif format_string_split[1] == 'HHH':
                hours = hours_three_digit
            else:
                # The expected dHM or HMS format pattern was not met
                self.logger.error("ERROR | [" + cur_filename + ":" +
                                  cur_function + "] | " + "The time must "
                                                          "" +
                                  "be in the format [ddd][H]HH[MMSS], "
                                  "where a " +
                                  "two digit hour is required.  "
                                  "Providing a " +
                                  "one-,two-, or three-digit hour,  "
                                  "two-digit minutes and two-digit "
                                  "seconds " +
                                  "are optional.")
                exit(0)

            # The hour in the day hour minute (dHM) format
            if format_string_split[2] == 'HH':
                hours = hours_two_digit
            elif format_string_split[2] == 'HHH':
                hours = hours_three_digit

            if day_flag:
                formatted_time_string = days + "_" + hours + MM
            else:
                formatted_time_string = hours + MMSS

        # Days hours (dH) or hours minutes (HM) format
        # Use the day_flag flag to determine whether we have dH or HM format
        # requested.
        elif len(format_string_split) == 3:
            day_flag = False
            # The dH vs HM formats are readily determined based on the first
            # formatting element: d or H.

            # day hour format
            if format_string_split[1] == 'dd':
                days = days_two_digit
                day_flag = True
            elif format_string_split[1] == 'ddd':
                days = days_three_digit
                day_flag = True

            # hour minute format
            elif format_string_split[1] == 'HH':
                hours = hours_two_digit
                day_flag = False
            elif format_string_split[1] == 'HHH':
                hours = hours_three_digit
                day_flag = False
            else:
                # The expected format of day-hour or hour-minute was not met.
                self.logger.error("ERROR | [" + cur_filename + ":" +
                                  cur_function + "] | " +
                                  "The time must be in the format " +
                                  "[ddd][H]HH[MMSS], where a two digit hour "
                                  "is " +
                                  "required.  Providing a one-, two-, "
                                  "or three-digit day, three-digit hour, " +
                                  "two digit minutes and a two-digit seconds" +
                                  " are optional.")
                exit(0)
            # The hour portion of the day hour format
            if format_string_split[2] == 'HH':
                hours = hours_two_digit
            elif format_string_split[2] == 'HHH':
                hours = hours_three_digit

            if day_flag:
                formatted_time_string = days + "_" + hours
            else:
                formatted_time_string = hours + MM

        # Hours only (Empty, HH or HHH)
        elif len(format_string_split) == 2:
            if format_string_split[1] == 'HH':
                hours_str = str(time_hours)
                hours = hours_str.zfill(TWO_DIGIT_PAD)
            elif format_string_split[1] == 'HHH':
                hours_str = str(time_hours)
                hours = hours_str.zfill(THREE_DIGIT_PAD)
            else:
                self.logger.error("ERROR | [" + cur_filename + ":" +
                                  cur_function + "] | " +
                                  "The time must be in the format " +
                                  "[ddd][H]HH[MMSS], where a two digit hour "
                                  "is " +
                                  "required.  Providing a one-, two- or "
                                  "three-digit day, three digit hour, " +
                                  "two digit minutes and a two digit seconds" +
                                  " are optional.")
                exit(0)

            formatted_time_string = hours
        else:
            self.logger.error("ERROR | [" + cur_filename + ":" +
                              cur_function + "] | " +
                              "The time must be in the format " +
                              "[ddd][H]HH[MMSS], where a two digit hour " +
                              "is required.  Providing a one-, two-, " +
                              "or three-digit day, three digit " +
                              "hour, two digit minutes and a two digit " +
                              "seconds are optional.")
            exit(0)

        return formatted_time_string

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
              cyclone:
                fmt - specifies the annual cyclone number as a 2- to 4-digit string.

              region:
                fmt - specifies the region/basin of cyclone.  A 2-character designation:
                      AL|WP|CP|EP|SH|IO|LS Upper or lower case supported.
              date:
                fmt - specifies the date format for a subdirectory in which track
                      data resides.  Recognizes YYYYMM (%Y%m) and YYYYMMDD (%Y%M%d) format.


        """

        cur_filename = sys._getframe().f_code.co_filename
        cur_function = sys._getframe().f_code.co_name

        # The . matches any single character except newline, and the
        # following + matches 1 or more occurrence of preceding expression.
        # The ? after the .+ makes it a lazy match so that it stops
        # after the first "}" instead of continuin to match as many
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
            # Check for init, lead, and valid time in kwargs.
            # If not present, compute.

            # Compute init time
            if (
                    VALID_STRING in self.kwargs and
                    LEAD_STRING in self.kwargs and
                    INIT_STRING not in self.kwargs
            ):
                self.kwargs[INIT_STRING] = self.dateCalcInit()
            # Compute valid time
            elif (
                    INIT_STRING in self.kwargs and
                    LEAD_STRING in self.kwargs and
                    VALID_STRING not in self.kwargs
            ):
                self.kwargs[VALID_STRING] = self.dateCalcValid()
            # Compute valid time for prepbufr file
            elif (
                    INIT_STRING in self.kwargs and
                    CYCLE_STRING in self.kwargs and
                    OFFSET_STRING in self.kwargs and
                    VALID_STRING not in self.kwargs and
                    LEAD_STRING not in self.kwargs
            ):
                self.kwargs[VALID_STRING] = self.calc_valid_for_prepbufr()
            # Compute lead time
            elif (
                    INIT_STRING in self.kwargs and
                    VALID_STRING in self.kwargs and
                    LEAD_STRING not in self.kwargs
            ):
                self.kwargs[LEAD_STRING] = self.dateCalcLead()

            # No times to compute. Just retrieve the string representation(s) of
            # the date (YYMM or YYMMMDD), or date and region, or date, region, and cyclone.
            elif (
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
                
            # Finally, check for misc string, which can occur with any combination of the above
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

                    # split_string[0] holds the key (e.g. "init", "valid", etc)
                    if split_string[0] not in self.kwargs.keys():
                        # Log and continue
                        self.logger.error("ERROR |  [" + cur_filename +
                                          ":" + cur_function + "] | " +
                                          "The key " + split_string[0] +
                                          "does not exist for template: " +
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
                            if (
                                    split_string[0] == VALID_STRING or
                                    split_string[0] == INIT_STRING
                            ):
                                # Get the value of the valid, init, etc. and
                                # convert to a datetime object with the
                                # requested FORMAT_STRING format
                                date_time_value = \
                                    self.kwargs.get(split_string[0], None)
                                dt_obj = \
                                    date_str_to_datetime_obj(date_time_value)
                                # Convert the datetime object back to a
                                # string of the requested format
                                date_time_str = \
                                    dt_obj.strftime(format_split_string[1])

                                # Add back the template identifiers to the
                                # matched string to replace and add the
                                # key, value pair to the dictionary
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN \
                                                    + match + \
                                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = \
                                    date_time_str

                            elif split_string[0] == LEAD_STRING:
                                value = \
                                    self.format_lead_level(LEAD_STRING,
                                                           format_split_string[
                                                               1])
                                string_to_replace = \
                                    TEMPLATE_IDENTIFIER_BEGIN + match + \
                                    TEMPLATE_IDENTIFIER_END

                                replacement_dict[string_to_replace] = value

                            elif split_string[0] == LEVEL_STRING:
                                value = \
                                    self.format_lead_level(LEVEL_STRING,
                                                           format_split_string[
                                                               1])
                                string_to_replace = \
                                    TEMPLATE_IDENTIFIER_BEGIN + match + \
                                    TEMPLATE_IDENTIFIER_END

                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == CYCLE_STRING:
                                value = self.format_cycle_offset(
                                        CYCLE_STRING, format_split_string[1])
                                string_to_replace = \
                                    TEMPLATE_IDENTIFIER_BEGIN + match + \
                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == OFFSET_STRING:
                                value = self.format_cycle_offset(
                                        OFFSET_STRING, format_split_string[1])
                                string_to_replace = \
                                    TEMPLATE_IDENTIFIER_BEGIN + match + \
                                    TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == DATE_STRING:
                                value = self.date
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match\
                                                    + TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == REGION_STRING:
                                value = str(self.region).lower()
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match \
                                                    + TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == CYCLONE_STRING:
                                value = str(self.cyclone)
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match \
                                                    + TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            elif split_string[0] == MISC_STRING:
                                value = str(self.misc)
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match \
                                                    + TEMPLATE_IDENTIFIER_END
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
        self.temp = temp
        self.fstr = fstr

        self.validTime = None
        self.initTime = None
        self.leadTime = -1
        self.levelTime = -1

    def getValidTime(self, fmt):
        if self.validTime is None:
            return ""
        return self.validTime.strftime(fmt)

    def getInitTime(self, fmt):
        if self.initTime is None:
            return ""
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
                        validYear = int(self.fstr[yIdx:yIdx + 4])
                    if mIdx != -1:
                        validMonth = int(self.fstr[mIdx:mIdx + 2])
                    if dIdx != -1:
                        validDay = int(self.fstr[dIdx:dIdx + 2])
                    if hIdx != -1:
                        validHour = int(self.fstr[hIdx:hIdx + 2])
                    if minIdx != -1:
                        validMin = int(self.fstr[minIdx:minIdx + 2])

                    yIdx = -1
                    mIdx = -1
                    dIdx = -1
                    hIdx = -1
                    minIdx = -1
                    inValid = False

                if inInit:
                    if yIdx != -1:
                        initYear = int(self.fstr[yIdx:yIdx + 4])
                    if mIdx != -1:
                        initMonth = int(self.fstr[mIdx:mIdx + 2])
                    if dIdx != -1:
                        initDay = int(self.fstr[dIdx:dIdx + 2])
                    if hIdx != -1:
                        initHour = int(self.fstr[hIdx:hIdx + 2])
                    if minIdx != -1:
                        initMin = int(self.fstr[minIdx:minIdx + 2])

                    yIdx = -1
                    mIdx = -1
                    dIdx = -1
                    hIdx = -1
                    minIdx = -1
                    inInit = False

                elif inLevel:
                    if level == -1:
                        self.logger.error("Invalid level time")
                        return False
                    self.levelTime = int(level) * SECONDS_PER_HOUR
                    level = -1
                    inLevel = False

                elif inLead:
                    if lead == -1:
                        self.logger.error("Invalid lead time")
                        return False
                    self.leadTime = int(lead) * SECONDS_PER_HOUR
                    lead = -1
                    inLead = False

            elif inValid or inInit:
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
