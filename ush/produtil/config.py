"""!Parses UNIX conf files and makes the result readily available

The produtil.config module reads configuration information for a
production system from one or more *.conf files, via the Python
ConfigParser module.  This module also automatically fills in certain
information, such as fields calculated from the tcvitals or date.  The
result is accessible via the ProdConfig class, which provides many
ways of automatically accessing configuration options."""

##@var __all__
# decides what symbols are imported by "from produtil.config import *"
__all__=['from_file','from-string','confwalker','ProdConfig','fordriver','ENVIRONMENT','ProdTask']

import collections,re,string,os,logging,threading
import os.path,sys
import datetime
import produtil.fileop, produtil.datastore
import produtil.numerics, produtil.log

import configparser
from configparser import ConfigParser
from io import StringIO

from produtil.datastore import Datastore,Task
from produtil.fileop import *

from produtil.numerics import to_datetime
from string import Formatter
from configparser import NoOptionError,NoSectionError

UNSPECIFIED=object()

class DuplicateTaskName(Exception):
    """!Raised when more than one task is registered with the same
    name in an ProdConfig object."""

########################################################################

class Environment(object):
    """!returns environment variables, allowing substitutions

    This class is used to read (but not write) environment variables
    and provide default values if an environment variable is unset or
    blank.  It is only meant to be used in string formats, by passing
    ENV=ENVIRONMENT.  There is a global constant in this module,
    ENVIRONMENT, which is an instance of this class.  You should never
    need to instantiate another one."""
    def __contains__(self,s):
        """!Determines if __getitem__ will return something (True) or
        raise KeyError (False).  Same as "s in os.environ" unless s
        contains "|-", in which case, the result is True."""
        return s.find('|-')>=0 or s in os.environ
    def __getitem__(self,s):
        """!Same as os.environ[s] unless s contains "|-".  
           ENVIRONMENT["VARNAME|-substitute"]
        will return os.environ[VARNAME] if VARNAME is defined and
        non-empty in os.environ.  Otherwise, it will return
        "substitute"."""
        if not s: return ''
        i=s.find('|-')
        if i<0: return os.environ[s]
        var=s[0:i]
        sub=s[(i+2):]
        val=os.environ.get(var,'')
        if val!='': return val
        return sub
    
## @var ENVIRONMENT
#  an Environment object.  You should never need to instantiate another one.
ENVIRONMENT=Environment()

class ConfFormatter(Formatter):
    """!Internal class that implements ProdConfig.strinterp()

    This class is part of the implementation of ProdConfig: it is
    used to interpolate strings using a syntax similar to
    string.format(), but it allows recursion in the config sections,
    and it also is able to use the [config] and [dir] sections as
    defaults for variables not found in the current section."""
    def __init__(self,quoted_literals=False):
        """!Constructor for ConfFormatter"""
        super(ConfFormatter,self).__init__()
        if quoted_literals:
            self.format=self.slow_format
            self.vformat=self.slow_vformat
            self.parse=qparse

    @property
    def quoted_literals(self):
        return self.parse==qparse

    def slow_format(self,format_string,*args,**kwargs):
        return self.vformat(format_string,args,kwargs)
    def slow_vformat(self,format_string,args,kwargs):
        out=StringIO()
        for literal_text, field_name, format_spec, conversion in \
                self.parse(format_string):
            if literal_text:
                out.write(literal_text)
            if field_name:
                (obj, used_key) = self.get_field(field_name,args,kwargs)
                if obj is None and used_key:
                    obj=self.get_value(used_key,args,kwargs)
                value=obj
                if conversion=='s':
                    value=str(value)
                elif conversion=='r':
                    value=repr(value)
                elif conversion:
                    raise ValueError('Unknown conversion %s'%(repr(conversion),))
                if format_spec:
                    value=value.__format__(format_spec)
                out.write(value)
        ret=out.getvalue()
        out.close()
        assert(ret is not None)
        assert(isinstance(ret,str))
        return ret

    def get_value(self,key,args,kwargs):
        """!Return the value of variable, or a substitution.

        Never call this function.  It is called automatically by
        str.format.  It provides the value of an variable,
        or a string substitution.
        @param key the string key being analyzed by str.format()
        @param args the indexed arguments to str.format()
        @param kwargs the keyword arguments to str.format()"""
        kwargs['__depth']+=1
        if kwargs['__depth']>=configparser.MAX_INTERPOLATION_DEPTH:
            raise configparser.InterpolationDepthError(kwargs['__key'],
                kwargs['__section'],key)
        try:
            if isinstance(key,int):
                return args[key]
            conf=kwargs.get('__conf',None)
            if key in kwargs:
                v=kwargs[key]
            elif '__taskvars' in kwargs \
                    and kwargs['__taskvars'] \
                    and key in kwargs['__taskvars']:
                v=kwargs['__taskvars'][key]
            else:
                isec=key.find('/')
                if isec>=0:
                    section=key[0:isec]
                    nkey=key[(isec+1):]
                    if not section:
                        section=kwargs.get('__section',None)
                    if nkey:
                        key=nkey
                else:
                    section=kwargs.get('__section',None)
                conf=kwargs.get('__conf',None)
                v=NOTFOUND
                if section is not None and conf is not None:
                    if conf.has_option(section,key):
                        v=conf.get(section,key,raw=True)
                    elif conf.has_option(section,'@inc'):
                        for osec in conf.get(section,'@inc').split(','):
                            if conf.has_option(osec,key):
                                v=conf.get(osec,key,raw=True)
                    if v is NOTFOUND:
                        if conf.has_option('config',key):
                            v=conf.get('config',key,raw=True)
                        elif conf.has_option('dir',key):
                            v=conf.get('dir',key,raw=True)
                    if v is NOTFOUND:
                        raise KeyError(key)

            if isinstance(v,str):
                if v.find('{')>=0 or v.find('%')>=0:
                    vnew=self.vformat(v,args,kwargs)
                    assert(vnew is not None)
                    return vnew
            return v
        finally:
            kwargs['__depth']-=1

def qparse(format_string):
    """!Replacement for Formatter.parse which can be added to Formatter objects
    to turn {'...'} and {"..."} blocks into literal strings (the ... part).
    Apply this by doing f=Formatter() ; f.parse=qparse.  """
    if not format_string: return []
    if not isinstance(format_string, str):
        raise TypeError('iterparse expects a str, not a %s %s'%(
                type(format_string).__name__,repr(format_string)))
    result=list()
    literal_text=''
    field_name=None
    format_spec=None
    conversion=None
    for m in re.finditer(r'''(?xs) (
            \{ \' (?P<qescape>  (?: \' (?! \} ) | [^'] )* ) \' \}
          | \{ \" (?P<dqescape> (?: \" (?! \} ) | [^"] )* ) \" \}
          | (?P<replacement_field>
               \{
                  (?P<field_name>
                     [^\}:!\['"\{] [^\}:!\[]*
                     (?: \. [a-zA-Z_][a-zA-Z_0-9]+
                       | \[ [^\]]+ \] )*
                  )
                  (?: ! (?P<conversion>[rs]) )?
                  (?: :
                     (?P<format_spec>
                       (?: [^\{\}]+
                         | \{[^\}]*\} )*
                     )
                  )?
               \} )
          | (?P<left_set> \{\{ )
          | (?P<right_set> \}\} )
          | (?P<literal_text> [^\{\}]+ )
          | (?P<error> . ) ) ''',format_string):
        if m.group('qescape'):
            literal_text+=m.group('qescape')
        elif m.group('dqescape'):
            literal_text+=m.group('dqescape')
        elif m.group('left_set'):
            literal_text+='{'
        elif m.group('right_set'):
            literal_text+='}'
        elif m.group('literal_text'):
            literal_text+=m.group('literal_text')
        elif m.group('replacement_field'):
            result.append( ( literal_text, 
                    m.group('field_name'),
                    m.group('format_spec'),
                    m.group('conversion') ) )
            literal_text=''
        elif m.group('error'):
            if m.group('error')=='{':
                raise ValueError("Single '{' encountered in format string")
            elif m.group('error')=='}':
                raise ValueError("Single '}' encountered in format string")
            else:
                raise ValueError("Unexpected %s in format string"%(
                        repr(m.group('error')),))
    if literal_text: 
        result.append( ( literal_text, None, None, None ) )
    return result

