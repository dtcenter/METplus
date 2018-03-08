##@namespace produtil.mpi_impl.mpiexec_mpt
# Adds SGI MPT support to produtil.run
#
# This module is part of the produtil.mpi_impl package.  It underlies
# the produtil.run.openmp, produtil.run.mpirun , and
# produtil.run.mpiserial functions, providing the implementation
# needed to run with the SGI MPT MPI implementation.
#
# @warning This module assumes the TOTAL_TASKS environment variable is
# set to the maximum number of MPI ranks the program has available to
# it.  That is used when the mpirunner is called with the
# allranks=True option.

import os, logging
import produtil.fileop,produtil.prog,produtil.mpiprog,produtil.pipeline

from .mpi_impl_base import CMDFGen,MPIMixed,MPIThreadsMixed, \
                           MPILocalOptsMixed,ImplementationBase
from produtil.mpiprog import MIXED_VALUES

class Implementation(ImplementationBase):
    """Adds SGI MPT support to produtil.run
    
    This class is part of the produtil.mpi_impl package.  It underlies
    the produtil.run.openmp, produtil.run.mpirun , and
    produtil.run.mpiserial functions, providing the implementation
    needed to run with the SGI MPT MPI implementation.
    
    @warning This class assumes the TOTAL_TASKS environment variable is
    set to the maximum number of MPI ranks the program has available to
    it.  That is used when the mpirunner is called with the
    allranks=True option."""

    @staticmethod
    def name():
        return 'mpiexec_mpt'
    
    @staticmethod
    def detect(mpiexec_mpt_path=None,mpiserial_path=None,total_tasks=None,logger=None,force=False,silent=False):
        """!Detects whether the SGI MPT is available by looking for mpiexec_mpt."""
        if mpiexec_mpt_path is None:
            if force:
                mpiexec_mpt_path='mpiexec_mpt'
            else:
                mpiexec_mpt_path=produtil.fileop.find_exe( \
                    'mpiexec_mpt',raise_missing=True)

        if logger is None:
            logger=logging.getLogger('mpi_impl')

        if total_tasks is None:
            total_tasks=os.environ['TOTAL_TASKS']
            total_tasks=int(total_tasks)

        return Implementation(mpiexec_mpt_path,mpiserial_path,total_tasks,
                              logger,force,silent)

    def __init__(self,mpiexec_mpt_path,mpiserial_path,total_tasks,logger,
                 force,silent):
        super(Implementation,self).__init__(logger)
        if mpiserial_path or force:
            self.mpiserial_path=mpiserial_path
        self.mpiexec_mpt_path=mpiexec_mpt_path
        self.total_tasks=total_tasks
        self.silent=silent

    ##@var mpiexec_mpt_path
    # Path to the mpiexec_mpt program.

    def runsync(self,logger=None):
        """!Runs the "sync" command as an exe()."""
        if logger is None: logger=self.logger
        sync=produtil.prog.Runner(['/bin/sync'])
        p=produtil.pipeline.Pipeline(sync,capture=True,logger=logger)
        version=p.to_string()
        status=p.poll()

    def openmp(self,arg,threads):
        """!Adds OpenMP support to the provided object
    
        @param arg An produtil.prog.Runner or
        produtil.mpiprog.MPIRanksBase object tree
        @param threads the number of threads, or threads per rank, an
        integer"""
        if threads is not None:
            if hasattr(arg,'threads'):
                arg.threads=threads
            if hasattr(arg,'env'):
                return arg.env(OMP_NUM_THREADS=threads)
        else:
            del arg.threads
        return arg
    
    def guess_nthreads(self,default):
        """!Tries to guess the number of threads in use
        @param default the value to return if the function cannot guess"""
        omp=int(os.environ.get('OMP_NUM_THREADS',None))
        mkl=int(os.environ.get('MKL_NUM_THREADS',None))
        if omp is None and mkl is None:
            return default
        omp = (1 if omp is None else omp)
        mkl = (1 if mkl is None else mkl)
        return omp*mkl
    
    def can_run_mpi(self):
        """!Does this class represent an MPI implementation? Returns True."""
        return True
    
    def make_bigexe(self,exe,**kwargs): 
        """!Returns an ImmutableRunner that will run the specified program.
        @returns an empty list
        @param exe The executable to run on compute nodes.
        @param kwargs Ignored."""
        return produtil.prog.ImmutableRunner([str(exe)],**kwargs)
    
    def mpirunner(self,arg,allranks=False,**kwargs):
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
            raise MPIMixed('Cannot mix serial and parallel MPI ranks in the same MPI program.')


        if arg.mixedlocalopts():
            raise MPILocalOptsMixed('Cannot mix different local options for different executables or blocks of MPI ranks in mpiexec_mpt')
        if arg.threads==MIXED_VALUES:
            raise MPIThreadsMixed('Cannot mix different thread counts for different executables or blocks of MPI ranks in mpiexec_mpt')

        if arg.nranks()==1 and allranks:
            arglist=[ a for a in arg.to_arglist(
                    pre=[self.mpiexec_mpt_path],
                    before=['-n','%d'%self.total_tasks],
                    between=[':'])]
            runner=produtil.prog.Runner(arglist)
        elif allranks:
            raise MPIAllRanksError("When using allranks=True, you must provide an mpi program specification with only one MPI rank (to be duplicated across all ranks).")
        elif serial:
            arg=produtil.mpiprog.collapse(arg)
            lines=[a for a in arg.to_arglist(to_shell=True,expand=True)]
            runner=produtil.prog.Runner(
                [self.mpiexec_mpt_path,'-n','%s'%(arg.nranks()),self.mpiserial_path],
                prerun=CMDFGen('serialcmdf',lines,silent=self.silent,**kwargs))
        else:
            arglist=[ a for a in arg.to_arglist(
                    pre=[self.mpiexec_mpt_path],   # command is mpiexec
                    before=['-n','%(n)d'], # pass env, number of procs is kw['n']
                    between=[':']) ] # separate commands with ':'
            runner=produtil.prog.Runner(arglist).env(MPI_TYPE_DEPTH=20)
        runner=runner.env(MPI_TYPE_DEPTH=20,MPI_BUFS_PER_PROC=256,MPI_BUFS_PER_HOST=1024)
        if arg.threads:
            s='%d'%arg.threads
            runner.env(OMP_NUM_THREADS=s,MKL_NUM_THREADS='1')
        return runner
    
