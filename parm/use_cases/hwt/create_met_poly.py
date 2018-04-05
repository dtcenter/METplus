#!/usr/bin/env python

import json
import datetime

now = datetime.datetime.now()
today_date = now.strftime("%Y%m%d")

domain_file = "/raid/efp/se2018_web/web_data/sector_bounds/hwt_primary."+today_date+".json"
json_data = open(domain_file).read()
domain_data = json.loads(json_data)
corner_pts = domain_data["corners"]

#Write output file
outfile = open("HWTSE_"+today_date+".poly","w")
outfile.write("HWTSE_"+today_date+"\n")
for pts in corner_pts:
  outfile.write(str(pts[0])+" "+str(pts[1])+"\n")

outfile.close()
