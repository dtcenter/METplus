
##@namespace produtil.mpi_impl
# Converts a group of MPI ranks to a runnable command.
#
# @section produtil_mpi_impl_overview Produtil MPI Implementation
#
# This package and its submodules implement execution of externals MPI
# programs.  This package is not intended to be used directly, instead
# one should use produtil.run.  This package appears to the outside to
# be a module that implements a common interface to various local MPI
# implementations.  This is done by automatically detecting which MPI
# implementation is in use, and then importing the entire contents of
# the corresponding sub-module of produtil.mpi_impl.  See the submodules
# for details on each implementation:
#
# *   produtil.mpi_impl.mpiexec --- MPICH or public MPVAPICH2
# *   produtil.mpi_impl.impi --- Intel MPI
# *   produtil.mpi_impl.mpiexec_mpt --- SGI MPT
# *   produtil.mpi_impl.mpirun_lsf --- LSF wrapped around IBMPE
# *   produtil.mpi_impl.no_mpi --- For a purely serial environment.
#
# @section produtil_mpi_impl_subroutines Subroutines Imported from Implementation Modules
#
# The following subroutines are imported from one of those modules.
# They are added to the mpi_impl package level to make the mpi_impl
# look identical to the underlying implementation module:
#
# *   openmp(arg,threads) - given a Runner, set it up to use OpenMP
#       If threads is provided, it is the number of threads to use.
#       Otherwise, no thread count is specified and it is assumed
#       that the underlying OpenMP implementation will use the 
#       correct number.
#
# *   can_run_mpi() - does this computer support running MPI programs?
#
# *   bigexe_prepend(arg,**kwargs) - Modifies an executable to run on a
#       compute node instead of the batch node.  This is intended for
#       future support of the Cray architecture, where the batch script
#       runs on a batch node, and must call "aprun" to execute a program
#       on a remote compute node.  This is the function that one would
#       use to prepend "aprun" and its various arguments.  This
#       functionality is not presently tested.
#
# *   mpirunner(arg,allranks=False,**kwargs) - Implementation of
#       produtil.run.mpirun().  Given an object that is a subclass of
#       produtil.mpiprog.MPIRanksBase, construct and return a
#       produtil.prog.Runner that will execute that MPI command.  The
#       allranks=True option requests that the program use all available
#       MPI ranks.  An exception should be raised if the program also
#       requests a specific number of ranks (other than 1).
#
#       There are two different types of MPI programs that mpirunner
#       must handle.  One is MPI execution of non-MPI programs, which
#       the caller requests via produtil.run.mpiserial.  Some MPI
#       implementations support running non-MPI programs directly, while
#       others don't.  The external C program "mpiserial" provides an
#       MPI wrapper program to work around that lack of support.  It is
#       a simple MPI program that directs each rank to execute a shell
#       command.  The other variety of program mpirunner must handle is,
#       of course, MPI programs.  These are differentiated via:
#           (serial,parallel)=arg.check_serial()
#       If serial is true, the program is serial, if parallel is true,
#       the program is parallel.  If both are true, MPIMixed should be
#       raised.
#
#       The mpirunner must also handle the allranks=True vs. False cases.
#       If allranks=True, the caller is requesting that the provided
#       MPI program be run on all available ranks.  If the MPI program
#       also provides a rank specification (detected via arg.nranks()!=1)
#       then the MPI_COMM_WORLD is overspecified and the mpirunner must
#       raise MPIAllRanksError.  
#
# These are the detection routines imported from each submodule, except
# for no_mpi.  The name of the routine is "detect()" in its module, and
# is renamed during import to the package-level namespace:
#
# *   impi_detect() --- returns True if the Intel MPI should be used
#
# *   mpiexec_detect() - returns True if the MPICH or MVAPICH2 MPI
#       should be used
#
# *   mpiexec_mpt_detect() - returns True if the SGI MPT should be used
#
# *   mpirun_lsf_detect() - returns True if LSF IBMPE should be used
#
# @section Adding New MPI Implementations
#
# To implement a new MPI implementation, one must create a new submodule
# of mpi_impl.  It is best to examine the existing modules and mimic
# them when doing this.  Most architectures are similar to either the
# mpirun_lsf (which uses command files) or mpiexec (which provides
# arguments to mpiexec on the command line).  In addition, the external
# program "mpiserial" provides a means by which to execute a list of
# serial programs via an MPI invocation for MPI implementations that do
# not natively support that (such as the problematic SGI MPT).
# Furthermore, some MPI implementations may have bugs or limitations
# that one must work around via setting environment variables (such as
# SGI MPT with its numerous hard-coded limits).  The mpirunner and
# openmp functions should work around those problems.
#
# Note that there are two utilities designed to simplify the
# implementation of a new MPI module:
#
# *   produtil.mpiprog.MPIRanksBase.to_arglist() -- walks the tree of
#       objects automatically generating an mpi invocation command
#       (mpiexec, mpirun, etc.) with arguments, based on a provided set
#       of rules.  This is how the three existing modules make their MPI
#       commands.  It is quite simple to use, and handles the hard work
#       of walking the object tree for you.
#
# *   produtil.mpi_impl.mpi_impl_base.CMDFGen - provides a way of easily
#       writing a command file based on produtil.mpiprog.MPISerial
#       objects.  This is for MPI implementations such as IBMPE that
#       require a file listing the commands to run on each MPI rank.  It
#       is also needed when using mpiserial to execute non-MPI programs
#       under MPI
#
# Once you have a new MPI implementation module, you must edit
# produtil/mpi_impl/__init__.py to detect your MPI implementation and
# correctly import the module.  The produtil/mpi_impl/__init__.py must
# import that module's detect() function, and detect whether the MPI
# implementation should be used.  If it should be, then __init__.py
# must import the relevant symbols from your module into the
# package-level namespace.  There are instructions in the code in
# __init__.py on how to modify it to achieve these steps.

