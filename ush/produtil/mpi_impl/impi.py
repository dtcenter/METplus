##@namespace produtil.mpi_impl.impi
# Adds Intel MPI support to produtil.run
#
# This module is part of the produtil.mpi_impl package -- see
# __init__.py for details.  This implements the Intel MPI, but may
# work for other MPI implementations that use the "mpirun" command and
# OpenMP implementations that use the KMP_NUM_THREADS or
# OMP_NUM_THREADS environment variables.
#
# @warning This module assumes the TOTAL_TASKS environment variable is
# set to the maximum number of MPI ranks the program has available to
# it.  That is used when the mpirunner is called with the
# allranks=True option.

import os, sys, logging
import produtil.fileop,produtil.prog,produtil.mpiprog,produtil.pipeline

from .mpi_impl_base import MPIMixed,CMDFGen

##@var mpirun_path
# Path to the mpirun program, or None if it could not be found.
mpirun_path=produtil.fileop.find_exe('mpirun',raise_missing=False)

module_logger=logging.getLogger('lsf_cray_intel')

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
    if threads is not None:
        if hasattr(arg,'threads'):
            arg.threads=threads
        if hasattr(arg,'env'):
            arg.env(OMP_NUM_THREADS=threads,KMP_NUM_THREADS=threads,
                    KMP_AFFINITY='scatter')
    else:
        del arg.threads
    return arg

def detect():
    """!Detects whether Intel MPI is available."""
    logger=logging.getLogger('produtil.mpi_impl.impi')
    if mpirun_path is None: return False
    try:
        mpirun=produtil.prog.Runner([mpirun_path])
        p=produtil.pipeline.Pipeline(mpirun,capture=True,logger=logger)
        version=p.to_string()
        status=p.poll()
        return version.find('Intel(R) MPI')>=0
    except Exception as e:
        logger.error('ERROR in mpirun --version: %s\n'%(str(e),),
                     exc_info=True)
        raise

def can_run_mpi():
    """!Does this module represent an MPI implementation? Returns True."""
    return True

def make_bigexe(exe,**kwargs): 
    """!Returns an ImmutableRunner that will run the specified program.
    @returns an empty list
    @param exe The executable to run on compute nodes.
    @param kwargs Ignored."""
    return produtil.prog.ImmutableRunner([str(exe)],**kwargs)

def mpirunner(arg,allranks=False,**kwargs):
    """!Turns a produtil.mpiprog.MPIRanksBase tree into a produtil.prog.Runner
    @param arg a tree of produtil.mpiprog.MPIRanksBase objects
    @param allranks if True, and only one rank is requested by arg, then
      all MPI ranks will be used
    @param kwargs passed to produtil.mpi_impl.mpi_impl_base.CMDFGen
      when mpiserial is in use.
    @returns a produtil.prog.Runner that will run the selected MPI program"""
    assert(isinstance(arg,produtil.mpiprog.MPIRanksBase))
    (serial,parallel)=arg.check_serial()
    if serial and parallel:
        raise MPIMixed('Cannot mix serial and parallel MPI ranks in the '
                       'same MPI program.')

    extra_args=[]

    if kwargs.get('label_io',False):
        extra_args.append('-l')

    if arg.nranks()==1 and allranks:
        arglist=[ a for a in arg.to_arglist(
                pre=[mpirun_path]+extra_args,
                before=['-np',os.environ['TOTAL_TASKS']],
                between=[':'])]
        return produtil.prog.Runner(arglist)
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
                'Attempting to run a serial program via mpirun but the '
                'mpiserial program is not in your $PATH.')
        return produtil.prog.Runner(
            [mpirun_path]+extra_args+['-np','%s'%(arg.nranks()),'mpiserial'],
            prerun=CMDFGen('serialcmdf',lines,**kwargs))
    else:
        arglist=[ a for a in arg.to_arglist(
                pre=[mpirun_path]+extra_args,   # command is mpirun
                before=['-np','%(n)d'], # pass env, number of procs is kw['n']
                between=[':']) ] # separate commands with ':'
        return produtil.prog.Runner(arglist)

