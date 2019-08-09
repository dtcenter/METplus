"""!Tokenizer for the produtil.testing.parser module."""

import re
import produtil.testing.utilities

__all__=[ 'Token', 'end_of_line_type', 'end_of_text_type', 'Tokenizer',
          'TokenizeFile' ]

class Token(object):
    """!Represents one token in the tokenized version of a file."""

    ##@var token_type
    # The type of token, a string

    ##@var token_value
    # The text that was tokenized, a string.

    ##@var filename
    # The file from which this token originates, a string.  The
    # special value produtil.testing.utilities.unknown_file indicates
    # the file is unknown or the token is not from a file.

    ##@var lineno
    # The line from file filename fron which this token originates, an integer.
    # The special value -1 means the line is unknown.

    def __init__(self,token_type,token_value,filename,lineno):
        """!Constructor for Token
        
        @param token_type The type of token, a string
        @param token_value The text this token represents, a string.

        @param filename The name of the file from which this token
        originates or produtil.testing.utilities.unknown_file if
        unknown.

        @param lineno The integer line number, counting from 1, from
        which this token originates.  Multi-line tokens should have a
        line number representative of the region the token originates,
        preferably on its first line.  If the token is not from a
        file, the value should be -1."""
        super(Token,self).__init__()
        self.token_type=token_type
        self.filename=filename
        self.lineno=lineno
        self.token_value=token_value
    def __repr__(self):
        """!A string representation of this token suitable for debugging.

        @returns Python code that would construct this token."""
        return 'Token(%s,%s,%s,%s)'%(
            repr(self.token_type),repr(self.token_value),
            repr(self.filename),repr(self.lineno))
    def __str__(self):
        """!A human-readable string representation of this token.

        @returns Python code that would construct this token."""
        return 'Token(%s,%s,%s,%s)'%(
            repr(self.token_type),repr(self.token_value),
            repr(self.filename),repr(self.lineno))

##@var end_of_line_type
# The token_type parameter to send to Token.__init__() to indicate the
# end of a line
end_of_line_type='\n'

##@var end_of_text_type
# The token_type parameter to send to Token.__init__() to indicate the
# end of a file or string.
end_of_text_type=''

