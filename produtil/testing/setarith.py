"""!Set arithmetic logic utilities.  This implements a simple set
logic language, and uses it to combine Python sets.  It operates on
produtil.testing.utilities.ListableSet objects.  The main entry point,
arithparse(), returns a result of the same type.

Examples:

@code
elements=ListableSet(["cat","dog","orange","salmon","bin"])
sets={ "alive":    ListableSet(["cat","dog","orange","salmon"]),
       "colors":   ListableSet(["orange","salmon"]),
       "commands": ListableSet(["cat","bin"]),
       "verbs":    ListableSet(["cat","dog","bin"])
       }

# Request a single set:
arithparse("alive",sets,elements)
#  --> ListableSet(["cat","dog","orange","salmon"])

# Subtraction of two sets:
arithparse("minus(alive,colors)",sets,elements)
#  --> ListableSet(["cat","dog"])

# Union of two sets:
arithparse("union(colors,commands)",sets,elements)
#  --> ListableSet(["orange","salmon","cat","bin"])

# Intersection of two sets:
arithparse("inter(alive,verbs)",sets,elements)
#  --> ListableSet(["cat","dog"])

# Individual elements:
arithparse("{cat,orange}")
#  --> ListableSet(["cat","orange"])

# Combination of the above:
arithparse("minus(inter(union({dog,orange},commands),alive),verbs)")
#  --> ListableSet(["dog"])
@endcode

"""

import os, re

from produtil.testing.utilities import peekable, ListableSet, PTParserError

__all__=[ 'ArithPTParserError', 'arithparse', 'ArithKeyError' ]

def arithparse(spec,sets,elements):
    """!Main entry point to the setarith module.

    Performs the specified set arithmetic on the given elements and
    sets, returning the resulting set.

    @param spec A setarith language expression describing the operation.

    @param sets A mapping from set name to
    produtil.testing.utilities.ListableSet objects that represent each
    set.

    @param elements All known elements.  This is a superset of all
    other sets, and may contain additional elements.
"""
    assert(isinstance(spec,str))
    tokiter=peekable(_arithtoken(spec))
    result=_arithparse_top(tokiter,sets,elements)
    return result

class ArithException(PTParserError):
    """!Raised for parser errors in the inputs to the set arithmetic
    parser (arithparse)."""

class ArithKeyError(ArithException,KeyError):
    """!Raised when an element or set is requested that does not exist"""

########################################################################

def _arithtoken(spec):
    """!Tokenizes a set arithmetic expression.
    @protected
    @see arithparse()"""
    assert(isinstance(spec,str))
    for m in re.finditer(r'''(?xs)
        (
            (?P<oper>[A-Za-z]+) \(
          | (?P<endoper> \) )
          | (?P<setname> [A-Za-z][A-Za-z%._0-9]* )
          | (?P<comma> , )
          | (?P<lset> \{ )
          | (?P<rset> \} )
          | (?P<whitespace>\s+)
          | (?P<star>\*)
          | (?P<error> . )
        )''',spec):
        if m.group('whitespace'):
            continue # ignore whitespace
        elif m.group('oper'):
            yield 'oper',m.group('oper')
        elif m.group('endoper'):
            yield ')',m.group('endoper')
        elif m.group('setname'):
            yield 'set',m.group('setname')
        elif m.group('comma'):
            yield ',',','
        elif m.group('lset'):
            yield '{','{'
        elif m.group('rset'):
            yield '}','}'
        elif m.group('star'):
            yield '*','*'
        elif m.group('error'):
            raise ArithException('Unexpected character %s'%(
                    repr(m.group('error')),))
    yield '',''

########################################################################

def each_not_all(sets):
    """!Iterates over the given ListableSet, yielding everything
    except the special set "*" """
    for s in sets.keys():
        if s[0]!='*':
            yield s

# Internal implementation routines

def _arithparse_set(tokiter,elements):
    """!Parses an explicit set definition

    Parses a list of elements:

    @code
      {element1,element2,element3}
    @endcode

    @param tokiter a peekable iterator that yields tokens
    @param elements All known elements.  This is a superset of all
    other sets, and may contain additional elements.

    @returns a new ListableSet
    @protected
    """
    typ,data=tokiter.peek()
    result=ListableSet()
    while typ=='set':
        if data in elements:
            result.add(elements[data])
        else:
            raise ArithKeyError(
                'Unknown test %s. Please select one of: { %s }'%(
                    repr(data), ', '.join([
                            str(k) for k in elements.keys()])))
        next(tokiter) # discard element name
        typ,data=tokiter.peek()
        if typ==',':
            typ,data=next(tokiter) # discard comma and then
            typ,data=tokiter.peek() # peek next token
    if not typ:
        raise ArithException(
            'Unexpected end of text when parsing an '
            'argument list to an operator.')
    if typ!='}':
        raise ArithException(
            'Unexpected %s when parsing an set {} definition '%(repr(data),))
    else:
        next(tokiter)
    return result

