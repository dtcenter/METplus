"""!Internal module that launches and monitors processes.

Do not use this module directly: it is part of the internal
implementation of the produtil.prog and produtil.run modules.  It
converts a produtil.prog.Runner object to processes, and monitors the
processes until they exit, sending and receiving data as needed.  This
replaces the built-in "subprocess" module which is not capable of
general-purpose pipeline execution."""

##@var __all__
# List of symbols exported by "from produtil.pipeline import *"
__all__ = [ "launch", "manage", "PIPE", "ERR2OUT", "kill_all", 
            "kill_for_thread" ]

class NoMoreProcesses(KeyboardInterrupt): 
    """!Raised when the produtil.sigsafety package catches a fatal
    signal.  Indicates to callers that the thread should exit."""

import os, signal, select, logging, sys, io, time, errno, \
    fcntl, threading, weakref, collections
import stat,errno,fcntl

class Constant(object):
    """!A class used to implement named constants."""
    def __init__(self,s,r=None):
        """!Creates a named constant
        @param s the return value of __str__() = str(self)
        @param r the return value of __repr__() = repr(self)"""
        self.__s=s
        if r is None:
            r='Constant(%s)@0x%x'%(repr(s),id(self))
        self.__r=r
    def __str__(self): 
        """!Returns the s argument to the constructor."""
        return self.__s
    def __repr__(self): 
        """!Returns the r argument of the constructor."""
        return self.__r

##@var plock
# A global lock for this module.
plock=threading.Lock()

##@var pipes_to_close
# Set of pipes that must be closed after forking to avoid deadlocks.
pipes_to_close=set()

##@var PIPE
# Indicates that stdout, stdin or stderr should be a pipe.
PIPE=Constant('PIPE')

##@var ERR2OUT
# Request that stderr and stdout be the same stream.
ERR2OUT=Constant('ERR2OUT')
def unblock(stream,logger=None):
    """!Attempts to modify the given stream to be non-blocking.  This
    only works with streams that have an underlying POSIX fileno, such
    as those from open.  

    Will re-raise any exception received, other than AttributeError
    and EnvironmentError.  Hence, I/O errors and attempts to make a
    non-fileno stream non-blocking will produce a False return value,
    while anything else will raise an exception.

    @param stream the stream to unblock
    @param logger a logging.Logger for log messages
    @returns True on success, False otherwise."""
    call_fcntrl(stream,os.O_NONBLOCK,0,logger)

def call_fcntrl(stream,on,off,logger=None):
    """!Internal function that implements unblock()
    @param stream the stream to modify
    @param on flags to turn on
    @param off flags to turn off
    @param logger a logging.Logger for messages
    @returns True on success, False otherwise."""
    try:
        if isinstance(stream,int):
            fd=stream
        else:
            fd=stream.fileno()
    except (AttributeError,EnvironmentError) as ee: 
        if logger is not None:
            logger.warning('%s: stream has no fileno, cannot switch to '
                           'non-blocking I/O: %s'%
                           (repr(stream),str(ee)),exc_info=True)
        return False
    
    try:
        flags=fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, (flags|on) & ~off)
        return True
    except EnvironmentError as ee:
        if logger is not None:
            logger.error('%s: cannot switch to non-blocking I/O: %s'%
                         (repr(stream),str(ee)),exc_info=True)
        return False

def pipe(logger=None):
    """!Creates a pipe that will be closed on exec.  Except that it
    does not seem to be reliably closed on exec, so there are other
    workarounds in this module.
    @param logger a logging.Logger for log messages"""
    with plock:
        (p1,p2)=os.pipe()
        call_fcntrl(p1,fcntl.FD_CLOEXEC,0,logger)
        call_fcntrl(p2,fcntl.FD_CLOEXEC,0,logger)
        return (p1,p2)

def padd(p):
    """!Adds a file descriptor to the list to close before exec.
    @param p the file descriptor"""
    with plock:
        pipes_to_close.add(p)

