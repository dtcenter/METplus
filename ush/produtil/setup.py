"""!Contains setup(), which initializes the produtil package.

This module contains the setup() function that should be called once
by every Python process started, immediately after Python starts."""

##@var __all__
# Lists symbols exported by "from produtil.setup import *"
__all__=['setup']

import logging, threading
import produtil.sigsafety, produtil.log, produtil.dbnalert, produtil.cluster
import produtil.batchsystem

def setup(ignore_hup=False,dbnalert_logger=None,jobname=None,cluster=None,
          send_dbn=None,thread_logger=False,thread_stack=2**24,**kwargs):
    """!Initializes the produtil package.  Calls the module
    initialization functions for all other modules in the produtil
    package.

    At present, it:

    1. Installs signal handlers that will cleanly abort the process.
    2. Sets up logging to the jlogfile, if $jlogfile is in the environment.
    3. Sets up logging to stdout and stderr.
    4. Sets up the produtil.dbnalert module so DBNAlert objects will
    function properly
    5. Sets the produtil.cluster's idea of what cluster it is on.  If no
    cluster is specified, the produtil.cluster is instructed to guess.

    This is a wrapper around the produtil.sigsafety, and produtil.log,
    and other module initializers.  Note that one could call each
    module's initialization functions directly instead.  However, one
    would have to keep up with changes to the produtil package during
    upgrades in order to do that.

    @param ignore_hup if True, this program will ignore SIGHUP.  Use
      this for UNIX daemon processes.  Turned off (False) by default,
      causing SIGHUP to be a terminal signal.
    @param dbnalert_logger  sent to dbnalert.init_module's logger argument
       to initialize the logging domain for informational messages
       about dbn alerts
    @param jobname  dbn_alert job string
    @param cluster  if specified and not None, sent to produtil.cluster's
      set_cluster.  Otherwise, produtil.cluster.where() is called to
      guess the cluster, or set suitable defaults.
    @param send_dbn  should dbn alerts be sent?
    @param thread_logger  if True, log messages will include thread name.
    @param thread_stack  passed to threading.stack_size(); the stack size in
      bytes for new threads.  The default is 2**24, which is 16 MB.
      See the threading module for details.  Set to None to disable
      changing of the threading stack size.
    @param kwargs all other keyword args sent to produtil.log.configureLogging()"""

    # Set the threading stack size first so any threads launched by
    # Python will have reasonable stack sizes.  This is intended to
    # prevent problems seen by some users where Python will be unable
    # to spawn any threads:
    if thread_stack is not None:
        threading.stack_size(thread_stack)

    # Set the default jobname.  This is usually used for manually-run
    # scripts to ensure they have a "jobname" in the logging system:
    if jobname is not None:
        produtil.batchsystem.set_default_name(jobname)

    # Configure logging next so that the install_handlers will be able
    # to log.
    produtil.log.configureLogging(thread_logger=thread_logger,**kwargs)
    # Install signal handlers, and let the caller configure SIGHUP settings:
    produtil.sigsafety.install_handlers(ignore_hup=ignore_hup)
    # Set up dbnalert:
    produtil.dbnalert.init_module(logger=dbnalert_logger,jobname=jobname,
                                  send_dbn=send_dbn)

    # Set up cluster:
    if cluster is not None:
        produtil.cluster.set_cluster(cluster)
    else:
        produtil.cluster.where() # guess cluster