def _arithparse_list(tokiter,sets,elements):
    """!Iterates over the arguments to a set arithmetic function,
    yielding sets.  Calls _arithparse_expr() on each argument.

    @param elements All known elements.  This is a superset of all
    other sets, and may contain additional elements.

    @param sets A mapping from set name to
    produtil.testing.utilities.ListableSet objects that represent each
    set.

    @protected
    @see arithparse()
    @returns Nothing; this is an iterator."""
    yielded=False
    typ,data=tokiter.peek()
    while typ in ['oper','set','{','*']:
        result=_arithparse_expr(tokiter,sets,elements)
        assert(isinstance(result,ListableSet))
        yield result
        yielded=True
        typ,data=tokiter.peek()
        if typ==',':
            typ,data=next(tokiter) # discard comma and then
            typ,data=tokiter.peek() # peek next token
    if not typ:
        raise ArithException(
            'Unexpected end of text when parsing an '
            'argument list to an operator.')
    if typ!=')':
        raise ArithException(
            'Unexpected %s when parsing an argument '
            'list to an operator.'%(repr(data),))
    else:
        typ,data=next(tokiter) # discard )

def _arithparse_expr(tokiter,sets,elements):
    """!Evaluates one set arithmetic expression.

    Parses any expression with balanced parentheses.  That can be
    anything from the entire string to a single set name.

    @protected

    @param tokiter a produtil.testing.utilities.peekable object that
    iterates over the expression.
    @param sets A mapping from set name to
    produtil.testing.utilities.ListableSet objects that represent each
    set.
    @param elements All known elements.  This is a superset of all
    other sets, and may contain additional elements.
    @returns the resulting ListableSet"""

    result='invalid value that should be replaced by below code'
    typ,data=next(tokiter)
    if typ=='oper':
        if data=='union':
            # Union of no sets is the empty set:
            result=None
            for subset in _arithparse_list(tokiter,sets,elements):
                if result is None:
                    result=subset
                else:
                    result.union(subset)
            if result is None:
                result=ListableSet()
        elif data=='inter':
            result=None
            for subset in _arithparse_list(tokiter,sets,elements):
                if result is None:
                    result=subset
                else:
                    result.inter(subset)
            if result is None:
                # Intersection of no sets is the empty set:
                result=ListableSet()
        elif data=='minus':
            result=None
            for subset in _arithparse_list(tokiter,sets,elements):
                if result is None:
                    result=subset
                else:
                    result.minus(subset)
        else:
            raise ArithException('Invalid operator %s.  Should be union, '
                            'inter, or minus.'%(data,))
    elif typ=='set':
        if data not in sets:
            raise ArithKeyError('Unknown runset %s.  Known sets: { %s }'%(
                    repr(data), ', '.join([
                            str(k) for k in each_not_all(sets)])))
        result=ListableSet(sets[data])
    elif typ=='*':
        result=ListableSet([val for key,val in elements.items()])
    elif typ=='{':
        result=_arithparse_set(tokiter,elements)
    else:
        raise ArithException('Unexpected %s in set spec.'%(repr(data),))
    assert(isinstance(result,ListableSet))
    return result

def _arithparse_top(tokiter,sets,elements):
    """!Evaluates the null string, or one set arithmetic expression.

    When given the null string, this immediately returns an empty
    ListableSet.  Otherwise, it passes control to _arithparse_expr()
    to parse the resulting expression.

    @protected

    @param tokiter a produtil.testing.utilities.peekable object that
    iterates over the expression.
    @param sets A mapping from set name to
    produtil.testing.utilities.ListableSet objects that represent each
    set.
    @param elements All known elements.  This is a superset of all
    other sets, and may contain additional elements.
    @returns the resulting ListableSet"""
    typ,data = tokiter.peek()
    if not typ:
        return ListableSet()
    return _arithparse_expr(tokiter,sets,elements)
