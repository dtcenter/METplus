"""!Common utilities used by other parts of the produtil.testing package."""
        
import sys, re, io, collections, os, datetime, logging

##@var __all__
# List of variables exported by "from produtil.testing.utilities import *"
__all__=[ 'module_logger', 'BASELINE', 'EXECUTION', 'elipses', 'splitkey',
          'dqstring2bracestring', 'is_valid_workflow_name', 'unknown_file',
          'peekable','bashify_string', 'ListableSet', 'PTParserError',
          'PTKeyError', 'PTPlatformError' ]

class PTParserError(Exception): pass
class PTPlatformError(PTParserError): pass
class PTKeyError(PTParserError,KeyError): pass

# def yell(arg):
#     """!Unused; needs to be removed.

#     @todo Remove this function."""
#     pass 

##@var module_logger
# The default logging.Logger to use if no logger is specified.
module_logger=logging.getLogger('produtil.testing')

##@var BASELINE
# A constant that indicates the suite is being run to generate a new baseline.
BASELINE=object()

##@var EXECUTION
# A constant that indicates the suite is being run to verify against
# an existing baseline.
EXECUTION=object()

##@var unknown_file
# A constant string used for logging purposes to indicate a filename
# was unspecified or unknown.
unknown_file='(**unknown**)'

def bashify_string(string):
        """Given a Python string, express it as a bash string.

        Expresses a python string as a bash string.

        Example:

        @code
           print bashify_string("123''$$")
           #  --> prints '123'"''"'$$'
        @endcode

        @param string Any subclass of str

        @returns valid bash code to represent the string"""
        output=io.StringIO()
        for m in re.finditer('''(?xs)
            (
                (?P<quotes>'+)
              | (?P<dquotes>"+)
              | (?P<printable>[!-&(-\[\]-~ ]+)
              | (?P<control>.)
            )''',string):
            if m.group('quotes'):
                output.write('"' + m.group('quotes') + '"')
            elif m.group('dquotes'):
                output.write("'" + m.group('dquotes') + "'")
            elif m.group('printable'):
                output.write("'"+m.group('printable')+"'")
            elif m.group('control'):
                output.write("$'\%03o'"%ord(m.group('control')))
        ret=output.getvalue()
        output.close()
        return ret

def elipses(long_string,max_length=40,elipses='...'):
    """!Returns a shortened version of long_string.

    If long_string is longer than max_length characters, returns a
    string of length max_length that starts with long_string and ends
    with elipses.  Hence, the number of characters of long_string that
    will be used is max_length-len(elipses)

    @param long_string a str or subclass thereof
    @param max_length maximum length string to return
    @param elipses the elipses string to append to the end"""
    strlen=len(long_string)
    if strlen<max_length:
        return long_string
    else:
        return long_string[0:max_length-len(elipses)]+elipses

def splitkey(key):
    """!Splits a string on "%" and returns the list, raising an
    exception if any components are empty.

    @returns a list of substrings of key, split on "%"
    @param key a string to split
    @raise ValueError if any substrings are empty"""
    names=key.split("%")
    if any([ not s  for  s in names ]):
        raise ValueError("Empty name component in \"%s\""%(key,))
    return names

def dqstring2bracestring(dq):
    """!Converts a bash-style double quote string to a tripple brace
    string.
    @param dq The bash-style double quote string, minus the 
      surrounding double quotes."""
    output=io.StringIO()
    for m in re.finditer(r'''(?xs)
        (
            \\ (?P<backslashed>.)
          | (?P<braces> [\]\[]+ )
          | (?P<text> [^\\@\]\[]+)
          | (?P<atblock>
                @ \[ @ \]
              | @ \[ ' [^']+ ' \]
              | @ \[ [^\]]+ \]
            )
          | (?P<literal_at> @ (?!\[) )
          | (?P<error> . )
        ) ''',dq):
        if m.group('backslashed'):
            s=m.group('backslashed')
            if s=='@':
                output.write('@[@]')
            elif s in '[]':
                output.write("@['"+s+"']")
            else:
                output.write(s)
        elif m.group('literal_at'):
            output.write('@[@]')
        elif m.group('atblock'):
            output.write(m.group('atblock'))
        elif m.group('braces'):
            output.write("@['"+m.group('braces')+"']")
        elif m.group('text'):
            output.write(m.group('text'))
        else:
            raise ValueError(
                'Cannot convert double-quote string \"%s\" to brace string: '
                'parser error around character \"%s\"."'%(dq,m.group()))
    value=output.getvalue()
    output.close()
    return value

