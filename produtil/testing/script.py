"""!Takes an object tree from produtil.parse.Parser and turns it into
a flat bash script that will run the entire test suite, one test at a
time."""

import io
 
__all__=['bash_functions','BashRunner']

import produtil.testing.parsetree
from produtil.testing.utilities import PTParserError

##@var bash_functions
# Utility functions for bash scripts.

bash_functions=r'''
function report_start() {
  local parent
  parent=$( dirname "$1" )
  for x in 1 2 3 4 5 6 7 8 9 0 ; do
    if [[ ! -d "$parent" ]] ; then
      mkdir -p "$parent" || true
    fi
  done
  rt__TEST_REPORT_FILE="$1"
  rt__TEST_SUCCESS="YES"
  shift 1
  echo "$*" > "$rt__TEST_REPORT_FILE"
  date >> "$rt__TEST_REPORT_FILE"
}

function report_line() {
  echo "$*" >> "$rt__TEST_REPORT_FILE"
}

function report_stdin() {
  cat >> "$rt__TEST_REPORT_FILE"
}

function report_failure() {
  echo "$*" >> "$rt__TEST_REPORT_FILE"
  rt__TEST_SUCCESS=NO
}

function report_finish() {
  if [[ "$rt__TEST_SUCCESS" == "YES" ]] ; then
    echo "TEST PASSED AT $( date )" >> "$rt__TEST_REPORT_FILE"
  else
    echo "TEST FAILED AT $( date )" >> "$rt__TEST_REPORT_FILE"
    exit 1
  fi
}

function deliver_file() {
  local src tgt parent
  set -e
  src="$1"
  tgt="$2"
  if [[ -d "$src" ]] ; then
    tgt=$( echo "$tgt" | sed 's,/*$,,g' )
    rm -rf "$tgt"
    cp -rp "$src" "$tgt"
  else
    # If the tgt is a directory, place the source within.
    # If the tgt does not exist, but appears to be the name of a
    # directory, make that directory and place the source within.
    #    /path/to/dirname/  <-- ends with /
    #    /path/to/place/.   <-- . is always a directory
    #    /path/to/place/..  <-- .. is always a directory
    if [[  -d "$tgt"                               || \
         ! -e "$tgt" && "${tgt: -1}" == /          || \
         ! -e "$tgt" && "$( basename $tgt )" == .  || \
         ! -e "$tgt" && "$( basename $tgt )" == .. ]] ; then
      tgt="$tgt"/$( basename "$src" )
    fi
    parent=$( dirname "$tgt" )
    if [[ ! -d "$parent" ]] ; then
      mkdir -p "$parent"
    fi
    tmpfile="$tgt.$$.$RANDOM.$RANDOM"
    cp -fp "$src" "$tmpfile"
    mv -fT "$tmpfile" "$tgt"
  fi
}
function comparison_wrapper() {
  local src tgt bn result origtgt
  set -e
  set +x
  cmd="$1"
  message="$2"
  src="$3"
  tgt="$4"
  if [[ -d "$tgt" ]] ; then
    bn=$( basename "$src" )
    tgt="$tgt/$bn"
  elif [[ -d "$src" ]] ; then
    bn=$( basename "$tgt" )
    src="$src/$bn"
  fi
  echo TARGET: $( md5sum $tgt )
  ls -l $tgt
  echo SOURCE: $( md5sum $src )
  ls -l $src
  set +e
  if [[ ! -e "$src" ]] ; then
    report_failure "$tgt: MISSING BASELINE FILE"
    return 1
  elif [[ ! -e "$tgt" ]] ; then
    report_failure "$src: MISSING OUTPUT FILE"
    return 1
  fi
  set -x
  $cmd "$src" "$tgt"
  result=$?
  if [[ "$result" != 0 ]] ; then
    report_failure "$src: $message MISMATCH"
  else
    report_line "$src: $message identical"
  fi
  return $result
}

function bitcmp() {
  comparison_wrapper cmp "bit-for-bit" "$1" "$2"
  result=$?
  return $result
}

function nccmp_vars() {
  comparison_wrapper "nccmp -d" "NetCDF variable data" "$1" "$2"
  result=$?
  return $result
}

function atparse {
    set +x # There is too much output if "set -x" is on.
    set +u # We expect empty variables in this function.
    set +e # We expect some evals to fail too.
    # Use __ in names to avoid clashing with variables in {var} blocks.
    local __text __before __after __during
    for __text in "$@" ; do
        if [[ $__text =~ ^([a-zA-Z][a-zA-Z0-9_]*)=(.*)$ ]] ; then
            eval "local ${BASH_REMATCH[1]}"
            eval "${BASH_REMATCH[1]}="'"${BASH_REMATCH[2]}"'
        else
            echo "ERROR: Ignoring invalid argument $__text\n" 1>&2
        fi
    done
    while IFS= read -r __text ; do
        while [[ "$__text" =~ ^([^@]*)(@\[[a-zA-Z_][a-zA-Z_0-9]*\]|@\[\'[^\']*\'\]|@\[@\]|@)(.*) ]] ; do
            __before="${BASH_REMATCH[1]}"
            __during="${BASH_REMATCH[2]}"
            __after="${BASH_REMATCH[3]}"
#            printf 'PARSE[%s|%s|%s]\n' "$__before" "$__during" "$__after"
            printf %s "$__before"
            if [[ "$__during" =~ ^@\[\'(.*)\'\]$ ]] ; then
                printf %s "${BASH_REMATCH[1]}"
            elif [[ "$__during" == '@[@]' ]] ; then
                printf @
            elif [[ "$__during" =~ ^@\[([a-zA-Z_][a-zA-Z_0-9]*)\] ]] ; then
                set -u
                eval 'printf %s "$'"${BASH_REMATCH[1]}"'"'
                set +u
            else
                printf '%s' "$__during"
            fi
            if [[ "$__after" == "$__text" ]] ; then
                break
            fi
            __text="$__after"
        done
        printf '%s\n' "$__text"
    done
}
'''

