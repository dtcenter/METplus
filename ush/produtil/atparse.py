"""!ATParser is a text parser that replaces strings with variables and
function output."""

import sys, os, re, StringIO, logging

##@var functions
# List of functions recognized
# @protected
functions=dict(lc=lambda x:str(x).lower(),
               uc=lambda x:str(x).upper(),
               len=lambda x:str(len(x)),
               trim=lambda x:str(x).strip())

class ParserSyntaxError(Exception): 
    """!Raised when the parser encounters a syntax error."""
class ScriptAssertion(Exception):
    """!Raised when a script @[VARNAME:?message] is encountered, and
    the variable does not exist."""
class ScriptAbort(Exception): 
    """!Raised when an "@** abort" directive is reached in a script."""
class NoSuchVariable(Exception):
    """!Raised when a script requests an unknown variable."""
    def __init__(self,infile,varname,line=None):
        """!NoSuchVariable constructor
        @param infile the input file that caused problems
        @param varname the variable that does not exist
        @param line the line number of the problematic line"""
        self.infile=infile
        self.varname=varname
        if line is None:
            self.line=None
            line='??'
        else:
            self.line=int(line)
            line=str(line)
        super(NoSuchVariable,self).__init__(
            '%s:%s: undefined variable %s'%(infile,line,varname))
    ##@var infile
    # The file that caused the problem

    ##@var line
    # The line number that caused the problem

    ##@var varname
    # The problematic variable name

def replace_backslashed(text):
    """!Turns \\t to tab, \\n to end of line, \\r to carriage return, \\b to
    backspace and \\(octal) to other characters.
    @param text the text to scan"""
    if '0123456789'.find(text[1])>=0:
        return chr(int(text[1:],8))
    elif text=='\\n':
        return "\n"
    elif text=='\\t':
        return "\t"
    elif text=='\\r':
        return "\r"
    elif text=='\\b':
        return "\b"
    else:
        return text

# Parser states:

##@var outer 
# Parser state for the portion of the file outside @[] and @** blocks
outer=dict(active=True,in_if_block=False,in_ifelse_block=False,used_if=False,ignore=False)

##@ var if_unused_if
# Parser state for within @**if blocks that are inactive
if_unused_if=dict(active=False,in_if_block=True,in_ifelse_block=False,used_if=False,ignore=False)

##@var if_active_if
# Parser state for within @** if blocks that are active
if_active_if=dict(active=True,in_if_block=True,in_ifelse_block=False,used_if=True,ignore=False)

##@var if_used_if
# Parser state for after the end of an @** if block
if_used_if=dict(active=False,in_if_block=True,in_ifelse_block=True,used_if=True,ignore=False)

##@var if_active_else
# Parser state for inside an "else" block
if_active_else=dict(active=True,in_if_block=False,in_ifelse_block=True,used_if=True,ignore=False)

##@var if_inactive_else 
# Parser state for inside an "else" block that was not used
if_inactive_else=dict(active=False,in_if_block=False,in_ifelse_block=True,used_if=True,ignore=False)

##@var ignore_if_block
# Parser state for an "if" block that was skipped
ignore_if_block=dict(active=False,in_if_block=True,in_ifelse_block=False,used_if=False,ignore=True)

##@var ignore_else_block
# Parser state for an "else" block that was skipped
ignore_else_block=dict(active=False,in_if_block=False,in_ifelse_block=True,used_if=False,ignore=True)

