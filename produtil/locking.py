"""!Handles file locking using Python "with" blocks.

This module implements a Python with construct that can hold a lock
and release it at the end of the "with" block.  It also implements a
safety feature to allow the program to disable locking, ensuring a
fatal exception (LockingDisabled) if anything tries to lock a file.
That functionality is connected to the produtil.sigsafety module,
which will disable locking if a fatal signal is received.

@code
import produtil.locking
with produtil.locking.LockFile("some.lockfile"):
    ... do things while the file is locked...
...  the file is now unlocked ...
@endcode"""

import fcntl, time, errno, os.path
import produtil.retry as retry
import produtil.fileop

##@var __all__
# Symbols exported by "from produtil.locking import *"
__all__=['LockingDisabled','disable_locking','LockFile','LockHeld']

##@var locks
# Part of the internal implementation of this module: the list of
# existing locks (LockFile objects) that may be held.
locks=set()

##@var locks_okay
# Part of the internal implementation of this module: if True,
# locking is allowed, if False, locking is forbidden.  When this is
# False, LockingDisabled is raised on any attempt to acquire a lock.
locks_okay=True

def disable_locking():
    """!Entirely disables all locking in this module.  

    If this is called, any locking attempts will raise
    LockingDisabled.  That exception derives directly from
    BaseException, which well-written Python code will never catch,
    hence ensuring a rapid, abnormal exit of the program.  This
    routine should never be called directly: it is only used as part
    of the implementation of the produtil.sigsafety, to prevent file
    locking after catching a terminal signal, hence allowing the
    program to exit as quickly as possible, and present a stack trace
    to any locations that attempt locking."""
    global locks_okay
    locks_okay=False
    for lock in locks:
        try:
            lock.release_impl()
        except (Exception,LockingDisabled) as l: pass

class LockHeld(Exception):
    """!This exception is raised when a LockFile cannot lock a file
    because another process or thread has locked it already."""

class LockingDisabled(BaseException):
    """!This exception is raised when a thread attempts to acquire a
    lock while Python is exiting according to produtil.sigsafety.
    
    @warning This is a subclass of BaseException, not Exception, to
    attempt to cleanly kill the thread."""

class LockFile(object):
    """!Automates locking of a lockfile

    @code
      with LockFile("/path/to/lock.file"):
          ... do things while file is locked ...
      ...file is no longer locked.
    @endcode"""
    def __hash__(self): 
        """!Return a hash of this object."""
        return hash(id(self))
    def __eq__(self,other):
        """!Is this lock the same as that lock?"""
        return self is other
    def __init__(self,filename,until=None,logger=None,max_tries=10,sleep_time=3,first_warn=0,giveup_quiet=False):
        """!Creates an object that will lock the specified file.  
        @param filename the file to lock
        @param until Unused.
        @param logger Optional: a logging.Logger to log messages
        @param max_tries Optional: maximum tries before giving up on locking
        @param sleep_time Optional: approximate sleep time between
          locking attempts.
        @param first_warn Optional: first locking failure at which to
          write warnings to the logger
        @param giveup_quiet Optional: if True, do not log the final
          failure to lock"""
        if not locks_okay:
            raise LockingDisabled('Attempted to create a LockFile object while the process was exiting.')
        self._logger=logger
        assert(filename is not None)
        assert(len(filename)>0)
        self._filename=filename
        self._max_tries=max_tries
        self._sleep_time=sleep_time
        self._first_warn=first_warn
        self._giveup_quiet=giveup_quiet
        self._fd=None
    def acquire_impl(self):
        """!Internal implementation function; do not call directly.
        Does the actual work of acquiring the lock, without retries,
        logging or sleeping.  Will raise LockHeld if it cannot acquire
        the lock."""
        if not locks_okay:
            raise LockingDisabled('Attempted to acquire a lock while '
                                  'the process was exiting.')
        thedir=os.path.dirname(self._filename)
        if thedir:
            produtil.fileop.makedirs(thedir)
        if self._fd is None:
            self._fd=open(self._filename,'wb')
        try:
            fcntl.lockf(self._fd.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except EnvironmentError as e:
            if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                raise LockHeld('%s: already locked by another process or '
                               'thread: %s'% ( self._filename, str(e)))
            raise
    def release_impl(self):
        """!Internal implementation function; do not call directly.
        Does the actual work of releasing the lock, without retries,
        logging or sleeping."""
        if self._fd is not None:
            fcntl.lockf(self._fd.fileno(),fcntl.LOCK_UN)
            self._fd.close()
            self._fd=None
    def acquire(self):
        """!Acquire the lock.  Will try for a while, and will raise
        LockHeld when giving up."""
        locks.add(self)
        return retry.retry_io(self._max_tries,self._sleep_time,self.acquire_impl,
                              fail=self._filename+': cannot lock',logger=self._logger,
                              first_warn=self._first_warn,giveup_quiet=self._giveup_quiet)
    def release(self):
        """!Release the lock.  May raise exceptions on unexpected
        failures."""
        try:
            return retry.retry_io(self._max_tries,self._sleep_time,self.release_impl,
                                  fail=self._filename+': cannot unlock',logger=self._logger,
                                  first_warn=self._first_warn,giveup_quiet=self._giveup_quiet)
        except:
            raise
        else:
            locks.remove(self)
    def __enter__(self):
        """!Calls self.acquire() to acquire the lock."""
        self.acquire()
        return self
    def __exit__(self,etype,evalue,etraceback):
        """!Calls self.release() to release the lock.
        @param etype,evalue,etraceback Exception information."""
        self.release()
