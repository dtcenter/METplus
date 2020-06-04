"""!Configures logging.

This module configures logging for stdout, stderr and the jlogfile.
It also contains the jlogger, a logger.Logger object that is used to
log directly to the jlogfile, and jlogdomain: a string name of the 
logger domain for the jlogfile."""

##@var __all__
# Symbols epxorted by "from produtil.log import *"
__all__ = [ 'configureLogging','jlogger','jlogdomain','postmsg',
            'MasterLogFormatter','JLogFormatter','stdout_is_stderr',
            'MasterLogHandler','JLogHandler','set_jlogfile' ]

import logging, os, sys, traceback, threading
import produtil.batchsystem

##@var logthread
# string for log messages to indicate thread number/name 
logthread='' 

##@var jlogdomain
# Logging domain for the jlogfile
jlogdomain='jlog'

##@var jlogger
# A logging.Logger for the jlogdomain
jlogger=logging.getLogger(jlogdomain)

##@var jloghandler
# A logging.LogHandler for the jlogger
jloghandler=None

##@var masterlogger
# Master log stream for MPI-split jobs.
#
# When a job is split via mpi_redirect, this logger will send data to
# the master log stream at lower log levels.  This is configurable via
# calls to mpi_redirect()
masterlogger=None

##@var masterdomain
# Logging domain for the masterlogger
masterdomain=None

class ThreadLogger(logging.Logger):
    """!Custom logging.Logger that inserts thread information."""
    def makeRecord(self,name,lvl,fn,lno,msg,*args,**kwargs):
        """!Replaces the logging.Logger.makeRecord() with a new
        implementation that inserts thread information from
        threading.current_thread()
        @param name,lvl,fn,lno,msg,args,kwargs Log message information.
          See the Python logging module documentation for details."""
        ct=threading.current_thread()
        msg='[%s] %s'%(str(ct.name),str(msg))
        x=logging.Logger.makeRecord(self,name,lvl,fn,lno,msg,*args,**kwargs)
        return x

def postmsg(message):
    """!Sends the message to the jlogfile logging stream at level INFO.

    This is identical to:
    @code
       jlogger.info(message).
    @endcode
    @param message the message to log."""
    return jlogger.info(message)

def set_jlogfile(filename):
    """!Tells the jlogger to log to the specified file instead of the
    current jlogfile.  Also updates the jlogfile environment variable.
    The argument must be a filename.
    @param filename the new jlogfile"""
    jloghandler.set_jlogfile(filename)
    os.environ['jlogfile']=filename

class MasterLogFormatter(logging.Formatter): 
    """!This is a custom log formatter that inserts the thread or
    process (logthread) that generated the log message.  Also, it
    always directly calls formatException from format, ensuring that
    cached information is not used.  That allows a subclass
    (JLogFormatter) to ignore exceptions.""" 
    def __init__(self,fmt=None,datefmt=None,logthread=None): 
        """!MasterLogFormatter constructor
        @param fmt the log message format
        @param datefmt the date format
        @param logthread the thread name for logging
        @note See the Python logging module documentation for details."""
        logging.Formatter.__init__(self,fmt=fmt,datefmt=datefmt)
        self._logthread=None 
    @property
    def logthread(self):
        """!The name of the batch thread or process that generated log
        messages, if the LogRecord does not supply that already.""" 
        global logthread # use global value if I don't have one 
        if self._logthread is None: return logthread 
        return self._logthread 
    def format(self, record):
        """!Replaces the logging.Formatter.format() function.

        We need to override this due to a "feature" in the
        Formatter.format: It ignores formatException (never calls it)
        and caches the exception info, even if the formatter is not
        supposed to output it.
        @param record the log record to format
        @note See the Python logging module documentation for details."""
        global logthread
        record.message = record.getMessage()
        if self._fmt.find("%(asctime)") >= 0:
            record.asctime = self.formatTime(record, self.datefmt)
        if 'logthread' not in record.__dict__:
            record.__dict__['logthread']=self.logthread
        s = self._fmt % record.__dict__
        if 'exc_info' in record.__dict__ and record.exc_info is not None:
            e = self.formatException(record.exc_info)
            if e:
                rec2=dict(record.__dict__)
                for line in str(e).splitlines():
                    rec2['message']=line
                    s="%s\n%s"%( s, self._fmt % rec2 )
        return s
    def formatException(self, ei):
        """!Returns nothing to indicate no exception information should
        be printed.
        @param ei the exception information to ignore"""

