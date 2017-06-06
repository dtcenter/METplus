"""!Contains the WorkPool class, which maintains pools of threads
that perform small tasks."""

##@var __all__
# List of symbols exported by "from produtil.workpool import *"
__all__=["WorkPool","WrongThread"]
import threading, collections, time
import produtil.pipeline, produtil.sigsafety

class WrongThread(Exception):
    """!Raised when a thread unrelated to a WorkPool attempts to
    interact with the WorkPool.  Only the thread that called the
    constructor, and the threads created by the WorkPool can interact
    with it."""

class WorkTask(object):
    """!Stores a piece of work.  This is an internal implementation
    class.  Do not use it directly.  It stores one piece of work to be
    done by a worker thread in a WorkPool."""

    def __init__(self,work,args=None):
        """!Create a WorkTask whose job is to call work()
        @param work the function to call
        @param args the arguments to work"""
        self.work=work
        self.__done=False
        self.__exception=None
        self.__args=list() if(args is None) else list(args)

    ##@var work
    # The function this WorkTask should call

    @property
    def args(self):
        """!The arguments to the work function"""
        return self.__args

    def _set_exception(self,e):
        """!Sets the exception that was raised by the work function.
        Sets the done status to False.
        @returns the exception
        @param e the exception."""
        self.__done=False
        self.__exception=e
        return self.__exception
    def _del_exception(self):
        """!Removes the exception that was raised by the work function."""
        self.__exception=None
    def _get_exception(self):
        """!Returns the exception that was raised by the work function."""
        if self.__done: return None
        return self.__exception

    ## The exception that was raised by the work function.
    exception=property(_get_exception,_set_exception,_del_exception,
                       """The exception raised by the last work attempt""")

    def _set_done(self,d):
        """!Sets the "done" versus "not done" state to d
        @returns a boolean version of d"""
        self.__done=bool(d)
        if self.__done:
            self.__exception=None
        return self.__done
    def _get_done(self):
        """!Is this task complete?"""
        return self.__done
    def _del_done(self):
        """!Same as self._set_done(False)"""
        self.__done=False

    ## Is this work task done?
    done=property(_get_done,_set_done,_del_done,
                  """Is this work done?  True or False.""")

def do_nothing(): 
    """!Does nothing.  Used to implement worker termination."""

##@var TERMINATE
# Special constant WorkTask used to terminate a WorkPool.
# Do not modify.
TERMINATE=WorkTask(do_nothing)