class ATParser:
    """!Takes input files or other data, and replaces certain strings
    with variables or functions.  

    The calling convention is quite simple:
    @code{.py}
    ap=ATParser(varhash={"NAME":"Katrina", "STID":"12L"})
    ap.parse_file("input-file.txt")
    lines="line 1\nline 2\nline 3 of @[NAME]"
    ap.parse_lines(lines,"(string-data)")
    ap.parse_stream(sys.stdin,"(stdin)")
    @endcode

    Inputs are general strings with @@[...] and @@** escape sequences which
    follow familiar shell syntax (but with @@[...] instead of ${...}):
    @code{.unformatted}
    My storm is @[NAME] and the RSMC is @[RSMC:-${center:-unknown}].
    @endcode
    In this case, it would print:
    @code{.unformatted}
    My storm is Katrina and the RSMC is unknown.
    @endcode
    since NAME is set, but RSMC and center are unset.
    
    There are also block if statements:
    @code{.unformatted}
    @** if NAME==BILLY
    storm is billy
    @** elseif name==KATRINA
    storm is katrina
    @** else
    another storm
    @** endif
    @endcode

    and a variety of other things:
    @code{.unformatted}
    @[<anotherfile.txt]  # read another file
    @[var=value] # assign a variable
    @[var:=value] # assign a variable and insert the value in the output stream
    @[var2:?] # abort if var2 is not assigned, otherwise insert var2's contents
    @[var3==BLAH?thencondition:elsecondition] # if-then-else substitution
    @[var3!=BLAH?thencondition:elsecondition] # same, but with a "not equal"
    @[var4:-substitution] # insert var4, or this substitution if var4 is unset
    @[var5:+text] # insert text if var5 is set
    @endcode

    There are also a small number of functions that modify text before
    it is sent to stdout.  (The original variable is unmodified, only
    the output text is changed.)
    @code{.unformatted}
    @[var1.uc] # uppercase value of var1
    @[var1.lc] # lowercase value of var1
    @[var1.len] # length of var1
    @[var1.trim] # var1 with leading and trailing whitespace removed
    @endcode
    """
    def __init__(self,stream=sys.stdout,varhash=None,logger=None,
                 max_lines=1000000):
        """!ATParser constructor
        @param stream the output stream
        @param varhash a dict of variables.  All values must be strings.
          If this is unspecified, os.environ will be used.
        @param logger the logging.Logger to read.
        @param max_lines the maximum number of lines to read"""
        if varhash is None:
            self.varhash=dict(os.environ)
        else:
            self.varhash=dict(varhash)
        self.__infiles=['(string)']
        self._states=list()
        self.__stream=stream
        self.__max_lines=int(max_lines)
        self.__logger=logger
    ##@var varhash
    # The dict of variables.  This is NOT the dict sent to the constructor --- a
    # copy was made.  That means it is safe to modify the variables all you want,
    # even if os.environ was used.

    def warn(self,text):
        """!Print a warning to the logger, if we have a logger.
        @protected
        @param text the warning text."""
        if self.__logger is not None:
            self.__logger.warn(text)
    @property
    def max_lines(self):
        """!The maximum number of lines to read."""
        return self.__max_lines
    @property
    def infile(self):
        """!The current input file name."""
        return self.__infiles[-1]
    def _write(self,data):
        """!Write data to the output stream
        @param data the data to write."""
        self.__stream.write(data)
    def applyfun(self,val,fun1,morefun):
        """!Applies a function to text.
        @param val the text
        @param fun1 the function to apply
        @param morefun more functions to apply
        @protected"""
        runme=functions.get(fun1,None)
        if runme is not None:
            val=runme(val)
            if val is None: val=''
        else:
            self.warn(
                'Ignoring unknown function \"%s\" -- I only know these: %s'
                 %(fun1, ' '.join(functions.keys())))
        m=re.match('\.([A-Za-z0-9_]+)(.*)',morefun)
        if m:
            (fun2,morefun2)=m.groups()
            return self.applyfun(val,fun2,morefun2)
        return val

    def from_var(self,varname,optional):
        """!Return the value of a variable with functions applied.
        @param varname the variable name, including functions
        @param optional if False, raise an exception if the variable is
          unset.  If True, return '' for unset variables.
        @protected"""
        m=re.match('([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)(.*)',varname)
        if m:
            (varname,fun1,morefun)=m.groups()
            val=self.from_var(varname,optional=optional)
            return self.applyfun(val,fun1,morefun)
        elif varname in self.varhash:
            return self.varhash[varname]
        elif optional:
            return ''
        else:
            raise NoSuchVariable(self.infile,varname)
    
    def optional_var(self,varname):
        """!Return the value of a variable with functions applied, or
        '' if the variable is unset.
        @param varname the name of the variable.
        @protected"""
        return self.from_var(varname,optional=True)

    def require_var(self,varname):
        """!Return the value of a variable with functions applied,
        raising an exception if the variable is unset.
        @param varname the name of the variable.
        @protected"""
        return self.from_var(varname,optional=False)
    
    def replace_vars(self,text):
        """!Expand @@[...] blocks in a string.
        @param text the string
        @returns a new string with expansions performed
        @protected"""
        (text,n) = re.subn(r'(?<!\\)\$[a-zA-Z_0-9.]+',
                             lambda x: self.require_var(x.group(0)[1:]),
                             text)
        (text,n) = re.subn(r'(?<!\\)\$\{[^{}]*\}',
                             lambda x: self.var_or_command(x.group(0)[2:-1]),
                             text)
        (text,n) = re.subn(r'\\([0-9]{3}|.)',
                             lambda x: replace_backslashed(x.group(0)),text)
        return text
    def parse_stream(self,stream,streamname):
        """!Read a stream and parse its contents
        @param stream the stream (an opened file)
        @param streamname a name for this stream for error messages"""
        lineno=1
        for line in stream:
            self.parse_line(line,streamname,lineno)
            lineno+=1

    def parse_file(self,filename):
        """!Read a file and parse its contents.
        @param filename the name of this file for error messages"""
        lineno=1
        with open(filename,'rt') as f:
            for line in f:
                self.parse_line(line,filename,lineno)
                lineno+=1

    def require_file(self,filename_pattern):
        """!Read the contents of a file and return it.
        @param filename_pattern a filename with ${} or @@[] blocks in it.
        @protected"""
        filename=self.replace_vars(filename_pattern)
        with open(filename,'rt') as f:
            return f.read()

    def getvar(self,varname):
        """!Return the value of a variable, or None if it is unset."""
        if varname in self.varhash: return self.varhash[varname]
        return None
    def var_or_command(self,data):
        """!Expand one ${...} or @@[...] block
        @param data the contents of the block
        @protected"""
        m=re.match(r'(?ms)\A([a-z_A-Z][a-zA-Z_0-9]*)'
                   r'((?:\.[A-Za-z0-9.]+)?)'
                   r'(?:(==|!=|:\+|:-|=|:=|:\?|<|:<|:)(.*))?\Z',
                   data)
        if not m:
            return ''
        (varname,functions,operator,operand)=m.groups()
        if operator:
            if operand is None: operand=''
            vartext=self.getvar(varname)
            varset = vartext is not None and vartext!=''
            if functions:
                if vartext is None: varetext=''
                mf=re.match(r'\A\.([A-Z0-9a-z_]+)(.*)\Z',functions)
                (fun,morefun)=mf.groups()
                vartext=self.applyfun(vartext,fun,morefun)
            if operator==':+':
                return self.replace_vars(operand) if varset else ''
            elif operator==':-':
                if not varset: vartext=self.replace_vars(operand)
                return vartext
            elif operator==':':
                val=vartext
                if val is None: val=''
                mo=re.match(r'\A([0-9]+)(?::([0-9]+))?',operand)
                if mo is None:
                    return val
                (start,count)=mo.groups()
                length=len(val)
                if start is None or start=='':
                    start=0
                else:
                    start=int(start)
                if start<0:
                    start=0
                if count is None or count=='':
                    count=length-start
                else:
                    count=int(count)
                if start+count>length:
                    count=length-start
                return val[ start : (start+count) ]
            elif operator=='=':
                replaced=self.replace_vars(operand)
                self.varhash[varname]=replaced
            elif operator=='==' or operator=='!=':
                # This is the ternary ?: operator.
                val=vartext
                mo=re.match(r'(?ms)\A((?:[^\\\?]|(?:\\\\)*|(?:\\\\)*\\.)*)\?(.*?):((?:[^\\:]|(?:\\\\)*|(?:\\\\)*\\.)*)\Z',operand)
                if mo is None:
                    (test,thendo,elsedo)=('','','')
                else:
                    (test,thendo,elsedo)=mo.groups()
                test=self.replace_vars(test)
                if operator=='==':
                    return self.replace_vars( 
                        thendo if (val==test) else elsedo)
                else:
                    return self.replace_vars(
                        thendo if (val!=test) else elsedo)
            elif operator==':=':
                if not varset:
                    self.varhash[varname]=self.replace_vars(operand)
                return self.varhash[varname]
            elif operator==':?':
                if varset:
                    return vartext
                elif operand=='':
                    raise ScriptAssertion('%s: you did not define this '
                                          'variable.  Aborting.'%(varname,))
                else:
                    raise ScriptAssertion('%s: %s'%(varname,operand))
        elif varname is not None and varname!='':
            return self.require_var(varname+functions)
        else:
            raise ParserSyntaxError(
                "Don't know what to do with text \"%s\""%(data,))

    def require_data(self,data):
        """!Expand text within an @@[...] block.
        @param data the contents of the block
        @protected"""
        if data[0]=='<':
            # This is an instruction to read in a file.
            return self.require_file(data[1:])
        elif data=='@':
            return '@' # @[@] is replaced with @
        elif data[0]=='#':
            if data.find('@[')>=0:
                raise ParserSyntaxError('Found a @[ construct nested within a comment (@[#...])')
            return '' # @[#stuff] is a comment
        else:
            # This is a variable name, command or error:
            return self.var_or_command(data)

    def str_state(self):
        """!Return a string description of the parser stack for debugging."""
        out=StringIO.StringIO()
        out.write('STATE STACK: \n')
        for state in self._states:
            out.write('state: ')
            if state['ignore']: 
                out.write('ignoring block: ')
            out.write('active ' if(state['active']) else 'inactive ')
            if state['in_if_block']: 
                out.write('in if block, before else ')
            if state['in_ifelse_block']: 
                out.write('in if block, after else ')
            if not state['in_if_block'] and not state['in_ifelse_block']:
                out.write('not if or else')
            if state['used_if']:
                out.write('(have activated a past if/elseif/else) ')
            out.write('\n')
        out.write('END\n')
        s=out.getvalue()
        out.close()
        return s
    
    @property
    def active(self):
        """!Is the current block active?
        @protected"""
        if self._states:
            for state in self._states:
                if not state['active']:
                    return False
        return True

    def top_state(self,what=None):
        """!Return the top parser state without removing it
        @param what why the state is being examined.  This is for
          error messages.
        @protected"""
        if what:
            if not self._states:
                raise AssertionError('Internal error: no state to search when looking for %s in top state.'%(what,))
            elif what not in self._states[-1]:
                raise AssertionError('Internal error: cannot find %s in top state.'%(what,))
            return bool(self._states[-1][what])
        else:
            return self._states[-1]

    def push_state(self,state):
        """!Push a new state to the top of the parser state stack
        @protected"""
        self._states.append(state)

    def pop_state(self):
        """!Remove and return the top parser state
        @protected"""
        return self._states.pop()

    def replace_state(self,state):
        """!Replace the top parser state.
        @protected
        @param state the new parser state"""
        self._states[len(self._states)-1]=state

    def parse_lines(self,lines,filename):
        """!Given a multi-line string, parse the contents line-by-line
        @param lines the multi-line string
        @param filename the name of the file it was from, for error messages"""
        lineno=1
        for line in lines.splitlines():
            self.parse_line(line,filename,lineno)
            lineno+=1

    def parse_line(self,line,filename,lineno):
        """!Parses one line of text.  
        @param line the line of text.
        @param filename the name of the source file, for error messages
        @param lineno the line number within the source file, for 
          error messages"""
        top_state=self.top_state
        replace_state=self.replace_state

        m=re.match(r'^\s*\@\*\*\s*if\s+([A-Za-z_][A-Za-z_0-9.]*)\s*([!=])=\s*(.*?)\s*$',line)
        if m:
            # This is the beginning of an IF block
            if not self.active:
                # This IF lies within an inactive block, so we skip
                # this whole if, elseif, else, endif block.
                self.push_state(ignore_if_block)
                return
            (left,comp,right)=m.groups()
            left=self.optional_var(left)
            right=self.replace_vars(right)
            if left==right:
                if comp=='=':
                    self.push_state(if_active_if)
                else:
                    self.push_state(if_unused_if)
