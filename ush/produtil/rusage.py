"""!This module allows querying resource usage and limits, as well as
setting resource limits.  It is a wrapper around the Python resource
module.

Setting resource limits:
@code
  use logging, produtil.rusage
  logger=logging.logger("rusage")
  produtil.rusage.setrlimit(logger,data=1e9,nofile=500,aspace=2e9,stack=5e8)
@endcode

Printing resource limits to a logger:
@code
  use logging, produtil.rusage
  logger=logging.logger("rusage")
  u.produtil.rusage.getrlimit(logger) # writes the limits to the logger
  # Limits are also in the returned object "u"
  # Send None instead of logger to avoid logging.
@endcode
"""

import resource, logging, StringIO, time

##@var rtypemap
# Maps the name used in this module for each resource class to the
# name used by the Python resource module
rtypemap=dict(core=resource.RLIMIT_CORE,
              cpu=resource.RLIMIT_CPU,
              fsize=resource.RLIMIT_FSIZE,
              data=resource.RLIMIT_DATA,
              stack=resource.RLIMIT_STACK,
              rss=resource.RLIMIT_RSS,
              nproc=resource.RLIMIT_NPROC,
              nofile=resource.RLIMIT_NOFILE,
              #ofile=resource.RLIMIT_OFILE,
              memlock=resource.RLIMIT_MEMLOCK,
              #vmem=resource.RLIMIT_VMEM,
              aspace=resource.RLIMIT_AS)
"""Maps the name used in this module for each resource class, to the
name used by the Python resource module."""

##@var rnamemap
# Maps the name used in this module for each resource class, to a
# short human-readable string explaining the resource's meaning.
rnamemap=dict(core='core file size',
              cpu='cpu usage',
              fsize='max. file size',
              data='max. heap size',
              stack='max. stack size',
              rss='max. resident set size',
              nproc='max. processes',
              nofile='max. open files',
              #ofile='max. open files (BSD)',
              memlock='max. locked memory',
              #vmem='max. virtual memory',
              aspace='max. address space')
"""Maps the name used in this module for each resource class, to a
short human-readable string explaining the resource's meaning."""

def setrlimit(logger=None, ignore=False, hard=False, **kwargs):
    """!Sets resource limits.  

    @param ignore If ignore=True, ignores any errors from
       getrlimit or setrlimit.  
    @param hard If hard=True, attempts to set hard
    limits, which generally requires administrator privileges.  
    @param logger The logger argument sets the logger (default:
    produtil.setrlimit logging domain).  
    @param kwargs The kwargs should be a list of resource limits.
    Accepted resource limits:
    *  core   = core file size (RLIMIT_CORE)
    *  cpu    = max. cpu usage (RLIMIT_CPU)
    *  fsize  = max. file size (RLIMIT_FSIZE)
    *  data   = max. heap size (RLIMIT_DATA)
    *  stack  = max. stack size (RLIMIT_STACK)
    *  rss    = max. resident set size (RLIMIT_RSS)
    *  nproc  = max. processes (RLIMIT_NPROC)
    *  nofile = max. open files (RLIMIT_NOFILE or RLIMIT_OFILE)
    *  memlock= max locked memory (RLIMIT_MEMLOCK)
    *  aspace = max. address space (RLIMIT_AS)
    See "man setrlimit" for details."""
    if logger is None: logger=logging.getLogger('produtil.setrlimit')
    for k,v in kwargs.iteritems():
        try:
            (softL,hardL)=resource.getrlimit(rtypemap[k])
            if hard: 
                hardL=kwargs[k]
            softL=kwargs[k]
            if logger is not None:
                logger.info('Requesting %s (%s) soft=%s hard=%s'
                            %(k,rnamemap[k],softL,hardL))
            resource.setrlimit(rtypemap[k],(softL,hardL))
        except (resource.error,EnvironmentError,ValueError,TypeError,KeyError) as e:
            if logger is not None:
                logger.warning("%s: cannot set limit: %s"%(k,str(e)),exc_info=True)
            if not ignore: raise

class RLimit(object):
    """!Gets the resource limits set on this process:
      core, cpu, fsize, data, stack, rss, nproc, nofile, memlock, aspace
    Each is set to a tuple containing the soft and hard limit."""
    def __init__(self,logger=None):
        """!RLimit constructor
        @param logger a logging.Logger for log messages."""
        if logger is None:
            logger=logging.getLogger('produtil.getrlimit')
        for (name,limit) in rtypemap.iteritems():
            try:
                r=resource.getrlimit(limit)
                if r is None:
                    logger.warning('%s: cannot get limit: '
                                   'getrlimit returned None.'%(name,))
                self.__dict__['_limits_'+name]=r
            except (resource.error,ValueError) as e:
                logger.warning('%s: cannot get limit: %s'%(name,str(e)),
                               exc_info=True)
    def __str__(self):
        """!Creates a multi-line string representation of the resource
        limits."""
        out=StringIO.StringIO()
        for k,v in self.__dict__.iteritems():
            kk=k[8:]
            if k[0:8]=='_limits_':
                (soft,hard)=v
                if(soft<0): soft=hard
                if soft<0: 
                    out.write('%7s - %25s = (unlimited)\n'%(kk,rnamemap[kk]))
                else:
                    out.write('%7s - %25s = %g\n'%(kk,rnamemap[kk],soft))
        return out.getvalue()