########################################################################

##@var FCST_KEYS
#  the list of forecast time keys recognized by ConfTimeFormatter 
FCST_KEYS={ 'fYMDHM':'%Y%m%d%H%M', 'fYMDH':'%Y%m%d%H', 'fYMD':'%Y%m%d',
            'fyear':'%Y', 'fYYYY':'%Y', 'fYY':'%y', 'fCC':'%C', 'fcen':'%C',
            'fmonth':'%m', 'fMM':'%m', 'fday':'%d', 'fDD':'%d', 'fhour':'%H',
            'fcyc':'%H', 'fHH':'%H', 'fminute':'%M', 'fmin':'%M' }
"""A list of keys recognized by ConfTimeFormatter if the key is
requested during string interpolation, and the key is not in the
relevant section.  This list of keys represents the forecast time.  It
is a dict mapping from the key name to the format sent to
datetime.datetime.strftime to generate the string value."""

##@var ANL_KEYS
#  the list of analysis time keys recognized by ConfTimeFormatter 
ANL_KEYS={ 'aYMDHM':'%Y%m%d%H%M', 'aYMDH':'%Y%m%d%H', 'aYMD':'%Y%m%d',
           'ayear':'%Y', 'aYYYY':'%Y', 'aYY':'%y', 'aCC':'%C', 'acen':'%C',
           'amonth':'%m', 'aMM':'%m', 'aday':'%d', 'aDD':'%d', 'ahour':'%H',
           'acyc':'%H', 'aHH':'%H', 'aminute':'%M', 'amin':'%M' }
"""A list of keys recognized by ConfTimeFormatter if the key is
requested during string interpolation, and the key is not in the
relevant section.  This list of keys represents the analysis time.  It
is a dict mapping from the key name to the format sent to
datetime.datetime.strftime to generate the string value."""

##@var M6_KEYS
#  the list of analysis time ( -6h ) keys recognized by ConfTimeFormatter 
ANL_M6_KEYS={ 'am6YMDHM':'%Y%m%d%H%M', 'am6YMDH':'%Y%m%d%H', 'am6YMD':'%Y%m%d',
           'am6year':'%Y', 'am6YYYY':'%Y', 'am6YY':'%y', 'am6CC':'%C', 'am6cen':'%C',
           'am6month':'%m', 'am6MM':'%m', 'am6day':'%d', 'am6DD':'%d', 'am6hour':'%H',
           'am6cyc':'%H', 'am6HH':'%H', 'am6minute':'%M', 'am6min':'%M' }
"""A list of keys recognized by ConfTimeFormatter if the key is
requested during string interpolation, and the key is not in the
relevant section.  This list of keys represents the analysis time.  It
is a dict mapping from the key name to the format sent to
datetime.datetime.strftime to generate the string value."""

##@var P6_KEYS
#  the list of analysis time ( +6h ) keys recognized by ConfTimeFormatter 
ANL_P6_KEYS={ 'ap6YMDHM':'%Y%m%d%H%M', 'ap6YMDH':'%Y%m%d%H', 'ap6YMD':'%Y%m%d',
           'ap6year':'%Y', 'ap6YYYY':'%Y', 'ap6YY':'%y', 'ap6CC':'%C', 'ap6cen':'%C',
           'ap6month':'%m', 'ap6MM':'%m', 'ap6day':'%d', 'ap6DD':'%d', 'ap6hour':'%H',
           'ap6cyc':'%H', 'ap6HH':'%H', 'ap6minute':'%M', 'ap6min':'%M' }
"""A list of keys recognized by ConfTimeFormatter if the key is
requested during string interpolation, and the key is not in the
relevant section.  This list of keys represents the analysis time.  It
is a dict mapping from the key name to the format sent to
datetime.datetime.strftime to generate the string value."""

##@var TIME_DIFF_KEYS
# the list of "forecast time minus analysis time" keys recognized by
# ConfTimeFormatter
TIME_DIFF_KEYS=set(['fahr','famin','fahrmin'])
"""A list of keys recognized by ConfTimeFormatter if the key is
requested during string interpolation, and the key is not in the
relevant section.  This list of keys represents the time difference
between the forecast and analysis time.  Unlike FCST_KEYS and
ANL_KEYS, this is not a mapping: it is a set."""

##@var NOTFOUND
#  a special constant that represents a key not being found
NOTFOUND=object()