class JLogFormatter(MasterLogFormatter):
    """!This subclass of MasterLogFormatter does not include exception
    information in the log file.  This is done to prevent cluttering
    of the log file."""
    def formatException(self, ei):
        """!Returns nothing to indicate no exception information should
        be printed.
        @param ei the exception information to ignore"""

def stdout_is_stderr():
    """!Returns True if it can determine that stdout and stderr are the
    same file or terminal.  Returns False if it can determine they are
    not, or if the result is inconclusive."""
    try:
        if os.fstat(sys.stdout.fileno()) == os.fstat(sys.stderr.fileno()):
            return True
        if sys.stdout.isatty() and sys.stderr.isatty():
            return True
    except Exception as e:
        pass
    return False

class MasterLogHandler(logging.Handler):
    """!Custom LogHandler for the master process of a multi-process job.

    This is a custom logging Handler class used for multi-process or
    multi-job batch scripts.  It has a higher minimum log level for
    messages not sent to the jlogfile domain.  Also, for every log
    message, the log file is opened, the message is written and the
    file is closed.  This is done to mimic the postmsg command.
    Exception information is never sent to the log file."""
    def __init__(self,logger,jlogdomain,otherlevels,joformat,jformat):
        """!MasterLogHandler constructor
        @param logger The logging.Logger for the master process.
        @param jlogdomain The logging domain for the jlogfile.
        @param otherlevels Log level for any extrema to go to the jlogfile.
        @param joformat Log format for other streams.
        @param jformat Log format for the jlogfile stream."""
        logging.Handler.__init__(self)
        self._logger=logger
        self._otherlevels=otherlevels
        self._jlogdomain=jlogdomain
        self._joformat=joformat
        self._jformat=jformat
    def stringify_record(self,record):
        """!Convert a log record to a string.
        @note See the Python logging module documentation for details.
        @returns a string message to print"""
        assert(isinstance(self._joformat,MasterLogFormatter))
        assert(isinstance(self._jformat,MasterLogFormatter))
        global logthread
        if record.name==self._jlogdomain:
            # Reformat for jlogdomain:
            message=self._jformat.format(record)
        elif record.levelno<self._otherlevels:
            return None # log level too low
        else:
            message=self._joformat.format(record)
        message+='\n'
        return message
    def emit(self,record):
        """!Write a log message.
        @param record the log record
        @note See the Python logging module documentation for details."""
        message=self.stringify_record(record)
        if message is None: return
        self._logger.write(message)

class JLogHandler(MasterLogHandler):
    """!Custom LogHandler for the jlogfile.

    This is a custom logging Handler class for the jlogfile.  It has a
    higher minimum log level for messages not sent to the jlogfile
    domain.  Also, for every log message, the log file is opened, the
    message is written and the file is closed.  This is done to mimic
    the postmsg command.  Exception information is never sent to the
    log file."""
    def emit(self,record):
        """!Write a log message.
        @param record the log record
        @note See the Python logging module documentation for details."""
        message=self.stringify_record(record)
        if message is None: return
        if isinstance(self._logger,str):
            # Open the file, write and close it, to mimic the postmsg script:
            dirn=os.path.dirname(self._logger)
            if not os.path.isdir(dirn):
                # NOTE: Cannot use produtil.fileop.makedirs here due
                # to order of module loads (fileop needs log, so log
                # cannot need fileop):
                for x in range(10):
                    try:
                        os.makedirs(dirn)
                    except EnvironmentError as e:
                        if os.path.isdir(dirn): 
                            break
                        elif os.path.exists(dirn):
                            raise
                        elif x<9:
                            continue
                        raise
            with open(self._logger,'at') as f:
                f.write(message)
        else:
            self._logger.write(message)
    def set_jlogfile(self, filename):
        """!Set the location of the jlogfile
        @param filename The path to the jlogfile."""
        if not isinstance(filename,str):
            raise TypeError(
                'In JLogHandler.set_jlogfile, the filename must be a '
                'string.  You passed a %s %s.'
                %(type(filename).__name__,repr(filename)))
        self._logger=filename

