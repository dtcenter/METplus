#!/usr/local/python/bin/python
#
# File: find_conf_var.py
# 
# Author: D. Adriaansen
#
# Date: 12 Sept 2018
#
# Purpose: Locate the use of a configuration variable within METplus source and conf areas
#
# Notes: You can search *just* conf areas via ./find_conf_var.py <var_name> conf, or
#        search *just* source areas via ./find_conf_var.py <var_name> py, or
#        search BOTH via ./find_conf_var.py <var_name>
#
#________________________________________________________________________________________

# Python modules
import subprocess, sys, string

# Path to METplus installation
mpinstall = '/home/dadriaan/projects/METplus'

# Get user variables
cv = sys.argv[1]

# What mode?
# 'conf' = only show conf files
# 'py' = only show py files
# 'all' = show all files
if len(sys.argv)==2:
  mode = 'all'
elif len(sys.argv)==3:
  mode = sys.argv[2]
else:
  print("")
  print("PLEASE PROVIDE CORRECT ARGUMENTS:")
  print("")
  print("./find_conf_var.py <var_name>")
  print("-or-")
  print("./find_conf_var.py <var_name> <mode>")
  print("where <mode> is either py or conf")
  print("")
  sys.exit(1)

# Split variable if appropriate
#if "_" in cv:
#  s1 = string.split(cv,"_")
#else:
#  s1 = []
s1 = []

if s1 == []:
  if mode=='conf':
    cmd = 'grep -H %s %s/parm/metplus_config/*.conf %s/parm/use_cases/*/*.conf %s/parm/use_cases/*/*/*.conf %s/ush/*.py | grep -v \'\.py\''% (cv,mpinstall,mpinstall,mpinstall,mpinstall)
  elif mode=='py':
    cmd = 'grep -H %s %s/parm/metplus_config/*.conf %s/parm/use_cases/*/*.conf %s/parm/use_cases/*/*/*.conf %s/ush/*.py | grep -v \'\.conf\''% (cv,mpinstall,mpinstall,mpinstall,mpinstall)
  else:
    cmd = 'grep -H %s %s/parm/metplus_config/*.conf %s/parm/use_cases/*/*.conf %s/parm/use_cases/*/*/*.conf %s/ush/*.py'% (cv,mpinstall,mpinstall,mpinstall,mpinstall)
  #print(cmd)
  subprocess.call('%s' % (cmd), shell=True, executable='/bin/csh')
else:
  for i in s1:
    cmd = 'grep -H _%s %s/parm/metplus_config/*.conf %s/parm/use_cases/*/*.conf %s/parm/use_cases/*/*/*.conf %s/ush/*.py'% (i,mpinstall,mpinstall,mpinstall,mpinstall)
    #print(cmd)
    subprocess.call('%s' % (cmd), shell=True, executable='/bin/csh')
