#! /usr/bin/env python

import logging, os
import produtil.setup
import produtil.run
from produtil.run import run, checkrun, exe, mpirun, mpi, alias, \
    ExitStatusException, runstr

# Initialize produtil.  The arguments I send are not necessary, but
# they do make the output more elegant.
produtil.setup.setup(
    send_dbn=False,       # eliminate two "I can't find dbn_alert" warnings
    jobname="example")    # Set the name of the job

logger=logging.getLogger('my/logging/domain')

logger.info('hello world examples')
logger.info('single argument to echo')
run(exe("echo")["hello world"]) # prints => hello world

logger.info('two arguments to echo')
run(exe("echo")["hello","world"]) # prints => hello world

logger.info('generate command step-by-step')
cmd=exe("echo")
for s in [ "hello", "world" ]:
    cmd=cmd[s]
run(cmd) # prints => hello world

logger.info('pass environment variables to sh')
cmd=exe("sh")['-c','$COMMAND $ENVAR1 $ENVAR2'].env(
    COMMAND='echo', ENVAR1='hello', ENVAR2='world')
run(cmd) # runs sh to print => hello world

logger.info('send a string to cat')
mytext='hello world\n'
run(exe('cat') << mytext) # prints => hello world

logger.info('send a file to cat')
with open('hello_world.txt','wt') as f:
    f.write('hello world\n')
run(exe('cat') < 'hello_world.txt')

logger.info('capture a string and print it')
hello_world = runstr(exe('echo')['hello world'])
logger.info('printed => %s'%(hello_world.strip(),))

logger.info( 'true/false exit status examples')

# "checkrun" example.  This will raise an exception if the program fails
for progname in [ '/bin/true', '/bin/false' ]:
    try:
        checkrun(exe(progname))
        logger.info('%s: Success! Rejoice! Exit status 0!'%(progname,))
    except ExitStatusException as ese:
        returncode=ese.returncode
        logger.error('OHNO! OHNO! %s returncode is %d'%(progname,returncode))

logger.info('logging examples with serial programs')

logger=logging.getLogger('example/domain')
run(exe('echo')['hello world'],logger=logger)
# prints => hello world
# but logs the execution of the program and the exit status

## Now we add logging.  Let's run a program that exits with status 3
run(exe("sh")['-c','echo will exit 3 ; exit 3'],logger=logger)

logger.info('mpi examples.  NOTE: this will fail unless you are in a batch job')

## MPI example, without logging.  I'm going to pretend "echo" is an
## MPI program.  If you had a real MPI program, then you would replace
## the initial cmd= line.

cmd=mpi('echo')['hello world'] * 24 # 24 ranks of echo hello world
cmd=mpirun(cmd) # convert to local machine's MPI execution syntax
print 'will run '+cmd.to_shell() # just for fun, print the command it will execute
run(cmd)

# MPMD example: twelve ranks each of "echo hello world" and
# "echo goodbye world".  This time, we'll use the logging
# functionality so produtil will print what it is going to do.
cmd=mpi('echo')['hello world'] * 12 + mpi('echo')['goodbye world'] * 12
cmd=mpirun(cmd,logger=logger)
run(cmd,logger=logger)