class WorkPool(object):
    """!A pool of threads that perform some list of tasks.  There is a
    function add_work() that adds a task to be performed.  

    Example: print the numbers from 1 to 10 in no particular order, 
    in three threads:
    @code
    def printit(num):
      print str(num)
    with WorkPool(3) as w:
      print "three threads are waiting for work"
      for x in xrange(10):
        w.add_work(printit,[x+1])
      print "all threads have work, but the work may not be complete"
      w.barrier()
      print "all work is now complete."
    print "once you get here, all workpool threads exited"
    @endcode"""

    def __init__(self,nthreads,logger=None,raise_at_exit=False):
        """!Create a WorkPool with the specified number of worker
        threads.  The nthreads must be at least 1."""
        self._work_queue=collections.deque()
        self._work_semaphore=threading.Semaphore(0)
        self._barrier_set=set()
        self._barrier_condition=threading.Condition()
        self._threads=set()
        self._master=threading.current_thread()
        self._modlock=threading.Lock()
        self._die=True # threads should exit
        self._last_id=0
        self._raise_at_exit=raise_at_exit
        self.logger=logger
        try:
            self.start_threads(nthreads)
        except (Exception,KeyboardInterrupt) as e:
            self.kill_threads()
            raise
    ##@var logger
    # a logging.Logger for log messages

    def __enter__(self): 
        """!Does nothing. Called from atop a "with" block."""
        return self
    def __exit__(self,etype,value,traceback):
        """!Called at the bottom of a "with" block.  If no exception
        was raised, and no "break" encountered, then waits for work to
        complete, and then kills threads.  Upon a fatal signal or
        break, kills threads as quickly as possible.
        @param etype,value,traceback exception information"""
        if value is None:
            self.barrier()
            self.kill_threads()
            if self._raise_at_exit:
                for ex in self.exceptions: pass
                raise ex
        elif isinstance(value,KeyboardInterrupt) \
                or isinstance(value,produtil.sigsafety.CaughtSignal):
            self._critical('Terminal signal caught.  Will try to kill '
                           'threads before exiting.')
            self.kill_threads()
        elif isinstance(value,GeneratorExit) \
                or isinstance(value,Exception):
            self.kill_threads()

    def exceptions(self):
        """!Iterates over all exceptions from worker threads."""
        for thread in self._threads:
            ex=thread.exception
            if ex is not None: yield ex
            
    def _info(self,message):
        """!Log to INFO level
        @param message the message to log"""
        me=threading.current_thread()
        if self.logger is None: return
        if me==self._master:
            self.logger.info('[master] '+message)
        else:
            self.logger.info('[%s] %s'%(me.name,message))

    def _debug(self,message):
        """!Log to DEBUG level
        @param message the message to log"""
        me=threading.current_thread()
        if self.logger is None: return
        if me==self._master:
            self.logger.debug('[master] '+message)
        else:
            self.logger.debug('[%s] %s'%(me.name,message))

    def _error(self,message,exc_info=False):
        """!Log to ERROR level
        @param message the message to log"""
        me=threading.current_thread()
        if self.logger is None: return
        if me==self._master:
            self.logger.error('[master] '+message,exc_info=exc_info)
        else:
            self.logger.error('[%s] %s'%(me.name,message),exc_info=exc_info)

    def _critical(self,message,exc_info=False):
        """!Log to CRITICAL level
        @param message the message to log"""
        me=threading.current_thread()
        if self.logger is None: return
        if me==self._master:
            self.logger.critical('[master] '+message,exc_info=exc_info)
        else:
            self.logger.critical('[%s] %s'%(me.name,message),exc_info=exc_info)


    @property
    def nthreads(self):
        """!The number of worker threads."""
        return len(self._threads)

    def add_work(self,work,args=None):
        """!Adds a piece of work to be done.  It must be a callable
        object.  If there are no worker threads, the work() is called
        immediately.  The args are passed, if present.
        @param work a callable object
        @param args a list of arguments to the work function"""
        me=threading.current_thread()
        if me!=self._master:
            raise WrongThread(
                "In WorkPool.add_work, thread %s is not the master "
                "thread and is not a work thread."%(str(me),))

        if self.nthreads<1: 
            if args is None:
                work()
            else:
                work(*args)
        else:
            worktask=WorkTask(work,args)
            self._work_queue.append(worktask)
            self._debug("Added work %s"%(repr(work),))
            self._work_semaphore.release()

    def _worker_exit_check(self):
        """!Return True if worker threads should keep running, False if
        they should exit."""
        produtil.sigsafety.checksig()
        return not self.die

    def _valid_thread(self):
        """!Returns True if this is the thread that called the
        constructor or any worker thread.  Returns False otherwise."""
        me=threading.current_thread()
        if me==self._master: return True
        for t in self._threads:
            if t==me: return True
        return False

    def _worker_main(self):
        """!Main function for worker threads.  Do not call directly."""
        me=threading.current_thread()
        if not self._valid_thread():
            raise WrongThread(
                "In WorkPool._worker_main, thread %s is not the master "
                "thread and is not a work thread."%(str(me),))

        while self._worker_exit_check():
            ws=self._work_semaphore
            #assert(isinstance(ws,threading.Semaphore))
            wq=self._work_queue
            assert(isinstance(wq,collections.deque))
            work=None
            try:
                self._debug('Ready for work.')
                ws.acquire()
                work=wq.popleft()
                if work is TERMINATE:
                    self._debug('terminate')
                    return
                self._debug(' ... working ... ')
                if work.args:
                    args=work.args
                    work.work(*args)
                else:
                    work.work()
                work.done=True
            except Exception as e:
                if work is not None:
                    work.exception=e
                    #wq.append(work)
                    #ws.release()
                    self._error('...failed.',exc_info=True)
                else:
                    raise

    def start_threads(self,n):
        """!Starts n new threads.  Can only be called from the thread
        that made this object.
        @param n number of threads to start, an integer greater than 0"""
        assert(n>=0)
        assert(isinstance(n,int))
        if n==0: return
        me=threading.current_thread()
        if me!=self._master:
            raise WrongThread(
                "In WorkPool.kill_threads, thread %s is not the master "
                "thread."%(str(me),))
        self.die=False
        for i in xrange(n):
            with self._modlock:
                tid=self._last_id+1
                thread=None
                try:
                    def doit(a):
                        a._worker_main()
                    thread=threading.Thread(target=doit,args=[self])
                    #thread.daemon=True
                    self._threads.add(thread)
                    self._last_id=tid
                    thread.start()
                except (Exception,KeyboardInterrupt) as e:
                    if thread in self._threads:
                        self._error('ERROR: '+str(e),exc_info=True)
                        self._threads.remove(thread)
                    raise

    ##@var die
    # If True, all threads should exit immediately.

    def kill_threads(self):
        """!Kills all worker threads.  Can only be called from the
        thread that made this object."""
        me=threading.current_thread()
        if me!=self._master:
            raise WrongThread(
                "In WorkPool.kill_threads, thread %s is not the master "
                "thread."%(str(me),))
        self.die=False
        wq=self._work_queue
        ws=self._work_semaphore
        with self._modlock:
            killme=set(self._threads)
            for thread in killme:
                if not isinstance(wq,collections.deque):
                    raise TypeError(
                        "self._work_queue should be a deque but it is a"
                        " %s %s"%(type(wq).__name__,repr(wq)))
                wq.appendleft(TERMINATE)
                ws.release()

            for thread in killme:
                self._debug("Kill worker thread %s"%(repr(thread),))
                produtil.pipeline.kill_for_thread(thread)
                thread.join()

            #self._threads.clear()
        self._debug("Done killing worker threads.")

    def barrier(self):
        """!Waits for all threads to reach the barrier function.  This
        can only be called by the master thread.  

        Upon calling, the master thread adds a WorkTask for each
        thread, telling the thread to call self.barrier().  Once all
        threads have reached that point, the barrier returns in all
        threads."""
        if self.nthreads<=0: return

        if not self._valid_thread():
            raise WrongThread(
                "In WorkPool.add_work, thread %s is not the master "
                "thread and is not a work thread."%(str(me),))

        me=threading.current_thread()
        if me==self._master:
            self._debug('BARRIER (master)')
            with self._modlock:
                # First, tell all worker threads to call this function:
                self._debug('Request barrier on all threads.')
                for i in xrange(len(self._threads)):
                    self.add_work(self.barrier)
                self._debug('Wait for all workers to reach barrier.')
                # Now wait for it to happen:
                while len(self._barrier_set) < len(self._threads):
                    time.sleep(0.01)
                with self._barrier_condition:
                    self._barrier_condition.notify_all()
                    self._barrier_set.clear()
        else:
            self._debug('BARRIER (worker)')
            for thread in self._threads:
                if me==thread:
                    with self._barrier_condition:
                        self._barrier_set.add(me)
                        self._barrier_condition.wait()
                    return
            raise WrongThread(
                "In WorkPool.barrier, thread %s is not the master thread "
                "and is not a worker thread."%(str(me),))
