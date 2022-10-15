#!/usr/bin/env python3

import os
import sys
import yaml
from metplotpy.contributed.fv3_physics_tend import planview_fv3

'''
Generate the plan view plot.  

Requires a configuration file that has the history and grid input files in addition to the location of 
the planview_fv3.py file
'''


if __name__ == "__main__":
    planview_fv3.main()

