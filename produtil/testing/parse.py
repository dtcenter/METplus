##@namespace produtil.testing.parse
# This module contains the parser for the produtil.testing test suite.  
#
# The main interface to the produtil.testing parser is
# produtil.testing.parse.Parser.parse().  It constructs an internal
# tree representation of a file, provided by the
# produtil.testing.tokenizer.Tokenizer.  The tree can then be
# converted to a workflow by produtil.testing.rocoto or
# produtil.testing.script.

import sys, re, io, collections, os, datetime, logging, math
import produtil.run, produtil.log, produtil.setup

# This module really does use everything public from utilities,
# parsetree and tokenize, hence the "import *"
from produtil.testing.utilities import *
from produtil.testing.parsetree import *
from produtil.testing.tokenize import *

from produtil.testing.setarith import arithparse

__all__=[ 'Parser' ]

########################################################################

class RunConPair(object):
    """!A tuple-like object of a runnable object and a
    produtil.testing.parsetree.Context.  This is used to store
    something that can be run, such as a compilation command or batch
    job, and the context from which its execution was requested."""
    def __init__(self,runnable,context):
        """!Constructor for RunConPair

        @param runnable  The runnable object for self.runnable
        @param context   The produtil.testing.parsetree.Context for self.context"""
        self.runnable=runnable
        self.context=context
        self.__requested_platform=None

    def set_requested_platform_name(self,platform):
        self.__requested_platform_name=str(platform)
    def get_requested_platform_name(self):
        return self.__requested_platform_name
    def del_requested_platform_name(self):
        self.__requested_platform=None
    requested_platform_name=property(get_requested_platform_name,
                                     set_requested_platform_name,
                                     del_requested_platform_name)

    @property
    def as_tuple(self):
        """!A tuple self.runnable,self.context"""
        return self.runnable,self.context
    def __iter__(self):
        yield self.runnable
        yield self.context
    def __hash__(self):
        return hash(self.runnable)
    def __eq__(self,other):
        if not isinstance(other,RunConPair):
            return self.runnable==other
        return self.runnable==other.runnable

    # Replacements for __cmp__:
    def __lt__(self,other):
        if not isinstance(other,RunConPair):
            return self.runnable<other
        return self.runnable<other.runnable
    def __gt__(self,other):
        if not isinstance(other,RunConPair):
            return self.runnable>other
        return self.runnable>other.runnable
    def __ne__(self,other):
        return not ( self == other )
    def __ge__(self,other):
        return self>other or self==other
    def __le__(self,other):
        return self<other or self==other

    def oldcmp(self,other):
        if not isinstance(other,RunConPair):
            return self.runnable.oldcmp(other)
        return self.runnable.oldcmp(other.runnable)

    ##@property as_tuple
    # A tuple containing the runnable and context
    #
    # Same as:
    # @code
    #   (self.runnable,self.context)
    # @endcode

    ##@var runnable
    # The first element of this RunConPair: a runnable object

    ##@var context
    # The second element of this RunConPair: a produtil.testing.parsetree.Context

