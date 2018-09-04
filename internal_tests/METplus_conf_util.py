#!/usr/local/python/bin/python
#
# File: METplus_conf_util.py
#
# Author: D. Adriaansen
#
# Date: 01 Jun 2018
#
# Purpose: Distill down all of the configuration options from conf files in the METplus repository,
#          remove duplicates, and check against an existing file to see if there are new/removed conf
#          options. Also provide an option for the user to replace the current existing file with an
#          updated one. This is mainly useful for keeping documentation up to date, as a developer utility
#          to make sure if they add new conf options, they are captured and the documentation can be updated
#          before pushing changes.
#
# Notes:
#______________________________________________________________________________________________________

# Python libraries
import string, subprocess, sys, os

##################################### User Config #############################################

# Path to METplus install
METPLUS_BASE = os.path.expanduser("~/projects/METplus")

# Path to existing static conf list. If this is the first time running,
# then set this to where you want to write the static conf list file and
# use mode "static" (see usage)
STATIC_CONF_LIST = "%s/internal_tests/conf_list.static" % (METPLUS_BASE)

# Path to temp directory to write a file to compare against
TMP_CONF_LIST_DIR = "/tmp"

# Debug flag
DEBUG = True

# List of files to check for config items
chklist = ['%s/parm/metplus_config/*.conf' % (METPLUS_BASE),'%s/parm/use_cases/*/*.conf' % (METPLUS_BASE), \
           '%s/parm/use_cases/*/*/*.conf' % (METPLUS_BASE)]

# List for current conf items
clist = []

# List for temp conf items
tlist = []

###############################################################################################

# Define usage statement for user
def usage():
  print("")
  print("  USAGE: METplus_conf_util.py <action>")
  print("")
  print("  Where <action> is either:")
  print("  check -or- update -or- static")
  print("  check = print list of differences")
  print("  update = same as check, but replace existing conf list with new one as well")
  print("  static = generate a single file from the current repository branch and don't compare")
  print("")
  print("  EXITING...")
  print("")
  sys.exit(1)

# Function to execute shell commands
def call(cmd):
  if DEBUG:
    print("  "+cmd)
  subprocess.call('%s' % (cmd), shell=True, executable='/bin/csh')

# Check users' arguments
if len(sys.argv)!=2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
  usage()
else:
  mode = sys.argv[1]

# Based on the requested mode, print things for the user
if mode=='update':
  print("")
  print("  WARNING! YOU ARE ABOUT TO OVERWRITE ANY EXISTING STATIC CONF LIST LOCATED HERE:")
  print("  "+STATIC_CONF_LIST)
  print("")
  print("  IS THIS WHAT YOU WANT TO DO?")
  status = raw_input("  y/n: ")
  if status == 'n':
    print("")
    print("  EXITING...")
    print("")
    sys.exit(1)
  else:
    print("")
    print("  UPDATING STATIC CONF LIST...")
elif mode=='check':
  print("")
  print("  PREPARING LIST OF DIFFERENCES BETWEEN REPOSITORY AND EXISTING CONF LIST...")
elif mode=='static':
  print("")
  print("  WARNING! YOU ARE ABOUT TO GENERATE A NEW CONF LIST AND OVERWRITE ANY EXISTING CONF LIST LOCATED HERE:")
  print("  "+STATIC_CONF_LIST)
  print("")
  print("  *** THIS MODE IS TYPICALLY NOT NEEDED! ***")
  print("")
  print("  IS THIS REALLY WHAT YOU WANT TO DO?")
  status = raw_input("  y/n: ")
  if status=='n':
    print("")
    print("  EXITING...")
    print("")
    sys.exit(1)
  else:
    print("")
    print("  WRITING STATIC CONF LIST TO %s..." % (STATIC_CONF_LIST))
else:
  print("")
  print("  FATAL! UNKNOWN MODE.")
  usage()

# Run the grep commands to create the temporary files. This is needed regardless of what the user is requesting.
if DEBUG:
  print("")
  print("  GATHERING CONF ITEMS FROM:")
  for f in chklist:
    print("  "+f)
  print("")
cmd = "cat "
for f in chklist:
  cmd += f+" "
