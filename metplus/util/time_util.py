"""
Program Name: time_util.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage: Create a subclass
Parameters: None
Input Files: N/A
Output Files: N/A
"""

import datetime
from dateutil.relativedelta import relativedelta
import re

'''!@namespace TimeInfo
@brief Utility to handle timing in METplus wrappers
@code{.sh}
Cannot be called directly. These are helper functions
to be used in other METplus wrappers
@endcode
'''

# dictionary where key is letter of time unit, i.e. Y and value is
# the string representation of it, i.e. year
TIME_LETTER_TO_STRING = {
    'Y': 'year',
    'm': 'month',
    'd': 'day',
    'H': 'hour',
    'M': 'minute',
    'S': 'second',
}

def get_relativedelta(value, default_unit='S'):
    """!Converts time values ending in Y, m, d, H, M, or S to relativedelta object
        Args:
          @param value time value optionally ending in Y,m,d,H,M,S
            Valid options match format 3600, 3600S, 60M, or 1H
          @param default_unit unit to assume if no letter is found at end of value
          @return relativedelta object containing offset time"""
    if isinstance(value, int):
        return get_relativedelta(str(value), default_unit)

    mult = 1
    reg = r'(-*)(\d+)([a-zA-Z]*)'
    match = re.match(reg, value)
    if match:
        if match.group(1) == '-':
            mult = -1
        time_value = int(match.group(2)) * mult
        unit_value = match.group(3)

        # create relativedelta (dateutil) object for unit
        # if no units specified, use seconds unless default_unit is specified
        if unit_value == '':
            if default_unit == 'S':
                return relativedelta(seconds=time_value)
            else:
                unit_value = default_unit

        if unit_value == 'H':
            return relativedelta(hours=time_value)

        if unit_value == 'M':
            return relativedelta(minutes=time_value)

        if unit_value == 'S':
            return relativedelta(seconds=time_value)

        if unit_value == 'd':
            return relativedelta(days=time_value)

        if unit_value == 'm':
            return relativedelta(months=time_value)

        if unit_value == 'Y':
            return relativedelta(years=time_value)

        # unsupported time unit specified, return None
        return None

def get_seconds_from_string(value, default_unit='S', valid_time=None):
    """!Convert string of time (optionally ending with time letter, i.e. HMSyMD to seconds
        Args:
          @param value string to convert, i.e. 3M, 4H, 17
          @param default_unit units to apply if not specified at end of string
          @returns time in seconds if successfully parsed, None if not"""
    rd_obj = get_relativedelta(value, default_unit)
    return ti_get_seconds_from_relativedelta(rd_obj, valid_time)

def time_string_to_met_time(time_string, default_unit='S'):
    """!Convert time string (3H, 4M, 7, etc.) to format expected by the MET
        tools ([H]HH[MM[SS]])"""
    total_seconds = get_seconds_from_string(time_string, default_unit)
    return seconds_to_met_time(total_seconds)

