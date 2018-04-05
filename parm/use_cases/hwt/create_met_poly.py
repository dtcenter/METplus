#!/usr/bin/env python

import json
import datetime

now = datetime.datetime.now()
today_date = now.strftime(%Y%m%d)

domain_file = "hwt_dd1."+today_date+".json"
json_data = open(domain_file).read()
domain_data = json.loads(json_data)
corner_pts = domain_data["corners"]

#Write output file
outfile = open("HWTSE_"+tdate+".poly","w")
outfile.write("HWTSE_"+tdate)

outfile.close()
