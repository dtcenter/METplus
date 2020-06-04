"""!A shell-like syntax for running serial, MPI and OpenMP programs.

This module implements a shell-like syntax for launching MPI and
non-MPI programs from Python.  It recognizes three types of
executables: mpi, "small serial" (safe for running on a batch node)
and "big serial" (which should be run via aprun if applicable).  There
is no difference between "small serial" and "big serial" programs
except on certain architectures (like Cray) where the job script runs
on a heavily-loaded batch node and has compute nodes assigned for
running other programs.

@section progtype Program Types

There are three types of programs: mpi, serial and "big non-MPI."  A
"big" executable is one that is either OpenMP, or is a serial program
that cannot safely be run on heavily loaded batch nodes.  On Cray
architecture machines, the job script runs on a heavily-populated
"batch" node, with some compute nodes assigned for "large" programs.
In such environments, the "big" executables are run on compute nodes
and the small ones on the batch node.  

* mpi('exename') = an executable "exename" that calls MPI_Init and
    MPI_Finalize exactly once each, in that order.
* exe('exename') = a small non-MPI program safe to run on a batch node
* bigexe('exename') = a big non-MPI program that must be run on a
    compute node it may or may not use other forms of parallelism

You can also make reusable aliases to avoid having to call those
functions over and over (more on that later).  Examples:

* Python:   wrf=mpi('./wrf.exe')
* Python:   lsl=alias(exe('/bin/ls')['-l'].env(LANG='C',LS_COLORS='never'))

Those can then be reused later on as if the code is pasted in, similar
to a shell alias.

@section serexs Serial Execution Syntax

Select your serial programs by exe('name') for small serial programs
and bigexe('name') for big serial programs.  The return value of those
functions can then be used with a shell-like syntax to specify
redirection and piping.  Example:

*  shell version: ls -l / | wc -l
*  Python version: run(exe('ls')['-l','/'] | exe('wc')['-l'])

Redirection syntax similar to the shell (< > and << operators):
@code
  run( ( exe('myprogram')['arg1','arg2','...'] < 'infile' ) > 'outfile')
@endcode

Note the extra set of parentheses: you cannot do "exe('prog') < infile
> outfile" because of the order of precedence of Python operators

Append also works:
@code
  run(exe('myprogram')['arg1','arg2','...'] >> 'appendfile')
@endcode

You can also send strings as input with <<
@code
  run(exe('myprogram')['arg1','arg2','...'] << 'some input string')
@endcode

One difference from shells is that < and << always modify the
beginning of the pipeline:

* shell: cat < infile | wc -l
* Python #1: ( exe('cat') < 'infile' ) | exe('wc')['-l']
* Python #2: exe('cat') | ( exe('wc')['-l'] < 'infile' )

Note that the last second one, equivalent to `cat|wc -l<infile`, would
NOT work in a shell since you would be giving wc -l two inputs.  

@section parexs Parallel Execution Syntax

Use mpi('exename') to select your executable, use [] to set arguments,
use multiplication to set the number of ranks and use addition to
combine different executables together into a multiple program
multiple data (MPMD) MPI program.

Run ten copies of ls -l:
@code
  run(mpirun(mpiserial(('ls')['-l'])*10))
@endcode

Run HyCOM coupled HWRF: one wm3c.exe, 30 hycom.exe and 204 wrf.exe:
@code
  run(mpirun(mpi('wm3c.exe') + mpi('hycom.exe')*30 + mpi('wrf.exe')*204))
@endcode

You can set environment variables, pipe MPI output and handle
redirection using the mpirun() function, which converts MPI programs
into an bigexe()-style object (Runner):

Shell version:
@code{.unformatted}
    result=$( mpirun -n 30 hostname | sort -u | wc -l )
@endcode

Python version:
@code
    result=runstr( mpirun(mpi('hostname')*30) | exe['sort']['-u'] | exe['wc']['-l'] )
@endcode

@section aliases Aliases

If you find yourself frequently needing the same command, or you need
to store a command for multiple uses, then then you should define an
alias.  Let's say you want "long output" format Japanese language "ls"
output:

@code
  exe('ls')['-l','/path/to/dir'].env(LANG='JP')
@endcode

but you find yourself running that on many different directories.
Then you may want to make an alias:

@code
  jplsl=alias(exe('ls')['-l'].env(LANG='JP'))
@endcode

The return value jplsl can be treated as an exe()-like return value
since it was from exe() originally, but any new arguments will be
appended to the original set:

@code
  run(jplsl['/path/to/dir'])
@endcode

Note that if we did this:
@code
  badlsl=exe('ls')['-l'].env(LANG='JP')  # Bad! No alias!
  run(badlsl['/'])  # will list /
  run(badlsl['/home'])  # will list / and /home
  run(badlsl['/usr/bin']) # will list / /home and /usr/bin

  goodlsl=alias(exe('ls')['-l'].env(LANG='JP')
  run(goodlsl['/'])  # will list /
  run(goodlsl['/home'])  # will list /home
  run(goodlsl['/usr/bin']) # will list /usr/bin
@endcode

Then the run(badlsl['/home']) would list /home AND / which is NOT what
we want.  Why does it do that?  It is because badlsl is not an alias
--- it is a regular output from exe(), so every time we call its []
operator, we add an argument to the original command.  When we call
alias() it returns a copy-on-write version (goodlsl), where every call
to [] creates a new object.

Note that alias() also works with pipelines, but most operations will
only modify the last the command in the pipeline (or the first, for
operations that change stdin).
"""