class ConfTimeFormatter(ConfFormatter):
    """!internal function that implements time formatting

    Like its superclass, ConfFormatter, this class is part of the
    implementation of ProdConfig, and is used to interpolate strings
    in a way similar to string.format().  It works the same way as
    ConfFormatter, but accepts additional keys generated based on the
    forecast and analysis times:
       
        fYMDHM - 201409171200 = forecast time September 17, 2014 at 12:00 UTC
        fYMDH  - 2014091712
        fYMD   - 20140917
        fyear  - 2014
        fYYYY  - 2014
        fYY    - 14   (year % 100)
        fCC    - 20   (century)
        fcen   - 20
        fmonth - 09
        fMM    - 09
        fday   - 17
        fDD    - 17
        fhour  - 12
        fcyc   - 12
        fHH    - 12
        fminute - 00
        fmin   - 00

    Replace the initial "f" with "a" for analysis times.  In addition,
    the following are available for the time difference between
    forecast and analysis time.  Suppose the forecast is twenty-three
    hours and nineteen minutes (23:19) after the analysis time:

        fahr - 23
        famin - 1399   ( = 23*60+19)
        fahrmin - 19  """
    def __init__(self,quoted_literals=False):
        """!constructor for ConfTimeFormatter"""
        super(ConfTimeFormatter,self).__init__(
            quoted_literals=bool(quoted_literals))
    def get_value(self,key,args,kwargs):
        """!return the value of a variable, or a substitution

        Never call this function.  It is called automatically by
        str.format.  It provides the value of an variable,
        or a string substitution.
        @param key the string key being analyzed by str.format()
        @param args the indexed arguments to str.format()
        @param kwargs the keyword arguments to str.format()"""
        v=NOTFOUND
        kwargs['__depth']+=1
        if kwargs['__depth']>=configparser.MAX_INTERPOLATION_DEPTH:
            raise configparser.InterpolationDepthError(
                kwargs['__key'],kwargs['__section'],v)
        try:
            if isinstance(key,int):
                return args[key]
            if key in kwargs:
                v=kwargs[key]
            elif '__taskvars' in kwargs \
                    and kwargs['__taskvars'] \
                    and key in kwargs['__taskvars']:
                v=kwargs['__taskvars'][key]
            elif '__ftime' in kwargs and key in FCST_KEYS:
                v=kwargs['__ftime'].strftime(FCST_KEYS[key])
            elif '__atime' in kwargs and key in ANL_KEYS:
                v=kwargs['__atime'].strftime(ANL_KEYS[key])
            elif '__atime' in kwargs and key in ANL_M6_KEYS:
                am6=kwargs['__atime']-datetime.timedelta(0,3600*6)
                v=am6.strftime(ANL_M6_KEYS[key])
            elif '__atime' in kwargs and key in ANL_P6_KEYS:
                ap6=kwargs['__atime']+datetime.timedelta(0,3600*6)
                v=ap6.strftime(ANL_P6_KEYS[key])
            elif '__ftime' in kwargs and '__atime' in kwargs and \
                    key in TIME_DIFF_KEYS:
                (ihours,iminutes)=produtil.numerics.fcst_hr_min(
                    kwargs['__ftime'],kwargs['__atime'])
                if key=='fahr':
                    v=int(ihours)
                elif key=='famin':
                    v=int(ihours*60+iminutes)
                elif key=='fahrmin':
                    v=int(iminutes)
                else:
                    v=int(ihours*60+iminutes)
            else:
                isec=key.find('/')
                if isec>=0:
                    section=key[0:isec]
                    nkey=key[(isec+1):]
                    if not section:
                        section=kwargs.get('__section',None)
                    if nkey:
                        key=nkey
                else:
                    section=kwargs.get('__section',None)
                conf=kwargs.get('__conf',None)
                if section and conf:
                    if conf.has_option(section,key):
                        v=conf.get(section,key)
                    elif conf.has_option(section,'@inc'):
                        for osec in conf.get(section,'@inc').split(','):
                            if conf.has_option(osec,key):
                                v=conf.get(osec,key)
                    if v is NOTFOUND:
                        if conf.has_option('config',key):
                            v=conf.get('config',key)
                        elif conf.has_option('dir',key):
                            v=conf.get('dir',key)
                    if v is NOTFOUND:                           
                        raise KeyError('Cannot find key %s in section %s'
                                       %(repr(key),repr(section)))
        
            if isinstance(v,str) and ( v.find('{')!=-1 or 
                                              v.find('%')!=-1 ):
                try:
                    vnew=self.vformat(v,args,kwargs)
                    assert(vnew is not None)
                    return vnew
                except KeyError as e:
                    # Seriously, does the exception's class name
                    # really need to be this long?
                    raise ConfigParser.InterpolationMissingOptionError(
                        kwargs['__key'],kwargs['__section'],v,str(e))
            return v
        finally:
            kwargs['__depth']-=1

########################################################################

def confwalker(conf,start,selector,acceptor,recursevar):
    """!walks through a ConfigParser-like object performing some action

    Recurses through a ConfigParser-like object "conf" starting at
    section "start", performing a specified action.  The special
    variable whose name is in recursevar specifies a list of
    additional sections to recurse into.  No section will be processed
    more than once, and sections are processed in breadth-first order.
    For each variable seen in each section (including recursevar),
    this will call selector(sectionname, varname) to see if the
    variable should be processed.  If selector returns True, then
    acceptor(section, varname, value) will be called.

    @param conf the ConfigParser-like object
    @param start the starting section
    @param selector a function selector(section,option) that decides
       if an option needs processing (True) or not (False)
    @param acceptor a function acceptor(section,option,value) 
       run on all options for which the selector returns True
    @param recursevar an option in each section that lists more
       sections the confwalker should touch.  If the selector returns
       True for the recursevar, then the recursevar will be sent to
       the acceptor.  However, it will be scanned for sections to
       recurse into even if the selector rejects it."""
    touched=set()
    requested=[str(start)]
    while len(requested)>0:
        sec=requested.pop(0)
        if sec in touched:
            continue
        touched.add(sec)
        for (key,val) in conf.items(sec):
            if selector(sec,key):
                acceptor(sec,key,val)
            if key==recursevar:
                for sec2 in reversed(val.split(',')):
                    trim=sec2.strip()
                    if len(trim)>0 and not trim in touched:
                        requested.append(trim)

########################################################################

def from_file(filename,quoted_literals=False):
    """!Reads the specified conf file into an ProdConfig object.

    Creates a new ProdConfig object and instructs it to read the specified file.
    @param filename the path to the file that is to be read
    @return  a new ProdConfig object"""
    if not isinstance(filename,str):
        raise TypeError('First input to produtil.config.from_file must be a string.')
    conf=ProdConfig(quoted_literals=bool(quoted_literals))
    conf.read(filename)
    return conf

def from_string(confstr,quoted_literals=False):
    """!Reads the given string as if it was a conf file into an ProdConfig object

    Creates a new ProdConfig object and reads the string data into it
    as if it was a config file
    @param confstr the config data
    @return a new ProdConfig object"""
    if not isinstance(confstr,str):
        raise TypeError('First input to produtil.config.from_string must be a string.')
    conf=ProdConfig(quoted_literals=bool(quoted_literals))
    conf.readstr(confstr)
    return conf