from . import no_mpi

########################################################################
# Import the MPI detection functions from all known modules.  We
# ignore ImportError in case the module is missing (which it will be
# for NCO, who only gets the WCOSS-specific modules).

try:
    from .impi import detect as impi_detect
except ImportError: pass

try:
    from .mpiexec import detect as mpiexec_detect
except ImportError: pass

try:
    from .srun import detect as srun_detect
except ImportError: pass

try:
    from .inside_aprun import detect as inside_aprun_detect
except ImportError: pass

try:
    from .mpiexec_mpt import detect as mpiexec_mpt_detect
except ImportError as e: pass

try:
    from .mpirun_lsf import detect as mpirun_lsf_detect
except ImportError as e: pass

try:
    from .lsf_cray_intel import detect as lsf_cray_intel_detect
except ImportError as e: pass

try:
    from .inside_aprun import detect as inside_aprun_detect
except ImportError as e: pass

########################################################################
# Decide what MPI implementation to use

if 'mpirun_lsf_detect' in dir() and mpirun_lsf_detect():
    from .mpirun_lsf import *
elif 'srun_detect' in dir() and srun_detect():
    from .srun import *
elif 'inside_aprun' in dir() and inside_aprun_detect():
    from .inside_aprun import *
elif 'lsf_cray_intel_detect' in dir() and lsf_cray_intel_detect():
    from .lsf_cray_intel import *
elif 'impi_detect' in dir() and impi_detect():
    from .impi import *
elif 'mpiexec_mpt_detect' in dir() and mpiexec_mpt_detect():
    from .mpiexec_mpt import *
elif 'mpiexec_detect' in dir() and mpiexec_detect():
    from .mpiexec import *
else:
    from .no_mpi import *

##@var __all__
# List of symbols to export by "from produtil.mpi_impl import *"
__all__=['mpirunner','can_run_mpi','bigexe_prepend',
         'guess_maxmpi','guess_nthreads']