def pclose(i):
    """!Closes a file descriptor, removing it from the list that must
    be closed on exec.
    @param i the file descriptor"""
    with plock:
        try:
            os.close(i)
        except EnvironmentError as e: pass
        if i in pipes_to_close: 
            pipes_to_close.remove(i)

def pclose_all(i=None,o=None,e=None,logger=None):
    """!Closes all file descriptors sent to padd.
    @param i my stdin, which should not be closed
    @param o my stdout, which should not be closed
    @param e my stderr, which should not be closed
    @param logger a logging.Logger for debug messages"""
    with plock:
        for p in pipes_to_close:
            if p!=i and p!=o and p!=e:
                if logger is not None:
                    logger.debug("In child, close old pipe fd %d"%p)
                os.close(p)
        pipes_to_close.clear()

def launch(cmd, env=None, stdin=None, stdout=None, stderr=None, 
           debug=False, cd=None):
    """!Starts the specified command (a list), with the specified
    environment (or None to copy this process's environment).

    @param stdin,stdout,stderr Specifies the stdin, stdout and stderr
    streams.  The special value PIPE means "make a pipe," and sending
    stderr=ERR2OUT requests redirection of stderr to stdout.
    @param cd The optional "cd" argument specifies a directory to cd
    into, in the child process, before executing the command.  Of
    course, you shouldn't care about any of this because you should be
    using the produtil.run package.
    @param cmd the command to run
    @param env the subprocess's environment, or None to use mine
    @param debug if True, send debug messages"""

    if cd is not None and not isinstance(cd,str):
        raise TypeError(
            "In produtil.pipeline.launch, cd must be a string or None")
    if cd=='':
        raise ValueError(
            "In produtil.pipeline.launch, cd must not be the empty string.")

    stdinP=None    ;   stdinC=None
    stdoutP=None   ;   stdoutC=None
    stderrP=None   ;   stderrC=None
    logger=logging.getLogger(cmd[0])
    global pipes_to_close
    if debug:
        logger.debug("Start %s"%(repr(cmd),))

    if stdin is PIPE:
        (stdinC,stdinP)=pipe(logger)
        if debug: 
            logger.debug("Pipe for stdin: %d<==%d"%(stdinC,stdinP))
    else:
        stdinC=stdin
    if stdout is PIPE:
        (stdoutP,stdoutC)=pipe(logger)
        if debug: 
            logger.debug("Pipe for stdout: %d<==%d"%(stdoutP,stdoutC))
    else:
        stdoutC=stdout
    if stderr is PIPE:
        (stderrP,stderrC)=pipe(logger)
        if debug: 
            logger.debug("Pipe for stderr: %d<==%d"%(stderrP,stderrC))
    elif stderr is not ERR2OUT:
        stderrC=stderr

    pid=os.fork()
    assert(pid>=0)
    if pid>0:
        # Parent process after successfull fork.
        if stdin is not None and stdin is not PIPE:
            if debug:
                logger.debug("Close stdin %d on parent."%stdin)
            pclose(stdin)
        if stdin is PIPE and stdinC is not None:
            if debug:
                logger.debug("Close stdinC %d on parent."%stdinC)
            pclose(stdinC)
            padd(stdinP)
        if stdout is not None and stdout is not PIPE:
            if debug:
                logger.debug("Close stdout %d on parent."%stdout)
            pclose(stdout)
        if stdout is PIPE and stdoutC is not None:
            if debug:
                logger.debug("Close stdoutC %d on parent."%stdoutC)
            pclose(stdoutC)
            padd(stdoutP)
        if stderr is not None and stderr is not PIPE and stderr is not ERR2OUT:
            if debug:
                logger.debug("Close stderr %d on parent."%stderr)
            pclose(stderr)
        if stderr is PIPE and stderrC is not None:
            if debug:
                logger.debug("Close stderrC %d on parent."%stderrC)
            pclose(stderrC)
            padd(stderrP)
        if debug:
            logger.debug("On parent, returning %s"%(
                    repr((pid, stdinP,stdoutP,stderrP))))
        return (pid, stdinP,stdoutP,stderrP)

    if isinstance(cd,str):
        os.chdir(cd)
    
    # We are in the child process
    pclose_all(i=stdin,o=stdout,e=stderr)

    if stdinP is not None:
        if debug:
            logger.debug("Close stdinP %d on child."%stdinP)
        pclose(stdinP)
    if stdinC is not None:
        if debug:
            logger.debug("Point stdin to stdinC %d on child and close original."%stdinC)
        os.dup2(stdinC,0)
        pclose(stdinC)

    if stdoutP is not None:
        if debug:
            logger.debug("Close stdoutP %d on child."%stdoutP)
        pclose(stdoutP)
    if stdoutC is not None:
        if debug:
            logger.debug("Point stdout to stdoutC %d on child and close original."%stdoutC)
        os.dup2(stdoutC,1)
        pclose(stdoutC)

    if stderr is ERR2OUT:
        if debug:
            logger.debug("Redirect stderr to stdout on child.")
        os.dup2(1,2)
    if stderrP is not None:
        if debug:
            logger.debug("Close stderrP %d on child."%stderrP)
        pclose(stderrP)
    if stderrC is not None:
        if debug:
            logger.debug("Point stderr to stderrC %d on child and close original."%stderrC)
        os.dup2(stderrC,2)
        pclose(stderrC)

    if debug:
        logger.debug("Reset signal handlers on child.")
    
    signal.signal(signal.SIGHUP,signal.SIG_DFL)
    signal.signal(signal.SIGTERM,signal.SIG_DFL)
    signal.signal(signal.SIGINT,signal.SIG_DFL)
    signal.signal(signal.SIGQUIT,signal.SIG_DFL)
    signal.signal(signal.SIGPIPE,signal.SIG_DFL)
    signal.signal(signal.SIGCHLD,signal.SIG_DFL)

    assert(cmd[0])

    try:
        if debug:
            logger.debug("Run %s %s on child"%(cmd[0], " ".join(cmd[1:])))
        if env is None:
            os.execvp(cmd[0],cmd)
        else:
            os.execvpe(cmd[0],cmd,env)
    except Exception as e:
        logger.error("%s: could not exec: %s"%(cmd[0],str(e)),exc_info=True)
        sys.exit(2)