class ProdutilRunner(produtil.testing.parsetree.Context):
    """!Uses produtil.run to generate an mpirun command from a
    produtil.testing.parsetree.SpawnProcess object"""
    def __init__(self,scopes,token,run_mode,logger,MPI,nodesize):
        """!Constructor

        @param scopes a list of nested scopes to search when resolving
        variable references (outermost first)
        @param token The token indicating the relevant file and line number
        @param run_mode produtil.testing.utilities.EXECUTION to
            execute and verify results, or
            produtil.testing.utilities.BASELINE to generate a new
            baseline.
        @param logger a logging.Logger for logging messages"""
        super(ProdutilRunner,self).__init__(
            scopes,token,run_mode,logger)
        MPI=MPI.lower()
        
        # Convert from common synonyms:
        if MPI=='lsf':      MPI='mpirun_lsf'
        if MPI=='lsfcray':  MPI='lsf_cray_intel'   # alias for Rocoto lsfcray
        if MPI=='mpich':    MPI='impi'
        if MPI=='lsf_impi': MPI='impi'
        if MPI=='mvapich2': MPI='mpiexec'
        if MPI=='moab':     MPI='moab_cray'        # alias for Rocoto moab

        self.mpiimpl=produtil.run.make_mpi(
            MPI,total_tasks=nodesize,nodesize=nodesize,force=True,silent=True)
    def mpirunner(self,spawnProcess,distribution):
        """!Generates the mpi launching command for the given
        produtil.testing.parsetree.SpawnProcess object

        @param spawnProcess a description of the process to execute
        @returns a string containing the mpirun command"""
        cmd=None
        is_mpi=False
        mpiimpl=self.mpiimpl
        for rank in spawnProcess.iterrank():

            ranks=rank.ranks(self)
            ppn=rank.ppn(self)
            threads=rank.threads(self)

            if cmd is not None and not ranks:
                raise PTParserError('Error: mixing MPI and non-MPI programs in the same command is not supported.')
        
            args=[ arg.string_context(self) for arg in rank.args ]

            if ranks:
                cmdpart=produtil.run.mpi(args[0])
                cmdpart=cmdpart[args[1:]]
                is_mpi=True
            else:
                cmdpart=produtil.run.exe(args[0],mpiimpl=mpiimpl)
                cmdpart=cmdpart[args[1:]]

            if ranks and ppn:
                cmdpart=cmdpart.rpn(ppn)
            
            if threads:
                cmdpart=produtil.run.openmp(cmdpart,threads=threads,mpiimpl=mpiimpl)

            if ranks:
                cmdpart=cmdpart*ranks

            if cmd is None:
                cmd=cmdpart
            else:
                cmd=cmd+cmdpart

        if is_mpi:
            cmd=produtil.run.mpirun(cmd,mpiimpl=mpiimpl,label_io=True,scheduler_distribution=distribution)
        return cmd.to_shell()

