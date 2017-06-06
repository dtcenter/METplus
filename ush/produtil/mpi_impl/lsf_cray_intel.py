## @namespace produtil.mpi_impl.lsf_cray_intel
# Adds support for LSF+aprun with the Intel OpenMP to produtil.run
#
# This module is part of the mpi_impl package -- see produtil.mpi_impl
# for details.  This implements the bizarre combination of LSF, Cray
# aprun with Intel OpenMP.  

import os, socket, logging, sys
import produtil.fileop,produtil.prog,produtil.mpiprog

from .mpi_impl_base import MPIMixed,CMDFGen

module_logger=logging.getLogger('lsf_cray_intel')

##@var mpirun_lsf_path
# Path to the mpirun.lsf program, or None if it isn't found.
aprun_path=produtil.fileop.find_exe('aprun',raise_missing=False)

##@var p_state_turbo
# Value to send to aprun --p-state option for Intel Turbo Mode.  
#
# This is the largest value printed out by 
#
#     cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies
#
# Which is either the highest allowed sustained clock speed, or the magic
# number for Turbo Mode.
p_state_turbo=None

def get_p_state_turbo():
    """!Value to send to aprun --p-state option for Intel Turbo Mode.  
    
    This is the largest value printed out by 
    
         cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies

    Which is either the highest allowed sustained clock speed, or the magic
    number for Turbo Mode."""
    global p_state_turbo
    if p_state_turbo is not None:
        return p_state_turbo
    states=list()
    with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies','rt') as saf:
        for line in saf.readlines():
            module_logger.info('saf line: '+repr(line))
            splat=line.split()
            module_logger.info('saf line split: '+repr(splat))
            for s in splat:
                try:
                    module_logger.info('saf entry: '+repr(s))
                    states.append(int(s))
                except ValueError as ve:
                    pass
    states.sort()
    module_logger.info('Possible --p-states options: '+repr(states))
    p_state_turbo=states[-1]
    module_logger.info('Turbo Mode --p-states option: %d'%p_state_turbo)
    assert(p_state_turbo>5e5)
    return p_state_turbo

def runsync(logger=None):
    """!Runs the "sync" command as an exe()."""
    if logger is None: logger=module_logger
    logger.info('Not running sync.')
    return

def openmp(arg,threads):
    """!Adds OpenMP support to the provided object

    @param arg An produtil.prog.Runner or
    produtil.mpiprog.MPIRanksBase object tree
    @param threads the number of threads, or threads per rank, an
    integer"""
    
    if threads is None:
        try:
            ont=os.environ.get('OMP_NUM_THREADS','')
            ont=int(ont)
            if ont>0:
                threads=ont
        except (KeyError,TypeError,ValueError) as e:
            pass

    if threads is None:
        nodesize=os.environ.get('PRODUTIL_RUN_NODESIZE','24')
        nodesize=int(nodesize)
        threads=max(1,nodesize-1)
        
    assert(threads>0)
    threads=int(threads)
    if hasattr(arg,'argins'):
        module_logger.info('Threaded with %s threads so add -cc depth.'%(
            repr(threads),))
        for a in reversed(['-cc','depth','-d',str(threads)]):
            arg=arg.argins(1,a)

        arg=arg.env(KMP_AFFINITY='disabled',OMP_NUM_THREADS=threads)

    if hasattr(arg,'threads'):
        arg.threads=threads
    return arg

def aprun_ln_sf(source,target,content,logger=None):
    if logger is None: logger=module_logger
    msg="Filesystem failure (will retry with aprun ln -sf): Cannot symlink \"%s\" -> \"%s\".  Instead, the symlink is to \"%s\"."%(
        target,source,content)
    logger.error(msg)
    status=produtil.pipeline.simple_run([
        aprun_path,'-q',"-N","1","-n","1","-j","1","/bin/ln","-sf",
        str(source),str(target)],   logger=logger)
    logger.warning('aprun ln -sf %s %s = %s'%(
        str(source),str(target),repr(status)))
    content=os.readlink(target)
    if content==source:
        logger.info('aprun ln -sf %s %s SUCCESS'%(
            str(source),str(target)))
        return True
    msg="FILESYSTEM FAILURE: Python and aprun ln -sf both cannot symlink \"%s\" -> \"%s\".  Instead, the symlink is to \"%s\"."%(
            target,source,content)
    logger.critical(msg)
    raise produtil.fileop.WrongSymlink(msg,target)

