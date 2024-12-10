"""!Provides information about the batch system.

This module is intended to be used to communicate with the batch
system.  At present, it just knows how to guess the job name and id,
as well as a "longname" that combines the two."""

##@var __all__
# List of symbols exported by "from produtil.batchsystem import *"
__all__=['jobname','jobid','joblongname','NONAME']
import os

class FakeClass:
    """!A special class for constants."""

##@var UNSPECIFIED
# Constant for unspecified arguments.
UNSPECIFIED=FakeClass()

##@var NONAME
# Name for jobs that have no name.
NONAME="NONAME"

##@var _set_jobname
# Manually-specified jobname, from set_jobname()
_set_jobname=None

##@var _set_jobid
# Manually specified job id from set_jobid()
_set_jobid=None

##@var _set_joblongname
# Manually specified job longname from set_joblongname()
_set_joblongname=None

##@var _set_default
# Manually specified job "everything name" from set_default_name()
_set_default=None

def set_default_name(default_name):
    """!Set default for all job names.

    Sets a default value to use for the job name and long name if it
    cannot be guessed from the environment.  This is used by
    produtil.setup.setup's jobname= argument.  This will override the
    fallback= arguments of both jobname() and joblongname()
    @param default_name the name"""
    global _set_default
    _set_default=default_name

def set_jobname(jobname):
    """!Sets the value that jobname() should return.
    @param jobname the name"""
    global _set_jobname
    _set_jobname=str(jobname)

def set_jobid(jobid):
    """!Sets the value that jobid() should return.
    @param jobid the id"""
    global _set_jobid
    _set_jobid=str(jobid)

def set_joblongname(joblongname):
    """!Sets the value that joblongname() should return.
    @param joblongname the new long name"""
    global _set_joblongname
    _set_joblongname=str(joblongname)

def getenvs(names,fallback=None):
    """!Get an environment variable, with various fallback options

    Tries the list of environment variable names, returning the first
    one that exists and is non-blank.  If none are found, returns the
    fallback.
    @param names the list of environment variables
    @param fallback the fallback option if none are set    """
    for name in names:
        if name not in os.environ:           continue
        val=os.environ[name]
        if not isinstance(val,str):          continue
        if len(val)<1:                       continue
        return val
    return fallback

def jobname(fallback=UNSPECIFIED):
    """!Get the batch job name

    Returns the human-readable job name, if one exists.  If
    set_jobname was called, returns its value.  Otherwise, attempts to
    get it from the NCO $job environment variable first, then
    tries the batch system variables.  If none are found, and
    fallback is specified, then the fallback is returned.  Otherwise,
    the module-level NONAME variable is returned (which defaults to
    "NONAME").
    @param fallback return value if no job name is known"""
    if _set_jobname: return _set_jobname
    ret=getenvs(['job','LSB_JOBNAME','PBS_JOBNAME','MOAB_JOBNAME',
                'LOADL_STEP_NAME','LOADL_JOB_NAME'])
    if ret is not None: return ret
    if _set_default is not None: return _set_default
    if fallback is not UNSPECIFIED: return fallback
    return NONAME

def jobid(fallback=UNSPECIFIED):
    """!Get the batch job ID

    Returns the batch system job id for the batch job that is running
    this program, if known.  If set_jobid was called, returns its
    value.  Otherwise, tries the NCO $pid first, then the various
    batch system environment variables.  If none are found, and the
    fallback is specified, returns the fallback.  Otherwise, returns
    "o$PID" where $PID is the process ID.
    @param fallback the fallback if no id is known"""
    ret=getenvs(['pid','LSB_JOBID','PBS_JOBID','MOAB_JOBID','LOADL_STEP_ID'])
    if ret is not None: return ret
    if _set_default is not None: return _set_default
    if fallback is not UNSPECIFIED: return fallback
    return 'o%s'%(str(os.getpid()),)

def joblongname(jobid_fallback=UNSPECIFIED,
                jobname_fallback=UNSPECIFIED):
    """!Get the job longname

    Returns a human-readable job name that includes both the batch
    system job name and id.  If set_joblongname was called, returns
    its value.  Next, returns the NCO $jobid variable if available,
    otherwise returns LL{jobid()}.o{jobname()} where jobid and jobname
    are the results of those two functions.  The jobid_fallback and
    jobname_fallback are passed as the fallback parameters to the
    calls to jobid and jobname.
    @param jobid_fallback the fallback if no id is known
    @param jobname_fallback the fallback if no name is known"""
    if _set_joblongname: return _set_joblongname
    ret=getenvs(['jobid'])
    if ret is not None: return ret
    return 'LL%s.%s'%(jobid(jobid_fallback),jobname(jobname_fallback))
