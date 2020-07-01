"""!Contains retry_io() which automates retrying operations."""

##@var __all__
# Symbols exported by "from produtil.retry import *"
__all__=['retry_io']

import time
import logging
import random

def retry_io(max_tries,sleep_time,operation,opargs=[],logger=None,
             fail=None,failargs=[],giveup=None,giveupargs=[],randsleep=True,
             backoff=1.3,first_warn=0,giveup_quiet=False):
    """!This function automates retrying an unreliable operation
    several times until it succeeds.  This subroutine will retry the
    operation up to a maximum number of times.  If the operation fails
    too many times, then the last exception thrown by the operation is
    passed on (raised) to the caller.

    @param max_tries  Maximum number of times to attempt the operation (mandatory)
    @param sleep_time Time to sleep between tries
    @param operation  A function or callable object that may thrown an Exception
    @param opargs     A list containing arguments to the operation
    @param logger     A logging.Logger object to use for logging, or None
                      to disable logging.
    @param fail       A string to print, or a function to call, when 
                      the operation fails but more retries are possible
    @param failargs   Optional: a list of arguments to fail, or None to disable
    @param giveup     A string to print, or a function to call when the
                      operation fails too many times, causing retry_io
                      to give up.  Default: same as fail
    @param giveupargs Optional: a list of arguments to giveup, or None to disable
    @param randsleep  Set to True (default) to enable an exponential backoff
                      algorithm, which will increase the sleep time between tries
    @param backoff    The exponent for the exponential backoff algorithm
    @param first_warn The first failure at which to warn via the logger
    @param giveup_quiet If True, a WARNING-level message is sent to the logger
                        if the operation fails more than max_tries times.
    @return The return value of the operation.
    @note If fail or giveup are functions, they are passed the contents of
    failargs (default: opargs) or giveupargs (default: failargs or
    opargs) with several additional arguments appended.  Those
    arguments are the exception that was caught, the number of
    attempts so far, the max_tries, the sleep_time, and then a boolean
    that is true iff the operation is about to be retried."""
        
    # Handle default arguments:
    if fail is not None:
        if failargs is None: failargs=opargs
        if giveup is None: giveup=fail
    if giveup is not None:
        if giveupargs is None: giveupargs=failargs

    if sleep_time is None:
        sleep_time=0.1
    sleepme=sleep_time

    for ntry in range(max_tries):
        try:
            if logger is not None:
                logger.debug('%s(%s)'%(repr(operation),repr(opargs)))
            return operation(*opargs)
        except(Exception) as e:
            if(ntry<max_tries-1):
                # Failed but have not given up yet.
                if logger is not None:
                    logger.debug('Failed but have not given up: %s'%(str(e),),
                                 exc_info=True)
                if sleep_time is not None:
                    if randsleep:
                        sleepmax=min(sleep_time,0.05) * \
                            min(max(1.0,backoff**ntry),50.0)
                        sleepme=random.uniform(sleepmax/2.0,sleepmax)
                if isinstance(fail,str):
                    if logger is not None and ntry>=first_warn:
                        logger.info("%s (try %d/%d; sleep %.3f and retry): %s"%\
                                           (fail,ntry+1,max_tries,sleepme,repr(e)))
                elif fail is not None:
                    arglist=failargs[:]
                    arglist.extend([e,ntry+1,max_tries,sleep_time,True])
                    if logger is not None:
                        logger.debug('arglist to fail (1): '+repr(arglist))
                    fail(*arglist)
                time.sleep(max(0.05,sleepme))
            else:
                # Gave up.
                if logger is not None:
                    logger.debug('Failed and gave up: %s'%(str(e),),
                                 exc_info=True)
                if isinstance(giveup,str) and not giveup_quiet:
                    if logger is not None:
                        logger.warning("%s (giving up after %d tries): %s"%\
                                          (giveup,ntry+1,repr(e)),exc_info=True)
                elif giveup is not None:
                    arglist=giveupargs[:]
                    arglist.extend([e,ntry+1,max_tries,sleep_time,False])
                    if logger is not None:
                        logger.debug('arglist to fail (2): '+repr(arglist))
                    if isinstance(fail,str):
                        if giveup_quiet and logger is not None:
                            logger.warning(fail)
                    else:
                        fail(*arglist)
                raise
