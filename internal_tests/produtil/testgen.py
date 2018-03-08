#! /usr/bin/env python

# FIXME: Remove if randstring is removed:
# import string, random

import logging
import os
import sys
import getopt
import datetime

import produtil.setup
produtil.setup.setup(send_dbn=False)

from produtil.testing.testgen import TestGen
from produtil.testing.utilities import BASELINE, EXECUTION
from produtil.testing.tokenize import Tokenizer, TokenizeFile
from produtil.testing.parse import Parser
from produtil.testing.rocoto import RocotoRunner
from produtil.testing.script import BashRunner

testgen=None

def usage(why=None):
    sys.stderr.write('''Generates a workflow to run a test suite.

     testgen [options] (-R | -B) (-b | -v) [--] /input/path /output/path

Mandatory arguments:
-R | -B
     Mandatory output type: [-R]ocoto workflow or flat [-B]ash script.
-b | -v
     Run mode: generate a new [-b]aseline or [-v]erify results by
     comparing to an old baseline.
/input/path
     Path to input file that describes the tests.
/output/path
     Where to create scripts; should be a parallel filesystem accessible
     by compute nodes.  Must not exist yet.

Optional arguments:
-d
     Requests a dry run; print what would be done without doing it.
-u integer
     Specifies the unique positive integer id of this test run.
     Default is to automatically generate one.
-P
     Enable Python profiling via cProfile.
''')
    if why is not None:
        sys.stderr.write('ABORTING: %s\n'%(why,))
    exit(2)

# FIXME: Remove this if unneeded:
# def randstring():
#     """!Generates a random number from 0 to 62**6-1 and expresses it
#     in base 62 as a six character string."""
#     sixtytwo = string.digits + string.lowercase + string.uppercase
#     i1=int(random.uniform(0,62**3))
#     i2=int(random.uniform(0,62**3))
#     randstring = \
#         ''.join([ sixtytwo[min(61,max(0,(i1/62**j) % 62))]
#                   for j in xrange(3) ] + \
#                 [ sixtytwo[min(61,max(0,(i2/62**j) % 62))]
#                   for j in xrange(3) ])

def parse_arguments(args):
    run_mode=None
    output_type=None
    output_path=None
    dry_run=False
    unique_id=None
    profile=False

    if len(args)<1: usage()

    optval,arglist=getopt.getopt(sys.argv[1:],'bvRBdu:P')

    for opt,val in optval:
        if opt=='-R':
            if output_type:
                usage('specified output type (-R, -B) more than once')
            output_type=RocotoRunner
        elif opt=='-B':
            if output_type:
                usage('specified output type (-R, -B) more than once')
            output_type=BashRunner
        elif opt=='-b':
            if run_mode:
                usage('specified run mode (-b, -v) more than once')
            run_mode=BASELINE
        elif opt=='-v':
            if run_mode:
                usage('specified run mode (-b, -v) more than once')
            run_mode=EXECUTION
        elif opt=='-P':
            profile=True
        elif opt=='-u':
            unique_id=int(val,10)
        elif opt=='-d':
            dry_run=True
        else:
            usage('unknown option '+opt)

    if not run_mode:
        usage('run mode (-b or -v) unspecified')
    elif not output_type:
        usage('output type (-R or -B) unspecified')
    elif len(arglist)!=2:
        usage('exactly two non-option arguments were expected, not %d'%(
                len(arglist),))

    input_location=arglist[0]
    output_path=arglist[1]

    if not os.path.exists(input_location):
        usage('%s: does not exist'%(input_location,))

    absinput=os.path.normpath(os.path.abspath(input_location))

    return run_mode, output_type, output_path, absinput, dry_run, \
           unique_id, profile

def main(args):
    run_mode, OutputType, outloc, inloc, dry_run, unique_id, profile = \
        parse_arguments(args)

    global testgen # global scope for cProfile
    testgen=TestGen(run_mode, OutputType, outloc, inloc, dry_run, unique_id)

    if profile:
        import cProfile
        cProfile.run('testgen.testgen()')
    else:
        testgen.testgen()

if __name__=='__main__':
    main(sys.argv[1:])