def mpi_redirect(threadname,stderrfile,stdoutfile,
                 threadlevel=logging.WARNING,
                 masterlevel=logging.INFO,
                 openmode=None,logger=None):
    """!Used to split to multiple logging streams.

    When the Python script splits itself into multiple processes via
    MPI, this function is called to redirect stdout to stdoutfile,
    stderr to stderrfile, and produce a new logging stream to the
    original stderr, with a logging level set to masterlevel.  That
    new logging stream is called the "master log" and will receive any
    messages at level masterlevel or higher, and any messages sent to
    the jlogdomain.

    This can also be used to redirect ONLY stdout, in which case no
    master logging stream is set up.  That is requested by
    stderrfile=None.
    @param threadname the name of this process for logging purposes
    @param stderrfile file to receive stderr
    @param stdoutfile file to receive stdout
    @param masterlevel log level to send to master log stream
    @param openmode integer mode to use when opening files
    @param logger a logging.Logger for logging errors while splitting
      the log stream.    """
    if logger is None: logger=logging.getLogger('produtil')
    if openmode is None:
        openmode=os.O_CREAT|os.O_WRONLY|os.O_APPEND
    elif not isinstance(openmode,int):
        raise TypeError(
            "In mpiRedirect, the openmode must be an int, not a "
            +type(openmode).__name__)
    if not isinstance(stdoutfile,str):
        raise TypeError(
            "In mpiRedirect, the stdoutfile must be a string, not a "
            +type(stdoutfile).__name__)
    if stderrfile is not None and not isinstance(stderrfile,str):
        raise TypeError(
            "In mpiRedirect, the stderrfile must be a string or None, not a "
            +type(stderrfile).__name__)
    if not isinstance(threadname,str):
        raise TypeError(
            "In mpiRedirect, the threadname must be a string, not a "
            +type(threadname))

    global logthread
    logthread='['+str(threadname)+']'

    logger.warning('Redirecting stdout to "%s" for thread %s'
                   %(stdoutfile,logthread))
    fd=os.open(stdoutfile,openmode)
    os.dup2(fd,1)

    if stderrfile is not None:
        logger.warning('Redirecting stderr to "%s" for thread %s'
                       %(stderrfile,logthread))

        olderrfd=os.dup(2)
        olderr=os.fdopen(olderrfd,'at',0)

        if(stdoutfile!=stderrfile):
            # Only reopen if stderr differs from stdout.
            fd=os.open(str(stderrfile),openmode)
        os.dup2(fd,2)
    
        oformat=MasterLogFormatter(
            "%(asctime)s.%(msecs)03d %(name)s %(logthread)s (%(filename)s:"
            "%(lineno)d) %(levelname)s: %(message)s",
            "%m/%d %H:%M:%S")

        # Create the master log handler.  It will send to the old stderr
        # (from before the redirection), and send everything from
        # masterlevel and higher from any logging domain.  Anything sent
        # to the jlogfile, at any level, will be sent to the master log
        # file as well.
        mloghandler=MasterLogHandler(olderr,masterdomain,threadlevel,oformat,
                                     oformat)
        logger.warning('Turning on logging of high priority messages to '
                       'original stderr stream.')
        if masterlevel!=logging.NOTSET:
            mloghandler.setLevel(masterlevel)
        else:
            raise BaseException('no master level')
        logging.getLogger().addHandler(mloghandler)
    global masterlogger
    masterlogger=logging.getLogger(masterdomain)

def _set_master_domain(d):
    global masterlogger, masterdomain
    masterdomain=d
    masterlogger=logging.getLogger(d)
    
