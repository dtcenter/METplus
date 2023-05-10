##@namespace produtil.mpi_impl.mpi_impl_base
# Utilities like CMDFGen to simplify adding new MPI implementations to the 
# produtil.run suite of modules.
#
# This module contains classes and functions to assist developers in
# extending the functionality of the produtil.mpi_impl package.  The
# main highlight is the CMDFGen, which generates command files.  Some
# MPI implementations, and the mpiserial program, want to read a file
# with one line per MPI rank telling what program to run on each rank.
# For example, LSF+IBMPE and LoadLeveler+IBMPE work this way if one
# wants to run different programs on different ranks.

import tempfile,stat,os, logging, io, re

import produtil.prog
import produtil.pipeline
from produtil.prog import shbackslash

module_logger=logging.getLogger('produtil.mpi_impl')

def guess_total_tasks(logger=None,silent=False):
    result=guess_total_tasks_impl(logger,silent)
    if logger and not silent:
        logger.info('Total tasks in this job: %s'%(repr(result),))
    return result

def guess_total_tasks_impl(logger,silent):
    total_tasks=os.environ.get('TOTAL_TASKS','')
    if total_tasks: return int(total_tasks,0)
    pbs_np=os.environ.get('PBS_NP','')
    pbs_num_ppn=os.environ.get('PBS_NUM_PPN','')
    if not pbs_np:
        raise KeyError('TOTAL_TASKS')
    np=int(pbs_np,10)
    if not pbs_num_ppn:
        return np
    ppn=int(pbs_num_ppn,10)
    if ppn<2:
        # workaround for Theia/Jet issue.  Not ideal
        cpus=set()
        cpu_cores=None
        with open('/proc/cpuinfo','rt') as cpuinfo:
            for line in cpuinfo:
                if line.find('physical id')>=0:
                    cpus.add(line.strip())
                m=re.search(r'cpu cores\s+:\s+(\d+)',line)
                if m:
                    cpu_cores=int(m.group(1),10)
        if not cpus or not cpu_cores:
            raise KeyError('TOTAL_TASKS')
        ppn=len(cpus)*cpu_cores
        if logger and not silent:
            logger.info('%d cpus with %d physical cores each = %d physical cores per node'%(
                    len(cpus),cpu_cores,ppn))
    return np*ppn

class MPIError(Exception):
    """!Base class of all exceptions related to launching MPI programs."""
class MPIMissingEnvironment(MPIError):
    """!Raised when the environment variables related to the MPI implementation are missing."""
class MPIEnvironmentInvalid(MPIError):
    """!Raised when the environment variables related to the MPI implementation are contain invalid data."""
class MPIConfigError(MPIError): 
    """!Base class of MPI configuration exceptions."""
class MPITooManyRanks(MPIError):
    """!Raised when the program requests more ranks than are available."""
class WrongMPI(MPIConfigError): 
    """!Unused: raised when the wrong MPI implementation is accessed.  """
class MPISerialMissing(MPIConfigError):
    """!Raised when the mpiserial program is required, but is missing."""
class MPIAllRanksError(MPIConfigError):
    """!Raised when the allranks=True keyword is sent to mpirun or mpirunner,
but the MPI program specification has more than one rank."""
class MPIMixed(MPIConfigError):
    """!Thrown to indicate serial and parallel processes are being mixed in a single mpi_comm_world."""
class MPILocalOptsMixed(MPIConfigError):
    """!Raised to indicate different MPI ranks have different local options, and that is not supported by the MPI implementation."""
class MPIThreadsMixed(MPIConfigError):
    """!Raised to indicate different MPI ranks have different numbers of threads, and that is not supported by the MPI implementation."""
class MPIDisabled(MPIConfigError):
    """!Thrown to MPI is not supported."""
class OpenMPDisabled(MPIConfigError):
    """!Raised when OpenMP is not supported by the present implementation."""
    