def getrlimit(logger=None):
    """!Gets the current resource limits.  If logger is not None,
    sends the limits to the logger at level INFO.
    @returns a RLimit object with resource information"""
    rlimit=RLimit(logger=logger)
    if logger is not None:
        for line in str(rlimit).splitlines():
            logger.info(line)
    return rlimit

##@var rusage_keys
# A tuple containing all rusage keys.
rusage_keys=('ru_utime','ru_stime','ru_maxrss','ru_ixrss','ru_idrss',
             'ru_isrss','ru_minflt','ru_majflt','ru_nswap','ru_inblock',
             'ru_oublock','ru_msgsnd','ru_msgrcv','ru_nsignals',
             'ru_nvcsw','ru_nivcsw')
"""Tuple containing all rusage keys."""

##@var rusage_meanings
# A mapping from rusage key to a human-readable explanation of the meaning.
rusage_meanings=dict(ru_utime='time in user mode',
                     ru_stime='time in system mode',
                     ru_maxrss='maximum resident set size',
                     ru_ixrss='shared memory size',
                     ru_idrss='unshared memory size',
                     ru_isrss='unshared stack size',
                     ru_minflt='page faults not requiring I/O',
                     ru_majflt='page faults requiring I/O',
                     ru_nswap='number of swap outs',
                     ru_inblock='block input operations',
                     ru_oublock='block output operations',
                     ru_msgsnd='messages sent',
                     ru_msgrcv='messages received',
                     ru_nsignals='signals received',
                     ru_nvcsw='voluntary context switches',
                     ru_nivcsw='involuntary context switches')
"""A mapping from rusage key to a human-readable explanation of the
meaning."""

class RUsageReport(Exception):
    """!Raised when caller makes an RUsage, and tries to generate its
    report, before calling its __enter__ or __exit__ routines."""

class RUsage(object):
    """!Contains resource usage (rusage) information that can be used
    with a Python "with" construct to collect the resources utilized
    by a block of code, or group of subprocesses executing during that
    block.

    Example:
    @code
      with produtil.rusage.RUsage(logger=logging.getLogger("usage")):
          ... do things ...
      ... stop doing things ...
    @endcode

    Just after the "with" block exits, the resource usage is printed
    to the given logger.  The information can be retained for
    inspection instead:
    @code
      u=produtil.rusage.RUsage(logger=logging.getLogger("usage"))
      with u:
          ... do things ...
      ... stop doing things ...
      # u.rusage_before is a dict of resource usage before the block
      # u.time_before contains the time before the block
      # u.rusage_after contains the resource usage at the end of the block
      # u.time_after contains the time after the block
    @endcode

    Note that the logger is optional: without it, nothing is logged."""
    def __init__(self,who=resource.RUSAGE_CHILDREN,logger=None):
        """!Creates an RUsage object for input to a "with" statement.

        @param who Pass who=resource.RUSAGE_SELF to get usage on this
        process or rusage.RUSAGE_CHILDREN (the default) to get
        resource usage on child processes.
        @param logger a logging.Logger for log messages"""
        self.logger=logger
        self.rusage_before=None
        self.rusage_after=None
        self.time_before=None
        self.time_after=None
        self._pagesize=resource.getpagesize()
        self._who=who
        self._report=None
    ##@var logger
    # The logging.Logger for log messages

    ##@var rusage_before
    # Resource usage before monitoring began

    ##@var rusage_after 
    # The resource usage after monitoring ended

    ##@var time_before
    # The current time before usage monitoring began

    ##@var time_after
    # The current time after monitoring ended.

    @property
    def who(self):
        """!The "who" parameter to the constructor, which selects
        whether the usage measured should be of the child processes
        (RUSAGE_CHILDREN) or this process (RUSAGE_SELF) .  See
        __init__ for details."""
        return self._who
    @property
    def pagesize(self):
        """!System page size in bytes from resource.getpagesize().
        This is needed to interpret return values."""
        return self._pagesize
    def __enter__(self):
        """!Gets the resource usage and time at the top of the "with"
        block.  This function is called automatically by the Python
        interpreter at the beginning of a "with" block."""
        self.rusage_before=resource.getrusage(self._who)
        self.time_before=float(time.time())
    def __exit__(self, type, value, tb):
        """!Gets the resource usage and time at the end of a "with"
        block.  This is called automatically by Python at the end of a
        "with" block.
        @param type,value,tb exception information"""
        self.time_after=float(time.time())
        self.rusage_after=resource.getrusage(self._who)
        if self.logger is not None:
            for line in self.report().splitlines():
                self.logger.info(line)
    def report(self):
        """!Generates a string report of the resource usage utilized.
        Accessible via str(self)."""
        if self._report is None:
            s=StringIO.StringIO()
            b=self.rusage_before
            a=self.rusage_after
            if a is None or b is None:
                raise RUsageNotRun("You cannot generate an RUsage report until you run RUsage.")
            dt=self.time_after-self.time_before
            for k in rusage_keys:
                if hasattr(a,k) and hasattr(b,k):
                    s.write('%11s - %29s = %g\n'%(k,rusage_meanings[k],
                                                  getattr(a,k)-getattr(b,k)))
            s.write('%11s - %29s = %g\n'%('ru_walltime','wallclock time',dt))
            self._report=s.getvalue()
        return self._report
    def __str__(self):
        """!Generates a string report of the resource usage utilized."""
        if self.rusage_before is None or self.rusage_after is None:
            return '(uninitialized RUsage report)'
        else:
            if self._report is None: self.report()
            return self._report

##@var produtil.rusage.rusage
# Alias for produtil.rusage.RUsage
rusage=RUsage
"""A synonym for RUsage"""