class Parser(object):
    """!Parser for the produtil.testing suite."""
    def __init__(self,run_mode=None,logger=None,verbose=True):
        """!Constructor for the Parser

        @param run_mode produtil.testing.utilities.EXECUTION to
            execute and verify results, or
            produtil.testing.utilities.BASELINE to generate a new
            baseline.
        @param logger a logging.Logger for logging messages, such as
            syntax errors
        @param verbose Increased verbosity flag: True = more verbose.
            """
        super(Parser,self).__init__()
        if logger is None: logger=module_logger
        if run_mode is None: run_mode=EXECUTION
        if run_mode is not EXECUTION and run_mode is not BASELINE:
            raise ValueError(
                'The Parser.__init__ run_mode argument must be the '
                'special module constants EXECUTION or BASELINE.')
        self.__runsets=collections.defaultdict(ListableSet)
        self.__runobjs=dict()
        self.__run_mode=run_mode
        self.__logger=logger
        self.__verbose=bool(verbose)

    ##@property run_mode
    # Returns the run mode: produtil.testing.utilities.EXECUTION or
    # produtil.testing.utilities.BASELINE

    @property
    def run_mode(self):
        """!Returns the run mode: produtil.testing.utilities.EXECUTION
        or produtil.testing.utilities.BASELINE"""
        return self.__run_mode

    ##@property verbose
    # Verbosity flag: True for verbose logging, False for quiet mode

    @property
    def verbose(self):
        """!Verbosity flag"""
        return self.__verbose

    ##@property logger
    # The logging.Logger to log messages

    @property
    def logger(self):
        """!The logging.Logger to log messages"""
        return self.__logger

    ##@property allset
    # Returns the special "**all**" runset, which contains all
    # runnables that had an explicit run statement.

    @property
    def allset(self):
        """!Returns the special "**all**" runset, which contains all
        runnables that had an explicit run statement."""
        return self.__runsets['**all**']

    def setarith(self,expr=None):
        """!Executes the specified expression via the setarith module,
        returning the resulting runset as a ListableSet.
        Automatically resolves dependencies."""
        if not expr:
            runme=ListableSet(self.allset)
        else:
            runme=arithparse(expr,self.__runsets,self.__runobjs)

        result=ListableSet()
        processed=set()
        for runcon in runme:
            self._resolve_deps_impl(result,processed,runcon)
        return result
    def iterrun(self,runset='**all**'):
        """!Iterates over all runnables in the runset.  

        @param runset The runset of interest.  If no runset is
        specified then the special "**all**" runset is used, which
        contains all runnables that had a "run" command, plus
        dependencies."""
        runset=runset or '**all**'
        for runcon in self.__runsets[runset]:
            yield runcon
    def itersets(self):
        """"!Iterates over all runset names in self, including the
        special "**all**" set, which contains all runnables that had a
        "run" command, plus dependencies."""
        for setname,runset in self.__runsets.items():
            yield setname,runset
    def con(self,token=None,scopes=None):
        """!Returns a context for the given token and scope.  

        @param token Used to determine the file and line number.  If
        the token is None, then a fileless context is used.  This
        indicates the context is not from any file or line.

        @param scope the list of Scopes.  If none are given, then an
        empty list is used.  This indicates the scope is from outside
        the parsed text entirely.

        @returns a produtil.testing.parsetree.Context for the given
        token and scope, or a fileless context if no token is
        provided."""
        if scopes is None: scopes=[]
        if token is None:
            return produtil.testing.parsetree.fileless_context(
                scopes=scopes,verbose=self.verbose)
        return Context(scopes,token,self.__run_mode,self.__logger,
                       verbose=self.verbose)
    def add_run(self,runset,runme,con):
        """!Adds another runnable object to execute in a given runset

        Updates the internal bookkeeping to indicate the given
        runnable object can be run.  If a runset is provided, then the
        set with the given name is updated to indicate it can run the
        object.  Regardless of runset, the special "**all**" set is
        updated to run the given runnable.  If the set already
        contains runme, adding it again has no effect.

        @param runset The set of"""
        if not isinstance(runme,Task) and not isinstance(runme,Test):
            raise TypeError(
                'The runme argument to add_run must be a Test or Task '
                '(in produtil.testing.parsetree) or subclass.  You '
                'provided a %s %s'%(
                    type(runme).__name__,elipses(repr(runme))))
        if runset is None:
            self.__runobjs[runme.name]=RunConPair(runme,con)
            return
        addme=RunConPair(runme,con)
        for xrunset in [ runset, '**all**' ]:
            self.__runsets[xrunset].add(addme)
    def _resolve_deps_impl(self,newset,processed,runcon):
        """!Adds a runnable object and its dependencies to a list of
        objects to run.

        Adds runcon to the processed set to mark that it is being
        processed, returning immediately if it was already there.
        Then recurses into each dependency of runcon, calling this
        function on each, and then adds runcon to newset.  The result
        is that the newset will contain all runnable objects in
        correct dependency order.
        
        @param newset The ListableSet to receive the runnable objects
        @param processed a set of all runnable objects already
        processed or being processed by recursive calls to this
        function. 
        @param runcon The runnable object to process, a RunConPair
        @returns None"""
        if not isinstance(runcon,RunConPair):
            raise TypeError('In _resolve_deps_impl, runcon must be a RunConPair, not a %s %s'%(type(runcon).__name__,elipses(repr(runcon))))
        assert(isinstance(runcon,RunConPair))
        assert(isinstance(newset,ListableSet))
        if runcon in processed: return
        processed.add(runcon)
        for prereq in runcon.runnable.iterdeps():
            if prereq not in newset:
                self._resolve_deps_impl(
                    newset,processed,RunConPair(prereq,runcon.context))
        newset.add(runcon)
    def resolve_deps(self):
        """!Resolves dependencies in the runsets, replacing them with
        new runsets that contain all dependencies and have runnables
        listed in correct dependency order.
        @returns None"""
        newrunsets=dict()
        for setname in self.__runsets.keys():
            processed=set()
            newset=ListableSet()
            for runcon in self.__runsets[setname]:
                assert(isinstance(runcon,RunConPair))
                self._resolve_deps_impl(newset,processed,runcon)
            newrunsets[setname]=newset
        self.__runsets=newrunsets
    def parse(self,tokenizer,scope=None,unique_id=None,morevars=None):
        """!Main entry point for the parser.  Parses the stream of
        tokens returned by the tokenizer.

        @param tokenizer The produtil.testing.tokenize.Tokenizer that
        returns a stream of tokens from some file or string

        @param scope The innermost produtil.testing.parsetree.Scope.
        If None, a new produtil.testing.parsetree.Scope is created.

        @param unique_id The value for the special UNIQUE_ID global variable.

        @param morevars A dict with additional variables to set in the
        global scope."""
        if scope is None:
            scope=Scope()
        if unique_id is None:
            unique_id=os.getpid()
        if morevars is not None:
            for k,v in morevars.items():
                scope.setlocal(str(k),String([scope],str(v),False))
        if not isinstance(unique_id,int):
            raise TypeError(
                'The unique_id argument to Parser.parse() must be an '
                'int, not a %s %s.'%( type(unique_id).__name__,
                                      elipses(repr(unique_id)) ))
        tokiter=peekable(tokenizer)
        scope.setlocal('ENV',Environ())
        assert(isinstance(unique_id,int))
        scope.setlocal('UNIQUE_ID',Numeric(unique_id))
        if self.run_mode==BASELINE:
            scope.setlocal('RUN_MODE',String([scope],'BASELINE',False))
        else:
            scope.setlocal('RUN_MODE',String([scope],'EXECUTION',False))
        result=self.parse_subscope(
            tokiter,[scope],[end_of_text_type],
            self.parse_between_assignments,
            allow_overwrite=False,
            allow_resolve=True,
            allow_run=True,
            allow_null=False,
            allow_use=False,
            allow_load=True,
                scope_name='global scope')
        self.resolve_deps()

    def parse_between_arguments(self,tokiter,ends=None):
        """!Used inside an argument list "function(arg,arg2,...)".
        Skips over the "," and whitespace between arguments.

        @param tokiter a peekable iterator that yields tokens
        @param ends: optional; the termination token for the argument list. Default: ")" 
        @return True if we are still inside the argument list, or False otherwise"""
        if ends is None: ends=[')']
        peek=tokiter.peek()
        # yell('%-7s peek type=%s value=%s\n'%(
        #         'BETWEEN',str(peek.token_type),elipses(str(
        #                 peek.token_value))))
        while True:
            if peek.token_type == ',':
                next(tokiter)
                # yell('%-7s consume ,\n'%('BETWEEN',))
                return True
            elif peek.token_type in ends:
                # yell('%-7s stop at %s\n'%('BETWEEN',peek.token_type))
                return False
            elif peek.token_type==end_of_line_type:
                # yell('%-7s saw \n'%('BETWEEN',))
                next(tokiter)
                peek=tokiter.peek()
            else:
                return False
    def skip_eoln(self,tokiter):
        """!Skips over end-of-line characters.
        @param tokiter a peekable iterator that yields tokens
        @returns None"""
        peek=tokiter.peek()
        while peek.token_type==end_of_line_type:
            next(tokiter)
            peek=tokiter.peek()
    def parse_between_assignments(self,tokiter):
        """!Skips over characters between assignments in a scope ,;

        Skips over , and ; between assignments.  Checks to see if the
        assignment block ended by looking for end-of-line, end-of-text or }

        @param tokiter a peekable iterator that yields tokens
        @return True if any , ; } end-of-line or end-of-text were seen"""
        peek=tokiter.peek()
        seen=False
        # yell('%-7s peek type=%s value=%s in parse_between_assignments\n'%(
        #         'BETWEEN',str(peek.token_type),
        #         elipses(str(peek.token_value))))
        while True:
            seen=True
            if peek.token_type in [ ',', ';' ]:
                next(tokiter)
                # yell('%-7s consume %s\n'%('BETWEEN',peek.token_type))
                return True
            elif peek.token_type in [ '}', end_of_text_type ]:
                # yell('%-7s stop at %s\n'%('BETWEEN',peek.token_type))
                return True
            elif peek.token_type==end_of_line_type:
                # yell('%-7s saw %s\n'%('BETWEEN',repr(peek.token_type)))
                seen=True
                next(tokiter)
                peek=tokiter.peek()
            else:
                break
        return seen
        self.error('between_assignments',peek)

    def parse_embed_script(self,tokiter,scopes,ends,parse_between=None):
        """!Parses an embedded script block.  Returns the resulting object.

        @param tokiter a peekable iterator that yields tokens
        @param scopes a list of nested scopes (innermost first) surrounding the embedded script block
        @param ends termination tokens of the containing scope

        @param parse_between an optional function that is called after
        the embedded script block.  This skips over tokens between the
        embedded script block and the next item in the scope

        @returns a tuple containing the token with the variable name,
        and the scope that represents the embedded script."""
        token=next(tokiter)
        if token.token_type != 'varname':
            self.error('embed',token)
        if token.token_value != 'bash':
            self.error('embed',token,'unknown language "%s"'%(
                    token.token_value,))
        nametoken=next(tokiter)
        if token.token_type != 'varname':
            self.error('embed script name',token)
        scope=EmbedBash(scopes)
        token=next(tokiter)

        while token.token_type==end_of_line_type: token=next(tokiter)
        if token.token_type=='(':
            self.parse_subscope(tokiter,[scope]+scopes,[')'],
                                self.parse_between_arguments,
                                allow_overwrite=False,
                                allow_resolve=False,
                                allow_null=True,
                                only_scalars=True,
                                scope_name='embed script parameters')
            scope=scope.as_parameters(self.con(token,scopes))
            token=next(tokiter)
        while token.token_type==end_of_line_type: token=next(tokiter)

        if token.token_type=='{':
            self.parse_subscope(tokiter,[scope]+scopes,['}'],
                                self.parse_between_assignments,
                                allow_overwrite=True,
                                allow_resolve=True,
                                allow_null=False,
                                allow_use=True,
                                only_scalars=True,
                                scope_name='embed script variables')
            token=next(tokiter)
        while token.token_type==end_of_line_type: token=next(tokiter)

        if token.token_type in [ 'qstring', 'dqstring', 'bracestring' ]:
            scope.settemplate(self.action_string([scope]+scopes,token))
        else:
            self.error('embed script contents',token)
        if parse_between: 
            parse_between(tokiter)
        return (nametoken.token_value,scope)

    def parse_set_list(self,tokiter,scopes):
        """!Iterates over a list of set names, yielding each one.

        Parses a comma-separated list of set names, yielding each set
        name as a token.  Skips intervening commas or whitespace.

        @param tokiter a peekable iterator that yields tokens
        @param scopes a list of nested scopes (innermost first) surrounding the set list
        @returns None (this is an iterator)"""
        peek=tokiter.peek()
        while peek.token_type=='varname':
            yield peek.token_value
            lvaltoken=peek
            next(tokiter) # discard varname
            peek=tokiter.peek()
            while peek.token_type==end_of_line_type:
                next(tokiter)
                peek=tokiter.peek()
            if peek.token_type=='==':
                # this is an "if var==value" condition
                next(tokiter) # consume ==
                peek=tokiter.peek()
                if peek.token_type!='varname':
                    self.error('run setname @ ... var==',peek)
                rvaltoken=next(tokiter)
                lval=self.action_resolve(lvaltoken,scopes)
                rval=self.action_resolve(rvaltoken,scopes)
                yield lval == rval

                peek=tokiter.peek()
            if peek.token_type!=',':
                return # reached end of list.
            next(tokiter) # discard ","
            peek=tokiter.peek()
                
    def parse_deplist(self,tokiter,scopes,task,ends):
        """!Parses and iterates over a list of dependencies.

        @param tokiter a peekable iterator that yields tokens
        @param scopes a list of nested scopes (innermost first) surrounding the list of dependencies
        @param task The task for which the dependencies are being declared
        @param ends List of termination tokens for the dependency list"""
        allscopes=[task]+scopes
        peek=tokiter.peek()
        while not peek.token_type in ends:
            if peek.token_type=='varname':
                varname=peek
                next(tokiter)
                peek=tokiter.peek()
                if peek.token_type==end_of_line_type:
                    continue # ignore blank lines
                elif self.parse_between_arguments(tokiter,['{']):
                    # varname is followed by a comma
                    dep=self.action_resolve(varname,allscopes)
                    self.action_dependency(task,scopes,dep)
                    peek=tokiter.peek()
                    continue
                elif peek.token_type in ends:
                    dep=self.action_resolve(varname,allscopes)
                    self.action_dependency(task,scopes,dep)
                    return
                elif peek.token_type == '(':
                    # This is a function call.
                    next(tokiter)
                    subscope=Scope(scopes)
                    self.parse_subscope(tokiter,scopes,[')'],
                                        self.parse_between_arguments,
                                        allow_overwrite=False,
                                        allow_resolve=False,
                                        allow_null=True,
                                        scope_name='dependency argument list')
                    subscope=subscope.as_parameters(self.con(peek,scopes))
                    peek=tokiter.peek()
                    if self.parse_between_arguments(tokiter) \
                            or peek.token_type in ends:
                        dep=self.action_call(varname,peek,scopes,subscope)
                        self.action_dependency(task,scopes,dep)
                        peek=tokiter.peek()
                        continue
            self.error('dependency argument list',peek)
    def parse_op_list(self,tokiter,scopes,subscope):
        """!Parses and iterates over list of "target .operator. source" expressions.

        @param tokiter a peekable iterator that yields tokens
        @param scopes a list of nested scopes (innermost first) surrounding the list
        @param subscope the Task for whom the operator list is being declared
        @returns None; this is an iterator"""
        token=next(tokiter)
        strings=[ 'qstring', 'dqstring', 'bracestring' ]
        if token.token_type != '{':
            self.error('operation list',token)
        while True:
            # Get target of operation:
            token=next(tokiter)
            while token.token_type==end_of_line_type:
                token=next(tokiter)
 
            if token.token_type=='varname' and token.token_value=='use':
                peek=tokiter.peek()
                if peek.token_type!='varname':
                    self.error('operation list use statement',peek)
                next(tokiter)
                subscope.use_from(self.action_resolve(peek,scopes))
                self.parse_between_assignments(tokiter)
                peek=tokiter.peek()
                if peek.token_type=='}':
                    next(tokiter)
                    return subscope
                continue
            elif token.token_type=='}':
                return subscope
            elif token.token_type not in strings:
                self.error('operator target',token)
            tgt=self.action_string(scopes,token)

            # Get operator:
            token=next(tokiter)
            while token.token_type==end_of_line_type:
                token=next(tokiter)
            if token.token_type!='oper':
                self.error('oper',token)
            op=self.action_operator(scopes,token)

            # Get source of operation (input or baseline file)
            token=next(tokiter)
            while token.token_type==end_of_line_type:
                token=next(tokiter)
            if token.token_type not in strings:
                self.error('operator source (input or baseline)',token)
            src=self.action_string(scopes,token)

            # Add operator:
            # FIXME: CONTEXT
            subscope.add_binary_operator(
                tgt,op,src,self.con(token,scopes))

            self.parse_between_assignments(tokiter)
            peek=tokiter.peek()
            if peek.token_type=='}':
                next(tokiter)
                return subscope


    def parse_hash_define(self,tokiter,scopes,subscope,parse_between=None,
                          allow_deps=False,hash_type='hash'):
        """!Parses a variable hash definition.

        Parses a definition of the syntax "{ varname = rvalue, varname=rvalue, ...}"
        where rvalue is any value that may be assigned to a variable (see parse_rvalue())

        @param tokiter a peekable iterator that yields tokens
        @param scopes a list of nested scopes (innermost first) surrounding the variable hash
        @param parse_between a function called between "varname=rvalue" assignments, to skip over such things as commas
        @param allow_deps If True, then parse_deplist() is called first, to parse a dependency list before the assignment list.
        @param hash_type The type of hash, such as "task," for error messages.

        @returns the resulting Scope"""
        token=next(tokiter)
        parameters=False

        # if token.token_type=='(':
        #     parameters=True
        #     self.parse_subscope(tokiter,[subscope]+scopes,[')'],
        #                         self.parse_between_arguments,
        #                         allow_overwrite=False,
        #                         allow_resolve=False,
        #                         allow_null=True,
        #                         scope_name=hash_type+' argument list')
        #     subscope=subscope.as_parameters()
        #     token=tokiter.next()

        if allow_deps and token.token_type==':':
            self.parse_deplist(
                tokiter,[subscope]+scopes,subscope,['{'])
            token=next(tokiter)

        if token.token_type=='{':
            next(tokiter)
            self.parse_subscope(tokiter,[subscope]+scopes,['}'],
                                self.parse_between_assignments,
                                allow_overwrite=True,
                                allow_resolve=True,
                                allow_null=False,
                                allow_use=True,
                                scope_name=hash_type+' definition')
        else:
            self.error(
                hash_type+' definition',token,
                'missing {...} block in '+hash_type+' definition')

        if parse_between:
            parse_between(tokiter)

        # yell('%-7s define Scope@%s with %sparameters\n'%(
        #         hash_type.upper(),str(id(subscope)),
        #         ' ' if parameters else 'no '))
        return subscope

    def parse_spawn_element(self,tokiter,scopes,spawn,ends):
        """!Parses one element (block of MPI ranks) of a process
        spawning block.  

        Parses the individual, comma-separated elements of a spawn block:

        @code
           {"program_name", ranks=32, threads=1}
        @endcode

        Combines the result into a single scope and array.

        @returns a tuple containing the array of arguments and the
        resulting Scope."""
        token=next(tokiter)
        args=list()
        opts=list()
        saw_vars=False
        strings=[ 'qstring', 'dqstring', 'bracestring' ]
        while token.token_type not in ends:
            if token.token_type in strings:
                if saw_vars:
                    self.error('spawn process',token,'var=value elements '
                               'must come after all arguments')
                args.append(token)
                self.parse_between_arguments(tokiter,ends)
                token=next(tokiter)
                continue
            elif token.token_type==end_of_line_type:
                token=next(tokiter)
                continue
            elif token.token_type=='varname':
                name=token.token_value
                peek=tokiter.peek()
                if peek.token_type != '=':
                    self.error('spawn process',token)
                next(tokiter)
            else:
                self.error('spawn process',token)
            # we're at the value in varname=value
            rvalue=self.parse_rvalue(
                tokiter,scopes,['}',','],
                only_scalars=True,use_references=True)
            self.parse_between_arguments(tokiter,ends)
            opts.append([name,rvalue])
            token=next(tokiter)
        scope=Scope(scopes)
        allscopes=[scope]+scopes
        for k,v in opts:
            scope.setlocal(k,v)
        if not args:
            self.error('spawn process',token,'no command nor arguments')
        for arg in args:
            assert(isinstance(arg,Token))
        argobjs=[ 
            self.action_string(allscopes,arg) for arg in args]
        return argobjs,scope

    def parse_spawn_block(self,tokiter,scopes,name,spawn,ends,parse_between):
        """!Parses a subprocess spawning subblock.

        Parses a block of this form:
        
        @code
           {"program_name", ranks=32, threads=1}
        @endcode

        The set braces are also parsed.  The parse_spawn_element()
        function parses the individual, comma-separated, elements
        within that block.  The results are sent to the spawn
        argument.

        @param tokiter a peekable iterator that yields tokens
        @param scopes a list of nested scopes (innermost first)
            surrounding the subprocess spawning block
        @param name the name of the subprocess spawning block
        @param ends the list of tokens that terminate the surrounding block
        @param pars_between if specified, a function to call between the
            individual subprocess spawn elements
        @returns None
        @see parse_spawn_element()"""
        token=next(tokiter)
        while token.token_type==end_of_line_type: 
            token=next(tokiter)
        while token.token_type not in ends:
            if token.token_type!='{':
                self.error('spawned process',token)
            (args,opts)=self.parse_spawn_element(
                    tokiter,scopes,spawn,['}'])
            spawn.add_rank(args,opts)
            if parse_between: parse_between(tokiter)
            token=next(tokiter)

    def parse_spawn(self,tokiter,scopes,name,spawn):
        """!Parses a subprocess spawning block

        Parses a block of this form:

        @code
           {
             {"program_name", ranks=32, threads=1}
             {"program_name", ranks=16, threads=1}
             {"another_program", ranks=80, threads=1}
           }
        @endcode

        The beginning and ending set braces are also consumed.  Uses
        the parse_spawn_block() to parse the individual subblocks.
        Constructs a scope containing the resuling information.

        @param tokiter a peekable iterator that yields tokens
        @param scopes a list of nested scopes (innermost first)
        surrounding the subprocess spawn block

        @param name the name of the subprocess spawn block
        @param spawn the scope in which to store the subprocess
        spawning block information.
        @returns spawn"""
        token=next(tokiter)
        if token.token_type!='{':
            self.error('spawn block',token)
        while self.parse_spawn_block(tokiter,scopes,name,spawn,['}'],
                                     self.parse_between_assignments):
            continue
        return spawn

    def parse_autodetect(self,tokiter,scopes,taskname,task):
        """!Parses an autodetect block

        Parses a block of this form:

        @code
            autodetect plat (/ wcoss.phase1, theia /)
        @endcode

        Places the resulting information in the task argument.

        @param tokiter a peekable iterator that yields tokens
        @param scopes a list of nested scopes (innermost first)
        surrounding the autodetect block
        @param taskname the name of the autodetect block
        @param task the scope in which to store the information."""
        # Check for the (/ and skip it:
        token=next(tokiter)
        while token.token_type==end_of_line_type:
            token=next(tokiter)
        if token.token_type!='(/':
            self.error('autodetect platform list',token)

        while True:
            peek=tokiter.peek()
            while peek.token_type==end_of_line_type:
                next(tokiter)
                peek=tokiter.peek()
            if peek.token_type=='/)':
                next(tokiter)
                return
            rvalue=self.parse_rvalue(tokiter,scopes,['/)'],
                                     self.parse_between_arguments,False)
            task.add(rvalue)
            peek=tokiter.peek()
            self.parse_between_arguments(tokiter)
            if peek.token_type=='/)':
                next(tokiter)
                return

    def parse_load(self,tokiter,scope,seen_run):
        """!Parses a "load" statement.
        
        Parses a statement of this form:

        @code
            load 'otherfile.input'
        @endcode

        This uses the tokiter's child() function to create a new
        tokenizer that parses the specified file.  The parser then
        parses the file using parse_subscope().  This acts as if the
        file was inserted in the location of the "load" statement.

        @param tokiter a peekable iterator that yields tokens.  It
        must also have a child() function that can create a new
        tokenizer for the loaded file
        @param scope the scope in which the "load" statement resides
        @param seen_run True if a "run" statement was seen.
        @returns None
        """
        filetoken=next(tokiter)
        if filetoken.token_type!='qstring':
            self.error('load',token,"load statements can only include "
                       "'single-quote strings'")
        eoln=tokiter.peek()
        if eoln.token_type not in [ end_of_line_type, end_of_text_type ]:
            self.error('load',eoln,"a load statement must be followed "
                       "by an end of line or the end of the script.")
        newfile=filetoken.token_value
        if not os.path.isabs(newfile):
            newfile=os.path.join(os.path.dirname(filetoken.filename),newfile)
        tokenizer=tokiter.child
        with open(newfile,'rt') as fileobj:
            new_tokenizer=tokenizer.for_file(fileobj,newfile)
            new_tokiter=peekable(new_tokenizer)
            self.parse_subscope(
                    new_tokiter,[scope],[end_of_text_type],
                    self.parse_between_assignments,
                    allow_overwrite=False,
                    allow_resolve=True,
                    allow_run=True,
                    allow_null=False,
                    allow_use=False,
                    allow_load=True,
                    scope_name='global scope',
                    seen_run=seen_run)
        
    def parse_subscope(
        self,tokiter,scopes,ends,parse_between,
        allow_overwrite=True,allow_resolve=True,
        allow_run=False,allow_null=False,
        allow_use=False,scope_name='subscope',
        only_scalars=False,allow_load=False,
        seen_run=False):

        try:
            return self.parse_subscope_impl(
                tokiter,scopes,ends,parse_between,allow_overwrite,
                allow_resolve,allow_run,allow_null,allow_use,scope_name,
                only_scalars,allow_load,seen_run)
        except Exception as e: # FIXME: change exception type
            if tokiter.at_end():
                sys.stderr.write('%s: %s\n'%(
                        type(e).__name__,str(e)))
            else:
                peek=tokiter.peek()
                filename=peek.filename
                lineno=peek.lineno
                sys.stderr.write('%s:%d: %s\n'%(
                        filename,lineno,str(e)))
            raise
        
    def parse_subscope_impl(
        self,tokiter,scopes,ends,parse_between,
        allow_overwrite=True,allow_resolve=True,
        allow_run=False,allow_null=False,
        allow_use=False,scope_name='subscope',
        only_scalars=False,allow_load=False,
        seen_run=False):
        """!General subscope parser, used for parsing most scopes.

        Parses a scope.  This includes the innermost (global) scope,
        and anything within blocks like these:

        @code
            ( ... declarations and arguments ... )
            { ... declarations ... }
            (/ ... array elements ... /)
        @endcode

        The various arguments control what is allowed within the scope.

        @param tokiter a peekable iterator that yields tokens

        @param scopes a list of nested scopes (innermost first)
          surrounding the scope to parse.  The scope being parsed is
          the first element in this array.

        @param ends tokens that indicate the end of the scope
        @param parse_between tokens that separate pieces of the scope,
          such as declarations, array elements, or arguments.
        @param allow_overwrite are we allowed to replace values
          that are already set in the scope?
          
        @param allow_resolve When a variable reference is encountered,
        are we allowed to resolve it within the scope that is being
        parsed?

        @param allow_run Are "run" statements allowed in this scope?
        @param allow_none If True, then lone variable names are allowed.
          This is intended for use in argument lists.
        @param allow_use Are "use" statements allowed in this scope?
        @param scope_name The name of this scope, used for error reporting.
        @param only_scalars If True, then only strings and numbers are 
          allowed to be assigned to variables.  If False, anything
          can be assigned.
        @param allow_load Do we allow "load" statements in this scope?
        @param seen_run Have we already seen a "run" statement within
          this scope, before parse_subscope() was called?  If so,
          it is an error to have declarations.

        """
        go=True # set to False once an "ends" is seen
        seen_run=bool(seen_run) # Did we see an execution request yet?
        token=None
        strings=[ 'qstring', 'dqstring', 'bracestring' ]
        def define(con,key,val):
            if seen_run:
                self.error(
                    scope_name,token,
                    reason='Definitions must come before execution '
                    'requests.')
            if not val.is_valid_rvalue(con):  # FIXME: con
                self.error(scope_name,token,'not a valid rvalue: %s'%(
                        elipses(repr(val)),))
            # yell('%s:%s: define %s=%s\n'%(
            #         token.filename,str(token.lineno),
            #         str(key),repr(val)))
            if allow_overwrite:
                scopes[0].force_define(key,val)
            else:
                scopes[0].check_define(key,val)
        if allow_resolve:
            search_scopes=scopes
        else:
            search_scopes=scopes[1:]
        while go:
            token=next(tokiter)
            if token.token_type=='varname':
                peek=tokiter.peek()
                if peek.token_type=='=':
                    next(tokiter)
                    define(self.con(token,scopes),token.token_value,
                           self.parse_rvalue(tokiter,search_scopes,ends,
                                             parse_between,
                                             only_scalars=only_scalars,
                                             use_references=True))
                    parse_between(tokiter)
                    continue
                elif token.token_value=='load' and peek.token_type in strings:
                    if not allow_load:
                        self.error('subscope',token,'load statements are '
                                   'only allowed in the global scope.')
                    self.parse_load(tokiter,scopes[-1],seen_run)
                    if parse_between:  parse_between(tokiter)
                    continue
                elif token.token_value=='use' and peek.token_type=='varname' \
                        and allow_use:
                    next(tokiter) # consume the peeked value
                    self.action_use(scopes,peek,
                                    only_scalars=only_scalars)
                    if parse_between:  parse_between(tokiter)
                    continue
                elif allow_run and token.token_value=='run' \
                        and peek.token_type=='varname':
                    set_rvalue=self.parse_rvalue(tokiter,search_scopes,
                                                 ends,parse_between)
                    set_con=self.con(peek,scopes)
                    runsets=list()
                    peek=tokiter.peek()
                    keep_by_set=True
                    keep_by_comparison=None # Will be True/False if "==" is used
                    if peek.token_type=='@':
                        next(tokiter) # discard the @
                        for setname in self.parse_set_list(
                                tokiter,search_scopes):
                            if setname is False or setname is True:
                                keep_by_comparison=keep_by_comparison or setname
                            elif setname not in runsets:
                                assert(isinstance(setname,str))
                                runsets.append(setname)
                    keep = keep_by_set
                    if keep_by_comparison is not None:
                        keep = keep and keep_by_comparison
                    if keep:
                        if not runsets:
                            runsets.append('**all**')
                        seen_run=True
                        self.action_run_by_name(set_rvalue,set_con)
                        for setname in runsets:
                            runobj=self.action_run_in_set(
                                setname,set_rvalue,set_con)
                    peek=tokiter.peek()
                    if parse_between: parse_between(tokiter)
                    continue
                elif not only_scalars and token.token_value=='spawn' \
                        and peek.token_type=='varname':
                    taskname=peek.token_value
                    next(tokiter)
                    task=self.parse_spawn(tokiter,scopes,peek.token_value,
                                          SpawnProcess(scopes))
                    define(self.con(peek,scopes),taskname,task)
                    if parse_between:  parse_between(tokiter)
                    del taskname,task
                    continue
                elif not only_scalars and token.token_value in [
                    'filters', 'criteria' ] and peek.token_type=='varname':
                    taskname=peek.token_value
                    next(tokiter)
                    if token.token_value=='filters':
                        task=Filters(scopes)
                    elif token.token_value=='criteria':
                        task=Criteria(scopes)
                    task=self.parse_op_list(tokiter,scopes,task)
                    define(self.con(peek,scopes),taskname,task)
                    if parse_between:  parse_between(tokiter)
                    del taskname,task
                    continue
                elif not only_scalars and token.token_value=='autodetect' \
                        and peek.token_type=='varname':
                    taskname=peek.token_value
                    taskcon=self.con(peek,scopes)
                    next(tokiter) # Skip name token
                    task=AutoDetectPlatform()
                    self.parse_autodetect(tokiter,scopes,taskname,task)
                    task=self.action_autodetect(self.con(peek,scopes),
                                                tokiter,scopes,taskname,task)
                    define(taskcon,taskname,task)
                    del taskname, task, taskcon
                    continue
                elif not only_scalars and token.token_value in [
                        'build', 'task', 'test', 'compset', 'platform' ] \
                        and peek.token_type=='varname':
                    taskname=peek.token_value
                    # yell('%-7s %-7s %s\n'%(
                    #         'PARSE',token.token_value,taskname))
                    next(tokiter) # consume the task name
                    # yell('%-7s %-7s %s\n'%(
                    #         'INIT',token.token_value,taskname))
                    if token.token_value=='task':
                        raise AssertionError('Should never make a Task')
                        task=Task(scopes,taskname)
                    elif token.token_value=='test' or token.token_value=='compset':
                        task=Test(scopes,taskname,self.__run_mode)
                        task._set_constants({'TEST_NAME':
                                      String(scopes,taskname,False)})
                    elif token.token_value=='build':
                        task=Build(scopes,taskname)
                        task._set_constants({'BUILD_NAME':
                                      String(scopes,taskname,False)})
                    elif token.token_value=='platform':
                        task=Platform(scopes,taskname)
                        task._set_constants({'PLATFORM_NAME':
                                      String(scopes,taskname,False)})
                    else:
                        raise AssertionError(
                            'Unrecognized subscope type "%s".'%(
                                token.token_value,))
                    task=self.parse_hash_define(
                            tokiter,scopes,task,parse_between,
                            allow_deps=token.token_value!='platform')
                    # yell('%-7s %-7s %s\n'%('DEFINE',token.token_value,
                    #                        taskname))
                    define(self.con(peek,scopes),taskname,task)
                    del taskname, task
                    if parse_between:  parse_between(tokiter)
                    continue
                elif not only_scalars \
                        and token.token_value=='hash' \
                        and peek.token_type=='varname':
                    hashname=peek.token_value
                    next(tokiter) # consume the hash name
                    define(self.con(peek,scopes),
                           hashname,self.parse_hash_define(
                            tokiter,scopes,Scope(scopes),parse_between))
                    del hashname
                    if parse_between:  parse_between(tokiter)
                    continue
                elif not only_scalars \
                        and token.token_value=='embed' \
                        and peek.token_type=='varname':
                    (varname,script)=self.parse_embed_script(
                        tokiter,scopes,parse_between)
                    define(self.con(peek,scopes),varname,script)
                    if parse_between:  parse_between(tokiter)
                    continue
                elif allow_null and (
                    peek.token_value in ends or
                    parse_between and parse_between(tokiter)):
                    define(self.con(peek,scopes),
                           token.token_value,null_value)
                    if parse_between:  parse_between(tokiter)
                    continue
            elif token.token_type in ends:
                return scopes[0]
            elif token.token_type==end_of_line_type:
                continue # ignore blank lines.
            self.error(scope_name,token)
    def parse_rvalue(self,tokiter,scopes,ends,parse_between=None,
                     only_scalars=False,use_references=False):
        """!Parses an rvalue, which is anything that can be stored in
        to a storage location.

        Parses rvalues.  Anything that can be stored in variables,
        arguments, or elsewhere is an rvalue.  This includes
        variables, strings, numbers, and named subscopes.

        @param tokiter a peekable iterator that yields tokens
        @param scopes a list of nested scopes (outermost first) surrounding the rvalue
        @param ends the list of tokens that indicate the end of the
          surrounding scope.
        @param parse_between if the surrounding scope is a list of
          expressions, arguments, or assignments, then this function is
          called to skip values after the rvalue
        @param only_scalars If True, only strings and numbers are allowed.
        @returns the resulting rvalue"""

        token=next(tokiter)
        if token.token_type in [ 'qstring', 'dqstring', 'bracestring' ]:
            ret=self.action_string(scopes,token)
            if parse_between: parse_between(tokiter)
            return ret
        elif token.token_type == 'number':
            ret=self.action_numeric(scopes,token)
            if parse_between: parse_between(tokiter)
            return ret
        elif not only_scalars and token.token_type in '{':
            subscope=Scope(scopes)
            ret=self.parse_subscope(
                tokiter,[subscope]+scopes,['}'],
                self.parse_between_assignments,
                allow_overwrite=True,
                allow_resolve=True,
                allow_run=False,
                allow_null=False,
                allow_use=True,
                scope_name="hash")
            if parse_between: parse_between(tokiter)
            return ret
        elif not only_scalars and token.token_type=='varname':
            varname=token.token_value
            peek=tokiter.peek()
            if peek.token_type=='(':
                # We are at the ( in varname(arguments...
                next(tokiter) # consume (
                subscope=Scope(scopes)
                scopesplus=[subscope]+scopes
                self.parse_subscope(tokiter,scopesplus,[')'],
                                    self.parse_between_arguments,
                                    allow_overwrite=False,
                                    allow_resolve=False,
                                    allow_null=True,
                                    scope_name='argument list')
                peek=tokiter.peek()
                if peek.token_type in ends or \
                        parse_between and parse_between(tokiter):
                    # This is a function call varname(arg,arg,...)
                    return self.action_call(varname,peek,scopes,subscope)
            elif peek.token_type in ends :
                if use_references:
                    return self.action_reference(token,scopes)
                else:
                    return self.action_resolve(token,scopes)
            elif parse_between and parse_between(tokiter):
                if use_references:
                    return self.action_reference(token,scopes)
                else:
                    return self.action_resolve(token,scopes)
        self.error('rvalue',token)
    def action_autodetect(self,con,tokiter,scopes,taskname,task):
        """!Executes an autodetect block

        Executes the "detect" function within each element of an
        autodetect block, choosing the block whose detect function
        returns True.  It is an error for more or less than one
        platform to return True."""
        matches=task.detect(con)
        if self.requested_platform_name:
            for match in matches:
                name=match.resolve('PLATFORM_NAME').string_context(
                    produtil.testing.parsetree.fileless_context(
                        verbose=self.verbose))
                if name == self.requested_platform_name:
                    return match
            raise PTParserError(
                'The platform "%s" is not detected on this machine.'%(
                    self.requested_platform_name,))
        if len(matches)==0:
            raise PTParserError(
                'You are using an unknown platform.  Check your platforms.input file "autodetect" block.  Add support for this platform, or correct your platform detection logic.')
        elif len(matches)>1:
            raise PTPlatformError(
                'This machine can submit to multiple platforms: '+(
                    ' '.join([
                      s.resolve('PLATFORM_NAME') \
                       .string_context(
                         produtil.testing.parsetree.fileless_context(
                           verbose=self.verbose)) \
                            for s in matches
                ])))
        return matches[0]
    def action_dependency(self,task,scopes,dep):
        """!Adds the specified dependency to the specified task.

        @param task The task for whom the dependency is to be added.
        @param dep The dependency
        @param scopes The surrounding scopes (presently unused)"""
        task.add_dependency(dep)
    def action_call(self,varname,token,scopes,parameters):
        """!Creates a scope that represents a function call.

        @param varname The function to call.
        @param parameters The arguments to the function.
        @param token the context from which the function call is requested.
        @param scopes a list of nested scopes (outermost first) surrounding the call

        @returns a scope representing the given function call"""
        # yell('%-7s %s in parameter scope %s\n'%(
        #         'CALL',repr(varname),repr(parameters)))
        callme=scopes[0].resolve(varname)
        # yell('CALL APPLY PARAMETERS\n')
        return callme.apply_parameters(parameters,self.con(token,scopes))
    def action_use(self,scopes,key_token,only_scalars=False):
        """!Performs the action of a "use" block within a subscope.

        Adds variables to scope[0] from another scope.  The scope is
        defined by key_token, a name that is resolved using scopes
        surrounding scope[0]

        @param scopes The relevant scopes: scope[0] is the scope that
        is "using," while the other scopes are those surrounding
        scope[0].

        @param key_token The token containing the name of the scope
        that is to be used.

        @param only_scalars If True, then it is an error to "use" a 
        scope that contains variables with non-scalar values.

        @returns None"""
        assert(isinstance(key_token,Token))
        assert(isinstance(scopes,list))
        assert(len(scopes)>=2)
        assert(isinstance(scopes[0],Scope))
        key=key_token.token_value
        got=scopes[1].resolve(key)
        found_non_scalars=scopes[0].use_from(got,only_scalars)
        if only_scalars and found_non_scalars:
            self.error('use',key_token,'found non-scalars when '
                       'using %s'%(key,))
        # for k,v in got.iterlocal():
        #     if only_scalars and not isinstance(v,String):
        #         self.error('use',key_token,'found non-scalars when '
        #                    'using %s'%(key,))
        #     scopes[0].setlocal(k,v)
    def action_operator(self,scopes,token):
        """!Creates an object that represents the operator ".oper." in
        the expression "a .oper. b"

        @param scopes a list of nested scopes (outermost first) surrounding the expression
        @param token the token containing the name of the operator

        @returns an object that represents the operator"""
        assert(isinstance(token,Token))
        if token.token_value=='.copy.':
            return Copy(scopes)
        elif token.token_value=='.copydir.' or token.token_value=='.copyfrom.':
            return CopyDir(scopes)
        elif token.token_value=='.bitcmp.':
            return BitCmp(scopes)
        elif token.token_value=='.nccmp_vars.':
            return NccmpVars(scopes)
        elif token.token_value=='.md5cmp.':
            return Md5Cmp(scopes)
        elif token.token_value=='.link.':
            return Link(scopes)
        elif token.token_value=='.atparse.':
            return AtParse(scopes)
        else:
            self.error('operator name',token,'unknown operator '+
                       token.token_value)
    def action_numeric(self,scopes,token):
        """!Returns a Numeric object for the given token.

        @param scopes a list of nested scopes (outermost first) surrounding the number
        @param token The token containing the number
        @returns a Numeric object"""
        value=float(token.token_value)
        return Numeric(value)
    def action_string(self,scopes,token):
        """!Returns a String object for the given token.

        @param scopes a list of nested scopes (outermost first) surrounding the string
        @param token The token containing the string
        @returns a String object"""
        assert(isinstance(token,Token))
        if token.token_type=='qstring':
            s=String(scopes,token.token_value,False)
        elif token.token_type=='dqstring':
            s=String(scopes,dqstring2bracestring(token.token_value),True)
        elif token.token_type=='bracestring':
            s=String(scopes,token.token_value,True)
        else:
            raise ValueError('Invalid token for a string: '+repr(token))
        # yell('%-7s %s = %s\n'%('STRING',repr(token.token_value),repr(s)))
        return s
    def action_reference(self,varname_token,scopes):
        return Reference(varname_token.token_value,scopes)
    def action_resolve(self,varname_token,scopes):
        """!Resolves a variable reference within a scope.

        @param varname_token The token containing the name of the variable reference.
        @param scopes a list of nested scopes (outermost first) surrounding the reference
        @returns the value of the referenced variable
        @raise PTKeyError if no such variable exists"""
        varname=varname_token.token_value
        for scope in scopes:
            try:
                return scope.resolve(varname)
            except PTKeyError as ke:
                pass
        raise PTKeyError(varname)
    def action_null_param(self,varname,scope):
        """!Defines a variable with no value in the given scope.

        @param varname the name of the variable, a string
        @param scope the scope in which to define the variable
        @returns None"""
        if '%' in varname:
            raise ValueError('%s: cannot have "%" in a parameter name.'%(
                    varname,))
        scope.check_define(varname,null_value)
    def action_assign_var(self,toscope,tovar,fromvar,fromscopes,
                          allow_overwrite):
        """!Assigns a value to a variable within a scope, from another
        variable in another scope.

        @param toscope The scope in which a variable is being defined.
        @param tovar The target variable name
        @param fromvar The variable reference to the source variable
        @param fromscopes The scopes, innermost first, in which to resolve
          the fromvar variable reference
        @param allow_overwrite If True, redefining tovar within toscope is allowed."""
        if fromscopes:
            value=fromscopes[0].resolve(fromvar)
        else: # Global scope assignment
            value=toscope.resolve(fromvar)
        self.action_assign(toscope,tovar,value,allow_overwrite)
    def action_assign(self,scope,varname,value,allow_overwrite):
        """!Assigns a value to a variable within a scope

        @param scope The scope in which to assign.
        @param varname The name of the variable within the scope, a string.
        @param value The value of the variable, a BaseObject
        @param allow_overwrite If True, replacing an existing
          variable's value is allowed.
        @return None"""
        assert(isinstance(scope,Scope))
        assert(isinstance(varname,str))
        assert(isinstance(value,BaseObject))
        if '%' in varname:
            raise ValueError('Cannot assign to %s; subscope definitions must be of syntax "var1 = { var2= { ...."'%(
                    varname,))
        # yell('%-7s %s = %s IN %s\n'%(
        #     'ASSIGN', varname, repr(value),repr(scope) ))
        if allow_overwrite:
            scope.force_define(varname,value)
        else:
            scope.check_define(varname,value)
    def action_run_in_set(self,setname,obj,con):
        """!Requests that a specified object be available for running,
        within a specific runset.  This is used to implement the part
        list of runsets in the "run" statement.

        @param setname The name of the set in which to run.
        @param obj The object to run.
        @param con The produtil.testing.parsetree.Context from which
        the run statement is made."""
        # yell('%-7s %s\n'%(
        #     'RUN', repr(obj)))
        return self.add_run(setname,obj,con)
    def action_run_by_name(self,obj,con):
        """!Requests that a specified object be available for running,
        without putting it in any runset.  This is used to implement
        the part of the "run" statement before set lists.
        
        @param obj The object to run.
        @param con The produtil.testing.parsetree.Context from which
        the run statement is made."""
        return self.add_run(None,obj,con)
    def error(self,mode,token,reason=None):
        """!Convenience function for error messages.

        Raises an exception explaining that an input file contains an
        error.  This is used for most syntax or semantic errors.

        @param mode The run mode, which can be anything that can be
         cast to a string via str()
        @param token The token at which the error occurred, or None
         if the end of the file was reached.
        @param reason
        @returns Never.  Always raises an exception."""
        if token is None:
            raise PTParserError('Unexpected end of file.')
        elif reason:
            raise PTParserError('%s:%s: %s (%s token with value %s)'%(
                    token.filename,token.lineno,str(reason),
                    repr(token.token_type),
                    repr(elipses(str(token.token_value)))))
        else:
            raise PTParserError(
                '%s:%s: unexpected %s in %s (token value %s)'%(
                    token.filename, token.lineno, repr(token.token_type),
                    str(mode), repr(elipses(str(token.token_value)))))
