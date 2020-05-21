"""!Implements the produtil.run: provides the object tree for
representing shell commands.

Do not load this module directly except for type checking
(instanceof(o,produtil.prog.Runner)).  It is meant to be used only by
the produtil.run module.  This module is part of the implementation of
a shell-like syntax for running programs.  The rest of the
implementation is in the produtil.run and produtil.pipeline modules.
MPI programs are implemented by the produtil.mpiprog and
produtil.mpi_impl.

This module implements a shell-like syntax of running shell programs
from Python.  This module should not be used directly: the
produtil.run implements critical parts of the functionality.
Specifically, this module implements the Runner and ImmutableRunner
classes.  It also knows how to convert them to
produtil.pipeline.Pipeline objects for actual execution.

* Runner --- This class represents a process that could be run.  It keeps
  track of all possible aspects of running a process, including the
  command, arguments, environment variables, stdout stream, stderr
  stream, stdin stream, and a list of functions or callable objects to
  run before executing the problem.  Provides public functions to modify
  the Runner.

* ImmutableRunner --- A Runner that cannot be changed: when modifying the
  Runner, it returns a new object.  This is to implement shell aliases.
  For example, one could make an ImmutableRunner for program to index
  GRIB2 files.  All the user would have to do is add the GRIB2 file as
  an argument, and capture the output.

Note that the actual work of creating the Runner or ImmutableRunner,
or turning them into Pipeline objects done by the produtil.run module.
Turning MPI programs into Runner objects is done by the
produtil.mpiprog module and produtil.mpi_impl package, with the public
interface in produtil.run.  Hence, nobody would ever load this module
directly, except for type checking (ie.: to see if your argument is a
Runner before passing it to produtil.run.checkrun).."""

import produtil.sigsafety
import io,select,io,re,time,fcntl,os,logging,signal

import produtil.mpi_impl
from produtil.pipeline import launch, manage, PIPE, ERR2OUT

class ProgSyntaxError(Exception): 
    """!Base class of exceptions raised when a Runner is given
    arguments that make no sense."""
class OverspecifiedStream(ProgSyntaxError): 
    """!Raised when one tries to specify the stdout, stderr or stdin to
    go to, or come from, more than one location"""
class MultipleStdin(OverspecifiedStream): 
    """!Raised when the caller specifies more than one source for the
    stdin of a Runner"""
class MultipleStdout(OverspecifiedStream): 
    """!Raised when the caller specifies more than one destination for
    a Runner's stdout"""
class MultipleStderr(OverspecifiedStream):
    """!Raised when the caller specifies more than one destination for
    a Runner's stderr"""
class InvalidPipeline(ProgSyntaxError): 
    """!Raised when the caller specifies an invalid input or output
    when piping a Runner into or out of another object."""

class NotValidPosixSh(Exception): 
    """!Base class of exceptions that are raised when converting a
    Runner or pipeline of Runners to a POSIX sh command, if the Runner
    cannot be expressed as POSIX sh."""
class PrerunNotValidPosixSh(NotValidPosixSh):
    """!Raised when trying to convert a pipeline of Runners to a POSIX
    sh string if the pipeline has a prerun object that lacks a to_shell
    function."""
class NoSuchRedirection(NotValidPosixSh): 
    """!Raised when trying to convert a pipeline of Runners to a POSIX
    sh string, if a redirection in the pipeline cannot be expressed in
    POSIX sh."""
class NotValidPosixShString(Exception): 
    """!Raised when converting a Runner or pipeline of Runners to a
    POSIX sh string.  If a string is sent to a program's stdin, this
    is raised when that string cannot be expressed in POSIX sh."""
class EqualInExecutable(Exception): 
    """!Raised when converting a Runner or pipeline of Runners to a
    posix sh string if a Runner's executable contains an equal ("=")
    sign."""
class EqualInEnv(Exception): 
    """!Raised when converting a Runner or pipeline of Runners to a
    POSIX sh string if there is an equal ("=") sign in an environment
    variable name."""



class InvalidRunArgument(ProgSyntaxError):
    """!Raised to indicate that an invalid argument was sent into one
    of the run module functions."""

class ExitStatusException(Exception):
    """!Raised to indicate that a program generated an invalid return
    code.  

    Examine the "returncode" member variable for the returncode value.
    Negative values indicate the program was terminated by a signal
    while zero and positive values indicate the program exited.  The
    highest exit status of the pipeline is returned when a pipeline is
    used.

    For MPI programs, the exit status is generally unreliable due to
    implementation-dependent issues, but this package attempts to
    return the highest exit status seen.  Generally, you can count on
    MPI implementations to return zero if you call MPI_Finalize() and
    exit normally, and non-zero if you call MPI_Abort with a non-zero
    argument.  Any other situation will produce unpredictable results."""
    ##@var message
    # A string description for what went wrong

    ##@var returncode
    # The return code, including signal information.  

    def __init__(self,message,status):
        """!ExitStatusException constructor
        @param message a description of what went wrong
        @param status the exit status"""
        self.message=message
        self.returncode=status

    @property
    def status(self):
        """!An alias for self.returncode: the exit status."""
        return self.returncode

    def __str__(self):
        """!A string description of the error."""
        return '%s (returncode=%d)'%(str(self.message),int(self.returncode))
    def __repr__(self):
        """!A pythonic description of the error for debugging."""
        return 'NonZeroExit(%s,%s)'%(repr(self.message),repr(self.returncode))



