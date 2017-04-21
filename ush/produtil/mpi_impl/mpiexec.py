##@namespace produtil.mpi_impl.mpiexec 
# Adds MPICH or MVAPICH2 support to produtil.run
#
# This module is part of the mpi_impl package -- see produtil.mpi_impl
# for details.  This implements the Hydra MPI wrapper and MPICH MPI
# implementation with Intel OpenMP, but may work for other MPI
# implementations that use the "mpiexec" command and OpenMP
# implementations that use the KMP_NUM_THREADS or OMP_NUM_THREADS
# environment variables.
#
# @warning This module assumes the TOTAL_TASKS environment variable is
# set to the maximum number of MPI ranks the program has available to
# it.  That is used when the mpirunner is called with the
# allranks=True option.

import os, logging
import produtil.fileop,produtil.prog,produtil.mpiprog,produtil.pipeline

from .mpi_impl_base import MPIMixed,CMDFGen

##@var mpiexec_path
# Path to the mpiexec program
mpiexec_path=produtil.fileop.find_exe('mpiexec',raise_missing=False)
module_logger=logging.getLogger('mpiexec')

def runsync(logger=None):
    """!Runs the "sync" command as an exe()."""
    if logger is None: logger=module_logger
    sync=produtil.prog.Runner(['/bin/sync'])
    p=produtil.pipeline.Pipeline(sync,capture=True,logger=logger)
    version=p.to_string()
    status=p.poll()

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
    if hasattr(arg,'env'):
        arg=arg.env(OMP_NUM_THREADS=threads,  # no, bad: KMP_AFFINITY='scatter',
                    KMP_NUM_THREADS=threads,MKL_NUM_THREADS=1)
        
    arg.threads=threads
    return arg

def detect():
    """!Detects whether the MPICH mpi implementation is available by
    looking for the mpiexec program in $PATH."""
    return mpiexec_path is not None

def can_run_mpi():
    """!Does this module represent an MPI implementation? Returns True."""
    return True

def make_bigexe(exe,**kwargs): 
    """!Returns an ImmutableRunner that will run the specified program.
    @returns an empty list
    @param exe The executable to run on compute nodes.
    @param kwargs Ignored."""
    return produtil.prog.ImmutableRunner([str(exe)],**kwargs)

def mpirunner(arg,allranks=False,logger=None,**kwargs):
    if logger is None:
        logger=module_logger
    m=mpirunner2(arg,allranks=allranks,logger=logger,**kwargs)
    logger.info('mpirunner: %s => %s'%(repr(arg),repr(m)))
    return m

def mpirunner2(arg,allranks=False,**kwargs):
    """!Turns a produtil.mpiprog.MPIRanksBase tree into a produtil.prog.Runner
    @param arg a tree of produtil.mpiprog.MPIRanksBase objects
    @param allranks if True, and only one rank is requested by arg, then
      all MPI ranks will be used
    @param kwargs passed to produtil.mpi_impl.mpi_impl_base.CMDFGen
      when mpiserial is in use.
    @returns a produtil.prog.Runner that will run the selected MPI program
    @warning Assumes the TOTAL_TASKS environment variable is set
      if allranks=True"""
    assert(isinstance(arg,produtil.mpiprog.MPIRanksBase))
    (serial,parallel)=arg.check_serial()
    if serial and parallel:
        raise MPIMixed('Cannot mix serial and parallel MPI ranks in the '
                       'same MPI program.')

    extra_args=[]

    if kwargs.get('label_io',False):
        extra_args.append('-prepend-rank')

    runner=None
    if arg.nranks()==1 and allranks:
        arglist=[ a for a in arg.to_arglist(
                pre=[mpiexec_path]+extra_args,
                before=['-np',os.environ['TOTAL_TASKS']],
                between=[':'])]
        runner=produtil.prog.Runner(arglist)
    elif allranks:
        raise MPIAllRanksError(
            "When using allranks=True, you must provide an mpi program "
            "specification with only one MPI rank (to be duplicated across "
            "all ranks).")
    elif serial:
        arg=produtil.mpiprog.collapse(arg)
        lines=[a for a in arg.to_arglist(to_shell=True,expand=True)]
        if produtil.fileop.find_exe('mpiserial') is None:
            raise MPISerialMissing(
                'Attempting to run a serial program via mpiexec but the '
                'mpiserial program is not in your $PATH.')
        runner=produtil.prog.Runner(
            [mpiexec_path]+extra_args+['-np','%s'%(arg.nranks()),'mpiserial'],
            prerun=CMDFGen('serialcmdf',lines,**kwargs))
    else:
        arglist=[ a for a in arg.to_arglist(
                pre=[mpiexec_path]+extra_args,   # command is mpiexec
                before=['-np','%(n)d'], # pass env, number of procs is kw['n']
                between=[':']) ] # separate commands with ':'
        runner=produtil.prog.Runner(arglist)
    
    threads=arg.threads
    if threads is not None and threads>1:
        runner=runner.env(OMP_NUM_THREADS=threads, # no, bad: KMP_AFFINITY='scatter',
                          KMP_NUM_THREADS=threads,MKL_NUM_THREADS=1)
    return runner
