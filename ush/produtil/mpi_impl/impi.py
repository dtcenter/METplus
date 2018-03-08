##@namespace produtil.mpi_impl.impi

import os, sys, logging
import produtil.fileop,produtil.prog,produtil.mpiprog,produtil.run

from .mpi_impl_base import MPIMixed,CMDFGen,ImplementationBase, \
                           MPIThreadsMixed,MPILocalOptsMixed, \
                           guess_total_tasks
from produtil.pipeline import NoMoreProcesses
from produtil.mpiprog import MIXED_VALUES

class Implementation(ImplementationBase):
    """!Adds Intel MPI support to produtil.run

    This module is part of the produtil.mpi_impl package -- see
    __init__.py for details.  This implements the Intel MPI, but may
    work for other MPI implementations that use the "mpirun" command
    and OpenMP implementations that use the KMP_NUM_THREADS or
    OMP_NUM_THREADS environment variables.

    @warning This module assumes the TOTAL_TASKS environment variable
    is set to the maximum number of MPI ranks the program has
    available to it.  That is used when the mpirunner is called with
    the allranks=True option."""

    ##@var mpirun_path
    # Path to the mpirun program, or None if it could not be found.

    @staticmethod
    def name():
        """!Returns the name of this MPI implementation: impi"""
        return "impi"

    @staticmethod
    def detect(mpirun_path=None,total_tasks=None,logger=None,
               force=False,mpiserial_path=None,silent=False,**kwargs):
        """!Detects whether Intel MPI is available.  If it is
        available, a new Implementation object is returned.

        @param mpirun_path Optional: path to the "mpirun" program.  If
          none is specified, the os.environ['PATH'] will be searched

        @param total_tasks Optional: the number of slots available to
          run processes.  This is the maximum value for
          MPI_COMM_WORLD*OMP_NUM_THREADS.

        @param logger a logging.Logger for messages

        @param force Optional: if True, then detect() will always succeed,
          and will use "mpirun" as the mpirun path if mpirun_path is missing"""
        if logger is None:
            logger=logging.getLogger('mpi_impl')

        if mpirun_path is None:
            if force:
                mpirun_path='mpirun'
            else:
                mpirun_path=produtil.fileop.find_exe('mpirun',raise_missing=True)

        if force:
            return Implementation(mpirun_path,mpiserial_path,total_tasks,logger,force,silent)

        try:
            version=produtil.run.runstr(produtil.run.exe(mpirun_path))
            if version.find('Intel(R) MPI')<0 and not silent:
                logger.warning('mpirun --version: could not find '
                               'version in output')
        except (TypeError,ValueError,KeyError,EnvironmentError,NoMoreProcesses,
                produtil.prog.ExitStatusException) as e:
            if not force:
                if not silent:
                    logger.info('impi not detected: mpirun --version: %s\n'%(str(e),),)
                raise
        return Implementation(mpirun_path,mpiserial_path,total_tasks,logger,force,silent)

    def __init__(self,mpirun_path,mpiserial_path,total_tasks,logger,force,silent):
        """!Constructor for Implementation.  Do not call this
        directly; call Implementation.detect() instead.

        @param mpirun_path path to the mpirun program
        @param logger Optional.  A logging.Logger object for messages."""
        super(Implementation,self).__init__(logger=logger)
        if mpiserial_path or force:
            self.mpiserial_path=mpiserial_path
        self.mpirun_path=mpirun_path
        if not total_tasks:
            self.total_tasks=guess_total_tasks(logger,silent)
        else:
            self.total_tasks=int(total_tasks)
        self.silent=silent
        assert(isinstance(self.total_tasks,int))

    def runsync(self,logger=None):
        """!Runs the "sync" command as an exe()."""
        if logger is None: logger=self.logger
        produtil.run.run(produtil.run.exe('/bin/sync'))
    
    def openmp(self,arg,threads,logger=None):
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
        @returns a produtil.prog.Runner that will run the selected MPI program"""
        if not isinstance(arg,produtil.mpiprog.MPIRanksBase):
            raise TypeError(
                'The first argument to mpirunner must be an MPIRanksBase.  '
                'You provided a %s %s.'%(
                    type(arg).__name__, repr(arg)))
        (serial,parallel)=arg.check_serial()
        if serial and parallel:
            raise MPIMixed('Cannot mix serial and parallel MPI ranks in the '
                           'same MPI program.')

        if arg.mixedlocalopts():
            raise MPILocalOptsMixed('Cannot mix different local options for different executables or blocks of MPI ranks in impi')
        if arg.threads==MIXED_VALUES:
            raise MPIThreadsMixed('Cannot mix different thread counts for different executables or blocks of MPI ranks in impi')


        extra_args=[]

        if kwargs.get('label_io',False):
            extra_args.append('-l')

        if arg.nranks()==1 and allranks:
            arglist=[ a for a in arg.to_arglist(
                    pre=[self.mpirun_path]+extra_args,
                    before=['-np','%d'%self.total_tasks],
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
            return produtil.prog.Runner(
                [self.mpirun_path]+extra_args+['-np','%s'%(arg.nranks()),self.mpiserial_path],
                    pre=[self.mpirun_path]+extra_args,   # command is mpirun
                    before=['-np','%(n)d'], # pass env, number of procs is kw['n']
                    between=[':']) # separate commands with ':'
        else:
            arglist=[ a for a in arg.to_arglist(
                    pre=[self.mpirun_path]+extra_args,   # command is mpirun
                    before=['-np','%(n)d'], # pass env, number of procs is kw['n']
                    between=[':']) ] # separate commands with ':'
            return produtil.prog.Runner(arglist)