def is_valid_workflow_name(name):
    """!is this a valid name for a produtil.testing workflow?

    Workflow names have to fit within certain restrictions of workflow
    automation suites.  For this reason, we restrict names to begin
    with a letter and only contain letters, numbers and
    underscores.
    @param name the name to check
    @returns True if the name meets requirements and False otherwise"""
    return bool(re.match('(?s)^[a-zA-Z][a-zA-Z0-9_]*$',name))

##@var NO_VALUE
# Special constant used by peekable to indicate nothing has been peeked yet.
# @warning Terrible things will happen if you overwrite this.
# @private
NO_VALUE=object()

class peekable(object):
    """!An iter-like object that has a peek() method to peek at the
    next token without consuming it.

    Example:

    @code
        a=peekable("12345")
        a.next() # 1
        a.next() # 2
        a.next() # 3
        a.peek() # 4 <--- peeks at next element
        a.next() # 4 <--- peek() did not consume 4, so next() returns 4
        a.next() # 5
    @endcode
    """
    def __init__(self,iterator):
        """!Constructor for peekable
        @param iterator any iterable object"""
        self.__child=iterator
        self.__iterator=iter(iterator)
        self.__peek=NO_VALUE
        self.__prior=NO_VALUE

    def has_prior(self):
            return self.__prior is not NO_VALUE

    def prior(self):
            if self.__prior is not NO_VALUE:
                    return self.__prior
            else:
                    return NO_VALUE

    def __next__(self):
        """!Advances the iterator to the next value and returns it"""
        if self.__peek is not NO_VALUE:
            p,self.__peek = self.__peek,NO_VALUE
        else:
            p=next(self.__iterator)
        self.__prior=p
        return p
    def peek(self):
        """!Returns the next value in the iterator or raises StopIteration"""
        if self.__peek is NO_VALUE:
            self.__peek=next(self.__iterator)
        return self.__peek
    def at_end(self):
        """!Returns True if the iterator has reached the last value"""
        if self.__peek is not NO_VALUE:
            return False
        try:
            self.__peek=next(self.__iterator)
        except StopIteration as se:
            return True
        return False
    def __iter__(self):
        """!Iterates over all remaining values."""
        p,self.__peek = self.__peek,NO_VALUE
        if p is not NO_VALUE:
            yield p
        for v in self.__iterator:
            yield v

    @property
    def child(self): 
        """!Returns the iterator"""
        return self.__child


    ##@var child
    # The object being iterated

class ListableSet(object):
    """!An ordered set."""
    def __init__(self,contents=None):
        """!Constructor

        @param contents an iterable object with the elements"""
        super(ListableSet,self).__init__()
        if contents is None:
            self._set=set()
            self._list=list()
        else:
            self._set=set(contents)
            self._list=list(contents)
        self._NOTHING=object()
    def __contains__(self,item):
        """!Is the item in this set?"""
        return item in self._set
    def __iter__(self):
        """!Iterates over the set's elements in order."""
        for s in self._list:
            yield s
    def __str__(self):
        """!A string representation of this set in set notation."""
        return '{ '+', '.join([ repr(s) for s in self._list ])+' }'
    def __repr__(self):
        """!A string representation of this set in pythonic notation"""
        return 'ListableSet([ '+', '.join(
            [ repr(s) for s in self._list ])+' ])'
    def add(self,item):
        """!Adds the item to the end of this set, unless it is already a member"""
        if item not in self:
            self._set.add(item)
            self._list.append(item)
    def minus(self,other):
        """!Removes the other set's items from this set."""
        for s in other:
            if s in self:
                self._set.discard(s)
                self._list.remove(s)
    def inter(self,other):
        """!Adds any items from the other set that are not in this set."""
        remove=set()
        for s in self:
            if s not in other:
                remove.add(s)
        for s in remove:
            self._set.discard(s)
            self._list.remove(s)
    def union(self,other):
        """!Performs a set union, adding the other set's items to this
        set, except those already present.  Preserves the order of the
        items while adding them by inserting new items in this set after
        immediately preceeding ones in the other set."""
        prior=self._NOTHING
        iprior=-1
        for s in other:
            if s in self:
                prior=s
                iprior=self._list.index(s)
            elif prior is not self._NOTHING:
                self._list.insert(iprior+1,s)
                self._set.add(s)
                prior=s
                iprior=iprior+1
            else:
                self._list.append(s)
                self._set.add(s)
                prior=s
                iprior=len(self._list)
