##@namespace produtil.testing.parsetree
# Parse tree classes for the produtil.testing suite.
#
# The produtil.testing.parse.Parser class uses this module to
# construct a parse tree of the test suite.  The tree consists of
# subclasses of BaseObject, connected to one another by scopes or
# operators.  The Context class provides filename, line number, run
# mode, call stack, and other information which the BaseObject
# subclasses use for evaluation to literals.

import sys, re, io, collections, os, datetime, logging, math
import produtil.run, produtil.log, produtil.setup

# This module really does use everything public from utilities and
# tokenize, hence the "import *"
from produtil.testing.utilities import *
from produtil.testing.tokenize import *

__all__=[ 'Context', 'BaseObject', 'null_value', 'TypelessObject', 'Scope',
          'make_params', 'make_scope', 'call_scope', 'Builtin', 'Copy', 
          'CopyDir', 'Link', 'AtParse', 'BitCmp', 'Criteria', 'Filters',
          'Rank', 'SpawnProcess', 'EmbedBash', 'Task', 'Build', 'Platform',
          'Test', 'AutoDetectPlatform', 'Numeric', 'String', 'Environ',
          'Md5Cmp', 'Reference', 'NccmpVars']

class Context(object):
    """!Represents the context from which a BaseObject is accessed.  

    The Context is used during any evaluation of a BaseObject to a
    logical, numeric, block of bash code, or other type.  A Context consists
    of the relevant token (for filename and line number), the run mode
    (baseline or execution), the call stack, and logging information.
    The BaseObject subclasses use that information for variable
    resolution or error reporting."""
    def __init__(self,scopes,token,run_mode,logger,verbose=True):
        """!Constructor for Context

        @param scopes The call stack for the context, innermost scope first.
        @param token The token that represents the Context; this is for
           error reporting.
        @param run_mode produtil.testing.utilities.BASELINE or
          produtil.testing.utilities.EXECUTION
        @param logger a logging.Logger object to log messages
        @param verbose send extra logging to assist debugging or tracking progress. """
        super(Context,self).__init__()
        self.run_mode=run_mode
        self.token=token
        self.scopes=scopes
        if logger is None:
            logger=module_logger
        self.logger=logger
        self.verbose=bool(verbose)
    @property
    def filename(self):
        """!The filename from self.token"""
        return self.token.filename
    @property
    def lineno(self):
        """!The line number from self.token"""
        return self.token.lineno

    def __str__(self):
        return "%s:%s"%(self.token.filename,str(self.token.lineno))

    def mpirunner(self,spawnProcess):
        """!Returns an object that can run the MPI program described
        in the spawnProcess.  The base class does not implement this;
        subclasses must override this function.

        @param spawnProcess a SpawnProcess object to run."""
        raise NotImplementedError('Base Context class does not know how '
                                  'to run MPI processes.')
    def info(self,message):
        """!Logs a message at logging.INFO level to self.logger
        @param message a string message to log"""
        message="%s:%s: %s"%(
                str(self.token.filename),
                repr(self.token.lineno),
                message)
        self.logger.info(message)
        return message
    def warning(self,message):
        """!Logs a message at logging.WARNING level to self.logger
        @param message a string message to log"""
        message="%s:%s: %s"%(
                str(self.token.filename),
                repr(self.token.lineno),
                message)
        self.logger.warning(message)
        return message
    def error(self,message):
        """!Logs a message at logging.ERROR level to self.logger
        @param message a string message to log"""
        message="%s:%s: %s"%(
                str(self.token.filename),
                repr(self.token.lineno),
                message)
        self.logger.error(message)
        return message

def fileless_context(scopes=None,filename=None,lineno=None,
                     run_mode=None,logger=None,verbose=True):
    """!Generates a Context object that is not connected to a
    Tokenizer.  This is to be used when resolving and evaluating
    objects from outside the workflow description.

    @param scopes Optional: the call stack, innermost scope first
    @param filename Optional: a filename representative of the Context
    @param lineno Optional: a line number representative of the Context
    @param run_mode """
    if scopes is None: scopes=[]
    if filename is None: filename=unknown_file
    if lineno is None: lineno=-1
    if logger is None: logger=module_logger
    if run_mode is None: run_mode=EXECUTION
    return Context(
        scopes,Token(end_of_line_type,end_of_line_type,filename,lineno),
        run_mode,logger,verbose)

class BaseObject(object):
    """!Base class of the parsetree hierarchy.  

    This class implements default behaviors representative of any
    parsetree node.  The properties and functions should be overridden
    by subclasses, as appropriate."""

    ##@var defscopes
    # A list of Scope objects that represent the call stack at
    # which this object is being called, or the stack to the context
    # at which the object is being defined.  Innermost Scope is first.

    ##@var is_scope
    # If True, this object can be treated as a Scope

    ##@var is_filters
    # If True, this object can be treated as a set of filters

    ##@var is_criteria
    # If True, this object can be treated as a list of output validation criteria

    ##@var is_scalar
    # If True, this is a scalar, such as a number or string.

    ##@var can_be_used
    # If True, this object is a valid target for a "use" statement

    ##@var is_test
    # If True, this object can be used as a Test.  This means it can
    # be, and have, dependencies.  It must also have a COM variable.

    def __init__(self,defscopes,set_flags=True):
        """!Constructor for BaseObject
        @param defscopes The list of nested scopes to the point at
        which this object is defined.  The innermost scope is listed
        first."""
        for s in defscopes:
            if not isinstance(s,Scope):
                raise TypeError('In BaseObject(), the defscopes must be a list '
                                'of Scope objects.  One of them is a %s %s'%(
                                    type(s).__name__,repr(s)))
        self.defscopes=defscopes
        if set_flags:
            self.is_scope=False
            self.is_filters=False
            self.is_criteria=False
            self.is_scalar=False
            self.can_be_used=False
            self.is_test=False
    def bash_context(self,con):
        """!Expresses this object in bash code.

        This function is intended to express this object as bash code.
        The default implementation raises an exception.

        @param con the Context in which this object is being evaluated
        @returns a string containing this object expressed in bash code"""
        raise PTParserError("Cannot express null_value in a bash string.")
    def oldcmp(self,other):
        iself=id(self)
        iother=id(other)
        if iself<iother: return -1
        if iself>iother: return 1
        return 0
    def is_valid_rvalue(self,con): 
        """!Can this value be assigned to a variable?
        @returns True if this BaseObject represents a value that can be
        assigned to a variable, False otherwise
        @param con the Context in which this object is being evaluated"""
        return True
    def string_context(self,con): 
        """!Expresses this object as a printable string

        Expresses the object as a human-readable string in the provide
        context.  The default implementation returns "null"

        @returns A string representation of this object
        @param con the Context in which this object is being evaluated"""
        return "null"
    def logical_context(self,con): 
        """!Expresses this object as a printable string

        Expresses the object as a boolean True/False value.  The
        default implementation returns False

        @returns A boolean representation of this object
        @param con the Context in which this object is being evaluated"""
        return False
    def numeric_context(self,con): 
        """!Expresses this object as a float

        Expresses the object as a Python float.  The default implementation
        returns 0.0

        @returns A float representation of this object
        @param con the Context in which this object is being evaluated"""
        return 0.0
    def _apply_rescope(self,scopemap=None,prepend=None):
        """!Replaces Scope objects in this object's defscopes variable.

        This function is the internal implementation of the "use"
        blocks and function calls when parsing or evaluating.
        Subclasses with a rescope() or similar function use
        _apply_rescope() to implement such functions.

        @param scopemap A mapping from old Scope to new Scope
        @param prepend A list of Scope objects to prepend to defscopes
        @protected"""
        if not prepend: prepend=[]
        if not scopemap: scopemap={}
        self.defscopes=prepend+[ scopemap[s] if s in scopemap else s
                                 for s in self.defscopes ]
        for s in self.defscopes:
            if not isinstance(s,Scope):
                raise TypeError(
                    'In make_scope, the defscopes must be a list '
                    'of Scope objects.  One of them is a %s %s'%(
                        type(s).__name__,repr(s)))

    def rescope(self,scopemap=None,prepend=None):
        """!Modifies this object's scopes, and that of any subobjects.

        Subclasses that can be expressed as non-constant values must
        implement this function for rescoping.  This function changes
        the stack of defining scopes, defscopes, based on arguments

        @param scopemap a mapping from old Scope to new Scope during
        the replacement

        @param prepend a list of Scope objects to prepend.  These
        become the innermost scopes.  The scopemap is NOT applied to
        the prepend list.
        @returns self"""
        raise NotImplementedError('Subclass %s did not implement rescope()'%(type(self).__name__,))
    def run(self,con): 
        """!Instructs this object to execute.

        Subclasses that can be executed, such as scripts, must
        implement this function to execute themselves.  The default
        implementation logs the string representation of this object
        at logging.INFO level.

        @param con the Context in which this object is being
        evaluated.  This Context is also used to get the logger for
        logging in the default implementation of this function.
        @returns None"""
        con.logger.info(self.string_context(con))
    def iterdeps(self):
        """!Iterates over all runnable objects that are dependencies
        of this object.

        Objects that can be executed, such as Test or Build, have a
        list of dependencies.  Those dependencies are instances of
        BaseObject subclasses, such as other Test or Build objects."""
        return
        yield 'a' # Syntactic trick to ensure this is an iterator.
    def __repr__(self):
        return '<BaseObject@%s>'%(id(self),)
    def __str__(self):
        return '<BaseObject@%s>'%(id(self),)

##@var null_value
# A special constant that indicates a variable without a value. 
# @warning Terrible things will happen if you overwrite this.
null_value=BaseObject([])

########################################################################

class TypelessObject(BaseObject):
    """!Represents an object that cannot be evauated in any context.
    This is a convenience class intended to be used by subclasses to
    disable all but certain contexts."""
    def bash_context(self,con):
        """!Raises TypeError to indicate the object cannot be evaluated.
        @param con the Context in which this object is being evaluated"""
        raise TypeError('Cannot evaluate %s in a bash context.'%(
                type(self).__name__,))
    def string_context(self,con):
        """!Raises TypeError to indicate the object cannot be evaluated.
        @param con the Context in which this object is being evaluated"""
        raise TypeError('Cannot evaluate %s in a string context.'%(
                type(self).__name__,))
    def logical_context(self,con):
        """!Raises TypeError to indicate the object cannot be evaluated.
        @param con the Context in which this object is being evaluated"""
        raise TypeError('Cannot evaluate %s in a logical context.'%(
                type(self).__name__,))
    def numeric_context(self,con):
        """!Raises TypeError to indicate the object cannot be evaluated.
        @param con the Context in which this object is being evaluated"""
        raise TypeError('Cannot evaluate %s in a numeric context.'%(
                type(self).__name__,))
    def run(self,con):
        """!Raises TypeError to indicate the object cannot be executed.
        @param con the Context in which this object is being evaluated"""
        raise TypeError('Cannot run objects of type %s.'%(
                type(self).__name__,))

########################################################################