def filenoify(f):
    """!Tries to convert f to a fileno
    @returns an integer UNIX file descriptor
    @param f ERR2OUT, PIPE, an integer fileno or a file-like object
    with a fileno() function."""
    if f is ERR2OUT or f is PIPE or f is None: return f
    if isinstance(f,int): return f
    return f.fileno()

########################################################################
# Auto-killing processes
_manage_set=collections.defaultdict(set)

##@var _kill_all
# Should all processes be killed?  Used by the produtil.sigsafety module.
_kill_all=None

def kill_for_thread(th):
    """!Sends a TERM signal to all processes that the specified thread
    (a threading.Thread) is waiting for."""
    tht=weakref.ref(th)
    killme=set(_manage_set[tht])
    for p in killme:
        try:
            os.kill(p,signal.SIGTERM)
        except EnvironmentError as e:
            pass
        try:
            _manage_set[th].remove(killme)
        except (ValueError,KeyError,TypeError) as e:
            pass

def kill_all():
    """!Sends a TERM signal to all processes that this module is
    managing"""
    _kill_all=True

########################################################################

def manage(proclist,inf=None,outf=None,errf=None,instr=None,logger=None,
           childset=None,sleeptime=None,binary=False):
    """!Watches a list of processes, handles their I/O, returns when
    all processes have exited and all I/O is complete.  

    @warning You should not be calling this function unless you are
      modifying the implementation of Pipeline.  Use the produtil.run
      module instead of calling launch() and manage().

    @param proclist the list of processes to watch
    @param inf the input file
    @param outf the output file
    @param errf the error file
    @param instr the input string, instead of an input file
    @param childset the set of child process ids
    @param sleeptime sleep time between checks of child processes
    @param logger Logs to the specified object, at level DEBUG, if a logger is
    specified.  
    @returns a tuple containing the stdout string (or None), the
    stderr string (or None) and a dict mapping from process id to the
    return value from os.wait4 called on that process."""

    me=weakref.ref(threading.current_thread())
    ms=_manage_set[me]
    assert(proclist)
    ms.update(proclist)
    assert(ms)

    bufsize=1048576
    work=list()
    done=dict() # mapping from pid to wait4 return value
    outio=None
    errio=None
    haveio=False

    inf=filenoify(inf)
    outf=filenoify(outf)
    errf=filenoify(errf)

    if inf is not None:
        if instr is None: 
            instr=""
        if logger is not None:
            logger.debug("Will write instr (%d bytes) to %d."
                         %(len(instr),inf))
        work.append([0,inf])
        unblock(inf,logger=logger)
        haveio=True

    if outf is not None:
        if logger is not None:
            logger.debug("Will read outstr from %d."%outf)
        work.append([1,outf])
        if binary:
            outio=io.BytesIO()
        else:
            outio=io.StringIO()
        unblock(outf,logger=logger)
        haveio=True

    if errf is not None:
        if logger is not None:
            logger.debug("Will read errstr from %d."%errf)
        work.append([1,errf])
        if binary:
            errio=io.BytesIO()
        else:
            errio=io.StringIO()
        unblock(errf,logger=logger)
        haveio=True

    for proc in proclist:
        if logger is not None:
            logger.debug("Monitor process %d."%proc)
        work.append([2,proc])

    nin=0
    lastproc=time.time()
    forceclose=False
    while work:
        i=0
        didproc=False
        if _kill_all is not None:
            if logger is not None:
                logger.debug("Kill all processes.")
            for (job,tgt) in work:
                if job==2:
                    os.kill(tgt,SIGTERM)
        while i<len(work):
            (job,tgt)=work[i]
            assert(job==0 or job==1 or job==2)
            if job==0:
                if logger is not None:
                    logger.debug("Attempt a write of %d characters to %d"
                                 %(len(instr)-nin,tgt))
                try:
                    if isinstance(instr,bytes):
                        n=os.write(tgt,instr[nin:])
                    else:
                        n=os.write(tgt,bytes(instr[nin:],encoding='UTF8'))
                except EnvironmentError as e:
                    if e.errno==errno.EAGAIN or e.errno==errno.EWOULDBLOCK:
                        n=None
                    else:
                        raise
                if n: 
                    if logger is not None:
                        logger.debug("Wrote %d bytes to %d."%(n,tgt))
                    nin+=n
                if nin>=len(instr):
                    if logger is not None:
                        logger.debug("Done writing all %d characters; close %d."
                                     %(nin,tgt))
                    pclose(tgt)
                    work.pop(i)
                    continue # do not increment i
                if forceclose:
                    if logger is not None:
                        logger.debug("Force close of in %d due to timeout."
                                     %tgt)
                    pclose(tgt)
                    work.pop(i)
                    continue # do not increment i
            elif job==1:
                try:
                    if logger is not None:
                        logger.debug("Attempt a read from %d"%tgt)
                    s=os.read(tgt,bufsize)
                except EnvironmentError as e:
                    if e.errno==errno.EAGAIN or e.errno==errno.EWOULDBLOCK:
                        if logger is not None:
                            logger.debug("Error %s from %d - assume no data"
                                         %(str(e),tgt))
                        s=None
                    else:
                        raise
                if s=='':
                    # end of file
                    if logger is not None:
                        logger.debug("eof reading output %d"%tgt)
                    pclose(tgt)
                    work.pop(i)
                    continue # do not increment i
                if s is not None:
                    if logger is not None:
                        logger.debug("Read %d characters from output %d"
                                     %(len(s),tgt))
                    # read something
                    if binary:
                        outio.write(s)
                    else:
                        outio.write(str(s,encoding='UTF8'))
                if forceclose:
                    if logger is not None:
                        logger.debug("Force close of %d due to timeout."
                                     %tgt)
                    pclose(tgt)
                    work.pop(i)
                    continue # do not increment i
            elif job==2:
                if logger is not None:
                    logger.debug("Check process %d"%tgt)
                didproc=True
                r=os.wait4(tgt,os.WNOHANG)
                if r and ( r[0]!=0 or r[1]!=0 ):
                    if logger is not None:
                        logger.debug("Process %d exited"%tgt)
                    work.pop(i)
                    try:
                        ms.remove(tgt)
                    except (ValueError,KeyError,TypeError) as e:
                        if logger is not None: 
                            logger.debug(
                                "Cannot remove pid %d from _manage_set: %s"
                                %(tgt,str(e)),exc_info=True)
                    if childset is not None:
                        try:
                            childset.remove(tgt)
                        except (ValueError,KeyError,TypeError) as e:
                            if logger is not None: 
                                logger.debug(
                                    "Cannot remove pid %d from childset: %s"
                                    %(tgt,str(e)),exc_info=True)
                    done[tgt]=r
                    continue # do not increment i
                else:
                    if logger is not None:
                        logger.debug("Process %d still running"%tgt)
            i+=1
        if didproc:
            lastproc=time.time()
        else:
            now=time.time()
            if now-lastproc > 2 and work:
                if logger is not None:
                    logger.debug(
                        "No data two seconds after processes exited.  "
                        "Forcing a close of all streams.")
                # No data in past two seconds and all processes have
                # exited.
                forceclose=True
                continue
        if work:
            if logger is not None:
                logger.debug("Bottom of loop with work=%s"%repr(work))
            if sleeptime:
                time.sleep(sleeptime)
            elif haveio:
                time.sleep(0.01)
            else:
                time.sleep(0.2)
    if logger is not None:
        logger.debug("Done monitoring pipeline.")

    outstr=None
    if outf is not None:
        outstr=outio.getvalue()
        outio.close()

    errstr=None
    if errf is not None:
        errstr=errio.getvalue()
        errio.close()

    if _kill_all is not None:
        raise NoMoreProcesses(
            "Master thread caught a signal.  This thread should exit.")
    return (outstr, errstr, done)

