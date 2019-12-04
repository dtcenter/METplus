
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

import logging
import produtil.fileop

##@var __all__
# An empty list that indicates no symbols are exported by "from
# produtil.mpi_impl import *"
__all__=[]

##@var detectors
# Mapping from MPI implementation name to its detection function
# 
# A mapping from MPI implementation name to a class static method that
# detects that implementation.  When detection succeeds, the function
# should return an instance of the class.  Otherwise, it should return
# None.  The function must have at least these two optional arguments
# and must be able to discard any other optional arguments:
#
#  - logger --- a logging.Logger object for log messages
#  - force --- if True, the detector must succeed and return
#              an Implementation that has suitable defaults.
#              This is used to generate mpi execution commands
#              outside the job that will run them.
detectors=dict()

##@var synonyms
# Allows multiple names for the same MPI implementation.  For example,
# "moab_cray" is an alias for "lsf_cray_intel"
synonyms=dict()

##@var detection_list
# Order in which MPI implementations should be detected.  
#
# Used when automatically detecting the MPI implementation.  This is a
# list of implementation names (keys in the detectors dict).  The first
# matching implementation is used.
detection_order=list()

##@var no_implementation
# The special implementation object that is used when no implementation is avalable.
no_implementation=None

def add_implementation(clazz):
    """!Adds an MPI implementation class to the list of
    implementations to detect.

    Adds this implementation to the module-level detectors and
    detection_order.  The class must have the following static
    methods:

    * name - the name of the class
    * detect - a function that detects the implementation

    @see produtil.mpi_impl.detectors for more information

    @param class a class that implements the name and detect functions"""
    name=clazz.name()
    detectors[name]=clazz.detect
    detection_order.append(name)
    for synonym in clazz.synonyms():
        synonyms[synonym]=name

##@var NO_NAME
# Special value for the get_mpi() mpi_name to indicate the mpi_name
# argument was not set.  Do not modify.
NO_NAME=object()

def register_implementations(logger=None):
    """!Adds all known MPI implementations to the list for get_mpi
    detection.

    @warning This is part of the internal implementation of get_mpi()
    and should never be called directly.

    Loops over all MPI implementation modules inside produtil.mpi_impl
    and adds each one to the list of MPI implementations.  Also adds
    the special "no implementation" fallback from
    produtil.mpi_impl.no_mpi.

    @see produtil.mpi_impl.no_implementation
    @see produtil.mpi_impl.get_mpi"""

    if logger is None: logger=logging.getLogger('mpi_impl')

    # IMPLEMENTATION NOTE: The "import" statements in this function
    # must NOT be at the module level.  This is because the submodules
    # of mpi_impl need to use produtil.run, but produtil.run must
    # import the mpi_impl package.  Hence, initialization of the
    # mpi_impl module-level variables, from mpi_impl submodules, has
    # to happen inside this function.

    # First, add the "no implementation" implementation.  This must be
    # done first to ensure this function is not called twice when the
    # implementation-specific code fails.  That is needed because
    # no_implementation=None is used to detect if
    # register_implementations was called.
    global no_implementation
    import produtil.mpi_impl.no_mpi
    no_implementation=produtil.mpi_impl.no_mpi.Implementation.detect()

    # Now add each implementation.  We need to wrap each around a
    # try...except so that NCEP Central Operations can delete the
    # unused produtil.mpi_impl.* modules without breaking produtil.run
    # functionality.

    try:
        # If we have srun, and we're in a pack group...
        import produtil.mpi_impl.srun_pack_groups
        add_implementation(produtil.mpi_impl.srun_pack_groups.Implementation)
    except ImportError as e: 
        # Some projects prefer to suppress this log message.
        # Temp comment out until this can be addressed properly.
        #logger.info('srun: cannot import: %s'%(str(e),))
        pass

    try:
        # This must be after the pack group case.
        # If we have srun and SLURM resources...
        import produtil.mpi_impl.srun
        add_implementation(produtil.mpi_impl.srun.Implementation)
    except ImportError as e: 
        # Some projects prefer to suppress this log message.
        # Temp comment out until this can be addressed properly.
        #logger.info('srun: cannot import: %s'%(str(e),))
        pass

    try:
        import produtil.mpi_impl.inside_aprun
        add_implementation(produtil.mpi_impl.inside_aprun.Implementation)
    except ImportError as e: 
        # Some projects prefer to suppress this log message.
        # Temp comment out until this can be addressed properly.
        #logger.info('inside_aprun: cannot import: %s'%(str(e),))
        pass

    try:
        import produtil.mpi_impl.lsf_cray_intel
        add_implementation(produtil.mpi_impl.lsf_cray_intel.Implementation)
    except ImportError as e: 
        # Some projects prefer to suppress this log message.
        # Temp comment out until this can be addressed properly.
        #logger.info('lsf_cray_intel: cannot import: %s'%(str(e),))
        pass

    try:
        import produtil.mpi_impl.impi
        add_implementation(produtil.mpi_impl.impi.Implementation)
    except ImportError as e: 
        # Some projects prefer to suppress this log message.
        # Temp comment out until this can be addressed properly.
        #logger.info('impi: cannot import: %s'%(str(e),))
        pass

    try:
        import produtil.mpi_impl.mpirun_lsf
        add_implementation(produtil.mpi_impl.mpirun_lsf.Implementation)
    except ImportError as e: 
        #logger.info('mpirun_lsf: cannot import: %s'%(str(e),))
        pass

    try:
        import produtil.mpi_impl.mpiexec_mpt
        add_implementation(produtil.mpi_impl.mpiexec_mpt.Implementation)
    except ImportError as e: 
        # Some projects prefer to suppress this log message.
        # Temp comment out until this can be addressed properly.
        #logger.info('mpiexec_mpt: cannot import: %s'%(str(e),))
        pass

    try:
        import produtil.mpi_impl.mpiexec
        add_implementation(produtil.mpi_impl.mpiexec.Implementation)
    except ImportError as e: 
        # Some projects prefer to suppress this log message.
        # Temp comment out until this can be addressed properly.
        #logger.info('mpiexec: cannot import: %s'%(str(e),))
        pass