class Reference(BaseObject):
    """!Represents a reference to another variable"""
    def __init__(self,path,defscopes=None):
        if defscopes is None:
            defscopes=list()
        super(Reference,self).__init__(defscopes,set_flags=False)
        self.__path=path
        
    @property
    def is_scope(self):
        return self.dereference().is_scope
    @property
    def is_filters(self):
        return self.dereference().is_filters
    @property
    def is_criteria(self):
        return self.dereference().is_criteria
    @property
    def is_scalar(self):
        return self.dereference().is_scalar
    @property
    def can_be_used(self):
        return self.dereference().can_be_used
    @property
    def is_test(self):
        return self.dereference().is_test
    def override_local(self,defscopes,key,val):
        return self.dereference().override_local(defscopes,key,val)
    def no_nulls(self):
        return self.dereference().no_nulls()
    def get_type(self,key):
        return self.dereference().get_type(key)
    def as_parameters(self,con):
        return self.dereference().as_parameters(con)
    def has_parameters(self):
        return self.dereference().has_parameters()
    def has_constants(self):
        return self.dereference().has_constants()
    def use_from(self,used_scope,only_scalars=False):
        return self.dereference().use_from(used_scopes,only_scalars)
    def apply_parameters(self,scope,con):
        return self.dereference().apply_parameters(scope,con)
    def subscope(self,key):
        return self.dereference().subscope(key)
    def getlocal(self,key):
        return self.dereference().getlocal(key)
    def setlocal(self,key):
        return self.dereference().setlocal(key)
    def haslocal(self,key):
        return self.dereference().haslocal(key)
    def iterlocal(self):
        for i in self.dereference().iterlocal():
            yield i
    def force_define(self,key,value,skip_constants=False):
        return self.dereference().force_define(key,value,skip_constants)
    def check_define(self,key,value):
        return self.check_define(key,value)
    def expand_string(self,key,value):
        return self.dereference().expand_string(string,con,scopes)
    def new_empty(self):
        return Reference(self.__path,self.defscopes)
    @property
    def path(self):
        return self.__path
    def rescope(self,scopemap=None,prepend=None):
        r=self.new_empty()
        r._apply_rescope(scopemap,prepend)
        return r
    def resolve(self,key,scopes=None):
        return self.dereference().resolve(key,scopes=scopes)
    def dereference(self):
        return self.defscopes[0].resolve(self.__path,self.defscopes[1:])
    def bash_context(self,con):
        return self.dereference().bash_context(con)
    def string_context(self,con):
        return self.dereference().string_context(con)
    def logical_context(self,con):
        return self.dereference().logical_context(con)
    def numeric_context(self,con):
        return self.dereference().numeric_context(con)
    def __str__(self):
        return 'Reference(path=%s)'%(str(self.__path),)
    def __repr__(self):
        return 'Reference(path=%s)'%(repr(self.__path),)
    def __bool__(self):
        return bool(self.__path)

########################################################################

class Scope(BaseObject):
    """!Represents a scope; the region of which a name binding can be
    evaluated. This includes hashes, tests, argument lists, and
    anything else with variable names or named arguments."""
    def __init__(self,defscopes=None):
        if defscopes is None:
            defscopes=list()
        super(Scope,self).__init__(defscopes)
        self.__const=dict()
        self.__vars=dict()
        self.__parameters=dict()
        self.is_scope=True
        self.can_be_used=True
        self.__overrides=collections.defaultdict(list)

    def __eq__(self,other):
        """!Scopes are equal iff they are the same object.
        @param the other Scope against which to compare"""
        return self is other

    def override_local(self,defscopes,key,val):
        """!Overrides a variable already defined in this scope or its subscopes

        @param defscopes a list of Scope objects that represent scopes
        outside of this one for the purpose of variable overrides
        @param key the path to the variable to override.  This may
        include "%" but it is always relative to this scope.
        @param val the valuate to assign.  This is re-expressed as a String"""
        names=splitkey(key)
        the_string=String(self.defscopes+[self],val,False)
        #print 'overrides %s%%%s = %s'%(repr(names[0]),repr(names[1:]),repr(the_string))

        self.__overrides[names[0]].append([ names[1:],the_string])

    def validate_parameter(self,name): 
        """!Raises an exception if the given name is not an acceptable
        keyword for constants or parameters.  The default
        implementation does nothing."""
        pass

    def new_empty(self): 
        """!Returns a new, empty scope that is within the same parent
        scope of this Scope (has the same defscopes)."""
        return Scope(self.defscopes)

    def bash_context(self,con):
        """!Raises an exception to indicate that a Scope cannot be
        expressed in bash code.
        @param con the Context in which this object is being evaluated"""
        raise PTParserError("Cannot express a hash in a bash string.")

    def string_context(self,con): 
        """!Evaluates the _as_string variable in this scope, in a
        string context, if it is defined.  Otherwise, returns the
        Python id of this Scope (id(self)) as a string.
        @param con the Context in which this object is being evaluated"""
        if self.haslocal('_as_string'):
            value=self.getlocal('_as_string')
            return value.string_context(con)
        else:
            return str(id(self))

    def no_nulls(self):
        """!Are there any local variables defined to have null values?
        @returns False if any local variable has a null_value, or True
        if no variables have null values """
        for k,v in self.iterlocal():
            if v is null_value:
                return False
        return True

    def _set_parameters(self,update):
        """!Internal implementation function that updates the list of
        parameters (arguments to function call)
        @param update a dict containing the new variable names and values"""
        self.__parameters.update(update)
        for p in self.__parameters.keys():
            self.validate_parameter(p)

    def _set_constants(self,update):
        """!Internal implementation function that updates the list of
        constants in this scope
        @param update a dict containing the new variable names and values"""
        self.__const.update(update)
        for p in self.__const.keys():
            self.validate_parameter(p)

    def numeric_context(self,con):
        """!Evaluates this scope in a numeric context

        @returns the number of variables, parameters (function call
        arguments) and constants defined in this Scope
        @param con the Context in which this object is being evaluated (unused)"""
        return len(self.__vars) + len(self.__parameters) + len(self.__const)

    def logical_context(self,con): 
        """!Evaluates this scope in a logical context
        @returns True if any variables, parameters (function call
        arguments) or constants are defined in this Scope.  Returns False otherwise.
        @param con the Context in which this object is being evaluated (unused)"""
        return bool(self.__vars) or bool(self.__parameters) or bool(self.__const)

    def get_type(self,key):
        """!Returns the type of variable that the key represents

        Searches for a variable name in the parameter (function call
        argument) list, the constant variable list, and the local
        variable list, in that order.  Returns the type of variable
        based on the first of those three lists that contains the
        variable name.  Note that this only searches for variable
        names; it will not work for variable paths (names containing "%")

        @param key the variable to search for; must not contain "%"
        @returns the variable type: "parameter" "constant" "var" or None"""
        if key in self.__parameters:
            return 'parameter'
        elif key in self.__const:
            return 'constant'
        elif key in self.__vars:
            return 'var'
        else:
            return None

    def as_parameters(self,con):
        """!Changes all variables to parameters.
        @param con the Context in which this object is being evaluated"""
        self.__parameters.update(self.__vars)
        self.__vars=dict()
        for p in self.__parameters.keys():
            self.validate_parameter(p)
        return self

    def _apply_rescope(self,scopemap=None,prepend=None):
        """!Internal implementation of rescope()

        Modifies the the context of this Scope and everything below
        it.  This is done by replacing Scope objects in defscopes.
        Asks all variables and subscopes to do the same, recursively.

        @protected
        @param scopemap a mapping from old Scope to new Scope;
        elements of defscopes are replaced based on this mapping
        @param prepend a list of Scope objects to prepend to
        defscopes.  The scopemap is not applied to the prepend
        list.
        @returns None"""
        super(Scope,self)._apply_rescope(scopemap,prepend)
        for d in [ self.__parameters, self.__vars, self.__const]:
            for k,v in d.items():
                v._apply_rescope(scopemap,prepend)

    def rescope(self,scopemap=None,prepend=None):
        """!Changes the context of this Scope.

        Modifies the the context of this Scope and everything below
        it, including parameters, variables and constants.  This is
        done by replacing Scope objects in defscopes.  Asks all
        variables and subscopes to do the same, recursively.  This
        recursion is done by calling the _apply_rescope() function in
        each object.

        @param scopemap a mapping from old Scope to new Scope;
        elements of defscopes are replaced based on this mapping
        @param prepend a list of Scope objects to prepend to
        defscopes.  The scopemap is not applied to the prepend
        list.
        @returns self"""
        scope=self.new_empty()
        scope._apply_rescope(scopemap,prepend)
        for k,v in self.__parameters.items():
            scope.__parameters[k]=v.rescope(scopemap,prepend)
        for k,v in self.__vars.items():
            scope.__vars[k]=v.rescope(scopemap,prepend)
        for k,v in self.__const.items():
            scope.__const[k]=v.rescope(scopemap,prepend)
        return scope

    def has_parameters(self):
        """!Does this Scope contain parameters (function call arguments)?
        @return True if any parameters (function call arguments) are present, False otherwise."""
        return bool(self.__parameters)

    def has_constants(self):
        """!Are there any constants defined in this scope?
        @return True if this scope contains constants, False otherwise"""
        return bool(self.__const)

    def use_from(self,used_scope,only_scalars=False):
        """!Implements a "use" statement; copies definitions from another Scope

        Copies parameters, constants, and variables from another scope
        into this one.  Copies are modified to have this scope in
        their definition or calling stack via the rescope() function.

        @param used_scope The scope whose data is being copied.
        @param only_scalars If True, then only the objects with
        is_scalar=True are copied.
        @returns True if all variables seen were scalar, False if any
        non-scalar variables were seen.  This includes variables that
        were found, but not "used," due to only_scalars=True"""
        if used_scope.has_parameters():
            raise PTParserError('A function cannot have a "use" statement.')
        if not used_scope.is_scope:
            raise PTParserError('Target of "use" statement is not a scope.')
        if not used_scope.can_be_used:
            raise PTParserError('Target of "use" statement cannot be used.')
        prepend_me=[ self ]
        found_non_scalars=False
        for k,v in used_scope.iterlocal():
            if only_scalars and v.is_scope:
                found_non_scalars=True
            if k not in self.__const:
                my_v=v.rescope({used_scope:self})
                self.force_define(k,my_v)

        if used_scope.haslocal('RUNDIR'):
            mycon=fileless_context([self])
            usedcon=fileless_context([used_scope])
                
        return found_non_scalars
    def apply_parameters(self,scope,con):
        """!Implements a function call using this Scope as the parameter list.

        Creates a new Scope where all parameters in this scope are
        converted to local variables and possibly overridden.  Scope
        self's parameters are used for the default argument values.
        The "scope" argument to apply_parameters() contains values to
        override those.  Hence, self is the function definition and
        scope is the values set in the function call.  

        A third Scope is created, containing the result of applying
        the function call and default values.  That third Scope has no
        parameters; all parameters have been converted to local
        values.  The returned Scope has the same defscopes as self.
        That means any unresolved variables within the function will
        be resolved in the defining context, NOT the calling context.

        @param scope The arguments provided to the function call.
        @param con the Context at which this function is being called.
           The defining location is in defscopes.
        @returns a Scope representing the function call."""
        assert(not scope.__parameters)
        assert(self.__parameters)
        if not self.__parameters:
            return self
        s=self.new_empty()
        s._apply_rescope({self:s,scope:s})
        caller=con.scopes[0]
        #print('APPLY PARAMETERS from %s to %s type %s\n'%(
        #        repr(scope),repr(self),type(s).__name__))
        for k,v in scope.iterlocal():
            if not k in self.__parameters:
                raise PTKeyError('%s: not a valid argument to this function.'%(
                        str(k),))
        for k,v in self.__parameters.items():
            if scope.haslocal(k):
                s.__vars[k]=scope.getlocal(k).rescope({self:s,scope:s})
            elif v is not null_value:
                s.__vars[k]=v.rescope({self:s,scope:s})
            else:
                raise PTParserError('%s: no argument sent for this parameter'%(
                        k,))
        for k,v in self.__vars.items():
            if k not in s.__vars:
                s.__vars[k]=v.rescope({self:s,scope:s})
        for k,v in self.__const.items():
            if k not in s.__const:
                s.__const[k]=v.rescope({self:s,scope:s})
        #print('APPLY RESULT IS %s %s\n'%(
        #        type(s).__name__,repr(s)))
        return s

    def __str__(self):
        return '{' + ','.join( [
                "%s=%s"%(str(s),repr(k)) for s,k in self.iterlocal()
                ] ) + '}'

    def __repr__(self):
        return '{' + ','.join( [
                "%s=%s"%(str(s),repr(k)) for s,k in self.iterlocal()
                ] ) + '}'

    def subscope(self,key):
        """!Returns a Scope within this Scope, with the given name.
        
        @param key a valid identifier within this scope
        @returns a Scope with the given name, within this Scope
        @raise ValueError if the key contains a "%"
        @raise TypeError if the key refers to something in this Scope
          that is not a Scope.  This is detected through the is_scope 
          attribute or property."""
        if "%" in key:
            raise ValueError("Key \"%s\" is not a valid identifier"%(key,))
        if key in self.__parameters:
            value=self.__parameters[key]
        elif key in self.__const:
            value=self.__const[key]
        else:
            value=self.__vars[key]
        try:
            if value.is_scope:
                return value
        except AttributeError as ae:
            pass # value does not define is_scope
        raise TypeError("Key \"%s\" refers to something that is not a Scope."
                        %(key,))

    def getlocal(self,key):
        """!Return the value of a key local to this scope without
        searching other scopes.  Will raise ValueError if the key
        contains a "%" 

        @param key a valid identifier within this scope
        @returns The value of the key from this scope.
        @raise ValueError if the key is syntactically not a valid identifier
           such as one that contains a "%"
        @raise KeyError if the key is a valid identifier but is not
        within this scope."""
        if "%" in key:
            raise ValueError("Key \"%s\" is not a valid identifier"%(key,))
        if key in self.__parameters:
            return self.__parameters[key]
        elif key in self.__const:
            return self.__const[key]
        elif key in self.__vars:
            return self.__vars[key]
        raise PTKeyError(key)

    def setlocal(self,key,value):
        """!Sets the value of a key within this scope.

        @param key a valid identifier to set within this scope
        @param valuel the value of the identifier
        @raise ValueError if the key is not a valid identifier, such as
          one that contains a "%" """
        if not isinstance(value,BaseObject):
            raise TypeError('The value argument to setlocal must be a '
                            'subclass of BaseObject, not a %s %s'%(
                    type(value).__name__,repr(value)))
        if '%' in key:
            raise ValueError("Key \"%s\" contains a \"%\""%(key,))
        if key in self.__parameters:
            raise PTParserError("Attempted to redefine function argument \"%s\"."%(key,))
        elif key in self.__const:
            raise PTParserError("Attempted to redefine constant \"%s\"."%(key,))
        self.__vars[key]=value
        global over
        try:
            if key in self.__overrides:
                for names,override in self.__overrides[key]:
                    #print 'Check override %s %s'%(names[-1],override)
                    subscope=self
                    for name in [key]+names[0:-1]:
                        subscope=subscope.resolve(name)
                        assert(subscope.is_scope)
                        if not subscope.is_scope:
                            continue # raise KeyError(name)
                    assert(isinstance(override,BaseObject))
                    subscope.force_define(names[-1],override)
                return override
        except KeyError as ke:
            raise
        return value

    def haslocal(self,key):
        """!Is there a variable with this name?

        Searches the parameter list, variable list, and constants list
        for the given variable name.  The name must be local; it can
        contain no "%"

        @param key a local variable name (contains no "%")
        @returns True if any variable is set with the given name.
        """
        return key in self.__parameters or key in self.__vars or \
            key in self.__const

    def iterlocal(self):
        """!Iterates over all local variables in this order:
        parameters, constants, variables"""
        for k,v in self.__parameters.items():
            yield k,v
        for k,v in self.__const.items():
            yield k,v
        for k,v in self.__vars.items():
            yield k,v

    def resolve(self,key,scopes=None):
        """!Given a path to a variable, return the variable.

        Searches this scope and its containing scopes for the given
        variable.  The variable can be a path to a variable
        (containing "%") or a local variable (no "%").  If the scopes
        parameter is given, then those scopes are treated as the
        containing scopes; otherwise defscopes is used.

        @param key a local variable (no "%") or a path to a variable
        (containing "%")
        @param scopes Optional.  Replaces defscopes as the containing
        scopes to search if the variable is not defined in this
        scope.
        @returns a BaseObject for the requested variable
        @raise KeyError if no such variable is defined"""
        assert(isinstance(key,str))
        names=splitkey(key)
        con=fileless_context()
        if scopes is None:
            search=[self]+self.defscopes
        else:
            search=[self]+scopes
        #scopestack=list()
        # yell('search for %s = %s in %s\n'%(repr(key),repr(names),repr(search)))
        for name in names:
            found=None
            for scope in search:
                try:
                    found=scope.getlocal(name)
                    # if name=='TEST_NAME':
                    #     print 'Found %s in scope %s = "%s" name "%s"'%(
                    #         str(name),id(scope),elipses(scope.getlocal(
                    #                 'TEST_DESCR').string_context(con)),
                    #         scope.getlocal('TEST_NAME').string_context(con))
                    #scopestack.insert(0,scope)
                    break # Done searching scopes.
                except KeyError as ke:
                    # yell('Key %s not in scope %s from top %s\n'%(
                    #         repr(name),repr(scope),repr(self)))
                    continue # Check for name in next scope.
            if found is None:
                raise PTKeyError(key)
            search=[found]
        if found is None:
            raise PTKeyError(key)
        # if subscopes: 
        #     return ( found, scopestack )
        # else:
        return found

    def force_define(self,key,value,skip_constants=False):
        """!Sets the value of a variable, replacing the value if a
        variable is already defined with that name.

        @param key the local variable name (must contain no "%")
        @param value a valid rvalue (is_rvalue=True)
        @param skip_constants if True, the variable is NOT overridden
        if it is already defined as a constant

        @returns the value, or None if no action was performed.  That
        can happen if skip_constants is True, and the name corresponds
        to a constant."""
        names=splitkey(key)
        lval=self
        for i in range(len(names)-1):
            lval=lval.getlocal(names[i])
        if skip_constants and lval.get_type(names[-1])=='constant':
            #module_logger.info('Do not redefine %s.'%(key,))
            return None
        assert(names[-1]!='TEST_NAME')
        lval.setlocal(names[-1],value)
        return value

    def check_define(self,key,value):
        """!Defines a local variable, raising an exception if a
        variable is already defined with the given name.

        @param key the local variable name (no "%")
        @param value a BaseObject that is a valid rvalue (is_rvalue=True)
        @returns value"""
        names=splitkey(key)
        lval=self
        for i in range(len(names)-1):
            lval=lval.subscope(names[i])
        assert(names[-1]!='TEST_NAME')
        if lval.haslocal(value):
            raise PTParserError('Symbol %s is already declared in this scope.'%(key,))
        #yell('setlocal %s = %s\n'%(names[-1],value))
        lval.setlocal(names[-1],value)
        return value

    def expand_string(self,string,con,scopes=None):
        """!Performs string expansion.

        Expands escape characters and variable references in a string.  

        @param string a python string to expand
        @param con the Context in which this object is being evaluated
        @param scopes sent to resolve(); these scopes will be searched instead
        of defscopes when a variable is not found in this scope.
        @returns the resulting python string"""
        stream=io.StringIO()
        # if string.find('TEST_NAME')>-1:
        #     print 'Expand "%s"'%(elipses(string,max_length=80),)
        # yell('Expand %s in %s\n'%(repr(string),repr(self)))
        def streamwrite(s):
            #yell("Append \"%s\" to output string.\n"%(s,))
            stream.write(s)
        for m in re.finditer(r'''(?sx)
            (
                (?P<text>[^@]+)
              | @ \[ (?P<escaped_at>@ ) \]
              | @ \[ ' (?P<escaped_text> [^']+ ) ' \]
              | @ \[ (?P<varexpr>[^\]]+) \]
              | (?P<literal_at>@ ) (?! \[ )
              | (?P<error>.)
            )''',string):
            if m.group('text'):
                streamwrite(m.group())
            elif m.group('escaped_text'):
                streamwrite(m.group('escaped_text'))
            elif m.group('escaped_at'):
                streamwrite(m.group('escaped_at'))
            elif m.group('literal_at'):
                streamwrite(m.group('literal_at'))
            elif m.group('varexpr'):
                streamwrite(self.resolve(m.group('varexpr'),scopes) \
                                .string_context(con))
            else:
                raise ValueError("Parser error: invalid character \"%s\" in"
                                 " \"%s\"\n"%(m.group(0),string))
        val=stream.getvalue()
        # if string.find('TEST_NAME')>-1:
        #     print 'Result "%s"'%(elipses(val,max_length=120),)
            #assert(val.find('nmm_cntrl')==-1)
        stream.close()
        return val