def configureLogging(jlogfile=None,
                     level=logging.INFO, # all messages filtered by this
                     jloglevel=logging.INFO,
                     japplevel=logging.ERROR, # should be >=jloglevel
                     eloglevel=logging.WARNING,
                     ologlevel=logging.NOTSET,
                     thread_logger=False,
                     masterdomain='master'):
    """!Configures log output to stderr, stdout and the jlogfile

    Configures log file locations and logging levels for all streams.

    @note Important notes when choosing levels:
    * level - sets the global minimum log level.  Anything below this
          level will be discarded regardless of other settings.
    * jloglevel - this limit is applied before japplevel

    @param jlogfile path to the jlogfile. Default: use
            os.environ('jlogfile') if set.  Otherwise, stderr.
    @param level minimum logging level globally.  Set to INFO by default.
            Change this to logging.DEBUG if you're debugging the program.
    @param jloglevel minimum logging level to send to jlogfile
    @param japplevel minimum logging level to send to jlogfile from all
            domains except that specified in jlogdomain.  Be careful
            when changing this as it logs directly to the WCOSS-wide
            jlogfile in operations.
    @param eloglevel minimum logging level to send to stderr from ALL logs
            Set to None to disable stderr logging
    @param ologlevel minimum logging level to send to stdout from ALL logs
            Default: logging.NOTSET (no filtering)
            Set to None to disable stdout logging.
    @param thread_logger True to include the thread name in log messages.
    @param masterdomain The logging domain that will send messages to the
            main log stream for the job, even within individual ranks of
            mpi-split jobs"""

    global jloghandler

    if thread_logger:
        logging.setLoggerClass(produtil.log.ThreadLogger)

    _set_master_domain(masterdomain)
    
    root=logging.getLogger()
    if level!=logging.NOTSET:
        root.setLevel(level) # set global minimum logging level

    # Configure log formatting:
    jlog=logging.getLogger('jlogfile')
    jobstr=os.environ.get('job',None)
    if jobstr is None:
        jobstr=produtil.batchsystem.jobname()
    jobstr=str(jobstr).replace('(','_').replace(')','_').replace('%','_')
    # Format for jlogfile domain logging to jlogfile:
    jformat=JLogFormatter(
        "%(asctime)sZ "+jobstr+"-%(levelname)s: %(logthread)s %(message)s",
        "%m/%d %H:%M:%S")
    # Format for other domains logging to jlogfile is the same, but
    # with the domain added:
    joformat=JLogFormatter(
        "%(asctime)sZ "+jobstr+
        "-%(name)s: %(levelname)s: %(logthread)s %(message)s",
        "%m/%d %H:%M:%S")
    # For stdout/stderr, a more verbose version with milliseconds,
    # file and line numbers:
    oformat=logging.Formatter(
        "%(asctime)s.%(msecs)03d %(name)s (%(filename)s:%(lineno)d) "
        "%(levelname)s: %(message)s",
        "%m/%d %H:%M:%S")

    if stdout_is_stderr():
        # Configure combined stdout+stderr logging:
        loglevel=min(ologlevel,eloglevel)
        logstream=logging.StreamHandler(sys.stderr)
        logstream.setFormatter(oformat)
        if loglevel!=logging.NOTSET: logstream.setLevel(loglevel)
        root.addHandler(logstream)
    else:
        # Configure stdout logging:
        if ologlevel is not None:
            ologstream=logging.StreamHandler(sys.stdout)
            ologstream.setFormatter(oformat)
            if ologlevel!=logging.NOTSET: ologstream.setLevel(ologlevel)
            root.addHandler(ologstream)

        # Configure stderr logging:
        if eloglevel is not None:
            elogstream=logging.StreamHandler(sys.stderr)
            elogstream.setFormatter(oformat) # same format as stdout
            if eloglevel!=logging.NOTSET: elogstream.setLevel(eloglevel)
            root.addHandler(elogstream)

    # Configure jlogfile logging:
    #   jlogfile domain: INFO and higher
    #   all domains: ERROR and higher
    if jlogfile is None:
        # Try to get the jlogfile from the environment if none is specified:
        var=str(os.environ.get('jlogfile',''))
        if len(var)>0: jlogfile=var
    # If we still don't have the jlogfile, use stderr:
    jlogfile=str(jlogfile) if jlogfile is not None else sys.stderr
    jloghandler=JLogHandler(jlogfile,jlogdomain,japplevel,joformat,jformat)
    if jloglevel!=logging.NOTSET: jloghandler.setLevel(jloglevel)

    root.addHandler(jloghandler)
