##@namespace produtil.mpi_impl.no_mpi
# Stub funcitons to allow produtil.mpi_impl  to run when MPI is unavailable.
#
# This module is part of the produtil.mpi_impl package.  It underlies
# the produtil.run.openmp, produtil.run.mpirun , and
# produtil.run.mpiserial functions, providing the implementation
# needed to run when MPI is unavailable.

import os, logging
import produtil.prog,produtil.pipeline
from .mpi_impl_base import MPIDisabled
module_logger=logging.getLogger('lsf_cray_intel')

def runsync(logger=None):
    """!Runs the "sync" command as an exe()."""
    if logger is None: logger=module_logger
    sync=produtil.prog.Runner(['/bin/sync'])
    p=produtil.pipeline.Pipeline(sync,capture=True,logger=logger)
    version=p.to_string()
    status=p.poll()
def openmp(arg,threads):
    """!Does nothing.  This implementation does not support OpenMP.

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
def mpirunner(arg,**kwargs):
    """!Raises an exception to indicate MPI is not supported
    @param arg,kwargs Ignored."""
    raise MPIDisabled('This job cannot run MPI programs.')
def can_run_mpi():
    """!Returns False to indicate MPI is not supported."""
    return False
def make_bigexe(exe,**kwargs): 
    """!Returns an ImmutableRunner that will run the specified program.
    @returns an empty list
    @param exe The executable to run on compute nodes.
    @param kwargs Ignored."""
    return produtil.prog.ImmutableRunner([str(exe)],**kwargs)

