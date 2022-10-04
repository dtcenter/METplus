#! /usr/bin/env python

import os
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

output_dir = os.path.dirname(output_file)
if not os.path.exists(output_dir):
    print(f'Creating output dir: {output_dir}')
    os.makedirs(output_dir)

filelist = open(output_file,'a+')
filelist.write(input_file + '\n')
filelist.close()
