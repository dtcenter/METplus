#! /usr/bin/env python

import produtil.setup
from produtil.run import *

produtil.setup.setup(send_dbn=False)

impi=make_mpi('impi',total_tasks=48,force=True)
mpiexec=make_mpi('mpiexec',total_tasks=48,nodesize=24,force=True,silent=True)
lsf_cray_intel=make_mpi(
    'lsf_cray_intel',total_tasks=48,nodesize=24,aprun_path='aprun',
    hyperthreads=1,p_state_turbo=2601000,force=True,silent=True)
inside_aprun=make_mpi('inside_aprun',force=True)
mpiexec_mpt=make_mpi('mpiexec_mpt',total_tasks=24,force=True,silent=True)
mpirun_lsf=make_mpi('mpirun_lsf',force=True,silent=True)
srun=make_mpi('srun',force=True,silent=True)
no_mpi=make_mpi(None,force=True)

def mpiserial_ls_10(mpiimpl):
    world='ls -l * 10 in mpiserial'
    cmd=mpiserial(exe('ls',mpiimpl=mpiimpl)['-l'])
    cmd=cmd*10
    cmd=mpirun(cmd,mpiimpl)
    return world,cmd

def world_n140_n50t2(mpiimpl):
    world=mpi('prog1')*140+openmp(mpi('prog2')*50,threads=2,mpiimpl=mpiimpl)
    mpirunner=mpirun(world,mpiimpl=mpiimpl,label_io=True)
    return world,mpirunner

def world_n1000(mpiimpl):
    world=mpi('prog1')*1000
    mpirunner=mpirun(world,mpiimpl=mpiimpl,label_io=True)
    return world,mpirunner

def world_loop_n1000(mpiimpl):
    world=mpi('prog1')
    for i in xrange(999):
        world+=mpi('prog1')
    mpirunner=mpirun(world,mpiimpl=mpiimpl,label_io=True)
    return world,mpirunner

def allranks(mpiimpl):
    world=mpi('prog1')
    mpirunner=mpirun(world,mpiimpl=mpiimpl,label_io=True,allranks=True)
    return world,mpirunner

def runsync(mpiimpl):
    world='runsync'
    mpiimpl.runsync()
    return world,'SUCCESS'

def exe_hello_world(mpiimpl):
    cmd=exe('/bin/echo',mpiimpl=mpiimpl)['hello','world']
    return '/bin/echo hello world - serial',cmd

def omp_hello_world(mpiimpl):
    cmd1=exe('/bin/echo',mpiimpl=mpiimpl)['hello','world']
    cmd2=openmp(cmd1,mpiimpl=mpiimpl,threads=24)
    return '/bin/echo hello world - 24 threads',cmd2

for worlder in [ exe_hello_world, allranks, world_n140_n50t2, world_n1000, world_loop_n1000 ]:
    first=True
    print '------------------------------------------------------------------------'
    for mpiimpl in [ lsf_cray_intel, impi, mpiexec, mpiexec_mpt, \
                     mpirun_lsf, srun, inside_aprun, no_mpi ]:
        try:
            (world,mpirunner) = worlder(mpiimpl)
            if first:
                print 'COMMAND: %s'%(repr(world),)
                print
                first=False
            if isinstance(mpirunner,str):
                cmd=mpirunner
            else:
                cmd=mpirunner.to_shell()
            if cmd.find('\n')<0:
                print '%20s ==> %s'%(mpiimpl.name(),cmd)
            else:
                pre=mpiimpl.name()
                arrow='==>'
                for line in cmd.splitlines():
                    print '%20s %s %s'%(pre,arrow,line)
                    pre=' '
                    arrow='   '
        except Exception as e:
            print '%20s (E) %s'%(
                mpiimpl.name(),str(e))
