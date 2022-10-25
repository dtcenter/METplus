#!/usr/bin/env python3

import os
import sys
import yaml
from metplotpy.contributed.fv3_physics_tend import cross_section_vert

'''
Generate the vertical cross section plots.  

Requires a configuration file that has the history and grid input files in addition to the location of 
the cross_section_vert.py file
'''


if __name__ == "__main__":
    cross_section_vert.main()

