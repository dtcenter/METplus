##@namespace produtil.mpi_impl.mpirun_lsf
# Adds LSF+IBMPE support to produtil.run
#
# This module is part of the produtil.mpi_impl package.  It underlies
# the produtil.run.openmp, produtil.run.mpirun , and
# produtil.run.mpiserial functions, providing the implementation
# needed to run with LSF combined with the IBMPE MPI implementation.
# It may work with other MPI implementations connected to LSF, as long
# as they use mpirun.lsf to launch MPI programs.
#
# @note Unlike other MPI implementations, LSF does not allow changing of the
#  number of MPI ranks used when running an MPI program.  You can only run
#  on all provided ranks, or one rank.  Hence the TOTAL_TASKS variable used
#  elsewhere in produtil, is ignored here.
import os, socket, logging, StringIO
import produtil.fileop,produtil.prog,produtil.mpiprog,produtil.pipeline

from .mpi_impl_base import MPIMixed,CMDFGen,ImplementationBase, \
                           MPIThreadsMixed,MPILocalOptsMixed
from produtil.mpiprog import MIXED_VALUES

class Implementation(ImplementationBase):
    """Adds LSF+IBMPE support to produtil.run

    This module is part of the produtil.mpi_impl package.  It underlies
    the produtil.run.openmp, produtil.run.mpirun , and
    produtil.run.mpiserial functions, providing the implementation
    needed to run with LSF combined with the IBMPE MPI implementation.
    It may work with other MPI implementations connected to LSF, as long
    as they use mpirun.lsf to launch MPI programs.

    @note Unlike other MPI implementations, LSF does not allow changing of the
    number of MPI ranks used when running an MPI program.  You can only run
    on all provided ranks, or one rank.  Hence the TOTAL_TASKS variable used
    elsewhere in produtil, is ignored here."""


    ##@var mpirun_lsf_path
    # Path to the mpirun.lsf program, or None if it isn't found.
    
    @staticmethod
    def name():
        return 'mpirun_lsf'

    @staticmethod
    def detect(mpirun_lsf_path=None,mpiserial_path=None,logger=None,force=False,silent=False,**kwargs):
        if logger is None:
            logger=logging.getLogger('mpi_impl')
        if mpirun_lsf_path is None:
            if force:
                mpirun_lsf_path='mpirun.lsf'
            else:
                mpirun_lsf_path=produtil.fileop.find_exe(
                    'mpirun.lsf',raise_missing=True)
        return Implementation(mpirun_lsf_path,mpiserial_path,logger,silent,force)

    def __init__(self,mpirun_lsf_path,mpiserial_path,logger,silent,force):
        super(Implementation,self).__init__(logger)
        self.mpirun_lsf_path=mpirun_lsf_path
        if mpiserial_path or force:
            self.mpiserial_path=mpiserial_path
        self.silent=silent

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
                arg.env(OMP_NUM_THREADS=threads)
        else:
            del arg.threads
        return arg
   
    def can_run_mpi(self):
        """!Does this module represent an MPI implementation? Returns True."""
        return True
    
    def make_bigexe(self,exe,**kwargs): 
        """!Returns an ImmutableRunner that will run the specified program.
        @returns an empty list
        @param exe The executable to run on compute nodes.
        @param kwargs Ignored."""
        return produtil.prog.ImmutableRunner([str(exe)],**kwargs)
    
    def info(self,message,logger=None):
        if logger is None: logger=self.logger
        if not self.silent:
            logger.info(message)
    
    def mpirunner(self,arg,allranks=False,logger=None,**kwargs):
        """!Turns a produtil.mpiprog.MPIRanksBase tree into a produtil.prog.Runner
        @param arg a tree of produtil.mpiprog.MPIRanksBase objects
        @param allranks if True, and only one rank is requested by arg, then
          all MPI ranks will be used
        @param logger a logging.Logger for log messages
        @param kwargs passed to produtil.mpi_impl.mpi_impl_base.CMDFGen
          when mpiserial is in use.
        @returns a produtil.prog.Runner that will run the selected MPI program
        @note LSF does not support modifying the number of MPI ranks
          to use when running a program.  You can only use all provided
          ranks, or one rank."""
        if logger is None:
            logger=logging.getLogger('mpirun_lsf')

        if arg.mixedlocalopts():
            raise MPILocalOptsMixed('Cannot mix different local options for different executables or blocks of MPI ranks in mpirun_lsf')
        if arg.threads==MIXED_VALUES:
            raise MPIThreadsMixed('Cannot mix different thread counts for different executables or blocks of MPI ranks in mpirun_lsf')

        assert(isinstance(arg,produtil.mpiprog.MPIRanksBase))
        (serial,parallel)=arg.check_serial()
        threads=arg.threads
        if not arg.threads:
            threads=1
        sthreads='%d'%threads
    
        more_env={}
        if kwargs.get('label_io',False):
            more_env={'MP_LABELIO':'yes'}
    
        if serial and parallel:
            raise MPIMixed(
                'Cannot mix serial and parallel MPI ranks in the same '
                'MPI program.')
        if arg.nranks()==1 and allranks:
            arglist=[ a for a in arg.to_arglist(
                    pre=[self.mpirun_lsf_path],
                    before=[],
                    between=[])]
            return produtil.prog.Runner(arglist) \
                .env(OMP_NUM_THREADS=sthreads,MKL_NUM_THREADS='1') \
                .env(**more_env)
        elif arg.nranks()==1:
            # Hack to get LSF to run only one MPI rank.  Tested on NCEP
            # WCOSS supercomputer and approved by its IBM support staff.
            host=socket.gethostname()
            runner=produtil.prog.Runner(
                [ a for a in arg.to_arglist(
                        pre=[self.mpirun_lsf_path],
                        before=[], between=[]) ])
            runner=runner.env(
                LSB_PJL_TASK_GEOMETRY="{(0)}",LSB_HOSTS=host,
                LSB_MCPU_HOSTS=host+" 1", LSB_DJOB_NUMPROC='1',
                LSB_MAX_NUM_PROCESSORS='1',MP_TASK_AFFINITY='core')
            if logger is not None:
                self.info(
                    'Using a hack to work around an LSF bug and run a one core '
                    'program: '+repr(runner))
            return runner
        elif allranks:
            raise MPIAllRanksError(
                "When using allranks=True, you must provide an mpi program "
                "specification with only one MPI rank (to be duplicated "
                "across all ranks).")
        elif serial:
            lines=[a for a in arg.to_arglist(to_shell=True,expand=True)]
            runner=produtil.prog.Runner([self.mpirun_lsf_path,self.mpiserial_path],
                                        prerun=CMDFGen('serialcmdf',lines,
                                                       cmd_envar='SCR_CMDFILE',
                                                       model_envar='SCR_PGMMODEL',
                                                       silent=self.silent,
                                                       **kwargs))
            return runner.env(OMP_NUM_THREADS=sthreads,MKL_NUM_THREADS='1') \
                         .env(**more_env)
        else:        
            lines=[a for a in arg.to_arglist(to_shell=True,expand=True)]
            runner=produtil.prog.Runner([self.mpirun_lsf_path],
                                        prerun=CMDFGen('mpirun_lsf_cmdf',lines,
                                                       cmd_envar='MP_CMDFILE',
                                                       model_envar='MP_PGMMODEL',
                                                       silent=self.silent,
                                                       **kwargs))
            return runner.env(OMP_NUM_THREADS=sthreads,MKL_NUM_THREADS='1') \
                         .env(**more_env)
    
    