class Tokenizer(object):
    """!Tokenizes a file, turning it into a stream of Token objects
    for parsing."""

    ##@var re
    # A compiled regular expression used to tokenize the file.

    def copy(self):
        """!Duplicates this object
        
        At present, a Tokenizer has no internal state information.
        Hence, this is equivalent to Tokenizer().  This may change in
        the future.  Hence, if you want to copy a Tokenizer, you
        should use the copy() function.

        @returns A new empty Tokenizer."""
        return Tokenizer()
    def __init__(self):
        """!Constructor for Tokenizer"""
        super(Tokenizer,self).__init__()
        #yell('compile\n')
        self.re=re.compile(r'''(?xs)
                (
                    (?P<comment> \# [^\r\n]+ (?: \r | \n )+ )
                  | (?P<commentend> \# [^\r\n]+ | \# ) $
                  | (?P<varname> [A-Za-z_] [A-Za-z_0-9.@]*
                       (?: % [A-Za-z_][A-Za-z_0-9.@]* )* )
                  | (?P<hash>\#)
                  | (?P<number>
                        [+-]? [0-9]+\.[0-9]+ (?: [eE] [+-]? [0-9]+ )?
                      | [+-]?       \.[0-9]+ (?: [eE] [+-]? [0-9]+ )?
                      | [+-]? [0-9]+\.       (?: [eE] [+-]? [0-9]+ )?
                      | [+-]? [0-9]+         (?: [eE] [+-]? [0-9]+ )?
                    )
                  | (?P<empty_qstring>  '' )
                  | (?P<empty_dqstring> "" )
                  | ' (?P<qstring> (?:
                        [^'\\]
                      | ( \\ . )+ ) * ) '
                  | " (?P<dqstring> (?:
                        [^"\\]
                      | ( \\ . )+ ) * ) "
                  | \[\[\[ (?P<bracestring> (?:
                        [^\]@]
                      | @ (?!\[)
                      | @ \[ @ \]
                      | @ \[ ' [^']+ ' \]
                      | @ \[ [^\]]+ \]
                      | \]\] (?!\])
                      | \] (?!\])
                    ) *? ) \]\]\]
                  |   (?P<endline>[ \t]* [\r\n]+)
                  |   (?P<equalequal> == )
                  |   (?P<equal> = )
                  |   (?P<astrisk> \* )
                  |   (?P<whitespace> [ \t]+ )
                  |   (?P<lset>\{)
                  |   (?P<rset>\})
                  |   (?P<lfort>\(/)
                  |   (?P<rfort>/\))
                  |   (?P<lparen>\()
                  |   (?P<rparen>\))
                  |   (?P<comma>,)
                  |   (?P<colon>:)
                  |   (?P<at>@)
                  |   (?P<oper>\.[a-zA-Z_][a-zA-Z0-9_.]*\.)
                  |   <=+ (?P<filter>[a-zA-Z_][a-zA-Z0-9_.]*) =+
                  |   (?P<error> . )
                )''')
    def tokenize(self,text,filename=produtil.testing.utilities.unknown_file,
                 first_line=1):
        """!Tokenizes the specified file, acting as an iterator over Token objects.

        Loops over the text of the given file, creating Token objects
        and yielding them.  

        @param text The text to tokenize.
        @param filename The file from which the text originates.  This may be used
          for two purposes.  The first is error reporting, and the second is 
          "load" statements, which load files relative to the path to the 
          current file.
        @param first_line The line number for the first line of the file."""
        lineno=first_line
        for m in self.re.finditer(text):
            if m is None: 
                raise ValueError('SHOULD NOT GET HERE: no match on "%s"'%(line,))
            # else:
            #     for dkey,dval in m.groupdict().items():
            #         if dval is not None:
            #             yell("%10s = %s\n"%(dkey,repr(dval)))
            if m.group('comment'):
                yield Token(end_of_line_type,m.group('comment'),
                            filename,lineno)
            elif m.group('commentend'):
                yield Token(end_of_line_type,m.group('commentend'),
                            filename,lineno)
            elif m.group('hash'):
                yield Token(end_of_line_type,m.group('commentend'),
                            filename,lineno)
            elif m.group('endline'):
                yield Token(end_of_line_type,m.group('endline'),
                            filename,lineno)
            elif m.group('oper'):
                yield Token('oper',m.group('oper'),filename,lineno)
            elif m.group('filter'):
                yield Token('oper','.'+m.group('filter')+'.',filename,lineno)
            elif m.group('varname'):
                yield Token('varname',m.group('varname'),filename,lineno)
            elif m.group('number'):
                yield Token('number',m.group('number'),filename,lineno)
            elif m.group('empty_qstring'):
                yield Token('qstring','',filename,lineno)
            elif m.group('empty_dqstring'):
                yield Token('dqstring','',filename,lineno)
            elif m.group('qstring'):
                yield Token('qstring',m.group('qstring'),filename,lineno)
            elif m.group('dqstring'):
                yield Token('dqstring',m.group('dqstring'),filename,lineno)
            elif m.group('bracestring'):
                yield Token('bracestring',m.group('bracestring'),
                            filename,lineno)
            elif m.group('at'):
                yield Token('@','@',filename,lineno)
            elif m.group('equalequal'):
                yield Token('==','==',filename,lineno)
            elif m.group('equal'):
                yield Token('=','=',filename,lineno)
            elif m.group('comma'):
                yield Token(',',',',filename,lineno)
            elif m.group('colon'):
                yield Token(':',':',filename,lineno)
            elif m.group('lset'):
                yield Token('{','{',filename,lineno)
            elif m.group('rset'):
                yield Token('}','}',filename,lineno)
            elif m.group('lparen'):
                yield Token('(','(',filename,lineno)
            elif m.group('rparen'):
                yield Token(')',')',filename,lineno)
            elif m.group('lfort'):
                yield Token('(/','(/',filename,lineno)
            elif m.group('rfort'):
                yield Token('/)','/)',filename,lineno)
            elif m.group('whitespace'):
                pass # Ignore whitespace outside strings
            else:
                raise ValueError('%s:%d: invalid text %s'%(
                        filename,lineno,repr(m.group(0))))
            lineno+=m.group(0).count('\n')
        yield Token(end_of_text_type,'',filename,lineno)

class TokenizeFile(object):
    """!Wrapper around a Tokenizer for a specified file.

    This is a convenience class; it is a wrapper around a Tokenizer,
    but also knows how to create new TokenizeFile objects for the same
    type of underlyting Tokenizer objects (for_file())."""

    ##@var tokenizer
    # The Tokenizer object that turns text into sequences of Token objects.
    
    ##@var fileobj
    # A file-like object that produces text for the tokenizer

    ##@var filename
    # The name of the file that fileobj reads.

    ##@var first_line
    # The integer first line of the file, usually 1.

    def __init__(self,tokenizer,fileobj,
                 filename=produtil.testing.utilities.unknown_file,
                 first_line=1):
        """!Constructor for TokenizeFile
        @param tokenizer The Tokenizer-like object to parse.
        @param fileobj The opened file-like object to read.
        @param filename The file from which the text originates.  This may be used
          for two purposes.  The first is error reporting, and the second is 
          "load" statements, which load files relative to the path to the 
          current file.
        @param first_line The line number for the first line of the file."""
        self.tokenizer=tokenizer
        self.fileobj=fileobj
        self.filename=filename
        self.first_line=first_line
    def for_file(self,fileobj,filename,first_line=1):
        """!Creates a new TokenizeFile object for the specified file.

        @param fileobj The file-like object to read.
        @param filename The file from which the text originates.  This
          may be used for two purposes.  The first is error reporting,
          and the second is "load" statements, which load files
          relative to the path to the current file.
        @param first_line The line number for the first line of the file."""
        return TokenizeFile(self.tokenizer.copy(),fileobj,filename,first_line)
    def __iter__(self):
        """!Iterates over tokens in self.fileobj."""
        text=self.fileobj.read()
        for token in self.tokenizer.tokenize(
            text,self.filename,self.first_line):
            yield token



