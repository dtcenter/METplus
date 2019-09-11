#!/usr/bin/env python

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

from __future__ import (print_function, division)

import datetime
from dateutil.relativedelta import relativedelta

'''!@namespace TimeInfo
@brief Utility to handle timing in METplus wrappers
@code{.sh}
Cannot be called directly. These are helper functions
to be used in other METplus wrappers
@endcode
'''

def ti_get_seconds_from_relativedelta(lead):
    """!Check relativedelta object contents and compute the total number of seconds
        in the time. Return None if years or months are set, because the exact number
        of seconds cannot be calculated without a relative time"""
    # return None if input is not relativedelta object
    if not isinstance(lead, relativedelta) or lead.months != 0 or lead.years != 0:
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

def ti_get_lead_string(lead):
    """!Check relativedelta object contents and create string representation
        of the highest unit available (year, then, month, day, hour, minute, second).
        This assumes that only one unit has been set in the object"""
    # return None if input is not relativedelta object
    if not isinstance(lead, relativedelta):
        return

    output = ''
    if lead.years != 0:
        output += f' {lead.years} year'
        if abs(lead.years) != 1:
            output += 's'

    if lead.months != 0:
        output += f' {lead.months} month'
        if abs(lead.months) != 1:
            output += 's'

    if lead.days != 0:
        output += f' {lead.days} day'
        if abs(lead.days) != 1:
            output += 's'

    if lead.hours != 0:
        output += f' {lead.hours} hour'
        if abs(lead.hours) != 1:
            output += 's'

    if lead.minutes != 0:
        output += f' {lead.minutes} minute'
        if abs(lead.minutes) != 1:
            output += 's'

    if lead.seconds != 0:
        output += f' {lead.seconds} second'
        if abs(lead.seconds) != 1:
            output += 's'

    # remove leading space and return string
    if output != '':
        return output[1:]

    # return 0 hour if no time units are set
    return '0 hours'

def ti_calculate(input_dict):
    out_dict = {}

    # set output dictionary to input items
    if 'now' in input_dict.keys():
        out_dict['now'] = input_dict['now']
        out_dict['today'] = out_dict['now'].strftime('%Y%m%d')

    # read in input dictionary items and compute missing items
    # valid inputs: valid, init, lead, offset

    # look for forecast lead information in input
    # set forecast lead to 0 if not specified
    if 'lead' in input_dict.keys():
        # if lead is relativedelta, pass it through
        # if lead is not, treat it as seconds
        if isinstance(input_dict['lead'], relativedelta):
            out_dict['lead'] = input_dict['lead']
        else:
            out_dict['lead'] = relativedelta(seconds=input_dict['lead'])

    elif 'lead_seconds' in input_dict.keys():
        out_dict['lead'] = relativedelta(seconds=input_dict['lead_seconds'])

    elif 'lead_minutes' in input_dict.keys():
        out_dict['lead'] = relativedelta(minutes=input_dict['lead_minutes'])

    elif 'lead_hours' in input_dict.keys():
        out_dict['lead'] = relativedelta(hours=input_dict['lead_hours'])

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
            exit(1)

        # compute valid from init and lead
        out_dict['valid'] = out_dict['init'] + out_dict['lead']

        # set loop_by to init or valid to be able to see what was set first
        out_dict['loop_by'] = 'init'
        
    # if valid is provided, compute init and da_init
    elif 'valid' in input_dict:
        out_dict['valid'] = input_dict['valid']

        # compute init from valid and lead
        out_dict['init'] = out_dict['valid'] - out_dict['lead']

        # set loop_by to init or valid to be able to see what was set first
        out_dict['loop_by'] = 'valid'

    # if da_init is provided, compute init and valid
    elif 'da_init' in input_dict.keys():
        out_dict['da_init'] = input_dict['da_init']

        if 'valid' in input_dict.keys():
            print("ERROR: Cannot specify both valid and da_init to time utility")
            exit(1)

        # compute valid from da_init and offset
        out_dict['valid'] = out_dict['da_init'] - out_dict['offset']

        # compute init from valid and lead
        out_dict['init'] = out_dict['valid'] - out_dict['lead']
    else:
        print("ERROR: Need to specify valid, init, or da_init to time utility")
        exit(1)

    # calculate da_init from valid and offset
    out_dict['da_init'] = out_dict['valid'] + out_dict['offset']

    # add common formatted items
    out_dict['init_fmt'] = out_dict['init'].strftime('%Y%m%d%H%M')
    out_dict['da_init_fmt'] = out_dict['da_init'].strftime('%Y%m%d%H%M')
    out_dict['valid_fmt'] = out_dict['valid'].strftime('%Y%m%d%H%M')

    # get difference between valid and init to get total seconds since relativedelta
    # does not have a fixed number of seconds
    total_seconds = int( (out_dict['valid'] - out_dict['init']).total_seconds() )

    # get string representation of forecast lead
    out_dict['lead_string'] = ti_get_lead_string(out_dict['lead'])

    # change relativedelta to integer seconds unless months or years are used
    # if they are, keep lead as a relativedelta object to be handled differently
    if out_dict['lead'].months == 0 and out_dict['lead'].years == 0:
        out_dict['lead'] = total_seconds

    out_dict['offset'] = int(out_dict['offset'].total_seconds())

    # add common uses for relative times
    # Specifying integer division // Python 3,
    # assuming that was the intent in Python 2.
    out_dict['lead_hours'] = int(total_seconds // 3600)
    out_dict['lead_minutes'] = int(total_seconds // 60)
    out_dict['lead_seconds'] = total_seconds
    out_dict['offset_hours'] = int(out_dict['offset'] // 3600)

    # set synonyms for items
    out_dict['date'] = out_dict['da_init']
    out_dict['cycle'] = out_dict['da_init']

    return out_dict