def shvarok(s):
    """!Returns True if the specified environment variable name is a
    valid POSIX sh variable name, and False otherwise.
    @param s an environment variable name"""
    if re.search(r'\A[A-Za-z][A-Za-z0-9_]*\z',s):
        return True
    else:
        return False

def shstrok(s):
    """!Returns True if the specified string can be expressed as a
    POSIX sh string, and false otherwise.
    @param s a string"""
    # Only allow non-whitespace ASCII and space (chr(32)-chr(126)):
    if re.search(r'\A[a-zA-Z0-9 !"#$%&?()*+,./:;<=>?@^_`{|}~\\\]\[\'-]*\Z',s):
        return True
    else:
        return False

def shbackslash(s):
    """!Given a Python str, returns a backslashed POSIX sh string, or
    raises NotValidPosixShString if that cannot be done.
    @param s a string to backslash"""
    s=str(s)
    if not shstrok(s):
        raise NotValidPosixShString('String is not expressable in POSIX sh: %s'%(repr(s),))
    if re.search(r'(?ms)[^a-zA-Z0-9_+.,/-]',s):
        return '"' + re.sub(r'(["\\\\$])',r"\\\1",s) + '"'
    return s

########################################################################

class StreamGenerator(object):
    """!This is part of the internal implementation of Runner, and is
    used to convert it to a produtil.pipeline.Pipeline for execution.
    This is an abstract class whose subclasses create the Popen's
    stdout, stdin and stderr."""  
    def for_input(self):
        """!Has no effect.  This exists only for debugging."""
        return '<unexpected:%s>'%(repr(self),)
    def for_output(self):
        """!Has no effect.  This exists only for debugging."""
        return '<unexpected:%s>'%(repr(self),)
    def repr_for_err(self):
        """!Returns the stderr value.  The default implementation
        returns repr_for_out(), causing stderr to receive whatever
        stdout receives."""
        return self.repr_for_out()

class FileOpener(StreamGenerator):
    """!This is part of the internal implementation of Runner, used to
    convert it to a produtil.pipeline.Pipeline for execution.  It
    represents stdin, stdout or stderr being connected to an open
    file.  It instructs the Runner to open the file before starting
    the process."""
    def __init__(self,filename,mode,err=False):
        """!FileOpener constructor
        @param filename the name of the file being opened
        @param mode how it is being opened
        @param err if True, this is for stderr"""
        self.filename=filename
        self.mode=mode
        self.err=err
    ##@var filename 
    # the name of the file being opened

    ##@var mode
    # how the file is being opened

    ##@var err
    # If True, this is for stderr.

    def copy(self):
        """!Creates a shallow copy of this object."""
        return FileOpener(self.filename,self.mode,self.err)
    def to_shell(self):
        """!Creates a POSIX sh representation of the part of the
        command that requests redirection."""
        more=''
        if self.err:
            more='2'
        if   self.mode=='ab': return '%s>> %s'%(more,shbackslash(self.filename))
        elif self.mode=='wb': return '%s> %s'%(more,shbackslash(self.filename))
        elif self.mode=='rb': return 'cat %s | '%(shbackslash(self.filename),)
        raise NoSuchRedirection('Cannot convert file open mode %s to a '
                                'POSIX sh redirection'%(self.mode,))
    @property 
    def intmode(self):
        """!Returns an integer version of mode suitable for os.open"""
        intmode=None
        assert('r' in 'rb')
        if 'r' in self.mode:
            intmode=os.O_RDONLY
        elif 'w' in self.mode:
            intmode=os.O_WRONLY|os.O_CREAT|os.O_TRUNC
        elif 'a' in self.mode:
            intmode=os.O_WRONLY|os.O_CREAT|os.O_APPEND
        assert(intmode is not None)
        return intmode
    def _gen_stream(self):
        """!Returns a tuple (None,stream,None,True) where "stream" is
        the opened file object."""
        return (None,os.open(self.filename,self.intmode),None,True)
    def __repr__(self):
        """!Returns a string representation of this object as valid
        Python code."""
        return 'FileOpener(%s,%s)'%(repr(self.filename),repr(self.mode))
    def repr_for_in(self):
        """!Part of the implementation of Runner.__repr__, this returns
        the filename and ",string=False"."""
        return repr(self.filename)+',string=False'
    def repr_for_out(self):
        """!Part of the implementation of Runner.__repr__, this returns
        the filename and ",string=False".  It also appends ",append=X"
        where X is the true/false flag for appending to the file."""
        return '%s,append=%s'%(repr(self.filename),repr(self.mode=='ab'))
    def repr_for_err(self): 
        """!Same as repr_for_out."""
        return self.repr_for_out()

