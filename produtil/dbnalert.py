"""!This module runs the NCO dbn_alert program, or logs dbn_alert messages
if run with dbn alerts disabled."""

##@var __all__
# Symbols exported by "from produtil.dbnalert import *"
__all__=["DBNAlert"]

import logging, os
import produtil.run

from produtil.prog import Runner
from produtil.run import checkrun, batchexe, alias, run

# Globals:

##@var log
# logging.Logger object to send dbnalert messages
log=None

##@var job
# a string representing this job (from os.environ['job'] by default)
job=None

##@var send_dbn_alerts
# False = don't run dbn_alert.  Just log the alerts.
send_dbn_alerts=True

##@var no_DBNROOT_warn
# True = I have already warned that $DBNROOT is unset
no_DBNROOT_warn=False

def find_dbn_alert():
    """!Locates the dbn_alert executable based on environment
    variables, and returns it as a produtil.prog.Runner object."""
    global no_DBNROOT_warn
    ENV=os.environ
    if ENV.get('DBNROOT','')!='':
        return alias(batchexe(os.path.join(ENV['DBNROOT'],'bin/dbn_alert')))
    else:
        if not no_DBNROOT_warn:
            log.warning("$DBNROOT is not set.  Will search for dbn_alert "
                        "in your $PATH.")
            no_DBNROOT_warn=True
        return alias(batchexe('dbn_alert'))

########################################################################
class DBNAlert(object):
    """!This class represents a call to dbn_alert, as a callable Python
    object.  It allows the instructions on how to make the call to be
    stored for later use by a produtil.datastore.Product object's
    add_callback and call_callbacks functions."""
    def __init__(self,args,loglevel=logging.WARNING,alert_exe=None):
        """!Create a new DBNAlert object that can be used to send an
        alert later on.
        @param args The arguments to dbn_alert.
        @param alert_exe The dbn_alert executable name.
        @param loglevel A Python logging level to log messages before each
        alert."""
        if not isinstance(args,list) and not isinstance(args,tuple):
            raise TypeError('In DBNAlert(), the first argument must be a list or tuple of arguments to send to dbn_alert')
        if alert_exe is not None and not isinstance(alert_exe,str) \
                and not isinstance(alert_exe,Runner):
            raise TypeError('In DBNAlert(), the alert_exe argument must be a string executable name, or a produtil.prog.Runner object')

        self.alert_args=[ str(s) for s in args ]
        if isinstance(alert_exe,Runner): alert_exe=alias(alert_exe)
        self.alert_exe=alert_exe
        if self.alert_exe is None: self.alert_exe=find_dbn_alert()
        self.loglevel=loglevel
    ##@var alert_args
    # Array of arguments to the alert function

    ##@var loglevel
    # Desired logging level.

    ##@var alert_exe
    # Alert executable

    def __call__(self,**kwargs):
        """!Expands strings specified in the constructor and calls
        dbn_alert with the results.  If dbn alerts are disabled, then
        the fact that a dbn alert would be run is logged, but
        dbn_alert is NOT called.
        @param kwargs string formatting variables for the dbn alert arguments"""
        assert(job is not None)
        kwargs['job']=str(job)
        alert_args=[ s.format(**kwargs) for s in self.alert_args ]
        if send_dbn_alerts:
            if isinstance(self.alert_exe,str):
                cmd=batchexe(self.alert_exe)[alert_args]
            else:
                cmd=self.alert_exe[alert_args]
            log.log(logging.INFO,'DBN Alert: '+repr(cmd))
            ret=run(cmd)
            exit_log_level=( logging.INFO if ret==0 else logging.ERROR )
            log.log(exit_log_level,'Exit status %s from dbn_alert.'%(repr(ret), ))
        else:
            log.log(self.loglevel,'dbn_alert is disabled')
            log.log(self.loglevel,'would run: dbn_alert '+( " ".join(alert_args) ))