import time, logging
import produtil.mpi_impl
import produtil.sigsafety
import produtil.prog as prog
import produtil.mpiprog as mpiprog
import produtil.pipeline as pipeline

# These two were moved to produtil.prog to avoid a cyclic import.
# They still need to be available from produtil.run:
from produtil.prog import InvalidRunArgument,ExitStatusException

##@var __all__
# List of symbols exported by "from produtil.run import *"
__all__=['alias','exe','run','runstr','mpi','mpiserial','mpirun',
         'runbg','prog','mpiprog','waitprocs','runsync',
         'InvalidRunArgument','ExitStatusException','checkrun',
         'batchexe','bigexe','openmp','make_mpi']

##@var module_logger
# Default logger used by some functions if no logger is given
module_logger=logging.getLogger('produtil.run')

##@var _detected_mpi
# The cached return value from detect_mpi()
_detected_mpi=None

def make_mpi(mpi_name=produtil.mpi_impl.NO_NAME,**kwargs):
    """!Creates an MPI implementation object for the specified MPI
    implementation. 

    Creates an object suitable for passing to the mpiimpl argument of
    various functions in produtil.run.  The object will implement the
    requested MPI implementation.  This object is NOT used to
    initialize the produtil.run; instead it is simply returned.

    @returns an MPI implementation object for the specified arguments

    @param mpi_name the name of the MPI implementation. If
    mpi_name=None, an mpiimpl for pure serial programs is returned.
    If no mpi_name is given, the local machine's available MPI
    implementation is detected and returned.

    @note When mpi_name is unset, the detection of the MPI
    implementation is redone, even if it had been done before by
    another call to get_mpi() or detect_mpi()

    @param kwargs additional arguments passed to produtil.mpi_impl.get_mpi()

    @see produtil.mpi_impl.impi.Implementation.detect()"""

    # The special value of None requests no MPI implementation.  That
    # situation does not need any initialization of the produtil.run
    # module:
    if mpi_name is None:
        return produtil.mpi_impl.get_mpi(None,**kwargs)

    # For anything other than "None," we have to ensure the
    # produtil.run is initialized to something before running
    # produtil.mpi_impl.get_mpi.
    detect_mpi()

    # Next, return the requested implementation:
    return produtil.mpi_impl.get_mpi(mpi_name,**kwargs)