def detect():
    """!Determines if Cray aprun should be used to run MPI programs by
    looking for the aprun program in $PATH"""
    # global aprun_path
    # aprun_path='/bin/true'
    detected=aprun_path is not None
    if detected:
        module_logger.info('lsf_cray_intel detected; replace produtil.fileop.ln_sf')
        produtil.fileop.ln_sf = aprun_ln_sf
    return detected

def can_run_mpi():
    """!Does this module represent an MPI implementation? Returns True."""
    return True

def make_bigexe(exe,**kwargs): 
    """!Returns an ImmutableRunner that will run the specified program.
    @returns an empty list
    @note This function does NOT search $PATH.  That ensures the $PATH
      will be expanded on the compute node instead.  Use
      produtil.fileop.find_exe() if you want to explicitly search the
      PATH before execution
    @param exe The executable to run on compute nodes.
    @param kwargs Ignored."""
    exe=str(exe)    
    inside_aprun=int(os.environ.get('INSIDE_APRUN','0'))
    inside_aprun+=1
    r=produtil.prog.Runner(['aprun','-q','-N','1','-j','1','-n','1',exe])\
        .env(INSIDE_APRUN=str(inside_aprun))
    return produtil.prog.ImmutableRunner(r)

def mpirunner(arg,allranks=False,logger=None,**kwargs):
    if logger is None:
        logger=module_logger
    m=mpirunner2(arg,allranks=allranks,logger=logger,**kwargs)
    logger.info('mpirunner: %s => %s'%(repr(arg),repr(m)))
    return m

