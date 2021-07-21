#! /usr/bin/env python

import os
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

filelist = open(output_file,'a+')
filelist.write(input_file + '\n')
filelist.close()
