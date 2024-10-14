"""!Sets up signal handlers to ensure a clean exit.

This module is a workaround for a deficiency of Python.  When Python
receives a fatal signal other than SIGINT, it exits immediately
without freeing utilized resources or otherwise cleaning up.  This
module causes Python to raise a fatal exception, that does NOT derive
from Exception, if a fatal signal is received.  Note that there is a
critical flaw in this design: raising an exception in a signal handler
only raises it in the main (initial) thread.  Other threads must call
the produtil.sigsafety.checksig function as frequently as possible to
check if a signal has been caught.  That function will raise the
appropriate exception if a signal was caught, or return immediately
otherwise.

The reason this HAD to be added to produtil is that the lack of proper
signal handling caused major problems.  In particular, it completely
broke file locking on Lustre and Panasas.  Both filesystems will
sometimes forget a file lock is released if the lock was held by a
process that exited abnormally.  There were also unverified cases of
this happening with GPFS.  Correctly handling SIGTERM, SIGQUIT, SIGHUP
and SIGINT has solved that problem thus far.

The base class of any exception thrown due to a signal is CaughtSignal.
It has two subclasses: FatalSignal, which is raised when a fatal
signal is received, and HangupSignal.  The HangupSignal is raised by
SIGHUP, unless the install_handlers requests otherwise.  Scripts
should catch HangupSignal if the program is intended to ignore
hangups.  However, nothing should ever catch FatalSignal.  Only
__exit__ and finalize blocks should be run in that situation, and they
should run as quickly as possible.

The install_handlers installs the signal handlers: term_handler and
optionally hup_handler.  The raise_signals option specifies the list
of signals that will raise FatalSignal, defaulting to SIGTERM, SIGINT
and SIGQUIT.  If SIGHUP is added to that list, then it will raise
FatalSignal as well.  Otherwise, the ignore_hup option controls the
SIGHUP behavior: if True, SIGHUP is simply ignored, otherwise it
raises HangupSignal.

One can call install_handlers directly, though it is recommended to
call produtil.setup.setup instead."""

import produtil.locking, produtil.pipeline
import signal

##@var defaultsigs
#Default signals for which to install terminal handlers.
defaultsigs=[signal.SIGTERM,signal.SIGINT,signal.SIGQUIT]

##@var modifiedsigs
#List of signals modified by install_handlers
modifiedsigs=list()

##@var __all__
# List of symbols exported by "from produtil.sigsafety import *"
__all__=['CaughtSignal','HangupSignal','FatalSignal','install_handlers','checksig']

class CaughtSignal(KeyboardInterrupt):
    """!Base class of the exceptions thrown when a signal is caught.
    Note that this does not derive from Exception, to ensure it is not
    caught accidentally.  At present, it derives directly from
    KeyboardInterrupt, though that may be changed in the future to
    BaseException."""
    def __init__(self,signum):
        """!CaughtSignal constructor
        @param signum the signal that was caught (an int)"""
        BaseException.__init__(self)
        self.signum=signum
    ##@var signum
    # The integer signal number.

    def __str__(self):
        """! A string description of this error."""
        return 'Caught signal %d'%(self.signum,)
class HangupSignal(CaughtSignal):
    """!With the default settings to install_handlers, this is raised
    when a SIGHUP is caught.  Note that this does not derive from
    Exception."""
class FatalSignal(CaughtSignal):
    """!Raised when a fatal signal is caught, as defined by the call to
    install_handlers.  Note that this does not derive from
    Exception."""

##@var caught_signal
#The signal number of the signal that was caught or None if no
#signal has been caught.  This is initialized by the signal handlers,
#and used by checksig to raise exceptions due to caught signals.
caught_signal=None

##@var caught_class
#The class that should be raised due to the caught signal, or None
#if no signal has been caught.  This is initialized by the signal
#handlers, and used by checksig to raise exceptions due to caught
#signals.
caught_class=None

def checksig():
    """!This should be called frequently from worker threads to
    determine if the main thread has received a signal.  If a signal
    was caught this function will raise the appropriate subclass of
    CaughtSignal.  Otherwise, it returns None."""
    global caught_signal,caught_class
    cs=caught_signal
    cc=caught_class
    if cs is not None and cc is not None:
        raise cc(cs)
    return None

def uninstall_handlers():
    """!Resets all signal handlers to their system-default settings
    (SIG_DFL).  Does NOT restore the original handlers.

    This function is a workaround for a design flaw in Python
    threading: you cannot kill a thread.  This workaround restores
    default signal handlers after a signal is caught, ensuring the
    next signal will entirely terminate Python.  Only the term_handler
    calls this function, so repeated hangups will still be ignored if
    the code desires it.

    Some may note you can kill a Python thread on Linux using a
    private function but it is not available on all platforms and
    breaks GC.  Another common workaround in Python is to use
    Thread.daemon, but that kills the thread immediately, preventing
    the thread from killing external processes or cleaning up other
    resources upon parent exit."""
    for isig in modifiedsigs:
        signal.signal(isig,signal.SIG_DFL)

def hup_handler(signum,frame):
    """!This is the signal handler for raising HangupSignal: it is used
    only for SIGHUP, and only if that is not specified in
    raise_signals and ignore_hup=False.
    @param signum,frame signal information"""
    global caught_signal,caught_class
    caught_signal=signum
    caught_class=HangupSignal

    produtil.locking.disable_locking()
    raise HangupSignal(signum)

def term_handler(signum,frame): 
    """!This is the signal handler for raising FatalSignal.
    @param signum,frame signal information"""
    global caught_signal,caught_class
    caught_signal=signum
    caught_class=FatalSignal

    produtil.locking.disable_locking() # forbid file locks
    produtil.pipeline.kill_all() # kill all subprocesses
    uninstall_handlers()
    raise FatalSignal(signum)

def install_handlers(ignore_hup=False,raise_signals=defaultsigs):
    """!Installs signal handlers that will raise exceptions.

    @param ignore_hup If True, SIGHUP is ignored, else SIGHUP will
            raise HangupSignal

    @param raise_signals - List of exceptions that will raise
            FatalSignal.  If SIGHUP is in this list, that overrides
            any decision made through ignore_hup.    """
    global modifiedsigs
    if(ignore_hup):
        signal.signal(signal.SIGHUP,signal.SIG_IGN)
    elif signal.SIGHUP not in raise_signals:
        signal.signal(signal.SIGHUP,hup_handler)
    for sig in raise_signals:
        signal.signal(sig,term_handler)
    modifiedsigs=list(raise_signals)