def mpirunner2(arg,allranks=False,logger=None,**kwargs):
    """!Turns a produtil.mpiprog.MPIRanksBase tree into a produtil.prog.Runner
    @param arg a tree of produtil.mpiprog.MPIRanksBase objects
    @param allranks if True, and only one rank is requested by arg, then
      all MPI ranks will be used
    @param logger a logging.Logger for log messages
    @param kwargs passed to produtil.mpi_impl.mpi_impl_base.CMDFGen
      when mpiserial is in use.
    @returns a produtil.prog.Runner that will run the selected MPI program"""
    if logger is None:
        logger=logging.getLogger('lsf_cray_intel')
    assert(isinstance(arg,produtil.mpiprog.MPIRanksBase))
    (serial,parallel)=arg.check_serial()
    if serial and parallel:
        raise MPIMixed(
            'Cannot mix serial and parallel MPI ranks in the same '
            'MPI program.')
    nodesize=os.environ.get('PRODUTIL_RUN_NODESIZE','24')
    nodesize=int(nodesize)
    hyperthreads=os.environ.get('PRODUTIL_RUN_HYPERTHREADS','1')
    hyperthreads=int(hyperthreads)
    maxtasks=os.environ['TOTAL_TASKS']
    maxtasks=int(maxtasks)

    # The returned runner object.  We'll add to this below:
    runner=produtil.prog.Runner([aprun_path])['-q'].env(KMP_AFFINITY='disabled')
    threads=arg.threads
    logger.info('Decide what to do with -cc option.')
    if threads is not None and threads>1:
        logger.info('Threaded with %s threads so add -cc depth.'%(
                repr(threads),))
        runner['-cc','depth','-d',str(threads)]
        runner.env(OMP_NUM_THREADS=str(threads))
    else:
        logger.info('No threads (threads=%s).'%(repr(threads),))
        runner['-cc','depth','-d','1']
        threads=1

    # Set up the INSIDE_APRUN variable so the executed MPI program
    # will be able to run serial programs.
    inside_aprun=int(os.environ.get('INSIDE_APRUN','0'))
    inside_aprun+=1
    runner=runner.env(INSIDE_APRUN=str(inside_aprun))

    if arg.nranks()==1 and allranks:
        for rank,count in arg.expand_iter(expand=False):
            pernode=min(maxtasks,nodesize//threads)
            rpn=rank.ranks_per_node
            if rpn: pernode=min(pernode,rpn)
            runner=runner['-j','%d'%(hyperthreads),
                          '-N','%d'%(pernode),
                          '-n','%d'%(maxtasks)]
            seenPS=False
            if rank.haslocalopts():
                localopts=[ str(x) for x in rank.localoptiter() ]
                seenPS='--p-state' in localopts
                runner=runner[localopts]
            if not seenPS and rank.turbomode:
                runner=runner['--p-state',str(get_p_state_turbo())]
            if maxtasks==1248:
                assert(rank.turbomode or seenPS)
            runner=runner[rank.args()]
            return runner
    elif allranks:
        raise MPIAllRanksError(
            "When using allranks=True, you must provide an mpi program "
            "specification with only one MPI rank (to be duplicated across "
            "all ranks).")
    elif serial:
        for rank,count in arg.expand_iter(False):
            try:
                if rank.runner.getenv('INSIDE_APRUN'):
                    raise MPIMixed('Trying to run aprun within aprun.  In mpiserial, you must run batchexe() programs only.')
            except KeyError as ke: pass
        lines=[a for a in arg.to_arglist(to_shell=True,expand=True)]
        if produtil.fileop.find_exe('mpiserial') is None:
            raise MPISerialMissing(
                'Attempting to run a serial program via aprun mpiserial but '
                'the mpiserial program is not in your $PATH.')

        first=True

        arg=produtil.mpiprog.collapse(arg)
        
        prior_arglist=[]
        total_count=0
            
        for rank,count in arg.expand_iter(expand=False):

            pernode=min(maxtasks,nodesize//threads)
            rpn=rank.ranks_per_node
            if rpn: pernode=min(pernode,rpn)

            #if not first: runner=runner[':']
            arglist=['-j','%d'%(hyperthreads), '-N','%d'%(pernode)]
            # runner=runner[,
            #               '-n','%d'%(count)]

            seenS=False
            seenPS=False
            if arg.haslocalopts():
                localopts=[ str(x) for x in arg.localoptiter() ]
                arglist.extend(localopts)
                seenS='-S' in localopts
                seenPS='--p-state' in localopts
            if not seenPS and arg.turbomode:
                arglist.extend(['--p-state',str(get_p_state_turbo())])

            if prior_arglist==arglist:
                total_count+=count
            elif not total_count or not prior_arglist:
                total_count=count
                prior_arglist=arglist
            else:
                if not first: runner=runner[':']
                runner=runner[prior_arglist]
                runner=runner['-n',str(total_count),'mpiserial']
                first=False
                prior_arglist=arglist
                total_count=count
        assert(runner is not None)

        if prior_arglist==arglist and total_count:
            if not first: runner=runner[':']
            runner=runner[prior_arglist]
            runner=runner['-n',str(total_count),'mpiserial']

        cmdfgen=CMDFGen('serialcmdf',lines,**kwargs)
        runner=runner.prerun(cmdfgen)
        assert(runner is not None)
        return runner
    else:
        first=True

        maxtasks=1
        for rank,count in arg.expand_iter(expand=False):
            maxtasks=max(count,maxtasks)
            
        for rank,count in arg.expand_iter(expand=False):
            pernode=min(count,maxtasks,nodesize//threads)
            rpn=rank.ranks_per_node
            if rpn: pernode=min(pernode,rpn)
            if not first: runner=runner[':']
            runner=runner['-j','%d'%(hyperthreads),
                          '-N','%d'%(pernode),
                          '-n','%d'%(count)]
            seenS=False
            seenPS=False
            if rank.haslocalopts():
                localopts=[ str(x) for x in rank.localoptiter() ]
                runner=runner[localopts]
                seenS='-S' in localopts
                seenPS='--p-state' in localopts
            if count<nodesize and count>1 and not seenS:
                runner=runner['-S',str((count+1)//2)]
            if not seenPS and rank.turbomode:
                runner=runner['--p-state',str(get_p_state_turbo())]
            runner=runner[rank.to_shell()]
            first=False
        return runner