def detect_mpi():
    """!Called by functions inside produtil.run to automatically
    detect the available MPI implementation.  

    Detects the available MPI implementation - but that isn't as
    simple as it sounds.  The detection logic requires calling
    produtil.run.  Hence, produtil.run must be usable during the call
    to detect_mpi().  The way this is handled is in three steps:

    1. Set the MPI implementation to "no MPI."  This will allow all
    serial (non-OpenMP, non-MPI) calls to succeed.

    2. Run the MPI implementation detection functions.  These will be
    able to use produtil.run to execute serial programs to detect 
    the MPI implementation.

    3. If an MPI implementation is detected, set the MPI
    implementation to that one.

    @note MPI implementation detection only happens during the first
    call to detect_mpi().  Any later calls will return the cached
    result from _detected_mpi.

    @returns a subclass of
    produtil.mpi_impl.mpi_impl_base.ImplementationBase for generation
    of produtil.prog.Runner objects from openmp or mpi program
    specifications.

    @see _detected_mpi"""
    global _detected_mpi
    if _detected_mpi: return _detected_mpi

    # First, set the implementation to None so that the mpi_impl
    # subclasses can use produtil.run.  This will only allow serial,
    # non-OpenMP programs:
    _detected_mpi=produtil.mpi_impl.get_mpi(None)

    # Next, ask produtil.mpi_impl to detect the MPI implementation:
    detected=produtil.mpi_impl.get_mpi()

    # If detection succeeds, override the selected MPI implementation:
    if detected:
        _detected_mpi=detected

    return _detected_mpi

def alias(arg):
    """!Attempts to generate an unmodifiable "copy on write" version
    of the argument.  The returned copy will generate a modifiable
    duplicate of itself if you attempt to change it.
    @returns a produtil.prog.ImmutableRunner
    @param arg a produtil.prog.Runner or produtil.prog.ImmutableRunner"""
    if isinstance(arg,prog.Runner):
        return prog.ImmutableRunner(arg)
    elif isinstance(arg,mpiprog.MPIRanksBase):
        arg.make_runners_immutable()
        return arg
    else:
        raise InvalidRunArgument('Arguments to alias() must be Runner objects (such as from exe()) or MPIRanksBase objects (such as from mpi() or mpiserial()).  Got: %s'%(repr(arg),))

def batchexe(name,**kwargs):
    """!Returns a prog.ImmutableRunner object that represents a small
    serial program that can be safely run on a busy batch node.
    @param name the executable name or path
    @param kwargs passed to produtil.prog.Runner.__init__
    @returns a new produtil.prog.ImmutableRunner"""
    return prog.ImmutableRunner([str(name)],**kwargs)

def exe(name,mpiimpl=None,**kwargs):
    """!Returns a prog.ImmutableRunner object that represents a large
    serial program that must be run on a compute node.
    @note This function does NOT search $PATH on Cray.  That ensures
      the $PATH will be expanded on the compute node instead.  Use
      produtil.fileop.find_exe() if you want to explicitly search the
      PATH before execution.
    @param name the executable name or path
    @param kwargs passed to produtil.prog.Runner.__init__
    @returns a new produtil.prog.ImmutableRunner"""
    if mpiimpl is None:
        mpiimpl=detect_mpi()
    return mpiimpl.make_bigexe(str(name),**kwargs)

def bigexe(name,**kwargs):
    """!Alias for exe() for backward compatibility.  Use exe() instead."""
    return exe(name,**kwargs)

def mpirun(arg,mpiimpl=None,**kwargs):
    """!Converts an MPI program specification into a runnable shell
    program suitable for run(), runstr() or checkrun().

    Options for kwargs:
    * allranks=True --- to run on all available MPI ranks.  This cannot be
      used if a specific number of ranks (other than 1) was requested in
      the arg.
    * logger=L --- a logging.Logger for log messages
    * Other platform-specific arguments.  See produtil.mpi_impl for details.

    @param arg the mpiprog.MPIRanksBase describing the MPI program to
    run.  This is the output of the mpi() or mpiserial() function.
    @param kwargs additional arguments to control output.  
    @returns a prog.Runner object for the specified
    mpiprog.MPIRanksBase object."""
    if mpiimpl is None:
        mpiimpl=detect_mpi()
    return mpiimpl.mpirunner(arg,**kwargs)

