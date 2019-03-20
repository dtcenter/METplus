#!/usr/bin/env python

'''
Program Name: time_util.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage: Create a subclass
Parameters: None
Input Files: N/A
Output Files: N/A
'''

from __future__ import (print_function, division)

import datetime


'''!@namespace TimeInfo
@brief Utility to handle timing in METplus wrappers
@code{.sh}
Cannot be called directly. These are helper functions
to be used in other METplus wrappers
@endcode
'''
def ti_calculate(input_dict):
    out_dict = {}

    # set output dictionary to input items
    if 'now' in input_dict.keys():
        out_dict['now'] = input_dict['now']
        out_dict['today'] = out_dict['now'].strftime('%Y%m%d')

    # read in input dictionary items and compute missing items
    # valid inputs: valid, init, lead, offset

    # set forecast lead to 0 if not specified
    if 'lead_hours' in input_dict.keys():
        out_dict['lead'] = datetime.timedelta(hours=input_dict['lead_hours'])
    elif 'lead_minutes' in input_dict.keys():
        out_dict['lead'] = datetime.timedelta(minutes=input_dict['lead_minutes'])
    elif 'lead_seconds' in input_dict.keys():
        out_dict['lead'] = datetime.timedelta(seconds=input_dict['lead_seconds'])
    elif 'lead' in input_dict.keys():
        out_dict['lead'] = datetime.timedelta(seconds=input_dict['lead'])
    else:
        out_dict['lead'] = datetime.timedelta(seconds=0)

    # set offset to 0 if not specified
    if 'offset' in input_dict.keys():
        out_dict['offset'] = datetime.timedelta(hours=input_dict['offset'])
    else:
        out_dict['offset'] = datetime.timedelta(seconds=0)

    if 'init' in input_dict.keys():
        out_dict['init'] = input_dict['init']

        if 'valid' in input_dict.keys():
            print("ERROR: Cannot specify both valid and init to time utility")
            exit(1)

        # compute valid from init and lead
        out_dict['valid'] = out_dict['init'] + out_dict['lead']
        
    # if valid is provided, compute init and da_init
    elif 'valid' in input_dict:
        out_dict['valid'] = input_dict['valid']

        # compute init from valid and lead
        out_dict['init'] = out_dict['valid'] - out_dict['lead']
    else:
        print("ERROR: Need to specify valid or init to time utility")
        exit(1)

    # calculate da_init from valid and offset
    out_dict['da_init'] = out_dict['valid'] - out_dict['offset']
        
    # add common formatted items
    out_dict['init_fmt'] = out_dict['init'].strftime('%Y%m%d%H%M')
    out_dict['da_init_fmt'] = out_dict['da_init'].strftime('%Y%m%d%H%M')
    out_dict['valid_fmt'] = out_dict['valid'].strftime('%Y%m%d%H%M')

    # change timedelta to integer
    total_seconds = int(out_dict['lead'].total_seconds())
    out_dict['lead'] = total_seconds
    out_dict['offset'] = int(out_dict['offset'].total_seconds())

    # add common uses for relative times
    out_dict['lead_hours'] = int(total_seconds / 3600)
    out_dict['lead_minutes'] = int(total_seconds / 60)
    out_dict['lead_seconds'] = total_seconds
    out_dict['offset_hours'] = int(out_dict['offset'] / 3600)

    # set synonyms for items
    out_dict['date'] = out_dict['da_init']
    out_dict['cycle'] = out_dict['da_init']

    return out_dict
    
        