class ProdConfig(object):
    """!a class that contains configuration information

    This class keeps track of configuration information for all tasks
    in a running model.  It can be used in a read-only manner as
    if it was a ConfigParser object.  All ProdTask objects require an
    ProdConfig object to keep track of registered task names via the
    register_task_name method, the current forecast cycle (cycle
    property) and the Datastore object (datastore property).

    This class should never be instantiated directly.  Instead, you
    should use the produtil.config.from_string or produtil.config.from_file to
    read configuration information from an in-memory string or a file."""

    def __init__(self,conf=None,quoted_literals=False,strict=False, inline_comment_prefixes=(';',)):
        """!ProdConfig constructor

        Creates a new ProdConfig object.
        @param conf the underlying configparser.ConfigParser object
        that stores the actual config data. This was a SafeConfigParser
        in Python 2 but in Python 3 the SafeConfigParser is now ConfigParser.
        @param quoted_literals if True, then {'...'} and {"..."} will 
          be interpreted as quoting the contained ... text.  Otherwise,
          those blocks will be considered errors.
        @param strict set default to False so it will not raise 
          DuplicateOptionError or DuplicateSectionError, This param was
          added when ported to Python 3.6, to maintain the previous 
          python 2 behavior.
        @param inline_comment_prefixes, defaults set to ;. This param was
          added when ported to Python 3.6, to maintain the previous
          python 2 behavior.
           
        Note: In Python 2, conf was ConfigParser.SafeConfigParser. In 
        Python 3.2, the old ConfigParser class was removed in favor of 
        SafeConfigParser which has in turn been renamed to ConfigParser. 
        Support for inline comments is now turned off by default and 
        section or option duplicates are not allowed in a single 
        configuration source."""
        self._logger=logging.getLogger('prodconfig')
        logger=self._logger
        self._lock=threading.RLock()
        self._formatter=ConfFormatter(bool(quoted_literals))
        self._time_formatter=ConfTimeFormatter(bool(quoted_literals))
        self._datastore=None
        self._tasknames=set()
        # Added strict=False and inline_comment_prefixes for Python 3,
        # so everything works as it did before in Python 2.
        # self._conf=ConfigParser(strict=False, inline_comment_prefixes=(';',)) if (conf is None) else conf
        self._conf=ConfigParser(strict=strict, inline_comment_prefixes=inline_comment_prefixes) if (conf is None) else conf
        self._conf.optionxform=str

        self._conf.add_section('config')
        self._conf.add_section('dir')
        self._fallback_callbacks=list()

    @property
    def quoted_literals(self):
        return self._time_formatter.quoted_literals and \
               self._formatter.quoted_literals

    def fallback(self,name,details):
        """!Asks whether the specified fallback is allowed.  May perform
        other tasks, such as alerting the operator.

        Calls the list of functions sent to add_fallback_callback.
        Each one receives the result of the last, and the final result
        at the end is returned.  Note that ALL of the callbacks are
        called, even if one returns False; this is not a short-circuit
        operation.  This is done to allow all reporting methods report
        to their operator and decide whether the fallback is allowed.
        
        Each function called is f(allow,name,details) where:

        - allow = True or False, whether the callbacks called thus far
          have allowed the fallback.

        - name = The short name of the fallback.

        - details = A long, human-readable description.  May be
          several lines long.

        @param name the name of the emergency situation

        @warning This function may take seconds or minutes to return.
        It could perform cpu- or time-intensive operations such as
        emailing an operator.

        """
        allow=self.getbool('config','allow_fallbacks',False)
        for fc in self._fallback_callbacks:
            allow=bool(fc(allow,name,details))
        return allow

    def add_fallback_callback(self,function):
        """!Appends a function to the list of fallback callback functions
        called by fallback()
        
        Appends the given function to the list that fallback()
        searches while determining if a workflow emergency fallback
        option is allowed.  

        @param function a function f(allow,name,details)
        @see fallbacks()"""
        self._fallback_callbacks.append(function)

    def readstr(self,source):

        """!read config data and add it to this object

        Given a string with conf data in it, parses the data.
        @param source the data to parse
        @return self"""
        fp=StringIO(str(source))
        self._conf.readfp(fp)
        fp.close()
        return self

    def from_args(self,args=None,allow_files=True,allow_options=True,
                  rel_path=None,verbose=False):
        """!Given a list of arguments, usually from sys.argv[1:], reads
        configuration files or sets option values.

        Reads list of strings of these formats:

        - /path/to/file.conf --- A configuration file to read.

        - section.option=value --- A configuration option to set in a
          specified section.

        Will read files in the order listed, and then will override
        options in the order listed.  Note that specified options
        override those read from files.  Also, later files override
        earlier files.

        @param args Typically argv[1:] or some other list of
        arguments.
        
        @param allow_files If True, filenames are allowed in args.
        Otherwise, they are ignored.

        @param allow_options If True, specified options
        (section.name=value) are allowed.  Otherwise they are detected
        and ignored.

        @param rel_path Any filenames that are relative will be
        relative to this path.  If None or unspecified, the current
        working directory as of the entry to this function is used.

        @returns self
        """
        allow_files=bool(allow_files)
        allow_options=bool(allow_options)
        verbose=bool(verbose)
        logger=self.log()
        if allow_files:
            if rel_path is None:
                rel_path=os.getcwd()
            else:
                rel_path=str(rel_path)
        elif not allow_options:
            # Nothing to do!
            return self
        infiles=list()
        moreopt=collections.defaultdict(dict)
        for arg in args:
            if not isinstance(arg,str):
                raise TypeError(
                    'In produtil.ProdConfig.from_args(), the args argument must '
                    'be an iterable of strings.  It contained an invalid %s %s '
                    'instead.'%(type(arg).__name__,repr(arg)))
            if verbose: logger.info(arg)
            m=re.match(r'''(?x)
              (?P<section>[a-zA-Z][a-zA-Z0-9_]*)
               \.(?P<option>[^=]+)
               =(?P<value>.*)$''',arg)
            if m:
                if allow_options:
                    if verbose:
                        logger.info('Set [%s] %s = %s'%(
                                m.group('section'),m.group('option'),
                                repr(m.group('value'))))
                    moreopt[m.group('section')][m.group('option')]=m.group('value')
                continue
            if allow_files:
                path=os.path.join(rel_path,arg)
                if os.path.exists(path):
                    infiles.append(arg)
                    continue
            if allow_files:
                logger.error('%s: invalid argument.  Not an config option '
                             '(a.b=c) nor a conf file.'%(args[iarg],))
            else:
                logger.error('%s: invalid argument.  Not an config option '
                             '(a.b=c).'%(args[iarg],))

        for path in infiles:
            if not os.path.exists(path):
                logger.error(path+': conf file does not exist.')
                sys.exit(2)
            elif not os.path.isfile(path):
                logger.error(path+': conf file is not a regular file.')
                sys.exit(2)
            elif not produtil.fileop.isnonempty(path):
                if verbose:
                    logger.warning(
                        path+': conf file is empty.  Will continue anyway.')
            if verbose: logger.info('Conf input: '+repr(path))
            self.read(path)

        for (sec,optval) in moreopt:
            (opt,val)=optval
            self.set(sec,opt,val)

    def read(self,source):
        """!reads and parses a config file

        Opens the specified config file and reads it, adding its
        contents to the configuration.  This is used to implement the
        from_file module-scope function.  You can use it again on an
        ProdConfig object to read additional files.
        @param source the file to read
        @return self"""
        self._conf.read(source)
        return self

    def readfp(self,source):
        """!read config data from an open file

        Reads a config file from the specified file-like object.
        This is used to implement the readstr.
        @param source the opened file to read
        @return self"""
        self._conf.readfp(source)
        return self

    def readstr(self,string):
        """!reads config data from an in-memory string

        Reads the given string as a config file.  This is used to
        implement the from_string module-scope function.  You can use
        it again to read more config data into an existing ProdConfig.
        @param string the string to parse
        @return self"""
        sio=StringIO(string)
        self._conf.readfp(sio)
        return self

    def set_options(self,section,**kwargs):
        """!set values of several options in a section

        Sets the value of several options in one section.  The
        keywords arguments are the names of the options to set and the
        keyword values are the option values.
        @param section the section being modified
        @param kwargs additional keyword arguments are the option names
            and values"""
        for k,v in kwargs.items():
            value=str(v)
            self._conf.set(section,k,value)

    @property
    def realtime(self):
        """!is this a real-time simulation?

        Is this configuration for a real-time simulation?  Defaults to
        True if unknown.  This is the same as doing
        getbool('config','realtime',True)."""
        return self.getbool('config','realtime',True)
    def set(self,section,key,value):
        """!set a config option

        Sets the specified config option (key) in the specified
        section, to the specified value.  All three are converted to
        strings via str() before setting the value."""
        self._conf.set(str(section),str(key),str(value))
    def __enter__(self):
        """!grab the thread lock

        Grabs this ProdConfig's thread lock.  This is only for future
        compatibility and is never used."""
        self._lock.acquire()
    def __exit__(self,a,b,c):
        """!release the thread lock

        Releases this ProdConfig's thread lock.  This is only for
        future compatibility and is never used.
        @param a,b,c unused"""
        self._lock.release()
    def register_task(self,name):
        """!add a ConfigurableTask to the database

        Checks to ensure that there is no other task by this name, and
        records the fact that there is now a task.  This is used by
        the ConfigurableTask to ensure only one task is made by
        any name."""
        with self:
            if name in self._tasknames:
                raise DuplicateTaskName(
                    '%s: attempted to use this task name twice'%(name,))
            self._tasknames.add(name)
    def log(self,sublog=None):
        """!returns a logging.Logger object

        Returns a logging.Logger object.  If the sublog argument is
        provided, then the logger will be under that subdomain of the
        "produtil" logging domain.  Otherwise, this ProdConfig's logger
        is returned.
        @param sublog the logging subdomain, or None
        @return a logging.Logger object"""
        if sublog is not None:
            with self:
                return logging.getLogger('produtil.'+sublog)
        return self._logger
    def getdatastore(self):
        """!returns the Datastore

        Returns the produtil.datastore.Datastore object for this
        ProdConfig."""
        d=self._datastore
        if d is not None:
            return d
        with self:
            if self._datastore is None:
                dsfile=self.getstr('config','datastore')
                self._datastore=produtil.datastore.Datastore(dsfile,
                    logger=self.log('datastore'))
            return self._datastore

    ##@var datastore
    #  read-only property: the Datastore object for this simulation
    datastore=property(getdatastore,None,None, \
        """Returns the Datastore object for this simulation,
        creating it if necessary.  If the underlying datastore file
        did not already exist, it will be opened in create=True mode.""")

    def getcycle(self):
        """!get the analysis time

        Returns the analysis time of this workflow as a
        datetime.datetime."""
        if self._cycle is None:
            self._cycle=to_datetime(self._conf.get('config','cycle'))
        return self._cycle
    def setcycle(self,cycle):
        """!set the analysis time

        Sets the analysis time of this workflow.  Also sets the
        [config] section's "cycle" option.  Accepts anything that
        produtil.numerics.to_datetime recognizes."""
        cycle=to_datetime(cycle)
        strcycle=cycle.strftime('%Y%m%d%H')
        self._conf.set('config','cycle',strcycle)
        self._cycle=cycle
        self.set_time_vars()

    ##@var cycle
    # the analysis cycle, a datetime.datetime object
    cycle=property(getcycle,setcycle,None,
        """The cycle this simulation should run, as a datetime.datetime.""")

    def set_time_vars(self):
        """!internal function that sets time-related variables

        Sets many config options in the [config] section based on this
        workflow's analysis time.  This is called automatically
        when the cycle property is assigned.  You never need to call
        this function directly.

         YMDHM - 201409171200 = forecast time September 17, 2014 at 12:00 UTC
         YMDH  - 2014091712
         YMD   - 20140917
         year  - 2014
         YYYY  - 2014
         YY    - 14   (year % 100)
         CC    - 20   (century)
         cen   - 20
         month - 09
         MM    - 09
         day   - 17
         DD    - 17
         hour  - 12
         cyc   - 12
         HH    - 12
         minute - 00
         min   - 00"""
        with self:
            for var,fmt in [ ('YMDHM','%Y%m%d%H%M'), ('YMDH','%Y%m%d%H'), 
                             ('YMD','%Y%m%d'), ('year','%Y'), ('YYYY','%Y'),
                             ('YY','%y'), ('CC','%C'), ('cen','%C'),
                             ('month','%m'), ('MM','%m'), ('day','%d'),
                             ('DD','%d'), ('hour','%H'), ('cyc','%H'),
                             ('HH','%H'), ('minute','%M'), ('min','%M') ]:
                self._conf.set('config',var,self._cycle.strftime(fmt))
    def add_section(self,sec):
        """!add a new config section

        Adds a section to this ProdConfig.  If the section did not
        already exist, it will be initialized empty.  Otherwise, this
        function has no effect.
        @param sec the new section's name"""
        with self:
            self._conf.add_section(sec)
            return self
    def has_section(self,sec): 
        """!does this section exist?

        Determines if a config section exists (even if it is empty)
        @return  True if this ProdConfig has the given section and
        False otherwise.
        @param   sec the section to check for"""
        with self:
            return self._conf.has_section(sec)
    def has_option(self,sec,opt):
        """! is this option set?
        
        Determines if an option is set in the specified section
        @return True if this ProdConfig has the given option in the
        specified section, and False otherwise.
        @param sec the section
        @param opt the name of the option in that section"""
        with self:
            return self._conf.has_option(sec,opt)
    def getdir(self,name,default=None,morevars=None,taskvars=None):
        """! query the "dir" section

        Search the "dir" section.
        @return the specified key (name) from the "dir" section.
        Other options are passed to self.getstr.

        @param default the default value if the option is unset
        @param morevars more variables for string substitution
        @param taskvars even more variables for string substitution
        @param name the option name to search for"""
        with self:
            return self.getstr('dir',name,default=default,
                               morevars=morevars,taskvars=taskvars)
    def getloc(self,name,default=None,morevars=None,taskvars=None):
        """!search the config, exe and dir sections in that order

        Find the location of a file in the named option.  Searches
        the [config], [exe] and [dir] sections in order for an option
        by that name, returning the first one found.
        @param default the default value if the option is unset
        @param morevars more variables for string substitution
        @param taskvars even more variables for string substitution
        @param name the option name to search for
        @returns the resulting value"""
        with self:
            if self.has_option('config',name):
                return self.getstr('config',name,default=default,
                                   morevars=morevars,taskvars=taskvars)
            elif self.has_option('exe',name):
                return self.getstr('exe',name,default=default,
                                   morevars=morevars,taskvars=taskvars)
            else:
                return self.getstr('dir',name,default=default,
                                   morevars=morevars,taskvars=taskvars)
    def getexe(self,name,default=None,morevars=None,taskvars=None):
        """! query the "exe" section

        Search the "exe" section.
        @return the specified key (name) from the "exe" section.
        Other options are passed to self.getstr.

        @param default the default value if the option is unset
        @param morevars more variables for string substitution
        @param taskvars even more variables for string substitution
        @param name the option name to search for"""
        with self:
            return self.getstr('exe',name,default=default,morevars=morevars,
                               taskvars=taskvars)
    def __getitem__(self,arg):
        """!convenience function; replaces self.items and self.get

        This is a convenience function that provides access to the
        self.items or self.get functions.  
        
        * conf["section"] -- returns a dict containing the results of
                              self.items(arg)
        * conf[a,b,c] -- returns self.get(a,b,c)
                          (b and c are optional)
        @param arg the arguments: a list or string"""
        with self:
            if isinstance(arg,str):
                return dict(self.items(arg))
            elif ( isinstance(arg,list) or isinstance(arg,tuple) ):
                if len(arg)==1:   return dict(self.items(arg))
                if len(arg)==2:   return self.get(str(arg[0]),str(arg[1]))
                if len(arg)==3:   return self.get(str(arg[0]),str(arg[1]),
                                                  default=arg[2])
        return NotImplemented
    def makedirs(self,*args):
        """!calls produtil.fileop.makedirs() on directories in the [dir] section

        This is a simple utility function that calls
        produtil.fileop.makedirs() on some of the directories in the
        [dir] section.  
        @param args the keys in the [dir] section for the directories
        to make."""
        with self:
            dirs=[self.getstr('dir',arg) for arg in args]
        for makeme in dirs:
            produtil.fileop.makedirs(makeme)
    def keys(self,sec):
        """!get options in a section

        Returns a list containing the config options in the given
        section.
        @param sec the string name of the section"""
        with self:
            return [ opt for opt in self._conf.options(sec) ]
        
    def sections(self):
        """!gets the list of all sections from a configuration object"""
        return self._conf.sections()
    
    def items(self,sec,morevars=None,taskvars=None):
        """!get the list of (option,value) tuples for a section

        Returns a section's options as a list of two-element
        tuples.  Each tuple contains a config option, and the value of
        the config option after string interpolation.  Note that the
        special config section inclusion option "@inc" is also
        returned.
        @param sec the section
        @param morevars variables for string substitution
        @param taskvars yet more variables
        @return a list of (option,value) tuples, where the value is
          after string expansion"""
        out=[]
        with self:
            for opt in self._conf.options(sec):
                out.append((opt,self._interp(sec,opt,morevars,
                                             taskvars=taskvars)))
        return out
    def write(self,fileobject):
        """!write the contents of this ProdConfig to a file

        Writes the contents of an ProdConfig to the specified file,
        without interpolating (expanding) any strings.  The file will
        be suitable for reading in to a new ProdConfig object in a
        later job.  This is used to create the initial config file.

        @param fileobject an opened file to write to"""
        with self:
            self._conf.write(fileobject)
    def getraw(self,sec,opt,default=None):
        """!return the raw value of an option

        Returns the raw value for the specified section and option,
        without string interpolation.  That is, any {...} will be
        returned unmodified.  Raises an exception if no value is set.
        Will not search other sections, unlike other accessors.
        @param sec the section
        @param opt the option name
        @param default the value to return if the option is unset.
           If unspecified or None, NoOptionError is raised"""
        try:
            return self._conf.get(sec,opt,raw=True)
        except NoOptionError:
            if default is not None: return default
            raise

    def strinterp(self,sec,string,**kwargs):
        """!perform string expansion

        Performs this ProdConfig's string interpolation on the
        specified string, as if it was a value from the specified
        section.
        @param sec the section name
        @param string the string to expand
        @param kwargs more variables for string substitution"""
        assert(isinstance(sec,str))
        assert(isinstance(string,str))
        with self:
            return self._formatter.format(string,__section=sec,
                __key='__string__',__depth=0,__conf=self._conf,
                ENV=ENVIRONMENT,**kwargs)
    def timestrinterp(self,sec,string,ftime=None,atime=None,**kwargs):
        """!performs string expansion, including time variables

        Performs this ProdConfig's string interpolation on the
        specified string, as self.strinterp would, but adds in
        additional keys based on the given analysis and forecast
        times.  The keys are the same as the keys added to [config]
        for the cycle, except with "a" prepended for the analysis
        time, or "f" for the forecast time.  There are three more keys
        for the difference between the forecast an analysis time.  The
        famin is the forecast time in minutes, rounded down.  The fahr
        and fahrmin are the forecast hour, rounded down, and the
        remainder in minutes, rounded down to the next nearest minute.

        If the analysis time is None or unspecified, then self.cycle
        is used.  The atime can be anything understood by
        produtil.numerics.to_datetime and the ftime can be anything
        understood by produtil.numerics.to_datetime_rel, given the atime
        (or, absent atime, self.cycle) as the second argument.

        This is implemented as a wrapper around the
        self._time_formatter object, which knows how to expand the a*
        and f* variables without having to generate all of them.

        @param sec the section name
        @param string the string to expand
        @param ftime the forecast time or None
        @param atime the analysis time or None
        @param kwargs more variables for string expansion"""
        if atime is not None:
            atime=produtil.numerics.to_datetime(atime)
        else:
            atime=self.cycle
        if ftime is None:
            ftime=atime
        else:
            ftime=produtil.numerics.to_datetime_rel(ftime,atime)
        with self:
            return self._time_formatter.format(string,__section=sec,
                __key='__string__',__depth=0,__conf=self._conf,ENV=ENVIRONMENT,
                __atime=atime, __ftime=ftime,**kwargs)

    def _interp(self,sec,opt,morevars=None,taskvars=None):
        """!implementation of data-getting routines

        This is the underlying implementation of the various self.get*
        routines, and lies below the self._get.  It reads a config
        option opt from the config section sec.

        If the string contains a {...} expansion, the _interp will
        perform string interpolation, expanding {...} strings
        according to ConfigParser rules.  If the section contains an
        @inc, and any variables requested are not found, then the
        sections listed in @inc are searched.  Failing that, the
        config and dir sections are searched.

        @param sec the section name
        @param opt the option name
        @param morevars a dict containing variables whose values will
        override anything in this ProdConfig when performing string
        interpolation.  
        @param taskvars  serves the same purpose as morevars, but
        provides a second scope.
        @return the result of the string expansion"""
        sections=( sec, 'config','dir', '@inc' )
        gotted=False
        for section in sections:
            if section=='@inc':
                try:
                    inc=self._conf.get(sec,'@inc')
                except NoOptionError:
                    inc=''
                if inc:
                    touched=set(( sec,'config','dir' ))
                    for incsection in inc.split(","):
                        trim=incsection.strip()
                        if len(trim)>0 and trim not in touched:
                            touched.add(trim)
                            try:
                                got=self._conf.get(trim,opt,raw=True)
                                gotted=True
                                break
                            except (KeyError,NoSectionError,NoOptionError) as e:
                                pass # var not in section; search elsewhere
                if gotted: break
            else:
                try:
                    got=self._conf.get(section,opt,raw=True)
                    gotted=True
                    break
                except (KeyError,NoSectionError,NoOptionError) as e:
                    pass # var not in section; search elsewhere

        if not gotted:
            raise NoOptionError(opt,sec)

        if morevars is None:
            return self._formatter.format(got,
                __section=sec,__key=opt,__depth=0,__conf=self._conf,
                ENV=ENVIRONMENT, __taskvars=taskvars)
        else:
            return self._formatter.format(got,
                __section=sec,__key=opt,__depth=0,__conf=self._conf,
                ENV=ENVIRONMENT,__taskvars=taskvars,**morevars)

    def _get(self,sec,opt,typeobj,default,badtypeok,morevars=None,taskvars=None):
        """! high-level implemention of get routines

        This is the implementation of all of the self.get* routines.
        It obtains option opt from section sec via the self._interp,
        providing the optional list of additional variables for string
        interpolation in the morevars.  It then converts to the given
        type via typeobj (for example, typeobj=int for int
        conversion).  If default is not None, and the variable cannot
        be found, then the default is returned.

        @param sec the section name
        @param opt the option name in that section
        @param default the default value to return if the variable
          cannot be found, or None if no default is provided.
        @param badtypeok if True and default is not None, and the type
          conversion failed, then default is returned.  Otherwise, the
          TypeError resulting from the failed type conversion is passed
          to the caller.
        @param morevars a dict containing variables whose values will
          override anything in this ProdConfig when performing string
          interpolation.  
        @param taskvars  serves the same purpose as morevars, but
          provides a second scope.        """
        try:
            s=self._interp(sec,opt,morevars=morevars,taskvars=taskvars)
            assert(s is not None)
            return typeobj(s)
        except NoOptionError:
            if default is not None:
                return default
            raise
        except TypeError:
            if badtypeok:
                if default is not None: return default
                return None
            raise
    def getint(self,sec,opt,default=None,badtypeok=False,morevars=None,taskvars=None):
        """!get an integer value

        Gets option opt from section sec and expands it; see "get" for
        details.  Attempts to convert it to an int.  

        @param sec,opt the section and option
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars,taskvars dicts of more variables for string expansion"""
        with self:
            return self._get(sec,opt,int,default,badtypeok,morevars,taskvars=taskvars)

    def getfloat(self,sec,opt,default=None,badtypeok=False,morevars=None,taskvars=None):
        """!get a float value

        Gets option opt from section sec and expands it; see "get" for
        details.  Attempts to convert it to a float

        @param sec,opt the section and option
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars,taskvars dicts of more variables for string expansion"""
        with self:
            return self._get(sec,opt,float,default,badtypeok,morevars,taskvars=taskvars)

    def getstr(self,sec,opt,default=None,badtypeok=False,morevars=None,taskvars=None):
        """!get a string value

        Gets option opt from section sec and expands it; see "get" for
        details.  Attempts to convert it to a str

        @param sec,opt the section and option
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars,taskvars dicts of more variables for string expansion"""
        with self:
            return self._get(sec,opt,str,default,badtypeok,morevars,taskvars=taskvars)

    def get(self,sec,opt,default=None,badtypeok=False,morevars=None,taskvars=None):
        """!get the value of an option from a section

        Gets option opt from section sec, expands it and converts
        to a string.  If the option is not found and default is
        specified, returns default.  If badtypeok, returns default if
        the option is found, but cannot be converted.  The morevars is
        used during string expansion: if {abc} is in the value of the
        given option, and morevars contains a key abc, then {abc} will
        be expanded using that value.  The morevars is a dict that
        allows the caller to override the list of variables for string
        extrapolation.
        @param sec,opt the section and option
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars,taskvars dicts of more variables for string expansion"""
        with self:
            try:
                return self._interp(sec,opt,morevars,taskvars=taskvars)
            except NoOptionError:
                if default is not None:
                    return default
                raise

    def options(self,sec):
        """!what options are in this section?

        Returns a list of options in the given section
        @param sec the section"""
        with self:
            return self._conf.options(sec)
    
    def getboolean(self,sec,opt,default=None,badtypeok=False,morevars=None,taskvars=None):
        """!alias for getbool: get a bool value

        This is an alias for getbool for code expecting a
        ConfigParser.  Gets option opt from section sec and expands
        it; see "get" for details.  Attempts to convert it to a bool

        @param sec,opt the section and option
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars,taskvars dicts of more variables for string expansion"""
        return self.getbool(sec,opt,default=default,badtypeok=badtypeok,
                            morevars=morevars,taskvars=taskvars)

    def getbool(self,sec,opt,default=None,badtypeok=False,morevars=None,taskvars=None):
        """!get a bool value

        Gets option opt from section sec and expands it; see "get" for
        details.  Attempts to convert it to a bool

        @param sec,opt the section and option
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars,taskvars dicts of more variables for string expansion"""
        try:
            with self:
                s=self._interp(sec,opt,morevars=morevars,taskvars=taskvars)
        except NoOptionError:
            if default is not None:
                return bool(default)
            raise
        if re.match(r'(?i)\A(?:T|\.true\.|true|yes|on|1)\Z',s):   return True
        if re.match(r'(?i)\A(?:F|\.false\.|false|no|off|0)\Z',s): return False
        try:
            return int(s)==0
        except ValueError as e: pass
        if badtypeok and default is not None:
            return bool(default)
        raise ValueError('%s.%s: invalid value for conf file boolean: %s'
                         %(sec,opt,repr(s)))