def make_pipeline(arg,capture,mpiimpl=None,**kwargs):
    """!This internal implementation function generates a
    prog.PopenCommand object for the specified input, which may be a
    prog.Runner or mpiprog.MPIRanksBase.
    @param arg the produtil.prog.Runner to convert.  This is the
      output of exe(), bigexe() or mpirun()
    @param capture if True, capture the stdout into a string
    @param kwargs additional keyword arguments, same as for  mpirun()"""
    if mpiimpl is None:
        mpiimpl=detect_mpi()
    if isinstance(arg,prog.Runner):
        runner=arg
    elif isinstance(arg, mpiprog.MPIRanksBase):
        runner=mpiimpl.mpirunner(arg,**kwargs)
    else:
        raise InvalidRunArgument(
            'Can only run a Runner object (such as from exe()) or an '
            'MPIRanksBase object (such as from mpi() or mpiserial()).  '
            'Got: %s'%(repr(arg),))
    logger=None
    if 'logger' in kwargs: logger=kwargs['logger']
    if logger is not None:
        logger.info('Starting: %s'%(repr(arg),))
        if capture: logger.info('  - and will capture output.')
    b=kwargs.get('binary',False)
    b=bool(b)
    pl=pipeline.Pipeline(runner,capture=capture,logger=logger,
                         binary=b)
    if logger is not None:
        logger.debug('Pipeline is %s'%(repr(pl),))
    return pl

def runbg(arg,capture=False,**kwargs):
    """!Not implemented: background execution

    Runs the specified process in the background.  Specify
    capture=True to capture the command's output.  Returns a
    produtil.prog.PopenCommand.  Call poll() to determine process
    completion, and use the stdout_data property to get the output
    after completion, if capture=True was specified.

    @bug produtil.run.runbg() is not implemented

    @warning this is not implemented

    @param arg the produtil.prog.Runner to execute (output of
      exe(), bigexe() or mpirun()
    @param capture if True, capture output
    @param kwargs same as for mpirun()"""
    p=make_pipeline(arg,capture,**kwargs)
    p.background()
    return p

def waitprocs(procs,logger=None,timeout=None,usleep=1000):
    """!Not implemented: background process monitoring

    Waits for one or more backgrounded processes to complete.  Logs to
    the specified logger while doing so.  If a timeout is specified,
    returns False after the given time if some processes have not
    returned.  The usleep argument is the number of microseconds to
    sleep between checks (can be a fraction).  The first argument,
    procs specifies the processes to check.  It must be a
    produtil.prog.Pipeline (return value from runbg) or an iterable
    (list or tuple) of such.

    @bug produtil.run.waitprocs() is untested

    @warning This is not tested and probably does not work.

    @param procs the processes to watch
    @param logger the logging.Logger for log messages
    @param timeout how long to wait before giving up
    @param usleep sleep time between checks"""
    p=set()
    if isinstance(procs,produtil.prog.PopenCommand):
        p.add(procs)
    else:
        for pp in procs:
            p.add(pp)
    if logger is not None: logger.info("Wait for: %s",repr(p))
    while p: # keep looping as long as there are unfinished processes
        p2=set()
        for proc in p:
            ret=proc.poll()
            if ret is not None:
                if logger is not None:
                    logger.info("%s returned %s"%(repr(proc),repr(ret)))
            elif logger is not None and usleep>4.99999e6:
                # babble about running processes if the sleep time is long.
                logger.info("%s is still running"%(repr(proc),))
                p2.add(proc)
        p=p2

        if not p: break # done! no need to sleep...

        if usleep>4.99999e6 and logger is not None:
            # babble about sleeping if the sleep time is 5sec or longer:
            logger.info("... sleep %f ..."%(float(usleep/1.e6),))
        time.sleep(usleep/1.e6)
    return False if(p) else True

def runsync(logger=None,mpiimpl=None):
    """!Runs the "sync" command as an exe()."""
    if mpiimpl is None:
        mpiimpl=detect_mpi()
    return mpiimpl.runsync(logger=logger)