def get_mpi(mpi_name=NO_NAME,force=False,logger=None,**kwargs):
    """!Selects a specified MPI implementation, or automatically
    detects the currently available one.

    @warning This is an internal implementation function that should
    never be called directly.  Use produtil.run.get_mpi() instead.

    @param mpi_name Optional: the name of the desired MPI
    implementation, or None to request running without MPI.

    @param force if True, and mpi_name is given, the MPI
    implementation will be used even if it is not available on the
    current machine.  Note that if the name is not recognized, this
    function will still raise an exception even if force=True.
    Default is False.

    @param logger a logging.Logger for messages.

    @param kwargs Optional: additional keyword arguments to pass to
    the MPI implementation detection functions.

    @raise NotImplementedError if the MPI implementation is unknown,
    or if the implementation is unavailble on this machine, and
    force=False"""

    if logger is None:
        logger=logging.getLogger('mpi_impl')

    # Initialize this module if we have not done so already:
    if no_implementation is None:
        register_implementations()

    # Handle the case where the caller explicitly selected no MPI.
    if mpi_name is None:
        return no_mpi.Implementation.detect(
            force=force,logger=logger,**kwargs)

    # Handle the case of a specified implementation.  We try to use
    # that implementation,
    if mpi_name is not NO_NAME:
        if mpi_name in synonyms:
            mpi_name=synonyms[mpi_name]
        if mpi_name not in detectors:
            raise NotImplementedError('The selected MPI implementation "%s" '
                                      'is unknown.'%(mpi_name,))
        detector=detectors[mpi_name]
        impl=detector(force=force,logger=logger,**kwargs)
        if impl is None:
            raise NotImplementedError('The selected MPI implementation "%s" '
                                      'is not available.'%(mpi_name,))
        return impl

    # Finally, handle the case where auto-detection is requested:
    for name in detection_order:
        detect=detectors[name]
        result=None
        try:
            result=detect(
                force=force,logger=logger,**kwargs)
        except (Exception,
                produtil.fileop.FileOpError,
                produtil.prog.ExitStatusException) as ee:
            # Ignore exceptions related to an inability to detect the
            # MPI implementation.  We assume the issue has already
            # been logged, and we move on to the next implementation's
            # detection function.

            # Some projects prefer to suppress this log message.
            # Temp comment out until this can be addressed properly.
            #logger.info('%s: not detected: %s'%(
            #        name,str(ee)))
            pass
        if result:
            # Detection succeeded.
            return result
    return no_mpi.Implementation.detect(
        force=force,logger=logger,**kwargs)
