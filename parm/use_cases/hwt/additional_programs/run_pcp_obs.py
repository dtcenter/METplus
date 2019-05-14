#!/usr/bin/env python

import os
import time
import datetime
import calendar
import met_util as util

sdate = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime("%Y%m%d")+"15"
edate = (datetime.datetime.now() - datetime.timedelta(hours=0)).strftime("%Y%m%d") +"12"
inc = "10800"

obs_dir = "/raid/student/twiest/Scorecard/ST4"
outdir = "/raid/efp/se2019/ftp/dtc/obs/pcp_combine/"

#Create a list of valid times to search
loop_time = calendar.timegm(time.strptime(sdate, "%Y%m%d%H"))
end_time = calendar.timegm(time.strptime(edate, "%Y%m%d%H"))

while loop_time <= end_time:
    #Create a list of files to loop over
    valid_time = time.strftime("%Y%m%d%H", time.gmtime(loop_time))
    valid_hr  = int(valid_time[8:10])

# Create 3 hour, pcp_combine
    fadd = ""
    for t in range(3):
fadd = fadd+obs_dir+"/ST4."+util.shift_time(valid_time+"00",-t)[0:10]+".01h 1 "
    outfile3 = outdir+"/ST4."+valid_time+"_A03.nc"

os.system("pcp_combine -add "+fadd+outfile3)

if (valid_hr % 6) == 0:
fadd6 = ""
for s in range(6):
fadd6 = fadd6+obs_dir+"/ST4."+util.shift_time(valid_time+"00",-s)[0:10]+".01h 1 "
outfile6 = outdir+"/ST4."+valid_time+"_A06.nc"

os.system("pcp_combine -add "+fadd6+outfile6)

loop_time+=int(inc)

fadd24 = ""
for f in range(24):
    fadd24 = fadd24+obs_dir+"/ST4."+util.shift_time(valid_time+"00",-f)[0:10]+".01h 1 "
outfile24 = outdir+"/ST4."+valid_time+"_A24.nc"
os.system("pcp_combine -add "+fadd24+outfile24)