def run(arg,logger=None,sleeptime=None,**kwargs):
    """!Executes the specified program and attempts to return its exit
    status.  In the case of a pipeline, the highest exit status seen
    is returned.  For MPI programs, exit statuses are unreliable and
    generally implementation-dependent, but it is usually safe to
    assume that a program that runs MPI_Finalize() and exits normally
    will return 0, and anything that runs MPI_Abort(MPI_COMM_WORLD)
    will return non-zero.  Programs that exit due to a signal will
    return statuses >255 and can be interpreted with WTERMSIG,
    WIFSIGNALLED, etc.
    @param arg the produtil.prog.Runner to execute (output of
      exe(), bigexe() or mpirun()
    @param logger a logging.Logger to log messages
    @param sleeptime time to sleep between checks of child process
    @param kwargs ignored"""
    p=make_pipeline(arg,False,logger=logger)
    p.communicate(sleeptime=sleeptime)
    result=p.poll()
    if logger is not None:
        logger.info('  - exit status %d'%(int(result),))
    return result

def checkrun(arg,logger=None,**kwargs):
    """!This is a simple wrapper round run that raises
    ExitStatusException if the program exit status is non-zero.  

    @param arg the produtil.prog.Runner to execute (output of
      exe(), bigexe() or mpirun()
    @param logger a logging.Logger to log messages
    @param kwargs The optional run=[] argument can provide a different
    list of acceptable exit statuses."""
    r=run(arg,logger=logger)
    if kwargs is not None and 'ret' in kwargs:
        if not r in kwargs['ret']:
            raise ExitStatusException('%s: unexpected exit status'%(repr(arg),),r)
    elif not r==0:
        raise ExitStatusException('%s: non-zero exit status'%(repr(arg),),r)
    return r

def openmp(arg,threads=None,mpiimpl=None):
    """!Sets the number of OpenMP threads for the specified program.

    @warning Generally, when using MPI with OpenMP, the batch system
    must be configured correctly to handle this or unexpected errors
    will result.

    @param arg The "arg" argument must be from mpiserial, mpi, exe or
    bigexe.

    @param threads The optional "threads" argument is an integer number of
    threads.  If it is not specified, the maximum possible number of
    threads will be used.  Note that using threads=None with
    mpirun(...,allranks=True) will generally not work unless the batch
    system has already configured the environment correctly for an
    MPI+OpenMP task with default maximum threads and ranks.
    @returns see run()"""
    if mpiimpl is None:
        mpiimpl=detect_mpi()
    return mpiimpl.openmp(arg,threads)
    
def runstr(arg,logger=None,**kwargs):
    """!Executes the specified program or pipeline, capturing its
    stdout and returning that as a string.  

    If the exit status is non-zero, then NonZeroExit is thrown.  

    Example:
    @code
      runstr(exe('false'),ret=(1))
    @endcode

    succeeds if "false" returns 1, and raises ExitStatusError otherwise.

    @param arg The "arg" argument must be from mpiserial, mpi, exe or
    bigexe.
    @param logger a logging.Logger for logging messages
    @param kwargs You can specify an optional list or tuple "ret" that
    contains an alternative list of valid return codes.  All return
    codes are zero or positive: negative values represent
    signal-terminated programs (ie.: SIGTERM produces -15, SIGKILL
    produces -9, etc.) """
    p=make_pipeline(arg,True,logger=logger)
    s=p.to_string()
    r=p.poll()
    if kwargs is not None and 'ret' in kwargs:
        if not r in kwargs['ret']:
            raise ExitStatusException('%s: unexpected exit status'%(repr(arg),),r)
    elif not r==0:
        raise ExitStatusException('%s: non-zero exit status'%(repr(arg),),r)
    return s

def mpi(arg,**kwargs):
    """!Returns an MPIRank object that represents the specified MPI
    executable.
    @param arg the MPI program to run
    @param kwargs logger=L for a logging.Logger to log messages"""
    return mpiprog.MPIRank(arg,**kwargs)

def mpiserial(arg,**kwargs):
    """!Generates an mpiprog.MPISerial object that represents an MPI
    rank that executes a serial (non-MPI) program.  The given value
    MUST be from bigexe() or exe(), NOT from mpi().
    @param arg the MPI program to run
    @param kwargs logger=L for a logging.Logger to log messages"""
    return mpiprog.MPISerial(arg.remove_prerun(),**kwargs)