class ImplementationBase(object):
    """!Abstract base class for all MPI implementations.  Default
    implementations for all functions represent a situation where no
    MPI implementation is available."""
    def __init__(self,logger=None):
        if logger is None:
            logger=logging.getLogger('produtil.mpi_impl')
        self.logger=logger
        self._mpiserial_path=None

    @staticmethod
    def synonyms():
        """!Iterates over alternative names for this MPI implementation, such
        as the names of other MPI implementations this class can handle."""
        return
        yield 'xyz' # trick to ensure this is an iterator

    def getmpiserial_path(self):
        if not self._mpiserial_path:
            self._mpiserial_path=self.find_mpiserial(None,False)
        if not self._mpiserial_path:
            raise MPISerialMissing('Cannot find the mpiserial program.')
        return self._mpiserial_path

    def setmpiserial_path(self,value):
        self._mpiserial_path=self.find_mpiserial(value,True)

    def find_mpiserial(self,mpiserial_path,force):
        if force:
            if not mpiserial_path:
                mpiserial_path='mpiserial'
            return mpiserial_path

        if not mpiserial_path:
            mpiserial_path=os.environ.get('MPISERIAL','')

        if not mpiserial_path or \
           not os.path.exists(mpiserial_path) or \
           not os.access(mpiserial_path,os.X_OK):
            mpiserial_path=produtil.fileop.find_exe(
                'mpiserial',raise_missing=False)

        if not mpiserial_path or \
           not os.path.exists(mpiserial_path) or \
           not os.access(mpiserial_path,os.X_OK):
           return None

        return mpiserial_path

    ##@property mpiserial_path
    # Path to the mpiserial program

    mpiserial_path=property(getmpiserial_path,setmpiserial_path,None,
      """Path to the mpiserial program""")

    def runsync(self,logger=None):
        """!Runs the "sync" command as an exe()."""
        if logger is None: logger=self.logger
        sync=produtil.prog.Runner(['/bin/sync'])
        p=produtil.pipeline.Pipeline(sync,capture=True,logger=logger)
        version=p.to_string()
        status=p.poll()
    def openmp(self,arg,threads):
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
    def mpirunner(self,arg,**kwargs):
        """!Raises an exception to indicate MPI is not supported
        @param arg,kwargs Ignored."""
        raise MPIDisabled('This job cannot run MPI programs.')
    def can_run_mpi(self):
        """!Returns False to indicate MPI is not supported."""
        return False
    def make_bigexe(self,exe,**kwargs): 
        """!Returns an ImmutableRunner that will run the specified program.
        @returns an empty list
        @param exe The executable to run on compute nodes.
        @param kwargs Ignored."""
        return produtil.prog.ImmutableRunner([str(exe)],**kwargs)
    
    
