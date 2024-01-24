from __future__ import print_function

import pandas as pd
import os
import sys
import datetime
import numpy as np

########################################################################

print("Python Script:\t" + repr(sys.argv[0]))

   ##
   ##  input file specified on the command line
   ##  load the data into the numpy array
   ##

if len(sys.argv) == 2:
    # Read the input file as the first argument
    input_file = os.path.expandvars(sys.argv[1])
    try:
        print("Input File:\t" + repr(input_file))

        # Read and format the input 11-column observations:
        #   (1)  string:  Message_Type
        #   (2)  string:  Station_ID
        #   (3)  string:  Valid_Time(YYYYMMDD_HHMMSS)
        #   (4)  numeric: Lat(Deg North)
        #   (5)  numeric: Lon(Deg East)
        #   (6)  numeric: Elevation(msl)
        #   (7)  string:  Var_Name(or GRIB_Code)
        #   (8)  numeric: Level
        #   (9)  numeric: Height(msl or agl)
        #   (10) string:  QC_String
        #   (11) numeric: Observation_Value

        holder = pd.read_csv(input_file,usecols=['ObservationDate','ObservationTime','StationNumber','Latitude','Longitude','TotalPrecipAmt'])
        #convert time stamps to MET friendly timestamps
        dat = holder['ObservationDate'].values.tolist()
        tim = holder['ObservationTime'].values.tolist()
        vld = []
        
        #grab the existing values from the csv and get them into list form
        sid = holder['StationNumber'].values.tolist()
        lat = holder['Latitude'].values.tolist()
        lon = holder['Longitude'].values.tolist()
        obs = holder['TotalPrecipAmt'].values.tolist()


        #this loop will result in an error if every date doesn't have a time (HHMM) associated with it
        #its purpose is threefold: first is to construct time strings that MET can handle
        #second is to strip the whitespaces that exist in the sid and obs list items
        #and third is to convert the obs items into floats
        for i in range(len(dat)):
            #convert the times
            mush = dat[i]+tim[i]
            dt = datetime.datetime.strptime(mush, '%b %d %Y %H:%M UT')
            vld.append(dt.strftime('%Y%m%d_%H%M%S'))
            #strip the whitespace
            sid[i] = sid[i].strip()
            #strip whitespace 
            obs[i] = obs[i].strip()
            #and convert. need to check if value is 'T'
            #if it is, set the value to 0
            if not obs[i].isalpha():
                obs[i] = float(obs[i].strip())
            else:
                obs[i] = float(0.0)


        #create dummy lists for the message type, elevation, variable name, level, height, and qc string
        #numpy is more efficient at creating the lists, but need to convert to Pythonic lists
        typ = np.full(len(vld),'ADPSFC').tolist()
        elv = np.zeros(len(vld)).tolist()
        var = np.full(len(vld),'TotalPrecipAmt').tolist()
        lvl = np.full(len(vld),1013.25).tolist()
        hgt = np.zeros(len(vld),dtype=int).tolist()
        qc = np.full(len(vld),'NA').tolist()



        #Now to put the lists into a list of lists
        #start by creating a list of tuples
        #then convert the tuples to lists

        
        l_tuple = list(zip(typ,sid,vld,lat,lon,elv,var,lvl,hgt,qc,obs))
        point_data = [list(ele) for ele in l_tuple]
        
        

        print("Data Length:\t" + repr(len(point_data)))
        print("Data Type:\t" + repr(type(point_data)))
    except NameError:
        print("Can't find the input file")
else:
    print("ERROR: read_ascii_point.py -> Must specify exactly one input file.")
    sys.exit(1)

########################################################################

