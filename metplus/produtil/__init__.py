##@namespace produtil
# Platform-independent weather and ocean forecasting utility package.
#
# @anchor produtil_overview
# The produtil package is a general production weather and ocean
# forecasting utility package.  It implements a number of classes and
# functions needed to implement a reliable, cross-platform weather or
# ocean forecasting system.  This package is entirely
# model-independent: nothing in it is specific to, or reliant on, the
# HWRF model.
#
# Note that before you use anything in this module, you must first
# call the produtil.setup.setup() function, and that function should
# only be called once per process.  Generally this is done at the top
# of the main program.
#
# @section file_and_prod_manip File and Product Manipulation
#
# There are a number of file and directory manipulation routines in
# the produtil package.  In many cases, these replace Python standard
# library routines that either have known bugs or lack logging
# functionality.  If a function exists in produtil and the Python
# standard library, it is best to use the produtil version to avoid
# Python's bugs.
# 
# * produtil.fileop --- Many simple routines to manipulate files and
#   directories.  Works around many Python bugs and adds logging to
#   file manipulation routines.
# * produtil.acl --- A wrapper around libacl.  This is used by the
#   produtil.fileop.deliver_file() to copy access control lists (ACLs)
# * produtil.cd --- Two classes to implement safe cd-in-cd-out blocks
#   using the Python "with" construct.  Also implements temporary 
#   directories and deletion of pre-existing directories if requested.
# * produtil.locking --- File locking that works around Lustre, GPFS
#   and Panasas bugs.
# * produtil.retry --- Retry operations.
# * produtil.rstprod --- Handle NOAA restricted data requirements.
# * produtil.dbn_alert --- Trigger DBNet alerts.
# * produtil.datastore --- A database and product tracking.
# * produtil.atparse --- A simple text preparser.
#
# @section prog_exec Program Execution
#
# The produtil package has flexible, shell-like syntaxes for
# specifying program execution, including complex MPI execution with
# multiple executables.  Most critically, this package works around a
# bug in Python's subprocess module, which forgets to close pipes
# after a fork() call, causing deadlocks in multi-stage pipelines.
# That bug renders Python's subprocess module worthless for complex
# pipelines.  The produtil.run does not suffer from that problem.
#
# * produtil.run --- shell-like syntax for running programs, including
#   a cross-platform way of requesting MPI and OpenMP program
#   execution.  
# * produtil.prog, produtil.mpiprog --- Object tree that underlies the
#   produtil.run implementation.
# * produtil.mpi_impl --- Contains one module for each MPI implementation
#   supported by produtil.
# * produtil.pipeline --- Launches and monitors processes for produtil.run.
#
# You should never need to access the mpi_impl or pipeline modules
# directly, and you should only need the prog and mpiprog modules for
# type checking.  (For example, is my argument a
# produtil.prog.ImmutableRunner?)  In nearly all cases, you can use
# the produtil.run functions to access the full functionality of all
# of the program execution modules.
#
# @section other_utils Other Utilities
# 
# * produtil.setup --- Contains the produtil.setup.setup() function, which
#   initializes the entire produtil package.  
# * produtil.log --- Initialization of the logging module.  Sets up 
#   logging to match what is required in the NCEP production environment.
#   This is highly configurable (as is the Python logging module).
# * produtil.sigsafety --- raises an exception on fatal signals,
#   instead of causing an immediate uncontrolled exit.  This is connected
#   to the produtil.locking module to work around bugs in Lustre, 
#   Panasas and GPFS file locking.
# * produtil.rusage --- monitor and limit process resource usage
# * produtil.batchsystem --- Query information about the batch system and 
#   current batch job.
# * produtil.cluster --- Query information about the cluster.

version='4.1'
