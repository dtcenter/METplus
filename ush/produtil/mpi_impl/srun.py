##@namespace produtil.mpi_impl.srun 
# Adds SLURM srun support to produtil.run
#
# This module is part of the mpi_impl package -- see produtil.mpi_impl
# for details.  This translates produtil.run directives to SLURM srun
# commands.

import os, logging
import produtil.fileop,produtil.prog,produtil.mpiprog,produtil.pipeline

from .mpi_impl_base import MPIMixed,CMDFGen

##@var srun_path
# Path to the srun program
srun_path=produtil.fileop.find_exe('srun',raise_missing=False)
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
    assert(arg is not None)
    if threads is not None:
        arg.threads=threads
        return arg.env(OMP_NUM_THREADS=threads,KMP_NUM_THREADS=threads,
                       KMP_AFFINITY='scatter')
    else:
        del arg.threads
        return arg

def detect():
    """!Detects whether the SLURM srun command is available by looking
    for it in the $PATH."""
    return srun_path is not None

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
    f=mpirunner_impl(arg,allranks=allranks,**kwargs)
    logging.getLogger('srun').info("%s => %s"%(repr(arg),repr(f)))
    return f

def mpirunner_impl(arg,allranks=False,**kwargs):
    """!This is the underlying implementation of mpirunner and should
    not be called directly."""
    assert(isinstance(arg,produtil.mpiprog.MPIRanksBase))
    (serial,parallel)=arg.check_serial()
    if serial and parallel:
        raise MPIMixed('Cannot mix serial and parallel MPI ranks in the '
                       'same MPI program.')

    srun_args=[srun_path,'--export=ALL','--cpu_bind=core','--distribution=block:block']

    if arg.nranks()==1 and allranks:
        arglist=[ str(a) for a in arg.to_arglist(
                pre=srun_args,before=[],between=[])]
        return produtil.prog.Runner(arglist)
    elif allranks:
        raise MPIAllRanksError(
            "When using allranks=True, you must provide an mpi program "
            "specification with only one MPI rank (to be duplicated across "
            "all ranks).")
    elif serial:
        arg=produtil.mpiprog.collapse(arg)
        lines=[str(a) for a in arg.to_arglist(to_shell=True,expand=True)]
        if produtil.fileop.find_exe('mpiserial') is None:
            raise MPISerialMissing(
                'Attempting to run a serial program via srun but the '
                'mpiserial program is not in your $PATH.')
        return produtil.prog.Runner(
            [srun_path,'-n','%s'%(arg.nranks()),'mpiserial'],
            prerun=CMDFGen('serialcmdf',lines,**kwargs))
    else:
        cmdfile=list()
        irank=0
        for rank,count in arg.expand_iter(expand=False):
            cmdfile.append('%d-%d %s'%(irank,irank+count-1,rank.to_shell()))
            irank+=count
        return produtil.prog.Runner(
            [srun_path,'-n',str(irank),'--multi-prog'],
            prerun=CMDFGen('srun_cmdfile',cmdfile,filename_arg=True,**kwargs))