cmd += "> %s/tmp.conf" % (TMP_CONF_LIST_DIR)
call(cmd)
cmd = "grep = %s/tmp.conf | grep -v \# | sort | uniq > %s/unique.conf" % (TMP_CONF_LIST_DIR,TMP_CONF_LIST_DIR)
call(cmd)

############ For static mode, just write out a file and exit.
if mode=='static':
  # Open temp file and read
  tfile = open("%s/unique.conf" % (TMP_CONF_LIST_DIR))
  tdata = tfile.readlines()
  tfile.close()

  # Create a list of unique items
  for tl in tdata:
    s1 = string.split(tl,"=")
    tlist.append(s1[0].strip())
    set(tlist)
  tlist = list(set(tlist))
  tlist.sort()

  # Open file for writing
  sfout = open(STATIC_CONF_LIST,"w")
  for i in tlist:
    sfout.write("%s\n" % (i))

  # Print entries found
  print("")
  print("  TOTAL CONF ENTRIES FOUND: %04d" % (len(tlist)))

  print("")
  print("  DONE.")
  sfout.close()
  sys.exit(0)

########### For check and update modes, we need all the information below.
# Open current file and read
cfile = open(STATIC_CONF_LIST,"r")
cdata = cfile.readlines()
cfile.close()
  
# Open temp file and read
tfile = open("%s/unique.conf" % (TMP_CONF_LIST_DIR))
tdata = tfile.readlines()
tfile.close()

# Create lists of unique items
for cl in cdata:
  s1 = string.split(cl,"=")
  clist.append(s1[0].strip())
clist = list(set(clist))
clist.sort()

for tl in tdata:
  s1 = string.split(tl,"=")
  tlist.append(s1[0].strip())
  set(tlist)
tlist = list(set(tlist))
tlist.sort()

# Use list comprehensions to print variables in clist but not tlist, and tlist but clist
conly = [x for x in clist if x not in tlist]
tonly = [x for x in tlist if x not in clist]
print("")
print("  TOTAL EXISTING CONF ENTRIES: %04d" % (int(len(clist))))
print("  TOTAL NEW CONF ENTRIES     : %04d" % (int(len(tlist)-len(clist))))
print("  TOTAL AFTER UPDATE         : %04d" % (int(len(tlist))))
print("")
if conly == []:
  print("  NO OBSOLETE ITEMS.")
else:
  print("  THE FOLLOWING CONF ITEMS ARE OBSOLETE:")
  print("")
  for i in conly:
    print("  + "+i)
  print("")
  print("  ********* PLEASE UPDATE LYX DOCUMENTATION! ************")
print("")
if tonly == []:
  print("  NO NEW ITEMS.")
else:
  print("  THE FOLLOWING CONF ITEMS ARE NEW:")
  print("")
  for i in tonly:
    print("  + "+i)
  print("")
  print("  ********* PLEASE UPDATE LYX DOCUMENTATION! ************")

# Write out data to files
cinspect = open("%s/current.conf" % (TMP_CONF_LIST_DIR),"w")
tinspect = open("%s/new.conf" % (TMP_CONF_LIST_DIR),"w")
for i in clist:
  cinspect.write("%s\n" % (i))
for i in tlist:
  tinspect.write("%s\n" % (i))
cinspect.close()
tinspect.close()
print("")
print("  INSPECT COMPARED FILES HERE:")
print("  %s/current.conf" % (TMP_CONF_LIST_DIR))
print("  %s/new.conf" % (TMP_CONF_LIST_DIR))

# If the user requested update, do that here.
if mode=='update':
  if conly!=[] or tonly!=[]:
    print("")
    print("  REPLACING FILE...")
    cmd = 'cp %s/new.conf %s' % (TMP_CONF_LIST_DIR,STATIC_CONF_LIST)
    call(cmd)
  else:
    print("")
    print("  NO CHANGES NEEDED TO FILE %s" % (STATIC_CONF_LIST))

# Clean up
print("")
print("  CLEANING UP...")
if DEBUG:
  cmd = 'rm -rf %s/unique.conf %s/tmp.conf' % (TMP_CONF_LIST_DIR,TMP_CONF_LIST_DIR)
else:
  cmd = 'rm -rf %s/unique.conf %s/tmp.conf' % (TMP_CONF_LIST_DIR,TMP_CONF_LIST_DIR)
call(cmd)

print("")
print("  DONE.")