########################################################################

def simple_run(cmd, env=None, stdin=None, stdout=None, stderr=None, 
               debug=False, cd=None, logger=None, binary=False):
    (pid, stdinP, stdoutP, stderrP) = launch(
        cmd,env,stdin,stdout,stderr,debug,cd)
    (outstder, errstr, done) = \
      manage([pid], inf=stdinP, outf=stdoutP, errf=stderrP, logger=logger, 
             binary=binary )
    result=done[pid][1]
    if os.WIFEXITED(result):
        return os.WEXITSTATUS(result)
    elif os.WIFSIGNALED(result):
        return -os.WTERMSIG(result)
    else:
        return -128

########################################################################

class Pipeline(object):
    """!This class is a wrapper around launch and manage.  It converts
    Runner objects to calls to "launch", and runs "manage" on the
    resulting processes."""
    def __init__(self,runner,capture=False,logger=None,debug=False,
                 binary=False):
        """!Pipeline constructor
        @param runner the produtil.prog.Runner to convert
        @param capture if True, capture the stdout of the runner
        @param logger a logging.Logger for messages
        @param debug if True, send debug messages
        @param binary use binary streams for input and output"""
        self.__children=set()
        self.__quads=list()
        self.__capture=capture
        self.__logger=logger
        self.__debug=debug
        self.__instring=None
        self.__out=None
        self.__err=None
        self.__stdin=None
        self.__stdout=None
        self.__stderr=None
        self.__managed=None
        self.__last_pid=None
        self.__lock=threading.Lock()
        self.__binary=bool(binary)
        runner._gen(self,logger=logger)
    def __repr__(self):
        """!Return a debug string representation of this Pipeline."""
        return "<Pipeline id=0x%x in=%s out=%s err=%s>"%(
            id(self),
            repr(self.__stdin),repr(self.__stdout),repr(self.__stderr))
    def _impl_add(self,command,endpipe,logger=None,
                  instring=None,stdin=None,stdout=None,stderr=None,
                  sendout=None,senderr=None,sendin=None,env=None,
                  closein=None,closeout=None,closeerr=None,
                  cd=None,binary=False):
        """!Adds another produtil.prog.Runner's contents to this Pipeline.
        @param command the command to run
        @param endpipe is this the end of a pipeline?
        @param logger a logging.Logger for log messages
        @param instring the string for stdin
        @param stdin a file, fileno or PIPE constant for stdin
        @param stdout a file, fileno or special constant for stdout
        @param stderr a file, fileno or special constant for stderr
        @param env subprocess environment variables
        @param closein,closeout,closeerr Unused.
        @param cd subprocess working directory"""
        pin = stdin if (sendin is None) else sendin
        pout = stdout if (sendout is None) else sendout
        perr = stderr if (senderr is None) else senderr

        if instring is not None:
            pin=PIPE
            self.__instring=instring
        if pin is None and self.__stdout is not None:
            pin=self.__stdout

        if self.__capture and endpipe and pout is None:
            pout=PIPE
        elif not endpipe:
            pout=PIPE

        (p,i,o,e)=launch(command,env,pin,pout,perr,self.__debug,cd)

        self.__children.add(p)
        if not self.__quads: self.__stdin=i
        self.__stdout=o
        self.__stderr=e
        self.__quads.append( (p,i,o,e) )
        self.__last_pid=p
        self.__binary=bool(binary)
    def send_signal(self,sig):
        """!Sends a signal to all children.
        @param sig the signal"""
        for p in self.__children:
            try:
                os.kill(p,sig)
            except EnvironmentError as e: pass

    def terminate(self):
        """!Sends SIGTERM to all children."""
        self.send_signal(signal.SIGTERM)
    def kill(self): 
        """!Sends SIGKILL to all children."""
        self.send_signal(signal.SIGKILL)

    # def __repr__(self):
    #     """Does not run the pipeline; simply returns <Pipeline at XX>
    #     where XX is the id of this object."""
    #     return '<Pipeline at 0x%x>'%(id(self),)

    def communicate(self,sleeptime=None):
        """!Writes to input, reads from output, waits for child
        processes, etc.  This is just a wrapper around the manage()
        function.  It will return immediately if self.communicate has
        already completed earlier.
        @param sleeptime the sleep time in seconds between checks"""
        with self.__lock:
            if self.__managed: return
            (o,e,m)=manage(
                [q[0] for q in self.__quads],
                self.__stdin, self.__stdout, self.__stderr, 
                self.__instring, self.__logger, self.__children,
                sleeptime, self.__binary)
            self.__managed=m
            self.__out=o
            self.__err=e

    def poll(self):
        """!Returns the exit status of the last element of the
        pipeline.  If the process died due to a signal, returns a
        negative number."""
        m=self.__managed
        if not m: return None
        result=m[self.__last_pid][1]
        if os.WIFEXITED(result):
            return os.WEXITSTATUS(result)
        elif os.WIFSIGNALED(result):
            return -os.WTERMSIG(result)
        else:
            return -128

    def to_string(self):
        """!Calls self.communicate(), and returns the stdout from the
        pipeline (self.outbytes).  The return value will be Null if
        the pipeline was redirected to a file or if the constructor's
        capture option was not True."""
        self.communicate()
        o=self.out
        if not isinstance(o,str):
            o=str(o)
        return o

    @property
    def out(self): 
        """!The stdout from the pipeline.  Will be Null if the pipeline
        was redirected to a file, or if the constructor's capture
        option was not True."""
        return self.__out
