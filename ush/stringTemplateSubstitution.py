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

TEMPLATE_IDENTIFIER_BEGIN = "{"
TEMPLATE_IDENTIFIER_END = "}"

FORMATTING_DELIMITER = "?"
FORMATTING_VALUE_DELIMITER = "="
FORMAT_STRING = "fmt"
LENGTH_STRING = "len"

VALID_STRING = "valid"
LEAD_STRING = "lead"
INIT_STRING = "init"

SECONDS_PER_HOUR = 3600
MINUTES_PER_HOUR = 60
SECONDS_PER_MINUTE = 60

TWO_DIGIT_PAD = 2

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

def time_str_to_time_tuple(time_str, format):
    
    """Convert year month day string to a datetime object. Works with [H]HH[MMSS]"""

    # Using %HH but need %H for two digits...
    
    int_time_str = int(time_str)
    time_string = str(int_time_str)
    
    # HH
    if len(time_str) == 2:
        #return datetime.datetime(None, None, None, int(str), 0, 0, 0, None)
        return time.strptime(time_string, format)
    # HHH
    elif len(time_str) == 3:
        return 
    # HHMM
    elif len(time_str) == 4:
        #return datetime.datetime(0, 0, 0, int(str[0:2]), int(str[2:4]), 0, 0, None)
        return time.strptime(time_string, format)
    # HHHMM
    elif len(time_str) == 5:
        return 
    # HHMMSS
    elif lentime_(str) == 6:
        #return datetime.datetime(0, 0, 0, int(str[0:2]), int(str[2:4]), int(str[4:6]), 0, None)
        return time.strptime(time_string, format)
    # HHHMMSS
    elif len(time_str) == 7:
        return 
    else:
        print("Lead time must be in the format [H]HH[MMSS], where a two digit hour is required.  Providing a three digit hour, two digit minutes and a two digit seconds are optional.")         
        exit(0)
        
    

def multiple_replace(dict, text): 

  """ Replace in 'text' all occurences of any key in the given dictionary by its corresponding value.  Returns the new string. """

  # Create a regular expression  from the dictionary keys
  regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

  # For each match, look-up corresponding value in dictionary
  return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

def get_lead_time_seconds(lead_time_string):

    """ Returns the number of seconds for the lead time string in the format [H]HH[MMSS]"""

    # HH
    if len(lead_time_string) == 2:
        return (int(lead_time_string) * SECONDS_PER_HOUR)
    # HHH
    elif len(lead_time_string) == 3:
        return (int(lead_time_string) * SECONDS_PER_HOUR)
    # HHMM
    elif len(lead_time_string) == 4:
        return ((int(lead_time_string[0:2]) * SECONDS_PER_HOUR) + (int(lead_time_string[2:4]) * MINUTES_PER_HOUR))
    # HHHMM
    elif len(lead_time_string) == 5:
        return ((int(lead_time_string[0:3]) * SECONDS_PER_HOUR) + (int(lead_time_string[3:5]) * MINUTES_PER_HOUR))
    # HHMMSS
    elif len(lead_time_string) == 6:
        return ((int(lead_time_string[0:2]) * SECONDS_PER_HOUR) + (int(lead_time_string[2:4]) * MINUTES_PER_HOUR) + int(lead_time_string[4:6]))
    # HHHMMSS
    elif len(lead_time_string) == 7:
        return ((int(lead_time_string[0:3]) * SECONDS_PER_HOUR) + (int(lead_time_string[3:5]) * MINUTES_PER_HOUR) + int(lead_time_string[5:7]))
    else:
        print("Lead time must be in the format [H]HH[MMSS], where a two digit hour is required.  Providing a three digit hour, two digit minutes and a two digit seconds are optional.")         
        exit(0)
        
