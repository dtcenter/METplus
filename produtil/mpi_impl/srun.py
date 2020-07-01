##@namespace produtil.mpi_impl.srun 
# Adds SLURM srun support to produtil.run
#
# This module is part of the mpi_impl package -- see produtil.mpi_impl
# for details.  This translates produtil.run directives to SLURM srun
# commands.

import os, logging, re
import produtil.fileop,produtil.prog,produtil.mpiprog,produtil.pipeline

from .mpi_impl_base import MPIMixed,CMDFGen,ImplementationBase, \
                           MPIThreadsMixed,MPILocalOptsMixed,MPITooManyRanks
from produtil.pipeline import NoMoreProcesses
from produtil.mpiprog import MIXED_VALUES

class Implementation(ImplementationBase):
    """Adds SLURM srun support to produtil.run
    
    This module is part of the mpi_impl package -- see produtil.mpi_impl
    for details.  This translates produtil.run directives to SLURM srun
    commands."""

    ##@var srun_path
    # Path to the srun program
    
    @staticmethod
    def name():
        return 'srun'

    @staticmethod
    def detect(srun_path=None,mpiserial_path=None,logger=None,force=False,silent=False,scontrol_path=None,**kwargs):
        """!Detects whether the SLURM srun command is available by
        looking for it in the $PATH.  Also requires the SLURM_NODELIST
        variable.  This is to detect the case where srun is available,
        but no slurm resources are available."""
        if srun_path is None:
            if force:
                srun_path='srun'
            else:
                srun_path=produtil.fileop.find_exe('srun',raise_missing=True)
        if scontrol_path is None:
            if force:
                scontrol_path='scontrol'
            else:
                scontrol_path=produtil.fileop.find_exe('scontrol',raise_missing=True)
        if 'SLURM_NODELIST' not in os.environ and not force:
            return None
        return Implementation(srun_path,scontrol_path,mpiserial_path,logger,silent,force)

    def __init__(self,srun_path,scontrol_path,mpiserial_path,logger,silent,force):
        super(Implementation,self).__init__(logger)
        if mpiserial_path or force:
            self.mpiserial_path=mpiserial_path
        self.srun_path=srun_path
        self.scontrol_path=scontrol_path
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
        assert(arg is not None)
        if threads is not None:
            arg.threads=threads
            return arg.env(OMP_NUM_THREADS=threads,KMP_NUM_THREADS=threads,
                           KMP_AFFINITY='scatter')
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
    
    def mpirunner(self,arg,allranks=False,**kwargs):
        """!Turns a produtil.mpiprog.MPIRanksBase tree into a produtil.prog.Runner
        @param arg a tree of produtil.mpiprog.MPIRanksBase objects
        @param allranks if True, and only one rank is requested by arg, then
          all MPI ranks will be used
        @param kwargs passed to produtil.mpi_impl.mpi_impl_base.CMDFGen
          when mpiserial is in use.
        @returns a produtil.prog.Runner that will run the selected MPI program"""
        f=self.mpirunner_impl(arg,allranks=allranks,**kwargs)
        if not self.silent:
            logging.getLogger('srun').info("%s => %s"%(repr(arg),repr(f)))
        return f

    def _get_available_nodes(self):
        available_nodes=list()
        nodeset=set()
        scontrol=produtil.prog.Runner([
            self.scontrol_path,'show','hostnames',
            os.environ['SLURM_NODELIST']])
        p=produtil.pipeline.Pipeline(
            scontrol,capture=True,logger=self.logger)
        nodelist=p.to_string()
        status=p.poll()
        for line in nodelist.splitlines():
            node=line.strip()
            if not node: next
            if node in nodeset: next
            nodeset.add(node)
            available_nodes.append(node)
        return available_nodes
    
    def mpirunner_impl(self,arg,allranks=False,rewrite_nodefile=True,**kwargs):
        """!This is the underlying implementation of mpirunner and should
        not be called directly."""
        assert(isinstance(arg,produtil.mpiprog.MPIRanksBase))
        (serial,parallel)=arg.check_serial()
        if serial and parallel:
            raise MPIMixed('Cannot mix serial and parallel MPI ranks in the '
                           'same MPI program.')
    

        if arg.mixedlocalopts():
            raise MPILocalOptsMixed('Cannot mix different local options for different executables or blocks of MPI ranks in impi')
        if arg.threads==MIXED_VALUES:
            raise MPIThreadsMixed('Cannot mix different thread counts for different executables or blocks of MPI ranks in impi')


        srun_args=[self.srun_path,'--export=ALL','--cpu_bind=core']
    
        if arg.nranks()==1 and allranks:
            srun_args.append('--distribution=block:block')
            arglist=[ str(a) for a in arg.to_arglist(
                    pre=srun_args,before=[],between=[])]
            return produtil.prog.Runner(arglist)
        elif allranks:
            raise MPIAllRanksError(
                "When using allranks=True, you must provide an mpi program "
                "specification with only one MPI rank (to be duplicated across "
                "all ranks).")
        elif serial:
            srun_args.append('--distribution=block:block')
            arg=produtil.mpiprog.collapse(arg)
            lines=[str(a) for a in arg.to_arglist(to_shell=True,expand=True)]
            return produtil.prog.Runner(
                [self.srun_path,'--ntasks','%s'%(arg.nranks()),self.mpiserial_path],
                prerun=CMDFGen('serialcmdf',lines,silent=self.silent,**kwargs))
        else:
            cmdfile=list()
            irank=0

            if rewrite_nodefile:
                nodefile=list()
                available_nodes=self._get_available_nodes()
                slurm_ppn_string=os.environ['SLURM_JOB_CPUS_PER_NODE'].strip()
                trim_extra=re.sub(r'^(\d+)(?:\(.*\))?',r'\1',slurm_ppn_string)
                node_size=int(trim_extra,10)
                remaining_nodes=list(available_nodes)

            for rank,count in arg.expand_iter(expand=False):
                if count<1: next
                cmdfile.append('%d-%d %s'%(irank,irank+count-1,rank.to_shell()))
                irank+=count
                if rewrite_nodefile:
                    rpn=max(min(node_size,rank.rpn()),1)
                    need_nodes=max(1,(count+rpn-1)//rpn)
                    if need_nodes>len(remaining_nodes):
                        raise MPITooManyRanks('Request is too large for %d nodes of size %d: %s'%(
                            len(available_nodes),node_size,repr(arg)))

                    # Split ranks evenly among nodes:
                    min_rpn=count//need_nodes
                    nodes_with_extra_rank=count-need_nodes*min_rpn
                    for n in range(need_nodes):
                        this_node_rpn=min_rpn
                        if n<nodes_with_extra_rank:
                            this_node_rpn+=1
                        nodefile.extend([remaining_nodes[n]] * this_node_rpn)

                    # Remove the nodes we used:
                    remaining_nodes=remaining_nodes[need_nodes:]

            srun_args.extend(['--ntasks',str(irank)])

            prerun=CMDFGen(
                'srun_cmdfile',cmdfile,filename_arg=True,silent=self.silent,
                filename_option='--multi-prog',**kwargs)

            if rewrite_nodefile:
                srun_args.extend(['--distribution','arbitrary'])
                prerun=CMDFGen(
                    'srun_nodefile',nodefile,filename_arg=True,
                    silent=self.silent,filename_option='--nodelist',
                    next_prerun=prerun,**kwargs)

            return produtil.prog.Runner(srun_args,prerun=prerun)