class StringInput(StreamGenerator):
    """!Represents sending a string to a process's stdin."""
    def __init__(self,obj):
        """!Creates a StringInput that sends the specified object to
        stdin.
        @param obj the object to send to stdin"""
        self.obj=obj
    ##@var obj
    # the object to send to stdin

    def copy(self):
        """!Returns a shallow copy of this object."""
        return StringInput(self.obj)
    def _gen_stream(self):
        """!Returns a tuple containing (O,None,None,None) where O was
        the object sent to the StringInput constructor."""
        return (self.obj,None,None,None)
    def __repr__(self):
        """!Returns a string representation of this object as valid
        Python code."""
        return 'StringInput(%s)'%(repr(self.obj),)
    def to_shell(self): 
        """!Converts this object, if possible, to an echo command
        followed by a pipe ("|")."""
        return 'echo %s | '%(shbackslash(self.obj))
    def repr_for_in(self):
        """!Part of the implementation of Runner.__repr__.  If
        possible, this creates valid Python code to represent
        specifying sending the given string to the stdin of a Runner.
        If the string is too long, it is abbreviated."""
        if len(self.obj)>40:
            return "%s...,string=True"%(repr(self.obj[0:37]+'...'),)
        else:
            return '%s,string=True'%(repr(self.obj),)

class StreamReuser(StreamGenerator):
    """!Arranges for a stream-like object to be sent to the stdout,
    stderr or stdin of a Runner."""
    def __init__(self,obj):
        """!Creates a StreamReuser for the specified stream-like object.
        @param obj the stream-like object to reuse."""
        self.obj=obj
    ##@var obj
    # the stream-like object to reuse.
    def copy(self):
        """!Returns a shallow copy of this object.  Note that means
        that the underlying stream object is not copied."""
        return StreamReuser(self.obj)
    def to_shell(self):
        """!Raises NotValidPosixSh to indicate that the stream cannot
        be represented as POSIX sh."""
        raise NotValidPosixSh('Python streams cannot be passed to '
                              'remote POSIX sh processes.')
    def _gen_stream(self):
        """!Returns a tuple (None,None,obj,False) where obj is the
        provided stream-like object."""
        return (None,None,self.obj,False)
    def repr_for_in(self):
        """!Returns repr(obj) where obj is the given stream-like
        object."""
        return repr(self.obj)
    def repr_for_out(self):
        """!Returns repr(obj) where obj is the given stream-like
        object."""
        return repr(self.obj)

class OutIsError(StreamGenerator):
    """!Instructs a Runner to send stderr to stdout"""
    def __init__(self):      
        """!OutIsError constructor."""
    def copy(self):
        """!Returns a new OutIsError object."""
        return OutIsError()
    def to_shell(self):      
        """!Returns "2>&1" """
        return '2>&1'
    def _gen_stream(self):
        """!Returns a tuple containing (None,None,pipeline.ERR2OUT,False)"""
        return (None,None,ERR2OUT,False)
    def repr_for_in(self):   
        """!This should never be called.  It returns ".err2out()"."""
        return '.err2out()'
    def repr_for_out(self):  
        """!Part of the representation of Runner.__repr__.  Returns
        ".err2out()" which instructs a Runner to send stderr to
        stdout."""
        return '.err2out()'
    def __eq__(self,other):  
        """!Is the other object an OutIsError?
        @param other the other object to analyze."""
        return isinstance(other,OutIsError)

########################################################################