def make_params(defscopes,**kwargs):
    """!Returns a new Scope with the given parameter list (function
    call definition)

    @param defscopes the new Scope's defining or calling location; a
    list of Scopes.  This will be copied into the defscopes member
    variable.
    @param kwargs (key,value) pairs mapping parameter name to the BaseObject value
    @returns a new Scope representing the given function definition"""
    s=Scope(defscopes)
    for k,v in kwargs.items():
        s.setlocal(k,v)
    return s.as_parameters()

def make_scope(defscopes,**kwargs):
    """!Creates a new scope with local variables defined

    @param defscopes the new Scope's defining or calling location; a
    list of Scopes.  This will be copied into the defscopes member
    variable.
    @param kwargs (key,value) pairs mapping variable name to the BaseObject value
    @returns a new Scope representing the given hash definition"""
    for scope in defscopes:
        if not isinstance(scope,Scope):
            raise TypeError('In make_scope, the defscopes must be a list '
                            'of Scope objects.  One of them is a %s %s'%(
                                type(scope).__name__,repr(scope)))
    s=Scope(defscopes)
    for k,v in kwargs.items():
        s.setlocal(k,v)
    return s

def call_scope(scope,con,defscopes,**kwargs):
    """!Implements a function call.

    @param scope the function to call
    @param con Unused.  This Context is passed to Scope.apply_parameters().
    @param defscopes the call stack to the location at which the
    function call is made
    @param kwargs arguments to the function call.  These will override
    default values set in scope.
    @returns the function call, as a Scope"""
    parms=make_scope(defscopes,**kwargs)
    assert(parms.no_nulls())
    s=scope.apply_parameters(parms,con)
    assert(s.no_nulls())
    return s
    
########################################################################

class Builtin(Scope):
    """!An abstract base class that represents a built-in operator,
    such as bit-wise comparison."""
    def __init__(self,defscopes,opname):
        """!Builtin constructor

        @param defscopes a stack of Scopes to the point at which the
        operator is defined, innermost Scope first.
        @param opname the string name of the operator        """
        super(Builtin,self).__init__(defscopes)
        self.__opname=opname
    def bash_context(self,con):
        """!Raises TypeError to indicate that the operator cannot be
        expressed in bash code."""
        raise TypeError('Cannot evaluate built-in operator %s in a '
                        'bash context.'%(self.__opname,))
    def string_context(self,con):
        """!Raises TypeError to indicate that the operator cannot be
        expressed as a string."""
        raise TypeError('Cannot evaluate built-in operator %s in a '
                        'string context.'%(self.__opname,))
    def logical_context(self,con):
        """!Raises TypeError to indicate that the operator cannot be
        expressed as a logical value."""
        raise TypeError('Cannot evaluate built-in operator %s in a '
                        'logical context.'%(self.__opname,))
    def numeric_context(self,con):
        """!Raises TypeError to indicate that the operator cannot be
        expressed as a numeric value."""
        raise TypeError('Cannot evaluate built-in operator %s in a '
                        'numeric context.'%(self.__opname,))
    def getcom(self,con):
        """!Returns the COM directory for the test that contains this
        operation.

        Walks up the nested scopes from inner to outer, searching for
        the innermost Test (detected via BaseObject.is_test).  When
        found, asks the test to resolve the "COM" symbol, and returns
        the result of that objects string_context function.

        @param con a Context from which this function is called

        @returns The COM directory for the innermost test in the
        defscopes as a string."""
        for scope in self.defscopes:
            if scope.is_test:
                return scope.resolve('COM').string_context(con)
        raise PTKeyError('COM')

    def run(self,con):
        """!Raises TypeError to indicate that the operator cannot be executed"""
        raise TypeError('Cannot run built-in operator %s.'%(self.__opname,))

    def __str__(self):
        return '(%s %s %s)'%(
            str(self.resolve('src')), self.__opname, str(self.resolve('tgt')))

    def new_empty(self):
        """!Returns a copy of self."""
        return Builtin(self.defscopes,self.__opname)

########################################################################