########################################################################
def init_logging(logger=None):
    """!Initializes logging for this module.  The argument is either a
    logging.Logger to log to, or the string name of the logging
    domain."""
    global log
    if logger is None:
        logger=logging.getLogger('dbn_alert')
    elif isinstance(logger,str):
        logger=logging.getLogger(logger)
    log=logger

########################################################################
def init_jobstring(jobname=None):
    """!Sets the job string (for dbn_alerts) to the specified value,
    or if unspecified, tries to guess one from the environment."""
    global job
    if jobname is not None:
        job=str(jobname)
        return

    ENV=os.environ
    if 'job' in ENV:
        job=str(ENV['job'])
        return

    # Cannot guess a full name, so try to piece one together.  It will
    # look like "LLMODEL_POST.30113"
    (name,iid)=(None,None) # name=MODEL_POST part, iid=30113 part

    # Get the job name:
    for namevar in ['LSB_JOBNAME','PBS_JOBNAME','MOAB_JOBNAME']:
        if namevar in ENV and ENV[namevar]!='':
            name=os.path.basename(ENV[namevar]) # remove slashes
            break
    if name is None: name='unknown'

    # Get the job id:
    for iidvar in ['LSB_JOBID','PBS_JOBID','MOAB_JOBID']:
        if iidvar in ENV and ENV[iidvar]!='':
            iid=str(ENV[iidvar])
    if iid is None: iid=str(os.getpid())

    job='LL%s.%s'%(name,iid)

########################################################################
def init_dbn_alert(send_dbn=None):
    """!DBN alert initialization helper function.

    This is part of the implementation of init_module: it decides
    whether to send DBNet alerts, and sets the module-scope
    send_dbn_alerts variable accordingly.  That will then be used by
    DBNAlert objects to decide whether to actually call the dbn_alert
    program.
    @protected
    @param send_dbn Do we send dbn alerts?"""
    logger=logging.getLogger('dbn_alert')
    global send_dbn_alerts
    ENV=os.environ
    send_dbn_alerts=False

    if send_dbn is not None and not send_dbn:
        send_dbn_alerts=send_dbn
        return

    if 'RUN_ENVIR' not in ENV:
        logger.warning('RUN_ENVIR is unset.  Disabling DBN alerts.')
    elif ENV['RUN_ENVIR'].upper()!='NCO':
        logger.info('RUN_ENVIR=%s is not "NCO".  Disabling DBN alerts.'
                       %(ENV['RUN_ENVIR'],))
    elif send_dbn is None:
        send_dbn_alerts = ( 'YES' == ENV.get('SENDDBN','NO').upper() )
        if send_dbn_alerts:
            logger.info('Enabling dbn_alerts because SENDDBN=YES')
        else:
            logger.info('Disabling dbn_alerts because SENDDBN is not YES')
    else:
        send_dbn_alerts=send_dbn
        if send_dbn_alerts:
            logger.info('Enabling dbn_alerts because the code manually '
                           'turned them on (send_dbn=True)')
        else:
            logger.info('Disabling dbn_alerts because the code manually '
                           'turned them off (send_dbn=False)')
    if 'DBNROOT' not in ENV:
        logger.warning('DBNROOT is unset.  Disabling DBN alerts.')
        send_dbn_alerts=False
    elif ENV.get('DBNROOT') == 'DBNROOT_OFF':
        logger.info(
            'DBNROOT is set to DBNROOT_OFF.  Disabling DBN alerts.')
        send_dbn_alerts=False

########################################################################
def init_module(logger=None,jobname=None,send_dbn=None):
    """!Call to initialize this module.

    Initializes the logging and job string for this module.
    @param logger Either a logging.Logger object to receive log
      messages, or the string name of a logger domain.
    @param jobname The dbn_alert job string for this job.
    @param send_dbn Optional.  If specified, this controls whether
      dbn_alert is actually run (True) or not (False).  If unspecified,
      then the SENDDBN environment variable is used."""
    init_jobstring(jobname)
    init_logging(logger)
    init_dbn_alert(send_dbn)