class Runner(object):
    """!Represents a single stage of a pipeline to execute.

    This is a linked list class used to store information about a
    program or pipeline of programs to be run.  It has the capability
    of converting itself to a Pipeline object (run(Runner)), or
    converting itself to a POSIX sh command (Runner.to_shell()).  Note
    that some commands cannot be represented in POSIX sh, such as
    commands with non-ASCII characters or commands that have Python
    streams as their stdout or stdin.  Those commands can still be run
    with a Pipeline, but trying to convert them to a POSIX sh command
    will throw NotValidPosixSh or a subclass thereof."""
    def __init__(self,args,**kwargs):
        """!Creates a new Runner.  

        The only non-keyword argument can be one of three things:

          1. A Runner to copy.  Every aspect of the Runner that can be
             copied will be.  Note that if a stream-like object is
             connected to stdin, stdout or stderr, it will NOT be
             copied.

          2. A list of strings.  This will be used as the command
             path, and arguments.

        Many options can be set via keyword arguments:

        * clearenv=True - the environment should be cleared before
            running this command.  Any arguments set by the env=
            keyword or the .env(...) member function ignore this.
            Also, PATH, USER, LOGNAME and HOME are retained since
            most programs cannot run without them.

        * env=dict(var=value,...) - a dict of environment variables to
            set before running the Runner.  Does NOT affect this
            parent's process, only the child process.

        * in=filename - a file to send to stdin.

        * instr=str - a string to send to stdin

        * out=filename - a file to connect to stdout.  Will truncate the file.

        * outa=filename - same as "out=filename," but appends to the file.

        * err2out - redirects stderr to stdout

        * err=filename - a file to connect to stderr.  Will truncate the file.

        * erra=filename - same as "err=filename," but appends to the file.

        * prerun=[obj,anotherobj,...] - sent to self.prerun, this is a
            list of functions or callable objects to run before
            executing the process.  The objects are not called until
            execution is requested via self._gen.
        @param args the arguments to the program
        @param kwargs other settings (see constructor description)."""

        self._stdin=self._stdout=self._stderr=self._prev=self._env=None
        self._prerun=self._cd=None
        self._threads=None

        if isinstance(args,Runner):
            r=args # other runner to copy
            self._args=list(r._args)
            if(r._stdin is not None): self._stdin=r._stdin.copy()
            if(r._stdout is not None): self._stdout=r._stdout.copy()
            if(r._stderr is not None): self._stderr=r._stderr.copy()
            if(r._prev is not None): self._prev=r._prev.copy()
            if(r._env is not None): self._env=dict(r._env)
            if(r._prerun is not None): self._prerun=list(r._prerun)
            self._copy_env=r._copy_env
        else:
            if not isinstance(args,list):
                raise TypeError('The args argument must be a list, not a %s %s.'%(
                        type(args).__name__,repr(args)))
            if not isinstance(args[0],str):
                raise TypeError('The first element of args must be a string, not a %s %s.'%(
                        type(args[0]).__name__,repr(args)))
            self._args=args
            self._copy_env=True

        # Initialize environment if requested:
        if 'clearenv' in kwargs and kwargs['clearenv']:   self.clearenv()
        if 'env' in kwargs:                               self._env=dict(kwargs['env'])

        # Initialize input/output/error if requested:
        if 'in' in kwargs:           self<kwargs['in']
        if 'instr' in kwargs:        self<<str(kwargs['instr'])
        if 'out' in kwargs:          self>kwargs['out']
        if 'outa' in kwargs:         self>>kwargs['outa']
        if 'err2out' in kwargs:      self.err2out()
        if 'err' in kwargs:          self.err(kwargs['err'],append=False)
        if 'erra' in kwargs:         self.err(kwargs['erra'],append=True)
        if 'cd' in kwargs:           self.cd(kwargs['cd'])
        
        # Allow a list of "prerun" callables that will be called at
        # the beginning of self._gen:
        if 'prerun' in kwargs:       self.prerun(kwargs['prerun'])

    def getthreads(self):
        """!Returns the number of threads requested by this program."""
        return self._threads
    def setthreads(self,nthreads):
        """!Sets the number of threads requested by this program."""
        self._threads=int(nthreads)
        return self._threads
    def delthreads(self):
        """!Removes the request for threads."""
        self._threads=None

    threads=property(getthreads,setthreads,delthreads,"""The number of threads per rank.""") 

    @property
    def first(self):
        """!Returns the first Runner in this pipeline."""
        if self._prev is None:
            return self
        return self._prev.first

    def remove_prerun(self):
        """!Removes all prerun objects.
        @see prerun()
        @return self"""
        if self._prerun: self._prerun=list()
        return self

    def __prerun_to_shell(self):
        """!Internal implementation function - do not use.

        Applies all prerun objects using their to_shell functions, and
        then clears the prerun list"""
        texts=list()
        for prerun in self._prerun:
            assert(prerun)
            ( text, runner ) = prerun.to_shell(self)
            texts.append(text)
        self._prerun=list()
        return ''.join(texts)

    def prerun(self,arg):
        """!Adds a function or callable object to be called before
        running the program.  

        The callables should be very fast operations, and are executed
        by self._gen when creating the Pipeline.  They take, as an
        argument, the Runner and an optional "logger" keyword argument
        that is either None, or a logging.Logger to use to log
        messages.
        @param arg a callable object that takes self as an argument, and
        an optional keyword argument "logger" with a logging.Logger for
        log messages"""
        if self._prerun is None:
            self._prerun=[arg]
        else:
            self._prerun.append(arg)
        return self
    def _stringify_arg(self,arg):
        """!Returns a string representation of the given argument to
        convert it to an input to produtil.pipeline.Pipeline.
        Conversions:
        * float --- converted via %g
        * int --- converted via %d
        * str --- no conversion; used directly
        * all others --- str(arg)
        @param arg the argument to convert
        @returns a string version of arg"""
        if isinstance(arg,float):
            return '%g'%(arg,)
        elif isinstance(arg,int):
            return '%d'%(arg,)
        elif isinstance(arg,str):
            return arg
        else:
            return str(arg)
    def __getitem__(self,args):
        """!Add one or more arguments to the executable.

        Can ONLY accept strings, ints, floats or iterables (tuple,
        list).  Strings, ints and floats are sent to _stringify_args,
        and the result is added to the end of the list of arguments to
        the command to run.  For iterables (tuple, list), adds all
        elements to the list of arguments, passing each through
        _stringify_args.
        @param args one or more arguments to add
        @returns self"""
        if isinstance(args,str) or isinstance(args,float) \
                or isinstance(args,int):
            self._args.append(self._stringify_arg(args))
        else:
            self._args.extend([self._stringify_arg(x) for x in args])
        return self
    def __str__(self): 
        """!Alias for __repr__()"""
        return self.__repr__()
    def __repr__(self):
        """!Attempts to produce valid Python code to represent this Runnable.
        Generally, that can be done, unless an input string is too
        long, no executable name is present, or a stream is connected
        to a Python object.  In those cases, human-readable
        representations are given, which are not exactly Python
        code.        """
        if self._prev is not None:
            s='%s | '%(repr(self._prev),)
        else:
            s=''
        if len(self._args)==0:
            s+='batchexe(<empty>)'
        else:
            s+='batchexe(%s)'%(repr(self._args[0]))
        if len(self._args)>1:
            s+='['+','.join([repr(x) for x in self._args[1:]])+']'
        if self._stdin is not None:
            s+='.in(%s)'%(self._stdin.repr_for_in(),)
        if self._stdout is not None:
            s+='.out(%s)'%(self._stdout.repr_for_out(),)
        if self._stderr is not None:
            if isinstance(self._stderr,OutIsError):
                s+='.err2out()'
            else:
                s+='.err(%s)'%(self._stderr.repr_for_err(),)
        if not self._copy_env:
            s+='.clearenv()'
        if self._env is not None:
            s+='.env('+(', '.join(['%s=%s'%(k,v) 
                                   for k,v in self._env.items()]))+')'
        if self._prerun is not None:
            s+=''.join(['.prerun(%s)'%(repr(x),) for x in self._prerun])
        if self._cd is not None:
            s+=".cd("+repr(self._cd)+")"
        return s
    
    def __eq__(self,other):
        """!Returns True if the other object is a Runner that is equal
        to this one, and False otherwise.
        @param other the object to compare"""
        if isinstance(other,Runner):
            return self._args==other._args and \
                self._copy_env==other._copy_env and \
                self._stdin==other._stdin and \
                self._stdout==other._stdout and \
                self._stderr==other._stderr and \
                self._env==other._env and \
                self._prerun==other._prerun
        else:
            return NotImplemented

    def isplainexe(self):
        """!Returns true if this is simply an executable with arguments
        (no redirection, no prerun objects, no environment
        modification, no piping), and False otherwise."""
        return self._stdin is None and self._stdout is None and \
            self._prerun is None and self._stderr is None and \
            self._env is None and self._prev is None

    def cd(self,dirpath):
        """!Requests that this process run in the specified directory.
        The directory must already exist before the program starts.
        @param dirpath the directory to cd into, which must already exist.
        @returns self"""
        self._cd=dirpath
        return self
    def __lt__(self,stdin):
        """!Connects the given object to stdin, via inp(stdin,string=False).
        @param stdin the stdin object
        @returns self"""
        return self.inp(stdin,string=False)
    def __gt__(self,stdout): 
        """!Connects the given object to stdout, truncating it if it is
        a file.  Same as out(stdout,append=False).
        @param stdout the stdout object
        @returns self"""
        return self.out(stdout,append=False)
    def __lshift__(self,stdin): 
        """!Sends the specified string into stdin.  Same as
        inp(stdin,string=True).
        @param stdin the stdin file
        @returns self"""
        return self.inp(stdin,string=True)
    def __rshift__(self,stdout): 
        """!Appends stdout to the specified file.  Same as
        out(stdout,append=True).
        @param stdout the stdout file
        @returns self"""
        return self.out(stdout,append=True)
    def __pos__(self): 
        """!Sends stderr to stdout.  Same as err2out().
        @returns self"""
        return self.err2out()
    def __ge__(self,outerr): 
        """!Redirects stderr and stdout to the specified file,
        truncating it.  Same as err2out().out(filename,append=False)
        @param outerr the stdout and stderr file
        @returns self"""
        return self.err2out().out(outerr,append=False)
    def __or__(self,other): 
        """!Pipes this Runner to the other Runner.  Same as pipeto(other).
        @returns other
        @param other the other runner to pipe into"""
        return self.pipeto(other)

    def argins(self,index,arg):
        """!Inserts the specified argument before the given index.

        This function is intended for internal use only.  It is used
        to implement threading on Cray, where arguments relating to
        threading have to be added after the Runner is generated.

        @warning It is generally not safe to call this function
        outside the produtil.mpi_impl subpackage since its modules may
        generate completely different commands than you asked in order
        to execute your requested programs.

        @param arg a string argument to add
        @param index the index to insert before
        @note Index 0 is the executable, while later indices are
        arguments."""
        self._args.insert(index,arg)
        return self

    def args(self):
        """!Iterates over the executable and arguments of this command"""
        for arg in self._args:
            yield arg

    def copy(self,typeobj=None):
        """!Returns a deep copy of this object, almost.  

        If stdin, stdout or stderr are connected to streams instead of
        files or strings, then the streams are not copied.  Instead,
        the exact same stream objects are connected to the same unit
        in the new Runner.
        @param typeobj the type of the new object or None for Runner.
          Do not set this unless you know what you're doing.
        @returns the new object"""
        if typeobj is None: typeobj=Runner
        assert(typeobj is not None)
        r=typeobj(list(self._args))
        r._copy_env=self._copy_env
        if self._stdin  is not None: r._stdin =self._stdin .copy()
        if self._stdout is not None: r._stdout=self._stdout.copy()
        if self._stderr is not None: r._stderr=self._stderr.copy()
        if self._env is not None: r._env=dict(self._env)
        if self._prev is not None: r._prev=self._prev.copy()
        if self._prerun is not None:
            r._prerun=list()
            for p in self._prerun:
                r._prerun.append(p)
        assert(r is not None)
        assert(isinstance(r,typeobj))
        return r

    def copyenv(self):
        """!Instructs this command to duplicate the parent process
        environment (the default).
        @returns self"""
        self._copy_env=True
        return self

    def clearenv(self):
        """!Instructs this command to start with an empty environment
        except for certain critical variables without which most
        programs cannot run.  (Retains PATH, USER, LOGNAME and HOME.)
        @returns self"""
        self._copy_env=False
        self._env={}
        return self

    def _impl_make_env(self):
        """!This internal function generates information about the
        environment variables to be input to this process.  If the
        parent environment is to be passed unmodified, None is
        returned.  Otherwise, this routine returns dict of environment
        variables calculated from os.environ and internal settings.
        @returns the new environment dict"""

        if self._env is None and self._copy_env:
            return None # copy parent process environment verbatim
        env={}
        if self._copy_env:
            env=dict(os.environ)
        else:
            env={}
            for key in ('PATH','USER','LOGNAME','HOME'):
                if key in os.environ:
                    env[key]=os.environ[key]
        if self._env is not None:
            for key in self._env:
                env[key]=self._env[key]
        return env

    def getenv(self,arg):
        if self._env is None:
            raise KeyError(arg)
        return self._env[arg]

    def env(self,**kwargs):
        """!Sets environment variables for this Runner.  The variables
        should be specified as keyword arguments.
        @param kwargs varname=value arguments
        @returns self"""
        if self._env is None:
            self._env={}
        for key in kwargs:
            self._env[str(key)]=str(kwargs[key])
        return self

    def to_shell(self):
        """!Returns a string that expresses this object as a POSIX sh
        shell command if possible, or raises a subclass of
        NotValidPosixSh if not."""

        if self._prerun:
            for prerun in self._prerun:
                if not hasattr(prerun,'to_shell'):
                    raise PrerunNotValidPosixSh(
                        '%s: has a prerun object that cannot be expressed '
                        'as posix sh'%(self._args[0],))
            no_prerun=self.copy()
            text=no_prerun.__prerun_to_shell()
            text+=no_prerun.to_shell()
            return text

        if self._prev is not None:
            s=self._prev.to_shell()+' | '
        elif self._stdin is not None:
            s=self._stdin.to_shell()
        else:
            s=''
        if self._cd is not None:
            s+="( set -e ; cd "+shbackslash(self._cd)+" ; exec "
        if self._env is not None or not self._copy_env:
            if(re.search('=',self._args[0])):
                raise EqualInExecutable(
                    '%s: cannot have an "=" in the executable name when '
                    'modifying the environment.'%(self._args[0],))
            s+='env'
            if not self._copy_env:
                s+=' -i'
            for key in self._env:
                if(re.search('=',key)):
                    raise EqualInEnv('%s: variable name contains an "="'
                                     %(key,))
                s+=' '+shbackslash("%s=%s"%(key,self._env[key]))
            if not self._copy_env:
                for key in ('PATH','USER','LOGNAME','HOME'):
                    if not key in self._env:
                        s+=' "%s=$%s"'%(key,key)
            s+=' '
        s+=' '.join([shbackslash(x) for x in self._args])
        if self._stdout is not None: s+=' '+self._stdout.to_shell()
        if self._stderr is not None: s+=' '+self._stderr.to_shell()
        if self._cd is not None:
            s+=" )"
        return s
    def runner(self):
        """!Returns self if self is modifiable, otherwise returns a
        modifiable copy of self.  This is intended to be used to
        implement unmodifiable subclasses of Runner
        @returns self"""
        return self
    def pipeto(self,other):
        """!Specifies that this Runner will send its stdout to the
        other runner's stdin.  This will raise MultipleStdout if this
        Runner's stdout target is already specified, or MultipleStdin
        if the other's stdin is already specified.
        @param other the runner to pipe into
        @returns other"""
        if not isinstance(other,Runner):
            raise InvalidPipeline(
                'Attempting to pipe a Runner into something that is not '
                'a Runner (likely a syntax error).')
        if other._prev is not None:
            raise MultipleStdin('Attempted to pipe more than one process '
                                'into stdin of the same process')
        if self._stdout is not None:
            raise MultipleStdout('More than one stdout is detected in '
                                 'prog|prog')
        if other._stdin is not None and self._stdin is not None:
            raise MultipleStdin('More than one stdin is detected in '
                                'prog|prog')

        # Get a modifiable copy of the other Runner and pipe to it:
        rother=other.runner()
        rother._prev=self
        if rother._stdin is not None:
            self.inp(rother._stdin)
            rother._stdin=None

        # Return the other object since it is later in the pipeline
        # (this is needed for syntactic reasons):
        return rother

    def inp(self,stdin,string=False):
        """!Specifies that the first Runner in this pipeline takes
        input from the given file or string specified by stdin.  If
        string=True, then stdin is converted to a string via str(),
        otherwise it must be a filename or a stream.  Raises
        MultipleStdin if the stdin source is already specified.
        @param stdin the input file or string
        @param string if True, stdin is a string.  Otherwise, it is a file.
        @returns self"""
        if self._prev is not None:
            self._prev.inp(stdin,string)
            return self
        # ---- to get past here, we have to be the beginning of the pipeline ----
        if self._stdin is not None:
            raise MultipleStdin('More than one stdin detected in Runner.inp')
        if isinstance(stdin,StringInput) or isinstance(stdin,FileOpener) or\
                isinstance(stdin,StreamReuser):
            self._stdin=stdin
        elif(string):
            self._stdin=StringInput(str(stdin))
        else:
            if isinstance(stdin,str):
                self._stdin=FileOpener(str(stdin),'rb')
            else:
                self._stdin=StreamReuser(stdin)
        return self

    def out(self,stdout,append=False):
        """!Specifies that this process sends output from its stdout
        stream to the given file or stream.  The stdout object must be
        a string filename, or a stream.  If append=False, and the
        stdout is a filename, the file will be truncated, if
        append=True then it is appended.  Raises MultipleStdout if the
        stdout location is already specified
        @param stdout the stdout file
        @param append if True, append to the file, otherwise truncate
        @returns self"""
        if self._stdout is not None:
            raise MultipleStdout('More than one stdout detected in call '
                                 'to Runner.out')
        if isinstance(stdout,str):
            if append:
                self._stdout=FileOpener(str(stdout),'ab')
            else:
                self._stdout=FileOpener(str(stdout),'wb')
        else:
            self._stdout=StreamReuser(stdout)
        return self

    def err2out(self):
        """!Sends stderr to stdout
        @returns self"""
        if self._stderr is not None:
            raise MultipleStderr(
                'More than one stderr detected in call to Runner.err')
        self._stderr=OutIsError()
        return self

    def err(self,stderr,append=False):
        """!Specifies that this process sends output from its stderr
        stream to the given file or stream.  The stderr object must be
        a string filename, or a stream.  If append=False, and the
        stderr is a filename, the file will be truncated, if
        append=True then it is appended.  Raises MultipleStderr if the
        stderr location is already specified.
        @param stderr the stderr output file
        @param append if True, append to the file otherwise truncate
        @returns self"""
        if self._stderr is not None:
            raise MultipleStderr(
                'More than one stderr detected in call to Runner.err')
        if isinstance(stderr,str):
            if append:
                self._stderr=FileOpener(str(stderr),'ab',True)
            else:
                self._stderr=FileOpener(str(stderr),'wb',True)
        else:
            self._stderr=StreamReuser(stderr)
        return self

    def _gen(self,pipeline,logger=None,next=None):
        """!Populates a Pipeline object with information from this
        Runner.  This is a recursive function that starts at the last
        element of the pipeline (output element) and walks back to the
        first (input element).  The "next" parameter points to the
        next (output-direction) element of the pipeline.  The optional
        logger parameter is where to send log messages.
        @param[out] pipeline the produtil.pipeline.Pipeline
        @param logger a logging.Logger for log messages
        @param next the next Runner in the pipeline"""

        if self._prev is not None:
            self._prev._gen(pipeline,logger=logger,next=self)
        elif logger is not None:
            logger.debug('GEN %s: recurse to %s'%(
                    repr(self),repr(self._prev)))
        if self._prerun is not None:
            for prerun in self._prerun:
                prerun(self,logger=logger)
        if logger is not None:
            logger.debug('GEN %s: gen to %s with cmd=%s'%(
                    repr(self),repr(pipeline),str(self._args[0])))

        kwargs={}

        if self._stdin is not None:
            (string,stream,send,close)=self._stdin._gen_stream()
            if string is not None: kwargs['instring']=string
            if stream is not None: kwargs['stdin']=stream
            if send is not None: kwargs['sendin']=send
            if close is not None: kwargs['closein']=close
        if self._stdout is not None:
            (string,stream,send,close)=self._stdout._gen_stream()
            assert(string is None)
            if stream is not None: kwargs['stdout']=stream
            if send is not None: kwargs['sendout']=send
            if close is not None: kwargs['closeout']=close
        if self._stderr is not None:
            (string,stream,send,close)=self._stderr._gen_stream()
            assert(string is None)
            if stream is not None: kwargs['stderr']=stream
            if send is not None: kwargs['senderr']=send
            if close is not None: kwargs['closeerr']=close
        if self._env is not None:
            kwargs['env']=self._impl_make_env()
        if logger is not None:
            kwargs['logger']=logger
        pipeline._impl_add(self._args,(next is None),cd=self._cd,**kwargs)

