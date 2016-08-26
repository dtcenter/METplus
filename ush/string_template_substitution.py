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

import os
import re
import datetime
import time
import calendar
import math

TEMPLATE_IDENTIFIER_BEGIN = "{"
TEMPLATE_IDENTIFIER_END = "}"

FORMATTING_DELIMITER = "?"
FORMATTING_VALUE_DELIMITER = "="
FORMAT_STRING = "fmt"

VALID_STRING = "valid"
LEAD_STRING = "lead"
INIT_STRING = "init"
ACCUM_STRING = "accum"

LEAD_ACCUM_FORMATTING_DELIMITER = "%"

SECONDS_PER_HOUR = 3600
MINUTES_PER_HOUR = 60
SECONDS_PER_MINUTE = 60

TWO_DIGIT_PAD = 2
THREE_DIGIT_PAD = 3

def date_str_to_datetime_obj(str):
    
    """Convert year month day string to a datetime object. Works with YYYYMMDDHHMMSS, YYYYMMDDHHMM, YYYYMMDDHH, YYYYMMDD"""

    length = len(str)
    if length == 14:
        return datetime.datetime(int(str[:4]), int(str[4:6]), int(str[6:8]), int(str[8:10]), int(str[10:12]), int(str[12:14]), 0, None)
    elif length == 8:
        return datetime.datetime(int(str[:4]), int(str[4:6]), int(str[6:8]), 0, 0, 0, 0, None)
    elif length == 10:
        return datetime.datetime(int(str[:4]), int(str[4:6]), int(str[6:8]), int(str[8:10]), 0, 0, 0, None)
    elif length == 12:
        return datetime.datetime(int(str[:4]), int(str[4:6]), int(str[6:8]), int(str[8:10]), int(str[10:12]), 0, 0, None)       
    

def multiple_replace(dict, text): 

  """ Replace in 'text' all occurences of any key in the given dictionary by its corresponding value.  Returns the new string. """

  # Create a regular expression  from the dictionary keys
  regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

  # For each match, look-up corresponding value in dictionary
  return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

def get_lead_accum_time_seconds(time_string):

    """ Returns the number of seconds for the time string in the format [H]HH[MMSS]"""

    # HH
    if len(time_string) == 2:
        return (int(time_string) * SECONDS_PER_HOUR)
    # HHH
    elif len(time_string) == 3:
        return (int(time_string) * SECONDS_PER_HOUR)
    # HHMM
    elif len(time_string) == 4:
        return ((int(time_string[0:2]) * SECONDS_PER_HOUR) + (int(time_string[2:4]) * MINUTES_PER_HOUR))
    # HHHMM
    elif len(time_string) == 5:
        return ((int(time_string[0:3]) * SECONDS_PER_HOUR) + (int(time_string[3:5]) * MINUTES_PER_HOUR))
    # HHMMSS
    elif len(time_string) == 6:
        return ((int(time_string[0:2]) * SECONDS_PER_HOUR) + (int(time_string[2:4]) * MINUTES_PER_HOUR) + int(time_string[4:6]))
    # HHHMMSS
    elif len(time_string) == 7:
        return ((int(time_string[0:3]) * SECONDS_PER_HOUR) + (int(time_string[3:5]) * MINUTES_PER_HOUR) + int(time_string[5:7]))
    else:
        print("The time must be in the format [H]HH[MMSS], where a two digit hour is required.  Providing a three digit hour, two digit minutes and a two digit seconds are optional.")         
        exit(0)
        