class CMDFGen(object):
    """!Generates files with one line per MPI rank, telling what
    program to run on each rank.

    This class is used to generate command files for mpiserial, poe or
    mpirun.lsf.  Command files are files with one MPI rank per line
    containing a shell command to run for that rank.  Generally the
    input (lines) is generated by the to_arglist function in a
    subclass of produtil.mpiprog.MPIRanksBase.  See the
    produtil.mpi_impl.mpirun_lsf for an example of how to use this."""
    def __init__(self,base,lines,cmd_envar='SCR_CMDFILE',
                 model_envar=None,filename_arg=False,
                 silent=False,filename_option=None,
                 next_prerun=None,**kwargs):
        """!CMDFGen constructor
        
        @param base type of command file being generated.  See below.
        @param lines the command file contents as a list of strings, one per line
        @param cmd_envar environment variable to set to the command file path
        @param model_envar environment variable to set to "MPMD" 
        @param kwargs Sets the command file name.  See below.
        @param filename_arg If True, the name of the command file is appended to the program argument list.
        @param filename_option A string or None.  If filename_arg is true, this string is appended before the filename_arg

        The command file is generated from
        tempfile.NamedTemporaryFile, passing several arguments from
        kwargs, if provided, or suitable defaults otherwise.  There
        are several arguments used.  In all cases, replace "base" with
        the contents of the @c base argument:

        * base_suffix --- temporary file suffix (default: "base.")
        * base_prefix --- temporary file prefix (default: ".cmdf")
        * base_tempdir --- directory in which to create the file

        @bug The base_suffix keyword is used for both the suffix and prefix"""
        assert(base is not None)
        assert(isinstance(lines,list))
        assert(len(lines)>0)
        assert(isinstance(lines[0],str))
        assert(len(lines[0])>0)
        self.filename=kwargs.get(str(base),None)
        self.tmpprefix=kwargs.get('%s_suffix'%(base,),'%s.'%(base,))
        self.tmpsuffix=kwargs.get('%s_suffix'%(base,),'.cmdf')
        self.tmpdir=kwargs.get('%s_tmpdir'%(base,),'.')
        self.cmd_envar=cmd_envar
        self.model_envar=model_envar
        self.filename_arg=filename_arg
        self.filename_option=filename_option
        self.silent=bool(silent)
        self.next_prerun=next_prerun
        out='\n'.join(lines)
        if len(out)>0:
            out+='\n'
        self.cmdf_contents=out
        return
    ##@var filename
    # command file's filename

    ##@var tmpprefix 
    # temporary file prefix
    
    ##@var tmpsuffix
    # temporary file suffix

    ##@var tmpdir
    # temporary file directory

    ##@var cmd_envar
    # Environment variable to set telling the path to the
    # command file

    ##@var model_envar
    # Environment variable to set to "MPMD"

    ##@var cmdf_contents
    # String containing the command file contents.

    def info(self,message,logger=None):
        if logger is None: logger=self.logger
        if not self.silent:
            logger.info(message)

    def _add_more_vars(self,envars,logger):
        """!Adds additional environment variables to the envars dict,
        needed to configure the MPI implementation correctly.  This is
        used to set MP_PGMMODEL="MPMD" if the constructor receives
        model_envar="MP_PGMMODEL".

        @param envars[out] the dict to modify
        @param logger a logging.Logger for log messages"""
        if self.model_envar is not None:
            self.info('Set %s="MPMD"'%(self.model_envar,),logger)
            envars[self.model_envar]='MPMD'

    def __call__(self,runner,logger=None):
        """!Adds the environment variables to @c runner and creates the command file.

        @param[out] runner A produtil.prog.Runner to modify
        @param logger a logging.Logger for log messages"""
        if logger is None: logger=module_logger
        if self.filename is not None:
            with open(self.filename,'wt') as f:
                f.write(self.cmdf_contents)
            if logger is not None:
                self.info('Write command file to %s'%(repr(filename),),logger)
            kw={self.cmd_envar: self.filename}
            self._add_more_vars(kw,logger)
            if logger is not None:
                for k,v in kw.items():
                    self.info('Set %s=%s'%(k,repr(v)),logger)
            if self.filename_arg:
                if filename_option:
                    runner=runner[self.filename_option]
                runner=runner[self.filename]
            result=runner.env(**kw)
        else:
            with tempfile.NamedTemporaryFile(mode='wt',suffix=self.tmpsuffix,
                    prefix=self.tmpprefix,dir=self.tmpdir,delete=False) as t:
                if logger is not None:
                    self.info('Write command file to %s'%(repr(t.name),),logger)
                t.write(self.cmdf_contents)
                # Make the file read-only and readable for everyone:
                os.fchmod(t.fileno(),stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH)
                kw={self.cmd_envar: t.name}
                self._add_more_vars(kw,logger)
                if logger is not None:
                    for k,v in kw.items():
                        self.info('Set %s=%s'%(k,repr(v)),logger)
                runner.env(**kw)
                if self.filename_arg:
                    if isinstance(self.filename_option,str):
                        runner=runner[str(self.filename_option)]
                    runner=runner[os.path.realpath(t.name)]
            result=runner
        if self.next_prerun is not None:
            return self.next_prerun(result)

    def to_shell(self,runner,logger=None):
        """!Adds the environment variables to @c runner and generates
        shell code that would create the command file.

        @param[out] runner A produtil.prog.Runner to modify
        @param logger a logging.Logger for log messages
        @returns a tuple containing shell code and the modified runner"""
        if logger is None: logger=module_logger
        sio=io.StringIO()
        filename=self.filename
        if filename is None:
            filename='tempfile'
        bsfilename=shbackslash(filename)

        sio.write('cat /dev/null >%s\n'%(bsfilename,))
        prior=None
        count=0
        for line in self.cmdf_contents.splitlines():
            if not count:
                prior=line
                count=1
            elif prior!=line:
                if count>1:
                    sio.write('for n in $( seq 1 %d ) ; do echo %s ; done >> %s\n'%(
                            count,shbackslash(line),bsfilename))
                else:
                    sio.write('echo %s >> %s\n'%(shbackslash(line),bsfilename))
                prior=line
                count=1
            else:
                count+=1
        if count>0:
            if count>1:
                sio.write('for n in $( seq 1 %d ) ; do echo %s ; done >> %s\n'%(
                        count,shbackslash(line),bsfilename))
            else:
                sio.write('echo %s >> %s\n'%(shbackslash(line),bsfilename))

        kw={self.cmd_envar: filename}
        self._add_more_vars(kw,logger)
        if logger is not None:
            for k,v in kw.items():
                self.info('Set %s=%s'%(k,repr(v)),logger)
        if self.filename_arg:
            runner=runner[filename]
        runner=runner.env(**kw)
        text=sio.getvalue()
        sio.close()
        return text, runner