class MPICHRunner(produtil.testing.parsetree.Context):
    """!Generates an mpirun command for running in MPICH, from a
    produtil.testing.parsetree.SpawnProcess object"""
    def __init__(self,scopes,token,run_mode,logger):
        """!Constructor

        @param scopes a list of nested scopes to search when resolving
        variable references (outermost first)
        @param token The token indicating the relevant file and line number
        @param run_mode produtil.testing.utilities.EXECUTION to
            execute and verify results, or
            produtil.testing.utilities.BASELINE to generate a new
            baseline.
        @param logger a logging.Logger for logging messages"""
        super(MPICHRunner,self).__init__(
            scopes,token,run_mode,logger)
    def mpirunner(self,spawnProcess,distribution):
        """!Generates the mpirun command for the given
        produtil.testing.parsetree.SpawnProcess object

        @param spawnProcess a description of the process to execute
        @returns a string containing the mpirun command"""
        out=io.StringIO()
        out.write('mpirun')
        for rank in spawnProcess.iterrank():
            out.write(' -np %d %s'%(
                    rank.ranks(self),
                    ' '.join([r.bash_context(self)
                              for r in rank.args])))
        ret=out.getvalue()
        out.close()
        return ret

class LSFRunner(produtil.testing.parsetree.Context):
    """!Generates an mpirun.lsf command for running within IBMPE and
    LSF, from a produtil.testing.parsetree.SpawnProcess object"""
    def __init__(self,scopes,token,run_mode,logger):
        """!Constructor

        @param scopes a list of nested scopes to search when resolving
        variable references (outermost first)
        @param token The token indicating the relevant file and line number
        @param run_mode produtil.testing.utilities.EXECUTION to
            execute and verify results, or
            produtil.testing.utilities.BASELINE to generate a new
            baseline.
        @param logger a logging.Logger for logging messages"""
        super(LSFRunner,self).__init__(
            scopes,token,run_mode,logger)
    def mpirunner(self,spawnProcess,distribution):
        """!Generates the mpirun.lsf command for the given
        produtil.testing.parsetree.SpawnProcess object

        @param spawnProcess a description of the process to execute
        @returns a string containing the mpirun.lsf command"""
        prior=None
        for rank in spawnProcess.iterrank():
            prog=' '.join([r.bash_context(self)
                           for r in rank.args])
            if prior is not None and prior!=prog:
                raise NotImplementedError(self.error(
                        'MPMD is not yet supported for LSF.'))
        return 'mpirun.lsf '+prog

def runner_context_for(con):
    """!Returns a context with an mpirunner(spawnProcess,distribution) function,
    such as the LSFRunner or MPICHRunner classes.

    @param con the context to use when resolving "plat%MPI" to get the
    requested MPI implementation.

    @returns A Context whose mpirunner() function can create MPI
    program launcher commands. """
    MPI=con.scopes[-1].resolve('plat%MPI').string_context(con)
    nodesize=con.scopes[-1].resolve('plat%cores_per_node').numeric_context(con)
    return ProdutilRunner(con.scopes,con.token,con.run_mode,con.logger,MPI,nodesize)

class BashRunner(object):
    """!Generates self-contained bash scripts that can run an entire test suite."""
    def __init__(self):
        """!Constructor for RocotoRunner.

        Initializes the object so that make_runner() will be able to
        function properly.  Presently, this function does nothing."""
        super(BashRunner,self).__init__()
    def make_runner(self,parser,output_file,dry_run=False,
                    setarith=None):
        """!Creates a bash script for the given arguments.

        @param parser The produtil.testing.parse.Parser containing all
        needed information.  This is used to get the list of runnable
        tasks and builds, the sets of tasks and builds, and all
        configuration information.

        @param output_file The name of the file to write.  This file
        will contain the bash script.

        @param dry_run If True, the make_runner only logs what is to
        be done without actually doing it.

        @param setarith Optional: a string recognized by
        produtil.testing.setarith.arithparse().  This is used to
        generate the list of Tasks and Builds to run.  If no setarith
        is given, all Tests and Builds with "run" blocks are run."""
        logger=parser.logger
        runset=parser.setarith(setarith)
        logger.info('%s: generate bash script'%(output_file,))
        if dry_run: return
        with open(output_file,'wt') as out:
            out.write(r'''#! /usr/bin/env bash

%s

set -xe

'''%(bash_functions,))

            seen=False
            for runcon in runset:
                runme,con=runcon.as_tuple
                seen=True
                out.write(runme.bash_context(runner_context_for(con)))
                out.write("\n\n")
        if not seen:
            raise ValueError('ERROR: No "run" statments seen; nothing to do.\n');