#                self.push_state( if_active_if if(comp=='=') else if_unused_if )
            else:
                if comp=='=':
                    self.push_state(if_unused_if)
                else:
                    self.push_state(if_active_if)
#                self.push_state( if_unused_if if(comp=='=') else if_active_if )
            return

        m=re.match(r'^\s*\@\*\*\s*abort\s+(.*)$',line)
        if m:
            if self.active:
                raise ScriptAbort('Found an abort directive on line %d: %s'%(
                    lineno, m.group(1)))
            return

        m=re.match(r'^\s*\@\*\*\s*warn\s+(.*)$',line)
        if m:
            if self.active:
                self.warn(self.replace_vars(m.group(1)))
            return

        m=re.match('^\s*\@\*\*\s*else\s*if\s+([A-Za-z_][A-Za-z_0-9.]*)\s*([!=])=\s*(.*?)\s*\Z',line)
        if m:
            if top_state('ignore'): return
            (left, comp, right) = m.groups()
            left=self.optional_var(left)
            right=self.replace_vars(right)
            if not self._states:
                raise ParserSyntaxError(
                    'Found an elseif without a matching if at line %d'%lineno)
            if not top_state('in_if_block'):
                if top_state('in_ifelse_block'):
                    raise ParserSyntaxError(
                        'Unexpected elseif after an else at line %d'%lineno)
                else:
                    raise ParserSyntaxError(
                        'Unexpected elseif at line %d'%lineno)
            elif top_state('used_if'):
                # the "if" or a prior elseif matched, so we ignore
                # this elseif and deactivate the block so all future
                # if/else/elseif will be unused.
                replace_state(if_used_if)
            elif not top_state('active'):
                activate=0
                if left==right:
                    activate = 3 if (comp=='=') else 0
                else:
                    activate = 0 if (comp=='=') else 3
                if activate:
                    replace_state(if_active_if)
            return

        m=re.match(r'^\s*\@\*\*\s*else\s*(?:\#.*)?$',line)
        if m:
            if top_state("used_if"):
                replace_state(if_inactive_else)
            elif top_state('in_ifelse_block'):
                raise ParserSyntaxError('Found an extra else at line %d'%lineno)
            elif not top_state('in_if_block'):
                raise ParserSyntaxError('Found an else outside an if at line %d'%lineno)
            elif top_state('ignore'):
                # We're ignoring a whole if/elseif/else/endif block
                # because it lies within an inactive block.
                replace_state(ignore_else_block)
            elif not top_state('used_if'):
                replace_state(if_active_else)
            else:
                replace_state(if_inactive_else)
            return

        m=re.match(r'^\s*\@\*\*\s*endif\s*(?:\#.*)?$',line)
        if m:
            if top_state('in_if_block') or top_state('in_ifelse_block'):
                self.pop_state()
            else:
                raise ParserSyntaxError('Found an endif without matching if at line %d'%lineno)
            return

        m=re.match(r'^\s*\@\*\*\s*insert\s*(\S.*?)\s*$',line)
        if m:
            if self.active:
                contents=self.require_file(m.group(1))
                self._write(contents)
            return

        m=re.match(r'^\s*\@\*\*\s*include\s*(\S.*?)\s*$',line)
        if m:
            if self.active:
                ffilename=m.group(1)
                contents=self.require_file(ffilename)
                self.parse_lines(contents,ffilename)
            return

        m=re.match(r'^\s*\@\*\*.*',line)
        if m:
            raise ParserSyntaxError('Invalid \@** directive in line \"%s\".  Ignoring line.\n'%(line,))
        
        if self._states and not self.active: 
            return # inside a disabled block

        # Replace text of the form @[VARNAME] with the contents of the
        # respective environment variable:
        (outline,n)=re.subn(r'\@\[((?:\n|[^\]])*)\]',
                    lambda x: self.require_data(x.group(0)[2:-1]),
                    line)
        if not isinstance(outline,basestring):
            raise TypeError('The re.subn returned a %s %s instead of a basestring.'%(type(outline).__name__,repr(outline)))
        self._write(outline)
        if lineno>self.max_lines:
            raise ParserLineLimit('Read past max_lines=%d lines from input file.  Something is probably wrong.'%self.max_lines)
