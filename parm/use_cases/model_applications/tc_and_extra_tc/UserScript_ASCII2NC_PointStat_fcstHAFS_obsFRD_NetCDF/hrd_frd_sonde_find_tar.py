#! /usr/bin/env python3
#####################################################################
#  This script will untar the FRD formatted dropsonde tar files from 
#  https://www.aoml.noaa.gov/hrd/data_sub/dropsonde.htmli
#  The untarred files will be downloaded in to a direcory
#  under USER_SCRIPT_OUTPUT_DIR. Arguments to the scripts includes
#  directory where the tar files exists, the user specified 
#  date in YYYYMMDD, and output directory
#  Author: biswas@ucar.edu
#####################################################################

import sys
import os
import glob
import tarfile

if len(sys.argv) == 4:
  path = sys.argv[1]
  date = sys.argv[2]
  outdir = sys.argv[3]

  if os.path.exists(path):
     print("Directory exists: "+ path)

     for name in glob.glob(path+'/'+str(date)+'*FRD.tar.gz'):
       print (name)

       drop_tar = tarfile.open(name)
       drop_tar.extractall(outdir + '/'+str(date))
       drop_files = os.listdir(outdir + '/'+str(date))
       print(drop_files)
       drop_tar.close()

  else: 
     print("Directory not present" + path)

else:
  print("ERROR : Must specify exactly one input data directory, date (YYYYMMDD), and output directory.")
  sys.exit(1)
  
####################################################################