class StringTemplateSubstitution:
    """
    tmpl_str - template string to populate
    kwargs - dictionary containing values for each template key

    This class provides functionality for substituting values for
    string templates.
    
    Possible keys for vals:
       init - must be in YYYYmmddHH[MMSS] format
       valid - must be in YYYYmmddHH[MMSS] format
       lead - must be in HH[MMSS] format
       accum - must be in HH[MMSS] fomrat
       level - the level number as a string (?)
       model - the name of the model
       domain - the domain number (01, 02, etc.) read in as a string

    See the description of doStringSub for further details.
       
    """

    def __init__(self, tmpl, **kwargs):

        self.tmpl = tmpl
        self.kwargs = kwargs
    
        if self.kwargs is not None:
            for key, value in kwargs.iteritems():
                #print("%s == %s" % (key, value))
                setattr(self, key, value)

        self.lead_time_seconds = 0
        self.accum_time_seconds = 0
        self.negative_lead = False
        self.negative_accum = False

        if (LEAD_STRING in self.kwargs):
            self.lead_time_seconds =  get_lead_accum_time_seconds((self.kwargs).get(LEAD_STRING, None))
        if (ACCUM_STRING in self.kwargs):
            self.accum_time_seconds =  get_lead_accum_time_seconds((self.kwargs).get(ACCUM_STRING, None))

        

    def dateCalcInit(self):

        """ Calculate the init time from the valid and lead time  """

        # Get the unix time for the valid time
        if len((self.kwargs).get(VALID_STRING, None)) == 10:
            valid_time_tuple = time.strptime((self.kwargs).get(VALID_STRING, None), "%Y%m%d%H")
        elif len((self.kwargs).get(VALID_STRING, None)) == 12:
            valid_time_tuple = time.strptime((self.kwargs).get(VALID_STRING, None), "%Y%m%d%H%M")
        elif len((self.kwargs).get(VALID_STRING, None)) == 14:
            valid_time_tuple = time.strptime((self.kwargs).get(VALID_STRING, None), "%Y%m%d%H%M%S")
        else:
            print("Valid time must be in the format YYYYmmddHH[MMSS]. Valid time currently = ", (self.kwargs).get(VALID_STRING, None))
            exit(0)

        valid_unix_time = calendar.timegm(valid_time_tuple)

        # Get the number of seconds for the lead time
        self.lead_time_seconds = get_lead_accum_time_seconds((self.kwargs).get(LEAD_STRING, None))

        init_unix_time = valid_unix_time - self.lead_time_seconds
        init_time = time.strftime("%Y%m%d%H%M%S", time.gmtime(init_unix_time))

        return init_time

    def dateCalcValid(self):

        """ Calculate the valid time from the init and lead time  """
             
        # Get the unix time for the init time
        if len((self.kwargs).get(INIT_STRING, None)) == 10:
            init_time_tuple = time.strptime((self.kwargs).get(INIT_STRING, None), "%Y%m%d%H")
        elif len((self.kwargs).get(INIT_STRING, None)) == 12:
            init_time_tuple = time.strptime((self.kwargs).get(INIT_STRING, None), "%Y%m%d%H%M")
        elif len((self.kwargs).get(INIT_STRING, None)) == 14:
            init_time_tuple = time.strptime((self.kwargs).get(INIT_STRING, None), "%Y%m%d%H%M%S")
        else:
            print("Init time must be in the format YYYYmmddHH[MMSS]. Init time currently = ", (self.kwargs).get(INIT_STRING, None))
            exit(0)

        init_unix_time = calendar.timegm(init_time_tuple)

        # Get the number of seconds for the lead time
        self.lead_time_seconds = get_lead_accum_time_seconds((self.kwargs).get(LEAD_STRING, None))

        valid_unix_time = init_unix_time + self.lead_time_seconds
        valid_time = time.strftime("%Y%m%d%H%M%S", time.gmtime(valid_unix_time))
        
        return valid_time

    def dateCalcLead(self):

        """ Calculate the lead time from the init and valid time """
             
        # Get the unix time for the init time
        if len((self.kwargs).get(INIT_STRING, None)) == 10:
            init_time_tuple = time.strptime((self.kwargs).get(INIT_STRING, None), "%Y%m%d%H")
        elif len((self.kwargs).get(INIT_STRING, None)) == 12:
            init_time_tuple = time.strptime((self.kwargs).get(INIT_STRING, None), "%Y%m%d%H%M")
        elif len((self.kwargs).get(INIT_STRING, None)) == 14:
            init_time_tuple = time.strptime((self.kwargs).get(INIT_STRING, None), "%Y%m%d%H%M%S")
        else:
            print("Init time must be in the format YYYYmmddHH[MMSS]. Init time currently = ", (self.kwargs).get(INIT_STRING, None))
            exit(0)
        init_unix_time = calendar.timegm(init_time_tuple)

        
        # Get the unix time for the valid time
        if len((self.kwargs).get(VALID_STRING, None)) == 10:
            valid_time_tuple = time.strptime((self.kwargs).get(VALID_STRING, None), "%Y%m%d%H")
        elif len((self.kwargs).get(VALID_STRING, None)) == 12:
            valid_time_tuple = time.strptime((self.kwargs).get(VALID_STRING, None), "%Y%m%d%H%M")
        elif len((self.kwargs).get(VALID_STRING, None)) == 14:
            valid_time_tuple = time.strptime((self.kwargs).get(VALID_STRING, None), "%Y%m%d%H%M%S")
        else:
            print("Valid time must be in the format YYYYmmddHH[MMSS]. Valid time currently = ", (self.kwargs).get(VALID_STRING, None))
            exit(0)
        valid_unix_time = calendar.timegm(valid_time_tuple)

        # Determine if the init time is greater than the lead time, if so lead time should be negative
        negative_lead_flag = 0
        if (valid_unix_time > init_unix_time):
            self.lead_time_seconds = valid_unix_time - init_unix_time
        else:
            self.lead_time_seconds = init_unix_time - valid_unix_time
            negative_lead_flag = 1
            self.negative_lead = True
        lead_seconds_str = str(datetime.timedelta(seconds=(self.lead_time_seconds)))
        
        # There are no days, but only HH:MM:SS information
        if len(lead_seconds_str) <= 8:
            HH,MM,SS = lead_seconds_str.split(":")
            lead_time = HH.zfill(TWO_DIGIT_PAD) + MM + SS
        # There are days in addition to HH:MM:SS information
        elif len(lead_seconds_str) > 8:
            # e.g. '4 days, 23:35:00' split on comma and get first value
            lead_seconds_str_split_comma = lead_seconds_str.split(",")
            # e.g. '4 days' split on space and get first value
            lead_seconds_str_split_space = lead_seconds_str_split_comma[0].split(" ")
            # Convert the number of days to hours
            days_to_hours = int(lead_seconds_str_split_space[0]) * 24
            # Get string values for the hours, minutes, seconds
            HH,MM,SS = lead_seconds_str.split(":")
            # e.g. '4 days, 23' split on comma and get second value
            HH_split = HH.split(", ")
            # Convert the hours string to an integer and add to the days in hours
            HH = int(HH_split[1])
            total_hours = days_to_hours + int(HH)
            # Put together the lead_time string in the format [H]HH[MMSS]
            lead_time = str(total_hours) + MM + SS
            
        # If the init time was greater than the valid time, the lead time should be negative
        if (negative_lead_flag == 1):
            lead_time = "-" + lead_time
        
        return lead_time

    def leadAccumStringFormat(self, parm_type, format_string):

        """ Formats the lead or accum in the requested format """
        
        formatted_time_string = ""
        time_seconds = 0
        negative_flag = False
        
        if (parm_type == LEAD_STRING):
            time_seconds = self.lead_time_seconds
            negative_flag = self.negative_lead
        elif (parm_type == ACCUM_STRING):
            time_seconds = self.accum_time_seconds
            negative_flag = self.negative_accum
        else:
            # Log and exit
            print("Invalid parm_type of %s.  Acceptable parm types are lead and accum.", parm_type)


        hours_value = math.floor(time_seconds / SECONDS_PER_HOUR)
        time_seconds = time_seconds - (hours_value * SECONDS_PER_HOUR)
        minutes_value = math.floor(time_seconds / MINUTES_PER_HOUR)
        time_seconds = time_seconds - (minutes_value * MINUTES_PER_HOUR)
        seconds_value = time_seconds

        hours_value_str = str(int(hours_value))
        minutes_value_str = str(int(minutes_value))
        seconds_value_str = str(int(seconds_value))
        
        format_string_split = format_string.split(LEAD_ACCUM_FORMATTING_DELIMITER)

        # Minutes and seconds should be included (Empty, HH or HHH, MMSS)
        if (len(format_string_split) == 3):
            MM = minutes_value_str.zfill(TWO_DIGIT_PAD)
            SS = seconds_value_str.zfill(TWO_DIGIT_PAD)
            MMSS = MM + SS
            if (format_string_split[1] == 'HH'):
                hours = hours_value_str.zfill(TWO_DIGIT_PAD)
                if (len(hours) == 3):
                    print("The requested hours formatting was %s, but the hours given are: %s. Returning a three digit hour." % (format_string_split[1], hours) )                   
            elif (format_string_split[1] == 'HHH'):
                hours = hours_value_str.zfill(THREE_DIGIT_PAD)
            else:
                print("The time must be in the format [H]HH[MMSS], where a two digit hour is required.  Providing a three digit hour, two digit minutes and a two digit seconds are optional.")         
                exit(0)
            
            formatted_time_string = hours + MMSS

        # Only hours should be included (Empty, HH or HHH)
        elif (len(format_string_split) == 2):
            if (format_string_split[1] == 'HH'):
                hours = hours_value_str.zfill(TWO_DIGIT_PAD)
                if (len(hours) == 3):
                    print("The requested hours formatting was %s, but the hours given are: %s. Returning a three digit hour." % (format_string_split[1], hours) )                   
            elif (format_string_split[1] == 'HHH'):
                hours = hours_value_str.zfill(THREE_DIGIT_PAD)
            else:
                print("The time must be in the format [H]HH[MMSS], where a two digit hour is required.  Providing a three digit hour, two digit minutes and a two digit seconds are optional.")         
                exit(0)

            formatted_time_string = hours

        else:
            print("The time must be in the format [H]HH[MMSS], where a two digit hour is required.  Providing a three digit hour, two digit minutes and a two digit seconds are optional.")         
            exit(0)

        if negative_flag:
            formatted_time_string = "-" + formatted_time_string
            
        return formatted_time_string
        
    def doStringSub(self):

        """ Populates the specified template with information from the kwargs dictionary.  The template
            structure is compresed of a fixed string populated with template place-holders inside curly
            braces, for example {tmpl_str}.  The tmpl_str must be present as a key in the kwargs
            dictionary, and the value will replace the {tmpl_str} in the returned string.

            In some cases, the template keys can have parameters containing formatting information.  The
            format of the template in this case is {tmpl_str?parm=val}.  The supported parameters are:

              init, valid:
                fmt - specifies a strftime format for the date/time
                      e.g. %Y%m%d%H%M%S, %Y%m%d%H
                
              lead, accum:
                fmt -  specifies an amount of time in [H]HH[MMSS] format
                       e.g. %HH, %HHH, %HH%MMSS, %HHH%MMSS 

        """
        
        # The . matches any single character except newline, and the following +
        # matches 1 or more occurrence of preceding expression.
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

        # Dictionary used to replace matches with the appropriate value
        match_replace = {}
        
        if match_list == 0:
            
            # Log and exit
            print "No matches found"

        elif len(match_list) != len(match_start_end_list):
                
            # Log and exit
            print "match_list and match_start_end_list should have the same length"
            
        else:
            
            # Check for init, lead, and valid time in kwargs.  If not present, compute.
            
            # Compute init time
            if ((VALID_STRING in self.kwargs and LEAD_STRING in self.kwargs) and not (INIT_STRING in self.kwargs)):
                self.kwargs[INIT_STRING] = self.dateCalcInit()
                
            # Compute valid time                
            elif ((INIT_STRING in self.kwargs and LEAD_STRING in self.kwargs) and not (VALID_STRING in self.kwargs)):
                self.kwargs[VALID_STRING] = self.dateCalcValid()
                
            # Compute lead time
            elif ((INIT_STRING in self.kwargs and VALID_STRING in self.kwargs) and not (LEAD_STRING in self.kwargs)):
                self.kwargs[LEAD_STRING] = self.dateCalcLead()
                #print("self.lead_time_seconds: ", self.lead_time_seconds)
                # Data is put into self.lead_time_seconds
                #self.dateCalcLead()
            #print self.kwargs[LEAD_STRING]

            # A dictionary that will contain the string to replace (key) and the string to replace it with (value)    
            replacement_dict = {}

            # Search for the FORMATTING_DELIMITER, currently ?, within the first string
            for index,match in enumerate(match_list):
                
                split_string = match.split(FORMATTING_DELIMITER)

                # valid, init, lead, etc.
                #print split_string[0]
                # value e.g. 2016012606, 3
                #print (self.kwargs).get(split_string[0], None)                
                
                # Formatting is requested or length is requested
                if len(split_string) == 2:

                    # split_string[0] holds the key (e.g. "init", "valid", etc.)
                    if split_string[0] not in (self.kwargs).keys():
                        # Log and continue
                        print "Some message about key not in key/value pair: ", split_string[0]

                    # Key is in the dictionary
                    else:
                        
                        # Check for formating/length request by splitting on FORMATTING_VALUE_DELIMITER
                        # split_string[1] holds the formatting/length information (e.g. "fmt=%Y%m%d", "len=3")
                        format_split_string = split_string[1].split(FORMATTING_VALUE_DELIMITER)
                        
                        # Check for requested FORMAT_STRING
                        # format_split_string[0] holds the formatting/length value delimiter (e.g. "fmt", "len")
                        if format_split_string[0] == FORMAT_STRING:

                            if ((split_string[0] == VALID_STRING) or (split_string[0] == INIT_STRING)):
                                # Get the value of the valid, init, etc. and convert to a datetime object with the requested FORMAT_STRING format
                                date_time_value = (self.kwargs).get(split_string[0], None)
                                dt_obj = date_str_to_datetime_obj(date_time_value)
                                # Convert the dateime object back to a string of the requested format
                                date_time_str = dt_obj.strftime(format_split_string[1])

                                # Add back the template identifiers to the matched string to replace and add the key, value pair to the dictionary
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match + TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = date_time_str

                            elif (split_string[0] == LEAD_STRING):
                                value = self.leadAccumStringFormat(LEAD_STRING, format_split_string[1])
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match + TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value

                            elif (string_string[0] == ACCUM_STRING):
                                value = self.leadAccumStringFormat(ACCUM_STRING, format_split_string[1])
                                string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match + TEMPLATE_IDENTIFIER_END
                                replacement_dict[string_to_replace] = value
                            
                # No formatting or length is requested            
                elif len(split_string) == 1:

                    # Add back the template identifiers to the matched string to replace and add the key, value pair to the dictionary
                    string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match + TEMPLATE_IDENTIFIER_END
                    replacement_dict[string_to_replace] = (self.kwargs).get(split_string[0], None)
                            
            # Replace regex with properly formatted information
            temp_str = multiple_replace(replacement_dict, self.tmpl)
            self.tmpl = temp_str
            return self.tmpl
    
    
if __name__ == "__main__":
    main()