class StringTemplateSubstitution:
    """
    tmpl_str - template string to populate
    kwargs - dictionary containing values for each template key
    
    Possible keys for vals:
       init - must be in YYYYmmddHH[MMSS] format
       valid - must be in YYYYmmddHH[MMSS] format
       lead - must be in HH[MMSS] format
       accum - must be in HH[MMSS] fomrat
       level - the level number as a string (?)
       model - the name of the model
       domain - the domain number (01, 02, etc.) read in as a string

       These keys can have parameters containing formatting information.
       The format of the template in this case is {tmpl_key?parm1=val1}.
       For example, 
       
    """

    def __init__(self, tmpl, **kwargs):

        self.tmpl = tmpl
        self.kwargs = kwargs
        if self.kwargs is not None:
            for key, value in kwargs.iteritems():
                #print("%s == %s" % (key, value))
                setattr(self, key, value)

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
        lead_time_seconds = get_lead_time_seconds((self.kwargs).get(LEAD_STRING, None))

        init_unix_time = valid_unix_time - lead_time_seconds
        init_time = time.strftime("%Y%m%d%H%M%S", time.gmtime(init_unix_time))
        #print("init_time: ", init_time)
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
        lead_time_seconds = get_lead_time_seconds((self.kwargs).get(LEAD_STRING, None))

        valid_unix_time = init_unix_time + lead_time_seconds
        valid_time = time.strftime("%Y%m%d%H%M%S", time.gmtime(valid_unix_time))
        #print("valid_time: ", valid_time)
        return valid_time

    def dateCalcLead(self):

        """ Calculate the lead time from the init and valid time
            Currently requires the valid time to be greater than the init time"""
             
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
            lead_seconds = valid_unix_time - init_unix_time
        else:
            print "Init time is greater than valid time"
            lead_seconds = init_unix_time - valid_unix_time
            negative_lead_flag = 1
        lead_seconds_str = str(datetime.timedelta(seconds=lead_seconds))
        #print("Valid time currently: %s, Init time currently: %s"  % ((self.kwargs).get(VALID_STRING, None), (self.kwargs).get(INIT_STRING, None)))

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

        #print("lead_time: ", lead_time)
        return lead_time

    def leadStringFormat(self, format_string):

        print "In leadStringFormat"
        print (self.kwargs).get(LEAD_STRING, None)
        print format_string

        date_time_value = (self.kwargs).get(LEAD_STRING, None)
        format_string = "\"" +  format_string +"\""
        print format_string
        #print type(date_time_value)
        time_tuple = time_str_to_time_tuple(date_time_value, format_string)
        print time_tuple
    
    def doStringSub(self):

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
                        print "Some message about key not in key/value pair"

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
                                value = self.leadStringFormat(format_split_string[1])

                            
                        """
                        # Check for requested LENGTH_STRING    
                        elif format_split_string[0] == LENGTH_STRING:

                            value = (self.kwargs).get(split_string[0], None)
                            if (split_string[0] == LEAD_STRING):
                              value = self.leadStringFormat(format_split_string[1])
                            # Get the value for the desired length and pad with zeros if not already the desired length
                            padded_value = value.zfill(int(format_split_string[1]))
                            
                            # Add back the template identifiers to the matched string to replace and add the key, value pair to the dictionary
                            string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match + TEMPLATE_IDENTIFIER_END
                            replacement_dict[string_to_replace] = padded_value
                        """    
                # No formatting or length is requested            
                elif len(split_string) == 1:

                    # Add back the template identifiers to the matched string to replace and add the key, value pair to the dictionary
                    string_to_replace = TEMPLATE_IDENTIFIER_BEGIN + match + TEMPLATE_IDENTIFIER_END
                    replacement_dict[string_to_replace] = (self.kwargs).get(split_string[0], None)
                            
            # Replace regex with properly formatted information
            #print replacement_dict
            #print "self.tmpl: ", self.tmpl
            temp_str = multiple_replace(replacement_dict, self.tmpl)
            print "temp_str: ", temp_str
            self.tmpl = temp_str
            return self.tmpl
            

        
                
    #def setSubs():

    #def subString():

    
    
if __name__ == "__main__":
    main()