########################################################################

class ProdTask(produtil.datastore.Task):
    """!A subclass of produtil.datastore.Task that provides a variety
    of convenience functions related to unix conf files and
    logging."""

    def __init__(self,dstore,conf,section,taskname=None,workdir=None,
                 outdir=None,taskvars=UNSPECIFIED,
                 **kwargs):
        """!Creates an ProdTask
        @param dstore passed to Datum: the Datastore object for this Task
        @param conf the conf object for this task
        @param section the conf section for this task
        @param taskname Optional: the taskname in the datastore.
               Default: the section name
        @param workdir directory in which this task should run.
               Any value set in the database will override this value.
        @param outdir  directory where output should be copied.  This
               argument must not be changed throughout the lifetime of
               the datstore database file.
        @param taskvars additonal variables for string expansion, sent to
               the taskvars arguments of produtil.config.ProdConfig member
               functions.
        @param kwargs passed to the parent class constructor."""
        if taskname is None:
            taskname=section
        conf.register_task(taskname)
        self.__taskvars=dict()
        if taskvars is not UNSPECIFIED:
            for k,v in taskvars.items():
                self.tvset(k,v)
        self._conf=conf
        self._section=str(section)
        if taskname is not None and not isinstance(taskname,str):
            raise TypeError('The taskname must be None or a str '
                            'subclass')
        if not isinstance(section,str):
            raise TypeError('The section be a str subclass')
        if workdir is None:
            workdir=self.confstr('workdir','')
            if workdir is None or workdir=='':
                workdir=os.path.join(self.getdir('WORK'),taskname)
        if outdir is None:
            outdir=self.confstr('workdir','')
            if outdir is None or outdir=='':
                outdir=os.path.join(self.getdir('intercom'),taskname)
        with dstore.transaction():
            super(ProdTask,self).__init__(dstore,taskname=taskname,
                                          logger=conf.log(taskname),**kwargs)
            mworkdir=self.meta('workdir','')
            moutdir=self.meta('outdir','')
            if mworkdir: 
                workdir=mworkdir
            else:
                self['workdir']=workdir
            if moutdir: 
                outdir=moutdir
            else:
                self['outdir']=outdir

    def get_workdir(self):
        """!Returns the directory the class should work in, as set by
        the "workdir" metadata value."""
        workdir=self.meta('workdir','')
        if not workdir:
            workdir=os.path.join(self.getdir('WORK'),self.taskname)
        assert(workdir!='/')
        return workdir
    def set_workdir(self,val):
        """!Sets the directory the class should work in.  This sets the
        "workdir" metadata value.
        @param val the new work directory"""
        self['workdir']=str(val)
    ##@var workdir
    # The directory in which this task should be run
    workdir=property(get_workdir,set_workdir,None,
        """!The directory in which this task should be run.""")

    def get_outdir(self):
        """!Gets the directory that should receive output data.  This
        is in the "outdir" metadata value."""
        outdir=self.meta('outdir','')
        if not outdir:
            outdir=os.path.join(self.getdir('intercom'),self.taskname)
        assert(outdir!='/')
        return outdir
    def set_outdir(self,val):
        """!Sets the directory that should receive output data.  Sets
        the "outdir" metadata value.
        @param val the new output directory"""
        self['outdir']=str(val)
    ##@var outdir
    # The directory in which this task should deliver its final output.
    # Note that changing this will NOT update products already in the
    # database.
    outdir=property(get_outdir,set_outdir,None,
        """!The directory to which this task should deliver its final output.""")

    def tvset(self,opt,val):
        """!Sets a taskvar option's value.

        Sets an object-local (taskvar) value for option "opt" to value "val".
        This will override config settings from the ProdConfig object.
        These are sent into the taskvars= parameter to the various
        ProdConfig member functions (hence the "tv" in "tvset").
        @param opt the name of the taskvar
        @param val the string value of the option"""
        sopt=str(opt)
        if sopt[0:2]=='__':
            raise ValueError(
                '%s: invalid option name.  Cannot begin with __'%(sopt,))
        self.__taskvars[sopt]=val

    def tvdel(self,opt):
        """!Deletes an object-local value set by tvset.
        @param opt the name of the taskvar to delete"""
        sopt=str(opt)
        del self.__taskvars[sopt]

    def tvget(self,opt):
        """!Gets a taskvar's value

        Returns the value of an object-local (taskvar) option set by tvset.
        @param opt the taskvar whose value should be returned"""
        sopt=str(opt)
        return self.__taskvars[sopt]

    def tvhave(self,opt=UNSPECIFIED):
        """!Is a taskvar set?

        If an option is specified, determines if the given option has
        an object-local (taskvar) value.  If no option is specified,
        returns True if ANY object-local values (taskvars) exist for
        any options.
        @param opt Optional: the name of the taskvar being checked."""
        if opt is UNSPECIFIED:
            return len(self.__taskvars)>0
        sopt=str(opt)
        return sopt in self.__taskvars

    @property
    def taskvars(self):
        """!The dict of object-local values used for string substitution."""
        return self.__taskvars


    def confint(self,opt,default=None,badtypeok=False,section=None,
                morevars=None):
        """!Alias for self.conf.getint for section self.section.
        @param opt the option name
        @param section Optional: the section.  Default: self.section.
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars dict of more variables for string expansion"""
        if(section is None): section=self._section
        return self._conf.getint(section,opt,default,badtypeok,
                                 morevars=morevars,taskvars=self.__taskvars)
    def confstr(self,opt,default=None,badtypeok=False,section=None,
                morevars=None):
        """!Alias for self.conf.getstr for section self.section.
        @param opt the option name
        @param section Optional: the section.  Default: self.section
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars dict of more variables for string expansion"""
        if(section is None): section=self._section
        return self._conf.getstr(section,opt,default,badtypeok,
                                 morevars=morevars,taskvars=self.__taskvars)
    def conffloat(self,opt,default=None,badtypeok=False,section=None,
                  morevars=None):
        """!Alias for self.conf.getfloat for section self.section.
        @param opt the option name
        @param section Optional: the section.  Default: self.section
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars dict of more variables for string expansion"""
        if(section is None): section=self._section
        return self._conf.getfloat(section,opt,default,badtypeok,
                                   morevars=morevars,taskvars=self.__taskvars)
    def confbool(self,opt,default=None,badtypeok=False,section=None,
                 morevars=None):
        """!Alias for self.conf.getbool for section self.section.
        @param opt the option name
        @param section Optional: the section.  Default: self.section
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars dict of more variables for string expansion"""
        if(section is None): section=self._section
        return self._conf.getbool(section,opt,default,badtypeok,
                                  morevars=morevars,taskvars=self.__taskvars)
    def confget(self,opt,default=None,badtypeok=False,section=None,
                morevars=None):
        """!Alias for self.conf.get for section self.section.
        @param opt the option name
        @param section Optional: the section.  Default: self.section
        @param default if specified and not None, then the default is
          returned if an option has no value or the section does not exist
        @param badtypeok is True, and the conversion fails, and a
          default is specified, the default will be returned.
        @param morevars dict of more variables for string expansion"""
        if(section is None): section=self._section
        return self._conf.get(section,opt,default,badtypeok,
                              morevars=morevars,taskvars=self.__taskvars)
    def confitems(self,section=None,morevars=None):
        """!Alias for self.conf.items for section self.section.
        @param section Optional: the section.  Default: self.section.
        @param morevars variables for string substitution"""
        if(section is None): section=self._section
        return self._conf.items(section,morevars=morevars,taskvars=self.__taskvars)

    def confstrinterp(self,string,section=None,**kwargs):
        """!Alias for self.icstr for backward compatibility
        @param string the string to expand
        @param section Optional: the section in which to expand it.
          Default: self.section.
        @param kwargs: more arguments for string substitution"""
        return self.icstr(string,section=section,**kwargs)

    def conftimestrinterp(self,string,ftime,atime=None,section=None,
                          **kwargs):
        """!Alias for self.timestr for backward comaptibility
        @param string the string to expand
        @param ftime: the forecast time
        @param atime: Optional: the analysis time.  Default: self.conf.cycle
        @param section Optional: the section in which to expand it.
          Default: self.section.
        @param kwargs: more arguments for string substitution"""
        return self.timestr(string,ftime,atime=atime,section=section,
                            taskvars=self.__taskvars,**kwargs)
    def confraw(self,opt,default=None,section=None):
        """!Get a raw configuration value before string expansion.

        Returns the raw, uninterpolated value for the specified
        option, raising an exception if that option is unset.  Will
        not search other sections, and will not search the taskvars,
        unlike other conf accessors.
        @param opt the option of interest
        @param section Optional: the section.  Default: self.section
        @param default Optional: value to return if nothing is found."""
        if section is None: section=self.section
        return self._conf.getraw(section,opt,default)

    def icstr(self,string,section=None,**kwargs):
        """!Expands a string in the given conf section. 

        Given a string, expand it as if it was a value in the
        specified conf section.  Makes this objects tcvitals, if any,
        available via the "vit" variable while interpolating strings.
        @param string the string to expand
        @param section Optional: the section in which to expand it.
          Default: self.section.
        @param kwargs: more arguments for string substitution"""
        if(section is None): section=self._section
        if self.storminfo and 'vit' not in kwargs: 
            kwargs['vit']=self.storminfo.__dict__
        return self._conf.strinterp(section,string,__taskvars=self.__taskvars,
                                    **kwargs)

    def timestr(self,string,ftime=None,atime=None,section=None,**kwargs):
        """!Expands a string in the given conf section, including time vars

        Expands a string in the given conf section (default:
        self.section), and includes forecast and analysis time
        (default: conf.cycle) information in the variables that can be
        expanded.  The mandatory ftime argument is the forecast time
        which will be used to expand values such as fHH, fYMDH, etc.
        The optional atime will be used to expand aHH, aYMDH, etc.,
        and the two will be used together for forecast minus analysis
        fields like fahr.  See produtil.config.timestrinterp for details

        As with self.icstr, this class's vitals are available via the
        "vit" variable while interpolating strings.
        @param string the string to expand
        @param ftime: the forecast time
        @param atime: Optional: the analysis time.  Default: self.conf.cycle
        @param section Optional: the section in which to expand it.
          Default: self.section.
        @param kwargs: more arguments for string substitution"""
        if(section is None): section=self._section
        if self.storminfo and 'vit' not in kwargs: 
            kwargs['vit']=self.storminfo.__dict__
        if 'taskvars' in kwargs:
            return self._conf.timestrinterp(section,string,ftime,atime,**kwargs)
        else:
            return self._conf.timestrinterp(section,string,ftime,atime,
                                            __taskvars=self.__taskvars,**kwargs)

    def getdir(self,opt,default=None,morevars=None):
        """!Alias for produtil.config.ProdConfig.get() for the "dir" section.
        @param opt the option name
        @param default Optional: default value if nothing is found.
        @param morevars Optional: more variables for string substitution"""
        return self._conf.get('dir',opt,default,morevars=morevars,
                              taskvars=self.__taskvars)
    def getexe(self,opt,default=None,morevars=None):
        """!Alias for produtil.config.ProdConfig.get() for the "exe" section.
        @param opt the option name
        @param default Optional: default value if nothing is found.
        @param morevars Optional: more variables for string substitution"""
        return self._conf.get('exe',opt,default,morevars=morevars,
                              taskvars=self.__taskvars)
    def getconf(self):
        """!Returns this ProdTask's produtil.config.ProdConfig object."""
        return self._conf

    ##@var conf
    # This ProdTask's produtil.config.ProdConfig object
    conf=property(getconf,None,None,
                  """!The ProdConfig for this ProdTask (read-only)""")
    def getsection(self):
        """!Returns this ProdTask's section name in the ProdConfig."""
        return self._section
    ##@var section
    # The confsection in self.section for this ProdTask (read-only)
    section=property(getsection,None,None,
        """!The confsection in self.section for this ProdTask (read-only)""")

    def log(self,subdom=None):
        """!Obtain a logging domain.

        Creates or returns a logging.Logger.  If subdom is None or
        unspecified, returns a cached logger for this task's logging
        domain.  Otherwise, returns a logger for the specified
        subdomain of this task's logging domain.
        @param subdom Optional: the desired logging domain"""
        if subdom is None:
            return self._logger
        return self._conf.log(self.taskname+'.'+str(subdom))