def seconds_to_met_time(total_seconds):
    seconds_time_string = str(total_seconds % 60).zfill(2)
    minutes_time_string = str(total_seconds // 60 % 60).zfill(2)
    hour_time_string = str(total_seconds // 3600).zfill(2)

    # if hour is 6 or more digits, we need to add minutes and seconds
    # also if minutes and/or seconds they are defined
    # add minutes if seconds are defined as well
    if len(hour_time_string) > 5 or minutes_time_string != '00' or seconds_time_string != '00':
        return hour_time_string + minutes_time_string + seconds_time_string
    else:
        return hour_time_string

def ti_get_hours_from_relativedelta(lead, valid_time=None):
    """! Get hours from relativedelta. Simply calls get seconds function and
         divides the result by 3600.

         @param lead relativedelta object to convert
         @param valid_time (optional) valid time required to convert values
          that contain months or years
         @returns integer value of hours or None if cannot compute
    """
    lead_seconds = ti_get_seconds_from_relativedelta(lead, valid_time)
    if lead_seconds is None:
        return None

    # integer division doesn't handle negative numbers properly
    # (result is always -1) so handle appropriately
    if lead_seconds < 0:
        return - (-lead_seconds // 3600)

    return lead_seconds // 3600

def ti_get_seconds_from_relativedelta(lead, valid_time=None):
    """!Check relativedelta object contents and compute the total number of seconds
        in the time. Return None if years or months are set, because the exact number
        of seconds cannot be calculated without a relative time"""

    # return None if input is not relativedelta object
    if not isinstance(lead, relativedelta):
        return None

    # if valid time is specified, use it to determine seconds
    if valid_time is not None:
        return int((valid_time - (valid_time - lead)).total_seconds())

    if lead.months != 0 or lead.years != 0:
        return None

    total_seconds = 0

    if lead.days != 0:
        total_seconds += lead.days * 86400

    if lead.hours != 0:
        total_seconds += lead.hours * 3600

    if lead.minutes != 0:
        total_seconds += lead.minutes * 60

    if lead.seconds != 0:
        total_seconds += lead.seconds

    return total_seconds

def ti_get_seconds_from_lead(lead, valid='*'):
    if isinstance(lead, int):
        return lead

    if valid == '*':
        valid_time = None
    else:
        valid_time = valid

    return ti_get_seconds_from_relativedelta(lead, valid_time)

def ti_get_hours_from_lead(lead, valid='*'):
    lead_seconds = ti_get_seconds_from_lead(lead, valid)
    if lead_seconds is None:
        return None

    return lead_seconds // 3600

def get_time_suffix(letter, letter_only):
    if letter_only:
        return letter

    return f" {TIME_LETTER_TO_STRING[letter]} "

def format_time_string(lead, letter, plural, letter_only):
    if letter == 'Y':
        value = lead.years
    elif letter == 'm':
        value = lead.months
    elif letter == 'd':
        value = lead.days
    elif letter == 'H':
        value = lead.hours
    elif letter == 'M':
        value = lead.minutes
    elif letter == 'S':
        value = lead.seconds
    else:
        return None

    if value == 0:
        return None

    abs_value = abs(value)
    suffix = get_time_suffix(letter, letter_only)
    output = f"{abs_value}{suffix}"
    if abs_value != 1 and plural and not letter_only:
        output = f"{output.strip()}s "

    return output

def ti_get_lead_string(lead, plural=True, letter_only=False):
    """!Check relativedelta object contents and create string representation
        of the highest unit available (year, then, month, day, hour, minute, second).
        This assumes that only one unit has been set in the object"""
    # if integer, assume seconds
    if isinstance(lead, int):
        return ti_get_lead_string(relativedelta(seconds=lead), plural=plural)

    # return None if input is not relativedelta object
    if not isinstance(lead, relativedelta):
        return None

    # if any of the values are negative, add - before the final result
    if (lead.years < 0 or lead.months < 0 or lead.days < 0 or lead.hours < 0 or
            lead.minutes < 0 or lead.seconds < 0):
        negative = '-'
    else:
        negative = ''

    output_list = []
    for time_letter in TIME_LETTER_TO_STRING.keys():
        output = format_time_string(lead, time_letter, plural, letter_only)
        if output is not None:
            output_list.append(output)

    # if nothing was found, return 0 hour(s) or 0H
    if not output_list:
        if letter_only:
            return '0H'

        return f"0 hour{'s' if plural else ''}"

    output = ''.join(output_list)
    # remove whitespace from beginning and end of string
    output = output.strip()

    return f"{negative}{output}"

def ti_calculate(input_dict_preserve):
    out_dict = {}
    input_dict = input_dict_preserve.copy()

    KEYS_TO_COPY = ['custom', 'instance']

    # set output dictionary to input items
    if 'now' in input_dict.keys():
        out_dict['now'] = input_dict['now']
        out_dict['today'] = out_dict['now'].strftime('%Y%m%d')

    # copy over values of some keys if it is set in input dictionary
    for key in KEYS_TO_COPY:
        if key in input_dict.keys():
            out_dict[key] = input_dict[key]

    # read in input dictionary items and compute missing items
    # valid inputs: valid, init, lead, offset

    # look for forecast lead information in input
    # set forecast lead to 0 if not specified
    if 'lead' in input_dict.keys():
        # if lead is relativedelta, pass it through
        # if lead is not, treat it as seconds
        if isinstance(input_dict['lead'], relativedelta):
            out_dict['lead'] = input_dict['lead']
        elif input_dict['lead'] == '*':
            out_dict['lead'] = input_dict['lead']
        else:
            out_dict['lead'] = relativedelta(seconds=input_dict['lead'])

    elif 'lead_seconds' in input_dict.keys():
        out_dict['lead'] = relativedelta(seconds=input_dict['lead_seconds'])

    elif 'lead_minutes' in input_dict.keys():
        out_dict['lead'] = relativedelta(minutes=input_dict['lead_minutes'])

    elif 'lead_hours' in input_dict.keys():
        lead_hours = int(input_dict['lead_hours'])
        lead_days = 0
        # if hours is more than a day, pull out days and relative hours
        if lead_hours > 23:
            lead_days = lead_hours // 24
            lead_hours = lead_hours % 24

        out_dict['lead'] = relativedelta(hours=lead_hours, days=lead_days)

    else:
        out_dict['lead'] = relativedelta(seconds=0)


    # set offset to 0 if not specified
    if 'offset_hours' in input_dict.keys():
        out_dict['offset'] = datetime.timedelta(hours=input_dict['offset_hours'])
    elif 'offset' in input_dict.keys():
        out_dict['offset'] = datetime.timedelta(seconds=input_dict['offset'])
    else:
        out_dict['offset'] = datetime.timedelta(seconds=0)


    # if init and valid are set, check which was set first via loop_by
    # remove the other to recalculate
    if 'init' in input_dict.keys() and 'valid' in input_dict.keys():
        if 'loop_by' in input_dict.keys():
            if input_dict['loop_by'] == 'init':
                del input_dict['valid']
            elif input_dict['loop_by'] == 'valid':
                del input_dict['init']

    if 'init' in input_dict.keys():
        out_dict['init'] = input_dict['init']

        if 'valid' in input_dict.keys():
            print("ERROR: Cannot specify both valid and init to time utility")
            return None

        # compute valid from init and lead if lead is not wildcard
        if out_dict['lead'] == '*':
            out_dict['valid'] = '*'
        else:
            out_dict['valid'] = out_dict['init'] + out_dict['lead']

        # set loop_by to init or valid to be able to see what was set first
        out_dict['loop_by'] = 'init'

    # if valid is provided, compute init and da_init
    elif 'valid' in input_dict:
        out_dict['valid'] = input_dict['valid']

        # compute init from valid and lead if lead is not wildcard
        if out_dict['lead'] == '*':
            out_dict['init'] = '*'
        else:
            out_dict['init'] = out_dict['valid'] - out_dict['lead']

        # set loop_by to init or valid to be able to see what was set first
        out_dict['loop_by'] = 'valid'

    # if da_init is provided, compute init and valid
    elif 'da_init' in input_dict.keys():
        out_dict['da_init'] = input_dict['da_init']

        if 'valid' in input_dict.keys():
            print("ERROR: Cannot specify both valid and da_init to time utility")
            return None

        # compute valid from da_init and offset
        out_dict['valid'] = out_dict['da_init'] - out_dict['offset']

        # compute init from valid and lead if lead is not wildcard
        if out_dict['lead'] == '*':
            out_dict['init'] = '*'
        else:
            out_dict['init'] = out_dict['valid'] - out_dict['lead']
    else:
        print("ERROR: Need to specify valid, init, or da_init to time utility")
        return None

    # calculate da_init from valid and offset
    if out_dict['valid'] != '*':
        out_dict['da_init'] = out_dict['valid'] + out_dict['offset']

        # add common formatted items
        out_dict['da_init_fmt'] = out_dict['da_init'].strftime('%Y%m%d%H%M%S')
        out_dict['valid_fmt'] = out_dict['valid'].strftime('%Y%m%d%H%M%S')

    if out_dict['init'] != '*':
        out_dict['init_fmt'] = out_dict['init'].strftime('%Y%m%d%H%M%S')

    # get string representation of forecast lead
    if out_dict['lead'] == '*':
        out_dict['lead_string'] = 'ALL'
    else:
        out_dict['lead_string'] = ti_get_lead_string(out_dict['lead'])

    out_dict['offset'] = int(out_dict['offset'].total_seconds())
    out_dict['offset_hours'] = int(out_dict['offset'] // 3600)

    # set synonyms for items
    if 'da_init' in out_dict:
        out_dict['date'] = out_dict['da_init']
        out_dict['cycle'] = out_dict['da_init']

    # if lead is wildcard, skip updating other lead values
    if out_dict['lead'] == '*':
        return out_dict

    # get difference between valid and init to get total seconds since relativedelta
    # does not have a fixed number of seconds
    total_seconds = int((out_dict['valid'] - out_dict['init']).total_seconds())

    # change relativedelta to integer seconds unless months or years are used
    # if they are, keep lead as a relativedelta object to be handled differently
    if out_dict['lead'].months == 0 and out_dict['lead'].years == 0:
        out_dict['lead'] = total_seconds

    # add common uses for relative times
    # Specifying integer division // Python 3,
    # assuming that was the intent in Python 2.
    out_dict['lead_hours'] = int(total_seconds // 3600)
    out_dict['lead_minutes'] = int(total_seconds // 60)
    out_dict['lead_seconds'] = total_seconds

    return out_dict