class Copy(Builtin):
    """!An operator that represents file copying."""
    def __init__(self,defscopes,empty=False):
        """!Constructor for Copy
        @param defscopes a stack of Scope objects to the point at which this Copy was defined, innermost Scope first
        @param empty if True, the "src" and "tgt" parameters will be
        set to the null_value.  If False, no variables will be set."""
        super(Copy,self).__init__(defscopes,'.copy.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        """!Creates a new, empty Copy object defined in the same
        location (defining stack of Scope objects) as self.
        @returns the new Copy"""
        return Copy(self.defscopes,empty=True)
    def run(self,con):
        """!Executes the copy using produtil.fileop.deliver_file()
        @param con the Context in which this object is being evaluated
        @returns None"""
        assert(self.no_nulls())
        src=self.resolve('src').string_context(con)
        tgt=self.resolve('tgt').string_context(con)
        produtil.fileop.deliver_file(src,tgt)
    def bash_context(self,con):
        """!Returns bash code that would execute the copy
        @param con the Context in which this object is being evaluated
        @returns the bash code in a string"""
        assert(self.no_nulls())
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').bash_context(con)
        return 'deliver_file %s %s\n'%(src,tgt)

########################################################################

class CopyDir(Builtin):
    """!Represents a copy of a set of files from a source directory to
    the local directory.  The operator source (src) is the directory
    from which to copy, and the operator target (tgt) is a glob for
    the files in that directory to copy."""
    def __init__(self,defscopes,empty=False):
        """!Constructor for CopyDir
        @param defscopes a stack of Scope objects to the point at which this CopyDir was defined, innermost Scope first
        @param empty if True, the "src" and "tgt" parameters will be
        set to the null_value.  If False, no variables will be set."""
        super(CopyDir,self).__init__(defscopes,'.copydir.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        """!Creates a new, empty CopyDir object defined in the same
        location (defining stack of Scope objects) as self.
        @returns the new CopyDir"""
        return CopyDir(self.defscopes,empty=True)
    def run(self,con):
        """!Not implemented; raises NotImplementedError"""
        raise NotImplementedError('CopyDir.run is not implemented yet.')
    def bash_context(self,con):
        """!Generates bash code that will copy the specified files.
        @param con the Context in which this object is being evaluated
        @returns the bash code as a string"""
        assert(self.no_nulls())
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').string_context(con)
        return '''
(
  shopt -u failglob ;
  shopt -s nullglob ;
  glob='%s'/$( basename '%s' )
  tgtdir=$( dirname '%s' )
  mkdir -p "$tgtdir"
  for srcfile in $glob ; do
    deliver_file "$srcfile" "$tgtdir/$( basename $srcfile )" ;
  done
)
'''%(src,tgt,tgt)

########################################################################

class Link(Builtin):
    """!An operator that represents creation of a symbolic link.  The
    source ("src") is the name of the link and the target ("tgt") is
    the file to link to."""
    def __init__(self,defscopes,empty=False):
        """!Constructor for Link
        @param defscopes a stack of Scope objects to the point at which this Link was defined, innermost Scope first
        @param empty if True, the "src" and "tgt" parameters will be
        set to the null_value.  If False, no variables will be set."""
        super(Link,self).__init__(defscopes,'.link.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        """!Creates a new, empty Link object defined in the same
        location (defining stack of Scope objects) as self.
        @returns the new Link"""
        return Link(self.defscopes,empty=True)
    def run(self,con):
        """!Makes the symbolic link using produtil.fileop.make_symlink"""
        assert(self.no_nulls())
        src=self.resolve('src').string_context(con)
        tgt=self.resolve('tgt').string_context(con)
        produtil.fileop.make_symlink(src,tgt)
    def bash_context(self,con):
        """!Generates bash code that will make the symlink
        @param con the Context in which this object is being evaluated
        @returns the bash code as a string"""
        assert(self.no_nulls())
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').bash_context(con)
        return 'rm -f %s\nln -sf %s %s\n'%(tgt,src,tgt)

########################################################################

class AtParse(Builtin):
    """!Represents the "atparse" command, which parses files,
    converting \@[varname] constructs into the variable's value.  The
    "src" variable is the *.IN file passed into atparse, while the
    "tgt" is the output file for the parsed value."""
    def __init__(self,defscopes,empty=False):
        """!Constructor for AtParse
        @param defscopes a stack of Scope objects to the point at which this AtParse was defined, innermost Scope first
        @param empty if True, the "src" and "tgt" parameters will be
        set to the null_value.  If False, no variables will be set."""
        super(AtParse,self).__init__(defscopes,'.atparse.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        """!Returns a new, empty, AtParse with the defining scopes
        (defscopes) the same as self."""
        return AtParse(self.defscopes,empty=True)
    def run(self,con):
        """!Raises NotImplementedError to indicate AtParse.run() is
        not implemented yet.
        @param con the Context in which this object is being evaluated"""
        raise NotImplementedError('You cannot "run" an atparse object.')
    def bash_context(self,con):
        """!Generates a block of bash code that will parse the file.
        @param con the Context in which this object is being evaluated
        @returns the resulting block of bash code"""
        out=io.StringIO()
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').bash_context(con)
        out.write("echo input to atparse from %s:\ncat %s\n"%(src,src))
        out.write("echo send to %s\n"%(tgt,))
        out.write("cat %s | atparse \\\n"%(src,))
        seen=set()
        for scope in self.defscopes:
            for k,v in scope.iterlocal():
                if k in seen: continue
                seen.add(k)
                if '%' in k or '.' in k:
                    pass#out.write('# $%s: skip; invalid shell variable name\n'%(k,))
                elif k[0:2] == '__':
                    pass#out.write("# $%s: skip; name begins with __\n"%(k,))
                elif v is null_value:
                    pass#out.write('# $%s: skip; has no value\n'%(k,))
                elif not v.is_scalar:
                    pass#out.write('# $%s: skip; value is not scalar\n'%(k,))
                else:
                    out.write('  %s=%s \\\n'%(k,v.bash_context(con)))
        out.write("  > %s\n"%(tgt,))
        if con.verbose:
            out.write("set -xe\n")
        else:
            out.write("set -e\n")
        out.write('cat %s\n\n'%(tgt,))
        ret=out.getvalue()
        out.close()
        return ret

########################################################################

class BitCmp(Builtin):
    """!Represents a bit-for-bit comparison between two files, as is
    done by the "cmp" shell command.  The "src" and "tgt" variables
    are the two files to compare"""
    def __init__(self,defscopes,empty=False):
        """!Constructor for BitCmp
        @param defscopes a stack of Scope objects to the point at which this BitCmp was defined, innermost Scope first
        @param empty if True, the "src" and "tgt" parameters will be
        set to the null_value.  If False, no variables will be set."""
        super(BitCmp,self).__init__(defscopes,'.bitcmp.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        """!Creates a new, empty BitCmp object defined in the same
        location (defining stack of Scope objects) as self.
        @returns the new BitCmp"""
        return BitCmp(self.defscopes,empty=True)
    def run(self,con):
        """!Executes the bit-for-bit comparison
        @returns True if the files match and False if they do not.  
        @param con the Context in which this object is being evaluated"""
        src=self.resolve('src').string_context(con)
        tgt=self.resolve('tgt').string_context(con)
        if con.run_mode==BASELINE:
            produtil.fileop.deliver_file(src,tgt)
            return
        if os.path.samefile(src,tgt):
            # Same file object in filesystems.
            return True
        with open(src,'rt') as srcf:
            with open(tgt,'rt') as tgtf:
                srcstat=os.fstat(src.fileno())
                tgtstat=os.fstat(tgt.fileno())
                if not srcstat: return False # file stopped existing
                if not tgtstat: return False # file stopped existing
                if srcstat.st_size!=tgtstat.st_size:
                    # Different size according to stat
                    return False
                eof=False
                while not eof:
                    srcdat=src.read(1048576)
                    tgtdat=tgt.read(1048576)
                    if len(srcdat)!=len(tgtdat):
                        return False # Lengths differ
                    if srcdat!=tgtdat:
                        return False # Contents differ
                    eof=not len(srcdat) or not len(tgtdat)
                return True
    def bash_context(self,con):
        """!Generates bash code that compares the two files and copies
        the source file to com.

        @param con the Context in which this object is being evaluated"""
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').bash_context(con)
        comdir=bashify_string(self.getcom(con))

        if con.run_mode==BASELINE:
            return 'deliver_file %s %s\n'%(tgt,src) + \
                   'deliver_file %s %s/%s\n'%(tgt,comdir,tgt)
        else:
            return '''deliver_file %s %s/%s\n
set +e # bitcmp failures are reported by report_failed\nbitcmp %s %s\nset -e\n'''%(
                tgt,comdir,tgt, # deliver_file $tgt $compath
                tgt,src)     # bitcmp $tgt $src

########################################################################

class NccmpVars(Builtin):
    """!Represents a bit-for-bit comparison between two files, as is
    done by the "cmp" shell command.  The "src" and "tgt" variables
    are the two files to compare"""
    def __init__(self,defscopes,empty=False):
        """!Constructor for NccmpVars
        
       @param defscopes a stack of Scope objects to the point at which
       this BitCmp was defined, innermost Scope first
        
        @param empty if True, the "src" and "tgt" parameters will be
        set to the null_value.  If False, no variables will be set."""
        super(NccmpVars,self).__init__(defscopes,'.nccmp_vars.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        """!Creates a new, empty BitCmp object defined in the same
        location (defining stack of Scope objects) as self.
        @returns the new BitCmp"""
        return NccmpVars(self.defscopes,empty=True)
    def bash_context(self,con):
        """!Generates bash code that compares the two files and copies
        the source file to com.

        @param con the Context in which this object is being evaluated"""
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').bash_context(con)
        comdir=bashify_string(self.getcom(con))

        if con.run_mode==BASELINE:
            return 'deliver_file %s %s\n'%(tgt,src) + \
                   'deliver_file %s %s/%s\n'%(tgt,comdir,tgt)
        else:
            return '''deliver_file %s %s/%s\n
set +e # nccmp failures are reported by report_failed\nnccmp_vars %s %s\nset -e\n'''%(
                tgt,comdir,tgt, # deliver_file $tgt $compath
                tgt,src)     # bitcmp $tgt $src

########################################################################

class Md5Cmp(Builtin):
    """!A class that will use store an MD5 sum of an executable for
    later validation."""
    def __init__(self,defscopes,empty=False):
        """!Constructor for Md5Cmp
        @param defscopes a stack of Scope objects to the point at which this Md5Cmp was defined, innermost Scope first
        @param empty if True, the "src" and "tgt" parameters will be
        set to the null_value.  If False, no variables will be set."""
        super(Md5Cmp,self).__init__(defscopes,'.md5cmp.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        """!Creates a new, empty Md5Cmp object defined in the same
        location (defining stack of Scope objects) as self.
        @returns the new CopyDir"""
        return Md5Cmp(self.defscopes,empty=True)
    def run(self,con):
        """!Raises Md5Cmp to indicated this function is not yet implemented"""
        raise NotImplementedError("Md5Cmp.run is not implemented.")
    def bash_context(self,con):
        """!Generates a block of bash code that will compute and store
        the md5sum.  The executable is the "tgt" variable and the
        reference MD5 sum is the "src" variable.  The new MD5 sum is
        stored in the COM directory as the executable basename with
        ".md5" appended.
        @param con the Context in which this object is being evaluated
        @returns the resulting bash code block"""
        md5ref=self.resolve('src').string_context(con) # reference md5sum
        exe=self.resolve('tgt').string_context(con) # executable
        md5sum=os.path.join(self.getcom(con),
                            os.path.basename(md5ref))
        md5ref=bashify_string(md5ref)
        exe=bashify_string(exe)
        md5sum=bashify_string(md5sum)
        # Behaves the same way in baseline and verification mode
        # because this is checking the executable used during the run
        return '''md5sum {exe} > {md5sum}
report_line md5sum: $( cat {md5sum} )
report_line md5sum "local="{md5sum}
report_line md5sum "reference="{md5ref}
'''.format(
            md5ref=md5ref,md5sum=md5sum,exe=exe)

########################################################################

class Criteria(TypelessObject):
    """!Represents a list of output validation criteria."""
    def __init__(self,defscopes):
        """Criteria constructor
        @param defscopes a stack of Scope objects to the point at which this Criteria was defined, innermost Scope first
        """
        super(Criteria,self).__init__(defscopes)
        self.__opmap=collections.defaultdict(list)
        self.__tgtlist=list()
        self.is_criteria=True
    def __str__(self):
        s='Criteria:'
        for tgt in self.__tgtlist:
            s+=' '+str(tgt)+': (/ '
            s+= ', '.join(type(callme).__name__+':'+str(callme) for callme in self.__opmap[tgt])
            s+=' /),'
        return s
    def add_binary_operator(self,tgt,op,src,con):
        """!Adds a binary operator criterion that compares src and tgt.

        @param tgt The target of the comparison, which represents the
        "known correct value" such as baseline data or an executable
        MD5 sum

        @param op the operaton to perform, a Scope.
        @param src The source of the comparison, an unknown or uncertain
        value to compare against "src".  Generally, the "src" is copied to COM.
        @param con the Context in which this object is being evaluated
        @returns None"""
        if tgt not in self.__opmap:
            self.__tgtlist.append(tgt)
        callme=call_scope(op,con,self.defscopes,tgt=tgt,src=src)
        for mycall in self.__opmap[tgt]:
            assert mycall is not null_value
            if mycall==callme:
                return
        callme=self.__opmap[tgt].append(callme)
        assert callme is not null_value
    def rescope(self,scopemap=None,prepend=None):
        """!Modifies this object's scopes, and that of any subobjects.

        Subclasses that can be expressed as non-constant values must
        implement this function for rescoping.  This function changes
        the stack of defining scopes, defscopes, based on arguments

        @param scopemap a mapping from old Scope to new Scope during
        the replacement

        @param prepend a list of Scope objects to prepend.  These
        become the innermost scopes.  The scopemap is NOT applied to
        the prepend list.
        @returns self"""
        if prepend is None: prepend=[]
        if scopemap is None: scopemap={}
        f=Criteria(prepend+[ scopemap[s] if s in scopemap else s
                        for s in self.defscopes ])
        assert(self.__tgtlist)
        for tgt in self.__tgtlist:
            for callme in self.__opmap[tgt]:
                assert(callme)
            rtgt=tgt.rescope(scopemap,prepend)
            f.__tgtlist.append(rtgt)
            f.__opmap[rtgt]=[ 
                callme.rescope(scopemap,prepend)
                for callme in self.__opmap[tgt] ]
        assert(f.__tgtlist)
        assert(f.__opmap)
        return f
    def _apply_rescope(self,scopemap=None,prepend=None):
        """!Replaces Scope objects in this object's defscopes variable.

        This function is the internal implementation of the "use"
        blocks and function calls when parsing or evaluating.
        Subclasses with a rescope() or similar function use
        _apply_rescope() to implement such functions.

        @param scopemap A mapping from old Scope to new Scope
        @param prepend A list of Scope objects to prepend to defscopes
        @protected"""
        super(Criteria,self)._apply_rescope(scopemap,prepend)
        for tgt in self.__tgtlist:
            tgt._apply_rescope(scopemap,prepend)
            for callme in self.__opmap[tgt]:
                callme._apply_rescope(scopemap,prepend)
    def use_from(self,criteria,only_scalars=False):
        """!Implements a "use" statement; copies definitions from another Scope

        Copies parameters, constants, and variables from another scope
        into this one.  Copies are modified to have this scope in
        their definition or calling stack via the rescope() function.

        @param used_scope The scope whose data is being copied.
        @param only_scalars If True, then only the objects with
        is_scalar=True are copied.
        @returns True if all variables seen were scalar, False if any
        non-scalar variables were seen.  This includes variables that
        were found, but not "used," due to only_scalars=True"""
        if only_scalars:
            raise ValueError('In Criteria.use_from, only_scalars must '
                             'be False.')
        if not criteria.is_criteria:
            raise TypeError('Criteria blocks can only use criteria blocks.')
        for tgt,callme in criteria.itercriteria():
            found=False
            for mycall in self.__opmap[tgt]:
                if callme==mycall:
                    found=True
                    break
            if not found: 
                self.__opmap[tgt].append(callme)
                self.__tgtlist.append(tgt)
        assert(self.__tgtlist)
        assert(self.__opmap)
    def itercriteria(self):
        """!Iterates over all  (tgt,criterion) pairs in this Criteria."""
        for tgt in self.__tgtlist:
            for callme in self.__opmap[tgt]:
                yield tgt,callme
    def bash_context(self,con):
        """!Generates a bash code block that will perform all criteria
        comparisons or baseline comparisons
        @param con the Context in which this object is being evaluated
        @returns the new bash code block."""
        out=io.StringIO()
        if con.run_mode==BASELINE:
            out.write('\n########################################################################\necho BASELINE GENERATION:\n\n')
        else:
            out.write('\n########################################################################\necho OUTPUT VALIDATION:\n\n')
        assert(self.__tgtlist)
        for tgt in self.__tgtlist:
            out.write('echo criteria for target %s:\n'%(
                      tgt.bash_context(con),))
            for callme in self.__opmap[tgt]:
                out.write(callme.bash_context(con))
                if con.run_mode==BASELINE: break
        if con.run_mode==BASELINE:
            out.write('\necho END OF BASELINE GENERATION\n########################################################################\n\n')
        else:
            out.write('\necho END OF OUTPUT VALIDATION\n########################################################################\n\n')
        ret=out.getvalue()
        out.close()
        return ret

########################################################################

class Filters(TypelessObject):
    """!Represents a list of input filters to run in sequence.  These
    use some "src" object, and a filter (binary operator) to generate
    the "tgt" object."""
    def __init__(self,defscopes):
        """!Constructor for Filters
        @param defscopes a stack of Scope objects to the point at which this Filters was defined, innermost Scope first"""
        super(Filters,self).__init__(defscopes)
        self.__opmap=dict()
        self.__tgtlist=list()
        self.is_filters=True
    def add_binary_operator(self,tgt,op,src,con):
        """!Adds a filter that compares src and tgt.

        @param tgt The target of the filter; the local file that is created.

        @param op the operaton to perform, a Scope.
        @param src The source of the file, generally a file or set of files
        @param con the Context in which this object is being evaluated
        @returns None"""
        if tgt not in self.__opmap:
            self.__tgtlist.append(tgt)
        self.__opmap[tgt]=call_scope(op,con,self.defscopes,
                                     tgt=tgt,src=src)
        assert self.__opmap[tgt] is not null_value
    def rescope(self,scopemap=None,prepend=None):
        """!Modifies this object's scopes, and that of any subobjects.

        Subclasses that can be expressed as non-constant values must
        implement this function for rescoping.  This function changes
        the stack of defining scopes, defscopes, based on arguments

        @param scopemap a mapping from old Scope to new Scope during
        the replacement

        @param prepend a list of Scope objects to prepend.  These
        become the innermost scopes.  The scopemap is NOT applied to
        the prepend list.
        @returns self"""
        if prepend is None: prepend=[]
        if scopemap is None: scopemap={}
        f=Filters(prepend+[ scopemap[s] if s in scopemap else s
                        for s in self.defscopes ])
        for tgt in self.__tgtlist:
            rtgt=tgt.rescope(scopemap,prepend)
            f.__tgtlist.append(rtgt)
            f.__opmap[rtgt]=self.__opmap[tgt].rescope(scopemap,prepend)
        return f
    def _apply_rescope(self,scopemap=None,prepend=None):
        """!Replaces Scope objects in this object's defscopes variable.

        This function is the internal implementation of the "use"
        blocks and function calls when parsing or evaluating.
        Subclasses with a rescope() or similar function use
        _apply_rescope() to implement such functions.

        @param scopemap A mapping from old Scope to new Scope
        @param prepend A list of Scope objects to prepend to defscopes
        @protected"""
        super(Filters,self)._apply_rescope(scopemap,prepend)
        for tgt in self.__tgtlist:
            tgt._apply_rescope(scopemap,prepend)
    def use_from(self,filters,only_scalars=False):
        """!Implements a "use" statement; copies definitions from another Scope

        Copies parameters, constants, and variables from another scope
        into this one.  Copies are modified to have this scope in
        their definition or calling stack via the rescope() function.

        @param used_scope The scope whose data is being copied.
        @param only_scalars If True, then only the objects with
        is_scalar=True are copied.
        @returns True if all variables seen were scalar, False if any
        non-scalar variables were seen.  This includes variables that
        were found, but not "used," due to only_scalars=True"""
        if only_scalars:
            raise ValueError('In Filters.use_from, only_scalars must '
                             'be False.')
        if not filters.is_filters:
            raise TypeError('Filters blocks can only use filters blocks.')
        for tgt,callme in filters.iterfilters():
            have_tgt=tgt in self.__opmap
            if have_tgt and self.__opmap[tgt]==callme:
                continue
            self.__opmap[tgt]=callme
            assert self.__opmap[tgt] is not null_value
            if not have_tgt:
                self.__tgtlist.append(tgt)
    def iterfilters(self):
        for tgt in self.__tgtlist:
            yield tgt,self.__opmap[tgt]
    def bash_context(self,con):
        """!Generates a bash code block that executes all filters in sequence
        @param con the Context in which this object is being evaluated
        @returns the resulting bash code as a string."""
        out=io.StringIO()
        out.write('\n########################################################################\necho INPUT FILTERS:\n\n')
        for tgt in self.__tgtlist:
            # out.write('echo Filter for target %s:\n'%(
            #         tgt.bash_context(con),))
            out.write(self.__opmap[tgt].bash_context(con))
        out.write('\necho END OF INPUT FILTERS\n########################################################################\n\n')
        ret=out.getvalue()
        out.close()
        return ret

########################################################################

class Rank(TypelessObject):
    """!Represents a single MPI rank or group of MPI ranks with
    identical resource requirements and executable.  This is merely a
    container class to store information for a SpawnProcess object."""
    def __init__(self,args,opts):
        """!Constructor for Rank

        @param args The executable (args[0]) and its arguments (args[1:])
        @param opts The options, a dict.  The meanings of the keys is defined by the SpawnProcess class."""
        self.__args=list(args)
        self.__opts=opts
        self._fields=dict()

    def init_fields(self,con):
        if self._fields: return
        f={ 'ranks':         max(0,self._getnum(con,'ranks',-1)),
            'cpus_per_core': self._getnum(con,'cpus_per_core',-1),
            'ppn':           max(0,self._getnum(con,'ppn',0)),
            'threads':       max(1,self._getnum(con,'threads',0))  }
        f['nonzero_ppn']=f['ppn']
        if f['cpus_per_core']<0:
            f['cpus_per_core']=self._getres(con,'plat%cpus_per_core',1)
        if not f['ppn']:
            cores_per_node=con.scopes[-1].resolve('plat%cores_per_node').\
                numeric_context(con)
            f['nonzero_ppn']=cores_per_node//f['threads']
        self._fields=f

    def ranks(self,con):
        self.init_fields(con)
        return self._fields['ranks']

    def cpus_per_core(self,con):
        self.init_fields(con)
        return self._fields['cpus_per_core']

    def ppn(self,con):
        self.init_fields(con)
        return self._fields['ppn']

    def threads(self,con):
        self.init_fields(con)
        return self._fields['threads']

    def _getnum(self,con,key,default):
        if self.__opts is None or not self.__opts.haslocal(key):
            return default
        return int(self.__opts.getlocal(key).numeric_context(con))

    def _getres(self,con,key,default):
        try:
            return int(self.__opts.resolve('plat%cpus_per_core').numeric_context(con))
        except KeyError:
            return default

    def __repr__(self):
        return 'Rank(args=%s,opts=%s)'%(
            repr(self.__args),repr(self.__opts))

    def new_empty(self):
        return Rank(list(),None)

    def rescope(self,scopemap=None,prepend=None):
        n=self.new_empty()
        n.__args=[ a.rescope(scopemap,prepend) for a in self.__args ]
        n.__opts=self.__opts.rescope(scopemap,prepend)
        return n

    ##@property args
    # A list containing the executable (args[0]) and its arguments (args[1:])

    def merge_into(self,con,others):
        self.init_fields(con)
        f=self._fields
        me={'ranks':max(1, f['ranks']),
            'args': list(self.__args),
            'cpus_per_core': max(1, f['cpus_per_core']),
            'ppn': max(0,f['nonzero_ppn']),
            'threads': f['threads'] }

        if not others: return [me]

        last=others[-1]
        if last['args']          == me['args'] and \
           last['cpus_per_core'] == me['cpus_per_core'] and \
           last['ppn']           == me['nonzero_ppn'] and \
           last['threads']       == me['threads']:
            others[-1]['ranks']  += me['ranks']
        else:
            others.append(me)
        return others

    @property
    def args(self):
        """!A list containing the executable (args[0]) and its
        arguments (args[1:])"""
        return self.__args

    def argiter(self):
        """!Iterates over executable and arguments in the args member
        variable"""
        for arg in self.__args:
            yield arg

########################################################################

def pack_ranks(nodesize,count):
    """!Spreads count MPI ranks over the fewest possible nodes whose
    maximum PETs per node (ppn) is nodesize.  Attempts to distribute
    the ranks per node as equally as possible.  Any node will never
    have more than one or less than one rank than any other node.

    @returns a list of two-element lists.  Each two element list
    contains a pair [number of nodes, PETs per node (ppn)] for nodes
    that have an identical number of PETs per node (ppn)
    @param nodesize the maximum number of PETS per node of any given compute node
    @param count the number of MPI ranks"""
    out=list()
    n=count
    if n<nodesize:  # special case: smaller than one node
        out.append([1,n])
    elif nodesize*(n//nodesize)==n: #exact number of nodes
        out.append([n//nodesize,nodesize])
    else:
        need=math.ceil(n/float(nodesize))
        averagef=n/math.ceil(need)
        af,ai = math.modf(averagef)
        n1=need-round(af*need)
        n2=round(af*need)
        if n1: out.append([n1, ai])
        if n2: out.append([n2, ai+1])
    return out

########################################################################

def expand_lists(iterable,max_depth=None):
    for i in iterable:
        if isinstance(i,list) or isinstance(i,tuple):
            if max_depth is None:
                for k in expand_lists(i): 
                    yield k
            elif max_depth>=0:
                for k in expand_lists(i,max_depth-1):
                    yield k
            else:
                yield i
        else:
            yield i

########################################################################

class SpawnProcess(TypelessObject):
    """!Represents a request to execute a process.  This process may
    be OpenMP, serial, MPI, or MPI+OpenMP.  This is the implementation
    of the "spawn" block."""
    def __init__(self,defscopes):
        """!SpawnProcess constructor
        @param defscopes a stack of Scope objects to the point at which this SpawnProcess was defined, innermost Scope first"""
        super(SpawnProcess,self).__init__(defscopes)
        self.__ranks=list()
    def new_empty(self):
        return SpawnProcess(self.defscopes)
    def rescope(self,scopemap=None,prepend=None):
        n=self.new_empty()
        n.__ranks=[ rank.rescope(scopemap,prepend) for rank in self.__ranks ]
        return n
    def add_rank(self,args,opts):
        """!Adds an MPI rank or block of MPI ranks, or serial program,
        or OpenMP program, to the SpawnProcess.

        Generates and stores a Rank object that contains the
        information in args and opts

        @param args the executable (args[0]) and command-line arguments (args[1:])
        @param opts the other options in the "spawn" block."""
        assert(isinstance(args,list))
        self.__ranks.append(Rank(args,opts))
    def iterrank(self):
        """!Iterates over all Rank objects generated by add_rank() calls."""
        for rank in self.__ranks:
            yield rank
    def mpi_comm_size(self,con):
        """!Computes the size of MPI_COMM_WORLD

        Analyzes all Rank objects created by add_rank() calls,
        calculating the number of MPI ranks requested.  Note that this
        includes ranks from all executables in an Multiple Program
        Multiple Data (MPMD) execution (executions with multiple
        executables in a single MPI_COMM_WORLD)

        @returns the size of MPI_COMM_WORLD, or 0 if this is not an MPI program.
        @param con the Context in which this object is being evaluated"""
        size=0
        for rank in self.__ranks:
            size+=rank.ranks(con)
        return size

    def _make_nodes_ppn(self,con):
        rank_info=list()
        for rank in self.__ranks:
            rank_info=rank.merge_into(con,rank_info)
        MPI=con.scopes[-1].resolve('plat%MPI').string_context(con)

        min_cpus_per_core=max(1, min([ r['cpus_per_core'] for r in rank_info ]))
        max_ppn_tpn=max(1, max([ r['ppn']*r['threads'] for r in rank_info ]))
        max_ppn=max(1, max([ r['ppn'] for r in rank_info ]))
        num_pets=max(1, sum([ r['ranks'] for r in rank_info ]))
        max_threads=max(1, max([ r['threads'] for r in rank_info ]))
        cores_per_node=con.scopes[-1].resolve('plat%cores_per_node').\
            numeric_context(con)
        assert(cores_per_node>0)

        # (nodes, ppn) pairs for blocks of similar nodes:
        packed=[ pack_ranks(r['ppn'],r['ranks']) for r in rank_info ]
        nodes=sum([ pr[0] for pr in expand_lists(packed,0) ])

        # Determine the acting node size:
        nodesize=cores_per_node # ideally, the number of cores
        affinity='core'
        if max_ppn_tpn>nodesize:
            # If it is bigger than that, try the number of cpus.
            nodesize=min_cpus_per_core*cores_per_node 
            affinity='cpu'
        if max_ppn_tpn>nodesize:
            # Caller wants to overcommit a node.  This usually fails,
            # but we'll try to request it anyway.  
            nodesize=max(nodesize,max_ppn_tpn)

        return MPI,nodesize,affinity,max_threads,nodes,max_ppn_tpn,max_ppn,packed

    def rocoto_resources(self,con):
        MPI,nodesize,affinity,max_threads,nodes,max_ppn_tpn,max_ppn,packed=\
            self._make_nodes_ppn(con)
        request=''

        if MPI.upper().find('LSF')>=0:
            request+="<nodesize>%d</nodesize>\n"%nodesize
            if MPI.upper().find('CRAY_INTEL')<0:
                request+="<native>-R 'affinity[%s(%d)]'</native>\n"%(
                    affinity, max_threads)
            elif nodes>1:
                request+="<nodes>%d:ppn=%d</nodes>\n"%(nodes,max_ppn_tpn)

        if max_ppn<2:
            # For serial jobs, use 2 cores to ensure exclusive access to node.
            request+="<cores>2</cores>\n"%max_ppn
        elif nodes<2:
            # For single node jobs, use the <cores> syntax.
            request+="<cores>%d</cores>\n"%max_ppn
        elif MPI.upper().find('LSF_CRAY_INTEL')<0:
            # For multi-node jobs, use the <nodes> syntax.  We exclude
            # LSF_CRAY_INTEL because it has a different method.
            nodespecs=[ '%d:ppn=%d'%(int(p[0]),int(p[1])) for p in expand_lists(packed,0) ]
            request+='<nodes>' + ('+'.join(nodespecs)) + '</nodes>\n'

        return request
        
    def bash_context(self,con):
        """!Generates a bash code block to run the specified program

        @param con the Context in which this object is being evaluated
        @returns a bash code block to run the program."""
        MPI,nodesize,affinity,max_threads,nodes,max_ppn_tpn,max_ppn,packed=\
            self._make_nodes_ppn(con)

        out=io.StringIO()
        out.write('# Embedded process execution:\n')
        need_ranks=len(self.__ranks)>1
        have_ranks=False
        ranks=list()
        threads=list()
        for rank in self.__ranks:
            nranks=rank.ranks(con)
            if nranks>0: have_ranks=True
            if nranks<1 and need_ranks:
                nranks=1
            ranks.append(nranks)
            threads.append(rank.threads(con))
            con.info('Rank block: threads=%s ranks=%s'%(repr(threads[-1]),
                                                          repr(ranks[-1])))
        nthreads=max(1,max(threads))
        out.write('export OMP_NUM_THREADS=%d MKL_NUM_THREADS=0\n'%(
                nthreads,))
        if not have_ranks:
            # Serial or openmp program.
            out.write(' '.join([r.bash_context(con) 
                                for r in self.__ranks[0].args]))
            out.write('\n')
        else:
            out.write('%s\n'%(con.mpirunner(self,distribution=packed[0]),))
        out.write('# End of embedded process execution.\n')
        ret=out.getvalue()
        out.close()
        return ret

########################################################################

class EmbedBash(Scope):
    """!Represents an embedded bash script.  This is the
    implementation of the "embed bash [[[code]]]" block."""
    def __init__(self,defscopes):
        """!Constructor for EmbedBash
        @param defscopes a stack of Scope objects to the point at which this EmbedBash was defined, innermost Scope first"""
        super(EmbedBash,self).__init__(defscopes)
        self.__template=None
    def __bool__(self):
        return bool(self.__template)
    def validate_parameter(self,name):
        """!Does nothing; this is a placeholder for variable name validation

        This function analyzes the given variable name and raises an
        exception if the variable name is invalid.  Presently, any
        variable name is valid, so this function is a no-op.  However,
        any variable name that contains a period (".") will not be
        passed in to generated bash code as a bash variable.

        @param name the name of a new parameter (function argument) to validate.
        @returns None"""
        pass
        #if not re.match('(?s)^[a-zA-Z][a-zA-Z0-9_]*$',name):
            #raise ValueError('Invalid bash variable name $%s FIXME: use better exception here'%(name,))

    def bash_context(self,con):
        """!Raises an exception to indicate that the bash script
        cannot be represented as a bash string.
        @param con the Context in which this object is being evaluated"""
        raise PTParserError("Cannot express bash script in a bash string.")

    def _apply_rescope(self,scopemap=None,prepend=None):
        """!Replaces Scope objects in this object's defscopes variable.

        This function is the internal implementation of the "use"
        blocks and function calls when parsing or evaluating.
        Subclasses with a rescope() or similar function use
        _apply_rescope() to implement such functions.

        @param scopemap A mapping from old Scope to new Scope
        @param prepend A list of Scope objects to prepend to defscopes
        @protected"""
        super(EmbedBash,self)._apply_rescope(scopemap,prepend)
        self.__template._apply_rescope(scopemap,prepend)
        self.__template.defscopes=[self]+self.defscopes

    def rescope(self,scopemap=None,prepend=None):
        """!Modifies this object's scopes, and that of any subobjects.

        Subclasses that can be expressed as non-constant values must
        implement this function for rescoping.  This function changes
        the stack of defining scopes, defscopes, based on arguments

        @param scopemap a mapping from old Scope to new Scope during
        the replacement

        @param prepend a list of Scope objects to prepend.  These
        become the innermost scopes.  The scopemap is NOT applied to
        the prepend list.
        @returns self"""
        s=super(EmbedBash,self).rescope(scopemap,prepend)
        s.__template=self.__template.rescope(scopemap,prepend)
        s.__template.defscopes=[self]+self.defscopes
        return s

    def __str__(self):
        return "bash script \"%s\" %s"%(
            elipses(repr(self.gettemplate())),
            super(EmbedBash,self).__str__())

    def __repr__(self):
        return "bash script \"%s\" %s"%(
            elipses(repr(self.gettemplate())),
            super(EmbedBash,self).__str__())

    def apply_parameters(self,scope,con):
        """!Implements a function call using this Scope as the parameter list.

        Creates a new Scope where all parameters in this scope are
        converted to local variables and possibly overridden.  Scope
        self's parameters are used for the default argument values.
        The "scope" argument to apply_parameters() contains values to
        override those.  Hence, self is the function definition and
        scope is the values set in the function call.  

        A third Scope is created, containing the result of applying
        the function call and default values.  That third Scope has no
        parameters; all parameters have been converted to local
        values.  The returned Scope has the same defscopes as self.
        That means any unresolved variables within the function will
        be resolved in the defining context, NOT the calling context.

        @param scope The arguments provided to the function call.
        @param con the Context at which this function is being called.
           The defining location is in defscopes.
        @returns a Scope representing the function call."""
        s=super(EmbedBash,self).apply_parameters(scope,con)
        s.__template=self.__template.rescope({self:s, scope:s})
        assert(s.__template)
        s.__template.defscopes=[self]+self.defscopes
        return s

    def is_valid_rvalue(self,con):
        """!Can this EmbedBash object be assigned to a variable?

        An EmbedBash definition and function call can always be
        assigned to a variable.  However, the result of
        apply_parameters() (also an EmbedBash object) cannot be.

        @returns True if this EmbedBash can be assigned to a variable,
        or False otherwise.
        @param con the Context in which this object is being evaluated"""
        return self.__template is not None

    def string_context(self,con): 
        """!Evaluates this EmbedBash in a string context.

        Executes this EmbedBash via run(), converts the result to a
        number (via numeric_context()) and then to a string via "%d" 

        @param con the Context in which this object is being evaluated
        @returns the string copy of the numeric result of run()"""
        return '%d'%(self.numeric_context(con),)

    def settemplate(self,template):
        """!Sets the scope used for string expansion of the embedded
        bash script.

        The embedded bash script's string expansion has a special
        Scope stack when it is evaluated.

        1. Function arguments are searched first. These function
        arguments are the result of applying the function call
        arguments to the function definition argument list (and
        default arguments).

        2. Defining scopes above the function definition are searched
        next.

        The settemplate sets the Scope used for this search.
        @param template the calling context
        @returns None"""
        assert(isinstance(template,String))
        self.__template=template
        self.__template.defscopes=[self]+self.defscopes

    def gettemplate(self):
        """!Returns the template that should be used for string
        expansion of the embedded bash script"""
        return self.__template

    def numeric_context(self,con):
        """!Executes the bash script, returning the result as a numeric value"""
        return self.run(con)

    def bash_context(self,con):
        """!Generates and returns a bash code block to run the
        embedded script with the script variables set to the function
        arguments.

        Generates a bash code block that sets bash local variables
        variables to the calling arguments.  Any variables whose names
        contain "." or "%" will not be set since they are not valid
        bash variable names.  Next, the code block contains the
        embedded bash code.  Finally, it will unset the local
        variables set in the first step.

        @param con the Context in which this object is being evaluated
        @returns the resulting bash code"""
        template=self.gettemplate()
        template.defscopes=[self]+self.defscopes # workaround for unknown bug
        expanded=template.string_context(con)
        #template=template.string_context(con)
        #expanded=self.expand_string(template,con)

        stream=io.StringIO()
        env=dict()
        unset_me=list()
        
        set_pre=''
        try:
            if self.getlocal('export.vars').logical_context(con):
                set_pre='export '
        except KeyError as ke: pass

        for k,v in self.iterlocal():
            if '%' in k or '.' in k:
                stream.write('# $%s: skip; invalid shell variable name\n'
                             %(k,))
            elif k[0:2] == '__':
                stream.write("# $%s: skip; name begins with __\n"%(k,))
            elif v is null_value:
                stream.write('# $%s: skip; has no value\n'%(k,))
            elif not v.is_scalar:
                stream.write('# $%s: skip; value is not scalar\n'%(k,))
            else:
                unset_me.append(k)
                stream.write('%s%s=%s\n'%(set_pre,k,v.bash_context(con)))
        stream.write("# Embedded bash script:\n")
        stream.write(expanded)
        stream.write('\n# End of embedded bash script.\n')
        for k in unset_me:
            stream.write('unset %s\n'%(k,))
        if con.verbose:
            stream.write('set -xe\n\n')
        else:
            stream.write('set -e\n\n')
        script=stream.getvalue()
        stream.close()
        return script

    def run(self,con):
        """!Runs the script generated by bash_context()

        Uses produtil.run.run() and produtil.run.exe() to execute this
        bash code block.  

        @returns the result of produtil.run.run()

        @note Since produtil.run.exe() is used, the program will be
        run as a "large" or "compute" program.  On Cray, this means
        the program will be run via "aprun," placing it on a compute
        node.

        @param con the Context in which this object is being evaluated
        @"""

        con.info('%s: run %s'%(str(con),elipses(str(self))))

        script=self.bash_context(con)
        # yell('%-7s %-7s %s\n'%("RUN","BASH",script))
        cmd=produtil.run.batchexe("bash")
        if con.verbose:
            cmd=cmd<<'set -xue\n'+script
        else:
            cmd=cmd<<'set -ue\n'+script
        env=dict(self.iterlocal())
        if env: cmd.env(**env)
        return produtil.run.run(cmd)
            
    def logical_context(self,con): 
        """!Executes this EmbedBash, returning True if the script
        returns a 0 status, and False otherwise.

        Uses run() to execute this program, via numeric_context() to
        get the numeric return value.  

        @returns True if the script return value was 0, False otherwise
        @param con the Context in which this object is being evaluated"""
        return bool(self.numeric_context(con)==0)

    def new_empty(self):
        """!Creates a new, empty EmbedBash object defined in the same
        location (defining stack of Scope objects) as self.
        @returns the new EmbedBash"""
        s=EmbedBash(self.defscopes)
        s.__template=self.__template.rescope({self:s})
        assert(s.__template)
        return s

########################################################################

class Task(Scope):
    """!Represents a task that has a name, and can be executed as a
    batch job.  The task may, optionally, have dependencies on other
    tasks."""
    def __init__(self,defscopes,name,runvar='run'):
        """!Constructor for Task

        @param defscopes a stack of Scope objects to the point at which this Task was defined, innermost Scope first
        @param name the name of this task
        @param runvar the name of the variable that is executed to run this Task"""
        super(Task,self).__init__(defscopes)
        self.__deps=list()
        self.__name=str(name)
        self.runvar=runvar

    ##@property name
    # the name of this task

    @property
    def name(self):
        """!The name of this task"""
        return self.__name
    def bash_context(self,con):
        """!Represents this task as a bash code block

        Represents the variable self.runvar in a bash context within
        the Context con.  That bash code block is used as the bash
        representation of this Task.

        @returns the bash code that represents runvar in a bash context"""
        assert(self.haslocal(self.runvar))
        return self.getlocal(self.runvar).bash_context(con)

    def iterdeps(self):
        """!Iterates over all dependencies that were added via add_dependency()"""
        for dep in self.__deps:
            yield dep

    def add_dependency(self,dep):
        """!Adds the given dependency to the list of dependencies for this task.

        @param dep a Task that must be run before this task"""
        self.__deps.append(dep)

    def is_valid_rvalue(self,con):
        """!Can this Task be assigned to a variable?

        Determines if this task can be assigned to a variable.  For
        that to be done, the Task must be able to be run.  That is, it
        must have its runvar assigned and non-null.

        @param con the Context in which this object is being evaluated
        @return True if this task can be assigned to a variable, False otherwise"""
        return self.haslocal(self.runvar) and \
            self.getlocal(self.runvar) is not null_value

    def string_context(self,con): 
        """!Generates a string that represents this Task

        Calls runvar's string_context function and returns that as
        this Task's string representation.

        @param con the Context in which this object is being evaluated
        @returns a string representation of runvar"""
        return self.getlocal(self.runvar).string_context(con)

    def numeric_context(self,scopes,con):
        """!Generates a number that represents this Task

        Calls runvar's numeric_context function and returns that as
        this Task's numeric representation.

        @param con the Context in which this object is being evaluated
        @returns a numeric representation of runvar"""
        return self.getlocal(self.runvar).numeric_context(con)

    def run(self,con):
        """!Executes this task.

        Runs the run function of runvar, returning the result.

        @return the result of runvar's run function"""
        return self.getlocal(self.runvar).run(con)
            
    def logical_context(self,con): 
        """!Generates a number that represents this Task

        Calls runvar's numeric_context function and returns that as
        this Task's numeric representation.

        @param con the Context in which this object is being evaluated
        @returns a numeric representation of runvar"""
        return self.getlocal(self.runvar).numeric_context(con)

    def new_empty(self):
        """!Creates an identical copy of this task, but without dependencies.

        Uses the Task constructor to copy this task but omits the dependency list.

        @returns the resulting Task"""
        return Task(self.defscopes,self.__name,self.runvar)

########################################################################

class Build(Task):
    """!A Task that represents a build process (anything that
    constructs a program to be executed)."""
    def __init__(self,defscopes,name):
        """!Constructor for Build.

        @param defscopes a stack of Scope objects to the point at
        which this Build was defined, innermost Scope first
        @param name the name of this Build"""
        super(Build,self).__init__(defscopes,name,'build')
    def new_empty(self):
        """!Creates an identical copy of this build, but without dependencies.

        Uses the Task constructor to copy this build but omits the dependency list.

        @returns the resulting Build"""
        return Build(self.defscopes,self.name)

########################################################################

class Platform(Task):
    """!Represents a Task whose job is to determine the local platform."""
    def __init__(self,defscopes,name):
        """!Constructor for Platform.

        @param defscopes a stack of Scope objects to the point at
        which this Platform was defined, innermost Scope first
        @param name the name of this Platform"""
        super(Platform,self).__init__(defscopes,name,'detect')
    def new_empty(self):
        """!Creates an identical copy of this platform, but without dependencies.

        Uses the Task constructor to copy this platform but omits the dependency list.

        @returns the resulting Platform"""
        return Platform(self.defscopes,self.name)

########################################################################

class Test(Scope):
    """!A Task that represents some Test to be run.  Generally the
    Test copies input files, runs some program or script, and
    validates against a baseline (or creates a new baseline)."""
    def __init__(self,defscopes,name,mode):
        """!Constructor for Test
        @param defscopes a stack of Scope objects to the point at which this Test was defined, innermost Scope first
        @param name the name of this Test
        @param mode produtil.testing.utilities.BASELINE or produtil.testing.utilities.EXECUTION"""
        super(Test,self).__init__(defscopes)
        assert(mode in [ BASELINE, EXECUTION ])
        self.mode=mode
        self.__name=str(name)
        self.__deps=list()
        self.is_test=True

    ##@var name
    # The name of this Test

    @property
    def name(self):
        """!The name of this test."""
        return self.__name

    def bash_context(self,con):
        """!Generates a bash script that will run this test.

        Generates a bash script by running the bash_context functions
        of each of these steps, taken from resolve():

        1. prep - prepares the environment for execution
        2. input - obtains input data
        3. execute - executes the test
        4. One of:
            a. make_baseline - creates a new baseline from the output of the above three steps
            b. verify - compares the output of the above three steps against the baseline

        If either "make_baseline" or "verify" is unavailable, then the
        "output" variable from resolve() is used in their place.  If
        that is also unavailable, KeyError is raised.

        @param con the Context in which this object is being evaluated
        @raise KeyError if one of the required variables is undefined
        @returns the resulting  bash code        """
        if self.mode==BASELINE:
            steps=['prep','input','prerun','execute','make_baseline']
        else:
            steps=['prep','input','prerun','execute','verify']

        name=self.resolve("TEST_NAME").bash_context(con)
        try:
            descr=self.resolve("TEST_DESCR").bash_context(con)
        except KeyError as ke:
            descr='no description'
        report=self.resolve("COM").bash_context(con)
        report=os.path.join(report,'report.txt')

        out=io.StringIO()
        out.write("report_start %s Test %s starting at $( date ) '('%s')'\n"%(
                report,name,descr))
        for step in steps:
            try:
                stepobj=self.getlocal(step)
            except KeyError as ke:
                if step in [ 'make_baseline', 'verify' ]:
                    stepobj=self.getlocal('output')
                elif step in [ 'prerun', 'input' ]:
                    continue # prerun and input steps are optional
                else:
                    raise
            out.write(stepobj.bash_context(con))
            out.write('\n')
        out.write("report_finish\n")
        ret=out.getvalue()
        out.close()
        return ret

    def iterdeps(self):
        """!Iterates over this Test's dependencies"""
        for dep in self.__deps:
            yield dep

    def add_dependency(self,dep):
        """!Adds a Task that must be executed before this Task
        @param dep the Task to be executed"""
        self.__deps.append(dep)

    def is_valid_rvalue(self,con):
        """!Can this Test be assigned to a variable

        Checks to see if all variables needed by bash_context() are defined

        In BASELINE mode: prep, input, execute and either make_baseline or output
        In EXECUTION mode: prep, input, execute, and either verify or output

        @param con the Context in which this object is being evaluated"""
        if self.mode==BASELINE:
            steps=['prep','input','execute','make_baseline']
        else:
            steps=['prep','input','execute','verify']

        for step in steps:
            if self.haslocal(step):
                if self.getlocal(step) is not null_value:
                    continue
            elif step in ['make_baseline','verify'] and \
                    self.haslocal('output'):
                if self.getlocal('output') is not null_value:
                    continue
            raise PTParserError('Compset is missing the step: '+step)
        return True

    def string_context(self,con): 
        """!Raises TypeError to indicate that a test cannot be evaluated
        @param con the Context in which this object is being evaluated"""
        raise TypeError('A Test cannot be evaluated in a string context.')

    def numeric_context(self,con):
        """!Raises TypeError to indicate that a test cannot be evaluated
        @param con the Context in which this object is being evaluated"""
        raise TypeError('A Test cannot be evaluated in a numeric context.')

    def run(self,con):
        """!Raises TypeError to indicate that a test cannot be evaluated
        @param con the Context in which this object is being evaluated"""
        raise TypeError('A Test cannot be run directly.')
            
    def logical_context(self,con): 
        """!Raises TypeError to indicate that a test cannot be evaluated
        @param con the Context in which this object is being evaluated"""
        raise TypeError('A Test cannot be evaluated in a logical context.')

    def new_empty(self):
        """!Creates a Test that is identical to this one, but without
        dependencies.

        Uses the Test.__init__() constructor to make a new Test that
        is identical to this one, but without dependencies

        @returns the copied Test"""
        return Test(self.defscopes,self.name,self.mode)

########################################################################

class AutoDetectPlatform(object):
    """!Uses a list of Platform objects to detect the local platform.
    This involves running scripts at parse time.  This is the
    implementation of the "autodetect" command."""
    def __init__(self):
        """!Constructor for AutoDetectPlatform"""
        super(AutoDetectPlatform,self).__init__()
        self.__platforms=list()
    def add(self,platform):
        """!Adds a Platform to the list of platforms to use for detection"""
        self.__platforms.append(platform)
    def detect(self,con):
        """!Returns the list of Platform objects detected on this machine.

        Resolves "detect" via Platform.resolve() on all platforms
        given to add().  Evaluates the resulting values in a logical
        context, and constructs a list with all Platform objects whose
        logical context is True.  

        @param con the Context in which this object is being evaluated
        @returns the list of detected platforms.  This list will be
        empty if no platforms are detected."""
        matches=list()
        names=list()
        for platform in self.__platforms:
            detecter=platform.resolve('detect')
            name=platform.resolve('PLATFORM_NAME')
            name=name.string_context(con)
            con.info('%s: detection...'%(name,))
            detection=detecter.logical_context(con)
            if detection:
                con.info('%s: PLATFORM DETECTED'%(name,))
                matches.append(platform)
                names.append(name)
            else:
                con.info('%s: not detected'%(name,))
        con.info('List of platforms detected: '+
                 ' '.join([ repr(s) for s in names ]))
        return matches

########################################################################

class Numeric(BaseObject):
    """!Represents a numeric literal.  This may be a real or integer value"""
    def __init__(self,value):
        """!Constructor for Numeric
        @param value The value, a float or int."""
        super(Numeric,self).__init__([])
        self.is_scalar=True
        self.__value=value
    def string_context(self,con):
        """!Uses "%g" to convert this Numeric's value to a string.
        @param con the Context in which this object is being evaluated
        @returns the resulting string"""
        return '%g'%self.__value
    def bash_context(self,con):
        """!Uses "%g" to convert this Numeric's value to a bash code block.
        @param con the Context in which this object is being evaluated
        @returns the resulting string"""
        return '"%g"'%self.__value
    def numeric_context(self,con):
        """!The value of this Numeric.
        @returns the value sent to the constructor."""
        return self.__value
    def logical_context(self,con):
        """!Is the value 0?

        @returns False if the value of this Numeric is identically 0,
        or True if it is not."""
        return self.numeric_context(con)!=0
    def __str__(self):
        return str(self.__value)
    def __repr__(self):
        return repr(self.__value)
    def rescope(self,scopemap=None,prepend=None): 
        """!Returns a copy of self
        @param scopemap ignored
        @param prepend ignored"""
        return Numeric(self.__value)
    
########################################################################

class String(BaseObject):
    """!Represents a string literal."""
    def __init__(self,defscopes,value,should_expand):
        """!Constructor for String

        @param defscopes a stack of Scope objects to the point at
        which this String was defined, innermost Scope first.  This is
        used for string expansion.

        @param value the string value
        @param should_expand if True, the string should be expanded
        when evaluated.  If False, the string value is returned
        without expansion."""
        super(String,self).__init__(defscopes)
        self.__value=str(value)
        self.is_scalar=True
        self.should_expand=bool(should_expand)
    def rescope(self,scopemap=None,prepend=None):
        """!Modifies this object's scopes, and that of any subobjects.

        Subclasses that can be expressed as non-constant values must
        implement this function for rescoping.  This function changes
        the stack of defining scopes, defscopes, based on arguments

        @param scopemap a mapping from old Scope to new Scope during
        the replacement

        @param prepend a list of Scope objects to prepend.  These
        become the innermost scopes.  The scopemap is NOT applied to
        the prepend list.
        @returns self"""
        if prepend is None: prepend=[]
        if scopemap is None: scopemap={}
        assert(isinstance(scopemap,dict))
        assert(isinstance(prepend,list))
        defscopes=list(prepend)
        for s in self.defscopes:
            assert(isinstance(s,Scope))
            if s in scopemap:
                defscopes.append(scopemap[s])
            else:
                defscopes.append(s)
                # prepend+[ scopemap[s] if s in scopemap else s
                #         for s in self.defscopes ],
        return String(defscopes,
                      self.__value,self.should_expand)
    def string_context(self,con):
        """!Returns this object in a string context.

        Returns a string version of this String.  If should_expand is
        True, then the string is expanded via Scope.expand_string().
        Otherwise, the value is returned unmodified.

        @param con the Context in which this object is being evaluated
        @returns the resulting string"""
        if self.should_expand:
            return self.defscopes[0].expand_string(
                self.__value,con,self.defscopes[1:])
        else:
            return self.__value
    def bash_context(self,con):
        """!Returns this string evaluated as a bash code block

        Uses string_context() to evaluate this String in a string
        context, which expands the string if needed.  Turns the result
        into a bash string definition using
        produtil.testing.utilities.bashify_string()

        @returns a bash string literal representing this String."""
        return bashify_string(self.string_context(con))
    def logical_context(self,con):
        """!Evaluates this string in a logical context.

        Uses string_context() to evaluate this String in a string
        context, which expands the string if needed.  Converts to a
        logical by looking for one of the following values, case
        insensitively:

        - .true., true, yes, t, y: return True
        - .false., false, no, f, n: return False
        - anything else: raise ValueError

        @return True or False if the contents of this string are
        recognized as a logical value
        @raise ValueError if the contents of this string are not
        recognized as a logical value."""
        s=self.string_context(con)
        s=s[-30:].lower()
        if s in [ '.true.', 'true', 'yes', 't', 'y' ]: return True
        if s in [ '.false.', 'false', 'no', 'f', 'n' ]: return False
        try:
            i=float(s)
        except ValueError as ve:
            pass
        raise ValueError('Cannot parse %s as a logical value.'%(s,))
    def numeric_context(self,con):
        """!Evaluates the string in a numeric context.

        Uses string_context() to evaluate this String in a string
        context, which expands the string if needed.  Converts to a
        float using the Python built-in float() constructor.

        @returns this string coerced to a float
        @raise ValueError if float() does not recognize the value"""
        s=self.string_context(con)
        return float(s)
    def __str__(self): return self.__value
    def __repr__(self): return 'String(%s)'%(repr(self.__value),)
    def __bool__(self):
        return bool(self.__value)

########################################################################

class Environ(Scope):
    """!A read-only Scope that represents os.environ"""
    def __init__(self):
        """!Constructor for Environ"""
        super(Environ,self).__init__([])
        self.can_be_used=False
    def new_empty(self): 
        """!Returns a new Environ via Environ.__init__()"""
        return Environ()
    def bash_context(self,con):
        """!Raises an Exception to indicate that Environ cannot be
        evaluated.
        @param con the Context in which this object is being evaluated"""
        raise PTParserError('Cannot express the environment in a bash context.')
    def string_context(self,con):
        """!Raises an Exception to indicate that Environ cannot be
        evaluated.
        @param con the Context in which this object is being evaluated"""
        raise PTParserError('Cannot evaluate the environment in a string context.')
    def no_nulls(self): return True
    def _set_parameters(self,update):
        """!Raises an Exception to indicate that Environ cannot be
        modified.
        @param con the Context in which this object is being evaluated"""
        raise PTParserError('Cannot set parameters in the environment.')
    def numeric_context(self,con):
        """!Raises an Exception to indicate that Environ cannot be
        evaluated.
        @param con the Context in which this object is being evaluated"""
        raise PTParserError('Cannot evaluate the environment in a numeric context.')
    def logical_context(self,con):
        """!Raises an Exception to indicate that Environ cannot be
        evaluated.
        @param con the Context in which this object is being evaluated"""
        raise PTParserError('Cannot evaluate the environment in a logical context.')
    def as_parameters(self,con):
        """!Raises an Exception to indicate that Environ cannot be
        modified.
        @param con the Context in which this object is being evaluated"""
        raise PTParserError('Cannot turn the environment into a parameter list.')
    def rescope(self,scopemap=None,prepend=None):
        """! Does nothing and returns self
        @param scopemap ignored
        @param prepend ignored
        @returns self"""
        return self
    def has_parameters(self):
        """!Returns False to indicate the environment contains no
        parameters (function arguments)"""
        return False
    def use_from(self,used_scope,only_scalars=False):
        """!Raises an exception to indicate that the environment
        cannot be modified."""
        raise PTParserError('Cannot use other scopes within the environment.')
    def apply_parameters(self,scope,con):
        """!Raises an exception to indicate that the environment cannot be executed"""
        raise PTParserError('Cannot call the environment.')
    def __str__(self):
        return 'Environ()'
    def __repr__(self):
        return 'Environ()'
    def subscope(self,key):
        """!Raises an exception to indicate that the environment has no subscopes."""
        raise TypeError('The environment has no subscopes.')
    def getlocal(self,key):
        """!Looks up the given environment variable.

        Searches os.environ for the environment variable named in key.
        Places the result in a String object with expand_string=False
        (no string expansion).  Environment variables set to the null
        string will have an empty String() returned.

        @return the value of the environment variable as a String
        @raise KeyError if the environment variable is not set"""
        return String([self],os.environ[key],False)
    def setlocal(self,key,value):
        """!Raises an exception to indicate that the environment cannot be modified."""
        raise PTParserError('Refusing to modify the environment.')
    def haslocal(self,key):
        """!Is this environment variable set?

        Checks os.environ for the environment variable.  

        @returns True if the environment variable is set, False
        otherwise.  Environment variables that are set to the null
        string are considered to be set, and will generate a True
        return value."""
        return key in os.environ
    def iterlocal(self):
        """!Iterates over the environment variables and their values

        Iterates over the environment, yielding tuples containing the
        environment variable name and its value.  Iteration is in the
        order returned by os.environ.iteritems()"""
        for k,v in os.environ.items():
            yield k,String([self],v,False)
    def resolve(self,key,scopes=None):
        """!Gets the environment variable, returning it as a python string.

        Searches for environment variables in os.environ.  It will
        refuse to look up keys with "." or "%" in them.  Otherwise, it
        is identical to os.environ.__getitem__()

        @returns the environment variable's value as a string
        @raise ValueError if the key contains "." or "%"
        @raise KeyError if the environment variable is not set.  A
        variable set to a null string is considered to be set, and
        will not generate a KeyError."""
        if '.' in key or '%' in key:
            raise ValueError('Invalid environment variable \"%s\".'%(key,))
        return os.environ[key]
    def force_define(self,key,value):
        """!Raises an exception to indicate that the environment cannot be modified."""
        raise PTParserError('Refusing to modify the environment.')
    def check_define(self,key,value):
        """!Raises an exception to indicate that the environment cannot be modified."""
        raise PTParserError('Refusing to modify the environment.')
