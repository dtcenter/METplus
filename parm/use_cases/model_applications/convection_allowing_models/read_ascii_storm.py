
import pandas as pd
import os
import sys
import ntpath

########################################################################

print('Python Script:\t', sys.argv[0])

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

        column_names = ["Message_Type","Station_ID","Valid_Time","Lat","Lon","Elevation","Var_Name","Level","Height","QC_String","Observation_Value"]

        # Create a blank dataframe based on the 11 column standard
        point_frame = pd.DataFrame(columns=column_names,dtype='str')

        #Read in the Storm report, 8 columns not matching the 11 column standard
        temp_data = pd.read_csv(input_file,names=['Time', 'Fscale', 'Location', 'County','Stat','Lat', 'Lon', 'Comment'], dtype=str ,skiprows=1)

        #Strip out any rows in the middle that are actually header rows
        #Allows for concatenating storm reports together
        temp_data = temp_data[temp_data["Time"] != "Time"]
         
        #Change some columns to floats and ints
        temp_data[["Lat","Lon"]] = temp_data[["Lat","Lon"]].apply(pd.to_numeric)

        #Assign approprite columns to point_frame leaving missing as empty strings 
        point_frame["Lat"] = temp_data["Lat"]
        point_frame["Lon"] = temp_data["Lon"]
        #point_frame["Station_ID"] = temp_data["County"] 
        point_frame["Station_ID"] = "NA"
        point_frame["Var_Name"] = "Fscale" 
        point_frame["Message_Type"] = "StormReport"

        #Assign 0.0 values to numeric point_frame columns that we don't have in the csv file 
        point_frame["Elevation"] = 0.0
        point_frame["Level"] = 0.0
        point_frame["Height"] = 0.0

        #Change Comments into a "QC" string Tornado=1, Hail=2, Wind=3, Other=4
        point_frame["QC_String"] = "4"
        mask = temp_data["Comment"].str.contains('TORNADO')
        point_frame.loc[mask,"QC_String"] = "1" 
        mask = temp_data["Comment"].str.contains('HAIL')
        point_frame.loc[mask,"QC_String"] = "2" 
        mask = temp_data["Comment"].str.contains('WIND')
        point_frame.loc[mask,"QC_String"] = "3" 

        #Time is HHMM in the csv file so we need to use a piece of the filename and 
        #this value to create a valid date string
        file_without_path = ntpath.basename(input_file)
        year_month_day = "20"+file_without_path[0:6]
        point_frame["Valid_Time"] = year_month_day+"_"+temp_data["Time"]+"00"

        #Currently we are only interested in the fact that we have a report at that locaton
        #and not its actual value so all values are 1.0
        point_frame["Observation_Value"] = 1.0

        #Ascii2nc wants the final values in a list
        point_data = point_frame.values.tolist()

        print("Data Length:\t" + repr(len(point_data)))
        print("Data Type:\t" + repr(type(point_data)))
    except NameError:
        print("Can't find the input file")
else:
    print("ERROR: read_ascii_storm.py -> Must specify exactly one input file.")
    sys.exit(1)

########################################################################