########################################################################

class ImmutableRunner(Runner):
    """!An copy-on-write version of Runner.

    This subclass of Runner is unmodifiable.  It is meant to be used
    for re-usable exe()-like objects.  For example, if one wants an
    object lsl that runs exe('ls')['-l'] with optional extra
    arguments, one could do:

      lsl=ImmutableRunner(Runner('ls')['-l'])

    and then every time one does run(lsl[argument list]), it generates
    a new object without modifying the original lsl, ensuring later
    calls to lsl will have the same effect:

      lsl['/']
      lsl['~']
      lsl['/']  # prints the same as the first

    This is implemented by a copy-on-write method: if a modification
    is requested, a Runner is returned with the requested
    modifications."""
    def __init__(self,args,**kwargs):
        """!Creates a new ImmutableRunner.  All arguments to this
        constructor have the same meanings as the Runner
        constructor.
        @param args,kwargs passed to Runner.__init__"""
        try:
            self._init=True
            Runner.__init__(self,args,**kwargs)
            if self._prev is not None:
                self._prev=ImmutableRunner(self._prev)
        finally:
            self._init=False

    def remove_prerun(self):
        """!Removes all prerun objects.
        @see prerun()"""
        return self._init_runner().remove_prerun()

    def copy(self,typeobj=None):
        """!Creates a deep copy of this runner, except if stream
        objects are connected to stdin, stdout or stderr.  In that
        case, those same stream objects are still connected.
        @param typeobj the type of the output object.  Do not use
          this unless you know what you're doing
        @returns a copy of self"""
        if typeobj is None: typeobj=ImmutableRunner
        return Runner.copy(self,typeobj)

    def runner(self):
        """!Returns a modifiable version of this object (as a Runner)."""
        return self.copy(Runner)
    def _init_runner(self):
        """!Do not call this function: it is an internal implementation
        function.  It returns self if self.__init__ is still being
        run, otherwise it returns self.runner()."""
        if self._init:
            x=self
        else:
            x=self.runner()
        assert(x is not None)
        assert(isinstance(x,Runner))
        return x
    def copyenv(self):
        """!Creates a new Runner that is like self in all ways except
        that it uses the parent process environment.
        @returns the new Runner"""
        return self._init_runner().copyenv()
    def clearenv(self): 
        """!Creates a new Runner which is like self in all ways except
        that it uses an empty environment except for a few critical
        variables without which most programs cannot run.  (Retains
        PATH, USER, LOGNAME and HOME.)
        @returns a new Runner"""
        return self._init_runner().clearenv()
    def cd(self,cd): 
        """!Returns a new Runner that is like self, except that it
        cd's to the target directory before running.  The directory
        must already exist before the program starts.
        @param cd the directory to cd into, which must already exist.
        @returns the new Runner"""
        return self._init_runner().cd(cd)
    def env(self,**kwargs): 
        """!Returns a new Runner that is like self in all ways except
        that the specified environment variables are set.
        @param kwargs varname=value arguments of environment variables to set
        @returns the new Runner"""
        return self._init_runner().env(**kwargs)
    def pipeto(self,other): 
        """!Returns a new Runner that is like self in all ways, except
        that it has been piped into the other Runner.
        @returns the new Runner
        @param other the Runner to pipe into."""
        return self.runner().pipeto(other)
    def inp(self,stdin,string=False): 
        """!Returns a new Runner that is like self in all ways except
        that it has a different stdin
        @param stdin the stdin string or filename
        @param string if True, stdin is a string"""
        return self._init_runner().inp(stdin,string)
    def out(self,stdout,append=False):
        """!Returns a new Runner that is like self in all ways except
        with a different stdout.
        @param stdout the stdout filename
        @param append if True, append to the file, otherwise truncate"""
        return self._init_runner().out(stdout,append)
    def err(self,stderr,append=False): 
        """!Returns a new Runner that is like self in all ways except
        with a different stderr.
        @param stderr the stderr filename
        @param append if True, append to the file, otherwise truncate"""
        return self._init_runner().err(stderr,append)
    def err2out(self): 
        """!Returns a new Runner that is like self in all ways except
        that stderr is piped into stdout."""
        return self._init_runner().err2out()
    def prerun(self,arg): 
        """!Returns a new Runner that is like self in all ways except
        that a new prerun function has been added.  
        @param arg the new prerun function
        @sa Runner.prerun()"""
        return self._init_runner().prerun(arg)
    def __getitem__(self,args): 
        """!Returns a new Runner that is like self in all ways except
        with new arguments.
        @param args the new argument or arguments
        @sa Runner.__getitem__"""
        return Runner.__getitem__(self._init_runner(),args)
    def argins(self,index,arg):
        """!Returns a new Runner that is like self in all ways, except
        with the specified argument inserted.
        @param index the index to insert before
        @param arg the argument to insert"""
        return self._init_runner().argins(index,arg)

    def _gen(self,pipeline,logger=None,next=None):
        """!Creates a Runner object that is a duplicate of this
        ImmutableRunner, and calls its _gen function.
        @param pipeline the produtil.pipeline.Pipeline to generate
        @param logger a logging.Logger for log messages
        @param next the next Runner in the chain
        @sa Runner._gen()"""
        return self.runner()._gen(pipeline,logger,next)

    def setthreads(self,nthreads):
        """!Sets the number of threads requested by this program."""
        r=self._init_runner()
        r.threads=nthreads
        return r
    def delthreads(self):
        """!Removes the request for threads.  Same as self.threads=1"""
        r=self._init_runner()
        del r.threads
        return r
