
import sys
import re
import numpy as np
import datetime as dt
from dateutil.relativedelta import *    # New import
from netCDF4 import Dataset, chartostring
from preprocessFun_Modified import preprocess, dominant_tercile_fcst, dominant_tercile_obs, get_init_year # New import

#grab input from user
#should be (1)input file using full path (2) variable name (3) valid time for the forecast in %Y%m%d%H%M format and (4) ensemble member number, all separated by ':' characters
#program can only accept that 1 input, while still maintaining user flexability to change multiple
#variables, including valid time, ens member, etc.
# Addition by Johnna - model, lead, init taken from file name
# Addition by Johnna - climatology and std dev caclulated for given lead, model, init
# Addition by Johnna - added command line pull for lead

print('Type in input_file using full path:variable name:valid time in %Y%m%d%H%M:ensemble member number:lead')
# Example
# /cpc/nmme/CFSv2/hcst_new/010100/CFSv2.tmp2m.198201.fcst.nc:tmp2m:198201010101:0:0

input_file, var_name, init_time, ens_mem, lead = sys.argv[1].split(':')
ens_mem = int(ens_mem)
lead    = int(lead)    # Added by Johnna
init_time = dt.datetime.strptime(init_time,"%Y%m%d%H%M")   

# ---
# Added by Johnna
input_file_split = input_file.split('/')
#EDIT BY JOHN O
init_temp = "010100"
#init_temp = input_file_split[5]

#fil_name = input_file_split[6]
fil_name = input_file
year_temp = fil_name.split('.')
#year = year_temp[2]
year = year_temp[-3]
print('YYYYMM: ' + str(year))

# Setup Climatology
#EDIT BY JOHN O
#model = input_file_split[3]
model = "CFSv2"
init  = init_temp.replace('0100','')
lead  = lead
clim_per = '1982_2010'
member = ens_mem
variable = var_name

# Get path based on model (only works for this file name)
input_file_split2 = input_file.split(model + '.')
path = input_file_split2[0]

# Calculate climatologies and standard deviations/etc.  This calculates every time the loop runs (i.e. for each file read into MET)
# There might be a better positioning for this function such that it doesn't recalc each loop, but I pulled from the command line input 
# above to create the function, so right now it has dependance on the file names/user input/etc.
# Fine for now since data are smallish, but if theres something higher res might slow things down.
print('Model: ' + model + ' Init: ' + str(init) + ' lead: ' + str(lead) + ' Member: ' + str(ens_mem) + ' Variable: ' + variable)

# We only need the fcst_cat_thresh
# Commenting out the original preprocess function
#clim, stddev, anom, std_anom = preprocess(path, model, init, variable, lead, clim_per, member)

# New preprocessing function to get the cat thresholds
# In order 0, 1, 2 where 0 is LT, 1 is MT, 2 is UT
# fcst_cat_thresh has ALL times (28), and is calculated for ALL 24 members
# So the array fcst_cat_thresh is time | 29, lat | 181, lon | 360)
# I wrote a clumsy function to split this into years based on the filename read in (get_init_year)
# But it works!  Basically just a bunch of if statements like if the filename is 198201 then its index 0 of the array and so on to the last index
# I also swap the fcst lats to be -90 to 90 instead of 90 to -90 and match up the longitudes (theres a cyclic point in the fcst so its actually 361 pts)
fcst_cat_thresh  = dominant_tercile_fcst(path, model, init, variable, clim_per, lead)
idx = get_init_year(year)
fcst_cat_thresh_1year = fcst_cat_thresh[idx,::-1,0:360]

# Going to do the obs in the same wrapper. I realized this would be easier so I hope this is okay...  I think its just a flag...?
# Using same clunky function to get the right year out of the big array
#EDIT BY JOHN O
obs_cat_thresh  = dominant_tercile_obs(path)
obs_cat_thresh_1year = obs_cat_thresh[idx,:,0:360]

# Redefine var_name to fcst (necessary for below)
var_name = 'fcst'
# ---

try:
    print('The file you are working on is: ' + input_file)
    # all of this is actually pointless eexcept to get the dimensions and times, all of the calculations are done in the functions
    #set pointers to file and group name in file

    f = Dataset(input_file)
    v = f[var_name][member,lead,:,:]

    #grab data from file
    lat = np.float64(f.variables['lat'][::-1])
    lon = np.float64(f.variables['lon'][:])
    
    # Grab and format time, this is taken from the file name, which might not be the best way of doing it
    # Can also potentially pull from the netCDF; but need an extra package in netCDF4 to do that, and its a little weird
    # given units of months since.  This was a bit easier.
    # Do need to add relativedelta package but thats fairly common (its from dateutil)
    val_time = init_time + relativedelta(months=lead)
    print('Valid Time: ' + str(val_time))


    # Coming from the function
    # uncomment out the obs one if you want to use the obs?    
    v = fcst_cat_thresh_1year
    #v = obs_cat_thresh_1year
    print('Shape of variable to read into MET: ' + str(v.shape)) 

    # --------------------------
    # Commented out by Johnna, defined above in user input
    # Print statement erroring so commented out
    #grab intialization time from file name and hold
    #also compute the lead time
    #i_time_ind = input_file.split("_").index("aod.nc")-1
    #i_time = input_file.split("_")[i_time_ind]
    #i_time_obj = dt.datetime.strptime(i_time,"%Y%m%d%H")
    #lead, rem = divmod((val_time - i_time_obj).total_seconds(), 3600) 

    #print("Ensemble Member evaluation for: "+f.members.split(',')[ens_mem])

    #checks if the the valid time for the forecast from user is present in file.
    #Exits if the time is not present with a message
    #if not val_time.timestamp() in f['time'][:]:
    #        print("valid time of "+str(val_time)+" is not present. Check file initialization time, passed valid time.")
    #        f.close()
    #        sys.exit(1)

    #grab index in the time array for the valid time provided by user (val_time)
    #val_time_ind = np.where(f['time'][:] == val_time.timestamp())[0][0]
    #var = np.float64(v[val_time_ind:val_time_ind+1,ens_mem:ens_mem+1,::-1,:])
    # --------------------------
    
    #squeeze out all 1d arrays, add fill value, convert to float64
    var = np.float64(v)  
    var[var < -800] = -9999

    met_data = np.squeeze(var).copy()
    #JOHN O ADDED TO TEST IF FLIPPING IS OCCURING
    met_data = met_data[::-1,:]
    met_data = np.nan_to_num(met_data, nan=-1)
    print('Done, no exceptions')

except NameError:
    print("Can't find input file")
    sys.exit(1)

##########
#create a metadata dictionary

attrs = {

        'valid': str(val_time.strftime("%Y%m%d"))+'_'+str(val_time.strftime("%H%M%S")),
        'init': str(init_time.strftime("%Y%m%d"))+'_'+str(init_time.strftime("%H%M%S")),
        'name': var_name,
        'long_name': input_file,
        'lead': str(int(lead)),
        'accum': '00',
        'level': 'sfc',
        'units': 'Degrees K',

        'grid': {
            'name': 'Global 1 degree',
            'type': 'LatLon',
            'lat_ll': -90.0,
            'lon_ll': 0.0,
            'delta_lat': 1.0,
            'delta_lon': 1.0,

            'Nlon': f.dimensions['lon'].size,
            'Nlat': f.dimensions['lat'].size,
            }
        }

#print some output to show script ran successfully
print("Input file: " + repr(input_file))
print("Variable name: " + repr(var_name))
print("valid time: " + repr(val_time.strftime("%Y%m%d%H%M")))
print("Attributes:\t" + repr(attrs))
f.close()

