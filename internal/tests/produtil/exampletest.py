#! /usr/bin/env python

from produtil.testing.tokenize import Tokenizer
from produtil.testing.parse import Parser
from produtil.testing.parsetree import fileless_context, Scope

mystring = '''

# Example of platform auto-detection.

# Note to self: need to implement an "embed python" directive.

platform wcoss.cray {
    NWPROD="/gpfs/hps/nco/ops/nwprod/"  
    embed bash detect [[[
        # This function is used at PARSE TIME to detect whether we are
        # on WCOSS Cray.  It must be very fast and low resource usage
        # since the parser runs it.
        if [[ -d /gpfs/hps && -e /etc/SuSE-release && -d /usrx ]] ; then
            exit 0
        fi
        exit 1
    ]]]
}

platform wcoss.phase1 {
    NWPROD="/gpfs/hps/nco/ops/nwprod/"  
    embed bash detect [[[
        # This function is used at PARSE TIME to detect whether we are
        # on WCOSS Phase 1.  It must be very fast and low resource
        # usage since the parser runs it.
        if [[ -d /usrx && -d /global && -e /etc/redhat-release && \
              -e /etc/prod ]] ; then
            # We are on WCOSS Phase 1 or 2.
            if ( ! cat /proc/cpuinfo |grep 'processor.*32' ) ; then
                # Fewer than 32 fake (hyperthreading) cpus, so Phase 1.
                exit 0
            fi
        fi
        exit 1
    ]]]
}

platform wcoss.phase2 {
    NWPROD="/gpfs/hps/nco/ops/nwprod/"  
    embed bash detect [[[
        # This function is used at PARSE TIME to detect whether we are
        # on WCOSS Phase 2.  It must be very fast and low resource
        # usage since the parser runs it.
        if [[ -d /usrx && -d /global && -e /etc/redhat-release && \
              -e /etc/prod ]] ; then
            # We are on WCOSS Phase 1 or 2.
            if ( cat /proc/cpuinfo |grep 'processor.*32' ) ; then
                # At least 32 fake (hyperthreading) cpus, so Phase 2.
                exit 0
            fi
        fi
        exit 1
    ]]]
}

platform theia {
    NWPROD='/scratch3/NCEPDEV/nwprod'
    embed bash detect [[[
        # This function is used at PARSE TIME to detect whether we are
        # on NOAA Theia.  It must be very fast and low resource usage
        # since the parser runs it.
        if [[ -d /scratch3 && -d /scratch4 && -d /contrib ]] ; then
            exit 0
        fi
        exit 1
    ]]]
}

# Specify list of platforms and request autodetection.  Resulting
# platform will be in the "plat" variable:

autodetect plat (/ wcoss.phase1, wcoss.phase2, wcoss.cray, theia /)



# Example variable hashes without "use" statements:

gfspaths = {
    HOMEgsm="@[NWPROD]/gfs.@[GFS_VERSION]"
    PARMGLOBAL="@[HOMEgsm]/parm"
    FIXGLOBAL="@[HOMEgsm]/fix"
    EXECGLOBAL="@[HOMEgsm]/exec"
}

enable_ndslfv = {
  NDSLFV='.true.'
  MASS_DP='.true.'
  PROCESS_SPLIT='.false.'
  dp_import=1
}


# example with "use" statements:

gfsvars={
  use gfspaths
  use plat
  use enable_ndslfv
  nam_dyn=[[[
&nam_dyn
# there would be many more variables here ...
  ndslfv=@[NDSLFV],
  mass_dp=@[MASS_DP],
  process_split=@[PROCESS_SPLIT],
/
]]]
  GFS_VERSION="v13.0.4"
}
'''

tokenizer=Tokenizer()
parser=Parser()
context=fileless_context()
scope=Scope()
parser.parse(tokenizer.tokenize(mystring,filename="(mystring)"),scope)

def get(var):
    return scope.resolve(var).string_context(context)

print "nam_dyn = \n%s\n"%(get('gfsvars%nam_dyn'),)
print "NWPROD = %s\n"%(get('plat%NWPROD'),)
print "FIXGLOBAL = %s\n"%(get('gfsvars%FIXGLOBAL'),)
