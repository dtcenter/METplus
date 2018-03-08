## @namespace produtil.mpi_impl.inside_aprun
# Adds support for running serial programs when one is inside an aprun
# execution.
#
# This module is part of the mpi_impl package -- see produtil.mpi_impl
# for details.  This implements execution of serial programs when one
# is inside an aprun execution.

import os, socket, logging
import produtil.fileop,produtil.prog,produtil.mpiprog,produtil.pipeline

from .mpi_impl_base import MPIMixed, MPIDisabled, OpenMPDisabled, ImplementationBase

class Implementation(ImplementationBase):
    """Adds support for running serial programs when one is inside an aprun
    execution.

    This module is part of the mpi_impl package -- see produtil.mpi_impl
    for details.  This implements execution of serial programs when one
    is inside an aprun execution."""
    
    @staticmethod
    def name():
        return 'inside_aprun'

    @staticmethod
    def detect(logger=None,force=False,**kwargs):
        if logger is None:
            logger=logging.getLogger('mpi_impl')
        detected=force
        if not force:
            inside_aprun=os.environ.get('INSIDE_APRUN','0')
            inside_aprun=int(inside_aprun)
            if not inside_aprun:
                raise ValueError('INSIDE_APRUN is not set or is 0')
        return Implementation(logger)

    def runsync(self,logger=None):
        """!Runs the "sync" command as an exe()."""
        if logger is None: logger=self.logger
        sync=produtil.prog.Runner(['/bin/sync'])
        p=produtil.pipeline.Pipeline(sync,capture=True,logger=logger)
        version=p.to_string()
        status=p.poll()

    def openmp(self,arg,threads):
        """!When more than one thread is requested, this raises
        OpenMPDisabled to indicate OpenMP is not allowed.
        
        @param arg An produtil.prog.Runner or
        produtil.mpiprog.MPIRanksBase object tree
        @param threads the number of threads, or threads per rank, an
        integer"""
        if threads is not None:
            threads=int(threads)
            if threads!=1:
                raise OpenMPDisabled("You cannot start a new OpenMP program from within an aprun invocation.")
    
    def mpirunner(self,arg,**kwargs):
        """!Raises an exception to indicate MPI is not supported
        @param arg,kwargs Ignored."""
        raise MPIDisabled('You cannot start a new MPI program from within an aprun invocation.')

    def can_run_mpi(self):
        """!Returns False to indicate MPI is not supported."""
        return False

    def make_bigexe(self,exe,**kwargs): 
        """!Returns an ImmutableRunner that will run the specified program.
        @returns an empty list
        @param exe The executable to run on compute nodes.
        @param kwargs Ignored."""
        return produtil.prog.ImmutableRunner([str(exe)],**kwargs)
