#! /usr/bin/env python

import sys, re, StringIO, collections, os, datetime, logging
import produtil.run, produtil.log, produtil.setup

##@var BASELINE
# A constant that indicates the suite is being run to generate a new baseline.
BASELINE=object()

##@var EXECUTION
# A constant that indicates the suite is being run to verify against an existing baseline.
EXECUTION=object()

run_mode=EXECUTION

module_logger=logging.getLogger('produtil.testing')

##@var bash_functions
# Functions used by the bash language scripts this package generates.
bash_functions=r'''
function deliver_file() {
  local src tgt
  set -e
  src="$1"
  tgt="$2"
  if [[ -d "$tgt" ]] ; then
    tgt="$tgt"/$( basename "$src" )
  fi
  tmpfile="$tgt.$$.$RANDOM.$RANDOM"
  cp -fp "$src" "$tmpfile"
  mv -fT "$tmpfile" "$tgt"
}

function bitcmp() {
  local src tgt bn result
  set -e
  src="$1"
  tgt="$2"
  if [[ -d "$tgt" ]] ; then
    bn=$( basename "$src" )
    tgt="$tgt/$bn"
  elif [[ -d "$src" ]] ; then
    bn=$( basename "$tgt" )
    src="$src/$bn"
  fi
  set +e
  cmp "$src" "$tgt"
  result=$?
  set -e
  return $result
}

function atparse {
    set +x # There is too much output if "set -x" is on.
    set +u # We expect empty variables in this function.
    set +e # We expect some evals to fail too.
    # Use __ in names to avoid clashing with variables in {var} blocks.
    local __text __before __after __during
    for __text in "$@" ; do
        if [[ $__text =~ ^([a-zA-Z][a-zA-Z0-9_]*)=(.*)$ ]] ; then
            eval "local ${BASH_REMATCH[1]}"
            eval "${BASH_REMATCH[1]}="'"${BASH_REMATCH[2]}"'
        else
            echo "ERROR: Ignoring invalid argument $__text\n" 1>&2
        fi
    done
    while IFS= read -r __text ; do
        while [[ "$__text" =~ ^([^@]*)(@\[[a-zA-Z_][a-zA-Z_0-9]*\]|@\[\'[^\']*\'\]|@\[@\]|@)(.*) ]] ; do
            __before="${BASH_REMATCH[1]}"
            __during="${BASH_REMATCH[2]}"
            __after="${BASH_REMATCH[3]}"
#            printf 'PARSE[%s|%s|%s]\n' "$__before" "$__during" "$__after"
            printf %s "$__before"
            if [[ "$__during" =~ ^@\[\'(.*)\'\]$ ]] ; then
                printf %s "${BASH_REMATCH[1]}"
            elif [[ "$__during" == '@[@]' ]] ; then
                printf @
            elif [[ "$__during" =~ ^@\[([a-zA-Z_][a-zA-Z_0-9]*)\] ]] ; then
                set -u
                eval 'printf %s "$'"${BASH_REMATCH[1]}"'"'
                set +u
            else
                printf '%s' "$__during"
            fi
            if [[ "$__after" == "$__text" ]] ; then
                break
            fi
            __text="$__after"
        done
        printf '%s\n' "$__text"
    done
}
'''

########################################################################

def elipses(long_string,max_length=20,elipses='...'):
    strlen=len(long_string)
    if strlen<max_length:
        return long_string
    else:
        return long_string[0:max_length-len(elipses)]+elipses

def yell(s):
    pass#sys.stderr.write(s)

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
    output=StringIO.StringIO()
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
            raise ValueError('Cannot convert double-quote string \"%s\" to brace string: parser error around character \"%s\"."'%(dq,m.group()))
    value=output.getvalue()
    output.close()
    return value

########################################################################

class Context:
    def __init__(self,scopes,token,run_mode,logger):
        self.run_mode=run_mode
        self.token=token
        self.scopes=scopes
        if logger is None:
            logger=module_logger
        self.logger=logger
    @property
    def filename(self):
        return self.token.filename
    @property
    def lineno(self):
        return self.token.lineno
    def info(self,message):
        self.logger.info("%s: %s: %s"%(
                str(self.token.filename),
                repr(self.token.lineno),
                message))
    def warning(self,message):
        self.logger.warning("%s: %s: %s"%(
                str(self.token.filename),
                repr(self.token.lineno),
                message))
    def error(self,message):
        self.logger.error("%s: %s: %s"%(
                str(self.token.filename),
                repr(self.token.lineno),
                message))

########################################################################

def is_valid_workflow_name(name):
    return bool(re.match('(?s)^[a-zA-Z][a-zA-Z0-9_]*$',name))

def to_rocoto_walltime(seconds):
    return '%02d:%02d:%02d'%(
        seconds//3600, (seconds//60)%60, (seconds//1)%60)

def as_xml_attr(val):
    return val.replace('&','&amp;').replace('<','&lt;') \
              .replace('>','&gt;').replace('"','&quot;') \
              .replace("'",'&apos;').replace('\n',' ')

########################################################################

class RocotoTask(object):
    def __init__(self,name,obj):
        super(RocotoTask,self).__init__()
        self.__name=name
        self.__obj=obj
    def get_test_resources(self,con):
        # Get resource information for everything except cpus and time:
        try:
            test_size=self.__obj.resolve('test_size')
        except KeyError:
            test_size='short'
        if test_size not in [ 'short', 'long' ]:
            raise ValueError('Test %s: test size %s is not "small" or "long"'%(
                    obj.name,repr(test_size)))
        elif test_size=='long':
            return self.__obj.defscopes[-1].resolve(
                'plat%rocoto%long_test_resources').string_context(con)
        else:
            return self.__obj.defscopes[-1].resolve(
                'plat%rocoto%short_test_resources').string_context(con)
    def get_walltime(self,con):
        # Get walltime requirements:
        try:
            return '<walltime>%s</walltime>'%(
                to_rocoto_walltime(self.__obj.resolve('walltime')
                                   .numeric_context(con)),)
        except KeyError as ke:
            return '<walltime>%s</walltime>'%(
                to_rocoto_walltime(self.__obj.defscopes[-1]
                                   .resolve('plat%DEFAULT_TEST_WALLTIME')
                                   .numeric_context(con)),)
    def get_cpu_resources(self,con):
        execute=self.__obj.resolve('execute')
        if isinstance(execute,SpawnProcess):
            return execute.rocoto_resources(con)
        else:
            return '<cores>2</cores>'
    def j_job_name(self,workflow,con):
        return os.path.join(workflow.install_dir(con),'jobs',
                            'J%s_%s'%(workflow.NAME,self.__name.upper()))
    def ex_script_name(self,workflow,con):
        return os.path.join(workflow.install_dir(con),'scripts',
                            'ex%s_%s'%(workflow.name,self.__name.lower()))
    def j_job_contents(self,workflow,con):
        return r'''#! /usr/bin/env bash

# DO NOT EDIT THIS SCRIPT; IT IS AUTOMATICALLY GENERATED

{script}

export HOME{workflow}="${{HOME{workflow}:-$RT_INSTALL_DIR}}"
export USH{workflow}="${{USH{workflow}:-$HOME{workflow}/ush}}"
export EX{workflow}="${{USH{workflow}:-$HOME{workflow}/scripts}}"

{ex_script}
'''.format(script=self.__obj.resolve('prep').bash_context(con),
           workflow=workflow.name,WORKFLOW=workflow.NAME,
           ex_script=self.ex_script_name(workflow,con))
    def ex_script_contents(self,workflow,con):
        return r'''#! /usr/bin/env bash

# DO NOT EDIT THIS SCRIPT; IT IS AUTOMATICALLY GENERATED

source $HOME{workflow}/ush/functions.bash

set -xe

{SCRIPT}
'''.format(SCRIPT=self.__obj.bash_context(con),
           WORKFLOW=workflow.NAME,workflow=workflow.name)
    def generate_xml(self,out,workflow,con):
        out.write(r'''  <task name="{name}" maxtries="&TEST_MAXTRIES;">
    <command>set -xue ; cd "&INSTALL_DIR;/jobs" ; ./J{WORKFLOW}_{NAME}</command>
    <jobname>rt_{name}</jobname>
    <account>&ACCOUNT;</account>
    {test_resources}
    {cpu_resources}
    {walltime}
    <envar>
      <name>{WORKFLOW}_INSTALL_DIR</name>
      <value>&INSTALL_DIR;</value>
    </envar>
    <join>&LOG_DIR;/{name}.log</join>
'''.format(name=self.__name,NAME=self.__name.upper(),
           test_resources=self.get_test_resources(con),
           cpu_resources=self.get_cpu_resources(con),
           walltime=self.get_walltime(con),
           WORKFLOW=workflow.name.upper()))
        deps=[ dep for dep in self.__obj.iterdeps()]
        if len(deps)==1:
            out.write('    <dependency>\n')
        elif len(deps)>1:
            out.write('    <dependency> <and>\n')
        for dep in deps:
            if isinstance(dep,Build):
                out.write('      <taskdep task="build_%s"/>\n'%(dep.name,))
            elif isinstance(dep,Test):
                out.write('      <taskdep task="test_%s"/>\n'%(dep.name,))
        if len(deps)==1:
            out.write('    </dependency>\n')
        elif len(deps)>1:
            out.write('    </and> </dependency>\n')
        out.write(r'''
  </task>
''')

########################################################################

class RocotoWorkflow(object):
    def __init__(self,name,scope):
        super(RocotoWorkflow,self).__init__()
        if not is_valid_workflow_name(name):
            raise Exception(
                '%s: not a valid workflow name; must begin with a letter '
                'and only contain alphanumerics and underscore.  Fixme: '
                'need better exception here.'%(name,))
        self.name=name.lower()
        self.NAME=name.upper()
        self.cycle=datetime.datetime.now().strftime('%Y%m%d%H%M')
        self.__scope=scope
        self.__tasklist=list()
        self.__taskdict=dict()
        self.__buildlist=list()
        self.__namemap=dict()
        self.__files=dict()
        self.__install=None
        self.__uninstall=None
        self.__end_build=r'''else
  echo ERROR: Invalid build "$1" 1>&2
  exit 1
fi
'''
    def generate_install_script(self):
        assert(self.__install is not None)
        if self.__install is None:
            return ''
        else:
            return self.__install.getvalue()+self.__end_build
    def generate_uninstall_script(self):
        assert(self.__uninstall is not None)
        if self.__uninstall is None:
            return ''
        else:
            return self.__uninstall.getvalue()+self.__end_build
    def has_builds(self):
        return bool(self.__buildlist)
    def getvar(self,var):
        return self.__scope.resolve(var)
    def as_attr(self,var,con):
        val=self.getvar(var)
        if isinstance(val,BaseObject):
            val=val.string_context(con)
        return as_xml_attr(val)
    def run(self,obj,con):
        if isinstance(obj,Test):
            self.run_test(obj,con)
        elif isinstance(obj,Build):
            self.run_build(obj,con)
        else:
            raise Exception(
                'Rocoto can only run Test and Build objects, not a %s %s.'%(
                    type(obj).__name__,repr(obj)))
    def run_test(self,test,con):
        self.add_test(test.name,test)
        # FIXME: INSERT CODE HERE
    def run_build(self,build,con):
        self.add_build(build.name)

        kwargs={ 'install_if':'elif',
                 'uninstall_if':'elif',
                 'name':build.name,
                 'script':build.bash_context(con),
                 'target':build.resolve('target').bash_context(con)
                 }

        if not self.__install:
            self.__install=StringIO.StringIO()
            self.__install.write(r'''#! /usr/bin/env bash

# DO NOT EDIT THIS SCRIPT; IT IS AUTOMATICALLY GENERATED
# This script installs executables in the build_* jobs.

set -xue

''')
            kwargs['install_if']='if'

        if not self.__uninstall:
            self.__uninstall=StringIO.StringIO()
            self.__uninstall.write(r'''#! /usr/bin/env bash

# DO NOT EDIT THIS SCRIPT; IT IS AUTOMATICALLY GENERATED
# This script uninstalls executables installed by the "install.sh" script.

set -xue

''')
            kwargs['uninstall_if']='if'


        self.__install.write(r'''
{install_if} [[ "$1" == {name} ]] ; then
########################################################################
###### BUILD SCRIPT FOR TARGET {name}
########################################################################
rm -f {target}
{script}
set -xe
test -s {target}
test -x {target}
'''.format(**kwargs))
        self.__uninstall.write(r'''
{uninstall_if} [[ "$1" == {name} ]] ; then
rm -f {target}
'''.format(**kwargs))


    def add_file(self,path,contents):
        path=os.path.normpath(path)
        if path in self.__files:
            raise Exception('%s: tried to redefine contents for this file.  '
                            'Fixme: need better exception here.'%(path,))
        contents=str(contents)
        self.__files[path]=contents
    def add_build(self,buildname):
        if buildname in self.__buildlist:
            raise Exception('%s: duplicate build name.  Fixme: need better '
                            'exception here.'%(buildname,))
        self.__buildlist.append(buildname)
    def add_test(self,taskname,obj):
        assert(taskname[0:5]!='test_')
        taskname='test_'+str(taskname)
        if taskname in self.__taskdict:
            raise Exception('%s: tried to redefine task.  Fixme: need better '
                            'exception here.'%(taskname,))
        task=RocotoTask(taskname,obj)
        self.__tasklist.append(taskname)
        self.__taskdict[taskname]=task
        return task
    def iter_buildnames(self):
        for buildname in self.__buildlist:
            yield buildname
    def iter_paths(self):
        for path in self.__files.iterkeys():
            yield path
    def iter_testnames(self):
        for taskname in self.__tasklist:
            yield taskname
    def iter_files(self):
        for path,contents in self.__files.iteritems():
            yield path,contents
    def iter_tests(self):
        for taskname in self.__tasklist:
            yield taskname,self.__taskdict[taskname]
    def as_walltime(self,time,con):
        time=to_rocoto_walltime(self.getvar(time).numeric_context(con))
        assert(time is not None)
        return time
    def install_dir(self,con):
        idir=self.getvar('plat%rocoto%install_dir').string_context(con)
        assert(idir.find('@')<0)
        return idir
    def generate_xml(self,out,con):
        kwargs={
            'account':self.as_attr('plat%CPU_ACCOUNT',con),
            'log_dir':self.as_attr('plat%rocoto%log_dir',con),
            'install_dir':self.as_attr('plat%rocoto%install_dir',con),
            'UNIQUE_ID':self.as_attr('UNIQUE_ID',con),
            'scheduler':self.as_attr('plat%rocoto%scheduler',con),
            'taskthrottle':5,
            'name':self.name,
            'cycle':'202012311830',
            'build_resources':self.getvar('plat%rocoto%build_resources').string_context(con),
            'build_walltime':self.as_walltime('plat%BUILD_WALLTIME',con)
            }
        out.write(r'''<?xml version="1.0"?>
<!DOCTYPE workflow
[
  <!ENTITY WORKFLOW_NAME "{name:s}">
  <!ENTITY LOG_DIR "{log_dir:s}">
  <!ENTITY INSTALL_DIR "{install_dir:s}">
  <!ENTITY ACCOUNT "{account:s}">
  <!ENTITY UNIQUE_ID "{UNIQUE_ID:s}">
  <!ENTITY BUILD_MAXTRIES "1">
  <!ENTITY TEST_MAXTRIES "1">
]>

<!-- Workflow begins here -->

<workflow realtime="F" cyclethrottle="1"
          scheduler="{scheduler:s}"
          taskthrottle="{taskthrottle:d}">

  <!-- Rocoto is cycle-based, so we have to specify a cycle to run.
       This does NOT set the cycle to run in each regression test; it
       is only for Rocoto bookkeeping purposes. -->
  <cycledef>{cycle:s} {cycle:s} 01:00:00</cycledef>

  <!-- Tell Rocoto where to put Rocoto-specific log messages. -->
  <log><cyclestr>&LOG_DIR;/rocoto_@Y@m@d@H.log</cyclestr></log>

  <!-- Test definitions begin here. -->
'''.format(**kwargs))

        for testname,test in self.iter_tests():
            test.generate_xml(out,self,con)

        out.write(r'''
  <!-- End of test definitions. -->

''')

        if self.has_builds():
            out.write(r'''  <!-- Build system definitions begin here -->
  <metatask name="builds" mode="serial">
    <var name="BUILD">'''.format(**kwargs))
            out.write(' '.join([ b for b in self.iter_buildnames()]))
            out.write(r'''</var>
    <task name="build_#BUILD#" maxtries="&BUILD_MAXTRIES;">
      <command>set -xue ; cd "&INSTALL_DIR;/src" ; ./install.sh "#BUILD#"</command>
      <jobname>rt_build_#BUILD#</jobname>
      <account>&ACCOUNT;</account>
      <walltime>{build_walltime}</walltime>
      {build_resources:s}
      <envar>
        <name>RT_INSTALL_DIR</name>
        <value>&INSTALL_DIR;</value>
      </envar>
      <join>&LOG_DIR;/build_#BUILD#.log</join>
      <rewind>
        <sh>set -xue ; cd "&INSTALL_DIR;/src" ; ./uninstall.sh "#BUILD#"</sh>
      </rewind>
    </task>
  </metatask>

'''.format(**kwargs))

        out.write(r'''</workflow>

<!-- End of Rocoto workflow document -->
''')

########################################################################

class RocotoRunner(object):
    def __init__(self):
        super(RocotoRunner,self).__init__()
    def make_runner(self,parser):
        work=None
        con=None
        for runme,runme_context in parser.iterrun():
            if work is None:
                work=RocotoWorkflow('rt',runme.defscopes[-1])
            work.run(runme,runme_context)
            assert(runme_context is not None)
            if con is None:
                con=runme_context
            assert(con is not None)

        if work is None:
            raise ValueError('ERROR: No "run" statments seen; '
                             'nothing to do.\n');

        assert(con is not None)

        def here(path):
            here=os.path.normpath(os.path.join(work.install_dir(con),path))
            dir=os.path.normpath(os.path.dirname(here))
            if dir!=here:
                produtil.fileop.makedirs(dir)
            print here
            return here

        with open(here('rocoto/workflow.xml'),'wt') as f:
            work.generate_xml(f,con)
        with open(here('src/install.sh'),'wt') as f:
            f.write(work.generate_install_script())
            os.fchmod(f.fileno(),0755)
        with open(here('src/uninstall.sh'),'wt') as f:
            f.write(work.generate_uninstall_script())
            os.fchmod(f.fileno(),0755)

        for name,test in work.iter_tests():
            with open(here(test.j_job_name(work,con)),'wt') as f:
                f.write(test.j_job_contents(work,con))
                os.fchmod(f.fileno(),0755)
            with open(here(test.ex_script_name(work,con)),'wt') as f:
                f.write(test.ex_script_contents(work,con))
                os.fchmod(f.fileno(),0755)

        with open(here('ush/functions.bash'),'wt') as f:
            f.write('# DO NOT EDIT THIS SCRIPT; IT IS AUTOMATICALLY GENERATED\n')
            f.write('# These are bash functions used by the ex-scripts.\n\n')
            f.write(bash_functions)

########################################################################

##@var _HAVE_NOT_PEEKED
# Special constant used by peekable to indicate nothing has been peeked yet.
# @warning Terrible things will happen if you overwrite this.
# @private
_HAVE_NOT_PEEKED=object()

class peekable(object):
    def __init__(self,iterator):
        self.__child=iterator
        self.__iterator=iter(iterator)
        self.__peek=_HAVE_NOT_PEEKED
    @property
    def child(self):
        return self.__child
    def next(self):
        if self.__peek is not _HAVE_NOT_PEEKED:
            p,self.__peek = self.__peek,_HAVE_NOT_PEEKED
        else:
            p=self.__iterator.next()
        return p
    def peek(self):
        if self.__peek is _HAVE_NOT_PEEKED:
            self.__peek=self.__iterator.next()
        return self.__peek
    def at_end(self):
        if self.__peek is not _HAVE_NOT_PEEKED:
            return False
        try:
            self.__peek=self.__iterator.next()
        except StopIteration as se:
            return True
        return False
    def __iter__(self):
        p,self.__peek = self.__peek,_HAVE_NOT_PEEKED
        if p is not _HAVE_NOT_PEEKED:
            yield p
        for v in self.__iterator:
            yield v

########################################################################

class BaseObject(object):
    def __init__(self,defscopes):
        self.defscopes=defscopes
        self.is_scope=False
        self.is_filters=False
        self.is_criteria=False
        self.is_scalar=False
        self.can_be_used=False
    def bash_context(self,con):
        raise Exception("Cannot express null_value in a bash string.")
    def is_valid_rvalue(self,con): return True
    def string_context(self,con): return "null"
    def logical_context(self,con): return False
    def numeric_context(self,con): return 0.0
    def _apply_rescope(self,scopemap=None,prepend=None):
        if not prepend: prepend=[]
        if not scopemap: scopemap={}
        self.defscopes=prepend+[ scopemap[s] if s in scopemap else s
                                 for s in self.defscopes ]
    def rescope(self,scopemap=None,prepend=None):
        if not prepend: prepend=[]
        if not scopemap: scopemap={}
        return BaseObject(prepend+[ scopemap[s] if s in scopemap else s
                                    for s in self.defscopes ])
    def run(self,con): 
        print self.string_context(con)
    def iterdeps(self):
        return
        yield 'a' # Syntactic trick to ensure this is an iterator.

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
        raise TypeError('Cannot evaluate %s in a bash context.'%(
                type(self).__name__,))
    def string_context(self,con):
        raise TypeError('Cannot evaluate %s in a string context.'%(
                type(self).__name__,))
    def logical_context(self,con):
        raise TypeError('Cannot evaluate %s in a logical context.'%(
                type(self).__name__,))
    def numeric_context(self,con):
        raise TypeError('Cannot evaluate %s in a numeric context.'%(
                type(self).__name__,))
    def run(self,con):
        raise TypeError('Cannot run objects of type %s.'%(
                type(self).__name__,))

########################################################################

class Scope(BaseObject):
    def __init__(self,defscopes):
        super(Scope,self).__init__(defscopes)
        self.__vars=dict()
        self.__parameters=dict()
        self.is_scope=True
        self.can_be_used=True

    def validate_parameter(self,name): pass

    def new_empty(self): return Scope(self.defscopes)

    def bash_context(self,con):
        raise Exception("Cannot express a hash in a bash string.")

    def string_context(self,con): 
        if self.haslocal('_as_string'):
            value=self.getlocal('_as_string')
            return value.string_context(con)
        else:
            return str(id(self))

    def no_nulls(self):
        for k,v in self.iterlocal():
            if v is null_value:
                return False
        return True

    def _set_parameters(self,update):
        self.__parameters.update(update)
        for p in self.__parameters.iterkeys():
            self.validate_parameter(p)

    def numeric_context(self,con):
        return len(self.__vars) + len(self.__parameters)
    def logical_context(self,con): 
        return bool(self.__vars) or bool(self.__parameters)

    def as_parameters(self,con):
        """!Changes all variables to parameters."""
        self.__parameters.update(self.__vars)
        self.__vars=dict()
        for p in self.__parameters.iterkeys():
            self.validate_parameter(p)
        return self

    def rescope(self,scopemap=None,prepend=None):
        scope=self.new_empty()
        scope._apply_rescope(scopemap,prepend)
        for k,v in self.__parameters.iteritems():
            scope.__parameters[k]=v.rescope(scopemap,prepend)
        for k,v in self.__vars.iteritems():
            scope.__vars[k]=v.rescope(scopemap,prepend)
        return scope

    def has_parameters(self):
        return bool(self.__parameters)

    def use_from(self,used_scope,only_scalars=False):
        if used_scope.has_parameters():
            raise Exception('Cannot "use" a function.  Fixme: use better exception here.')
        if not used_scope.is_scope:
            raise Exception('Target of "use" statement is not a scope.')
        if not used_scope.can_be_used:
            raise Exception('Target of "use" statement cannot be used.')
        prepend_me=[ self ]
        found_non_scalars=False
        for k,v in used_scope.iterlocal():
            if only_scalars and v.is_scope:
                found_non_scalars=True
            self.force_define(k,v.rescope({used_scope:self}))
        return found_non_scalars
    def apply_parameters(self,scope,con):
        assert(not scope.__parameters)
        assert(self.__parameters)
        if not self.__parameters:
            return self
        s=self.new_empty()
        yell('APPLY PARAMETERS from %s to %s type %s\n'%(
                repr(scope),repr(self),type(s).__name__))
        for k,v in self.__parameters.iteritems():
            if scope.haslocal(k):
                s.__vars[k]=scope.getlocal(k).rescope({self:s, scope:s})
            elif v is not null_value:
                s.__vars[k]=v.rescope({self:s, scope:s})
            else:
                raise Exception('%s: no argument sent for this parameter'%(
                        k,))
        for k,v in self.__vars.iteritems():
            if k not in s.__vars:
                s.__vars[k]=v.rescope({self:s, scope:s})
        yell('RESULT IS %s %s\n'%(
                type(s).__name__,repr(s)))
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
        elif key in self.__vars:
            return self.__vars[key]
        raise KeyError(key)

    def setlocal(self,key,value):
        """!Sets the value of a key within this scope.

        @param key a valid identifier to set within this scope
        @param valuel the value of the identifier
        @raise ValueError if the key is not a valid identifier, such as
          one that contains a "%" """
        if '%' in key:
            raise ValueError("Key \"%s\" contains a \"%\""%(key,))
        if key in self.__parameters:
            raise Exception("Key \"%s\" is already a parameter.  FIXME: Need better exception class."%(key,))
        self.__vars[key]=value
        return value

    def haslocal(self,key):
        return key in self.__parameters or key in self.__vars

    def iterlocal(self):
        for k,v in self.__parameters.iteritems():
            yield k,v
        for k,v in self.__vars.iteritems():
            yield k,v

    def resolve(self,key,scopes=None):
        assert(isinstance(key,basestring))
        names=splitkey(key)
        if scopes is None:
            search=[self]+self.defscopes
        else:
            search=[self]+scopes
        #scopestack=list()
        yell('search for %s = %s in %s\n'%(repr(key),repr(names),repr(search)))
        for name in names:
            found=None
            for scope in search:
                try:
                    found=scope.getlocal(name)
                    #scopestack.insert(0,scope)
                    break # Done searching scopes.
                except KeyError as ke:
                    yell('Key %s not in scope %s from top %s\n'%(
                            repr(name),repr(scope),repr(self)))
                    continue # Check for name in next scope.
            if found is None:
                raise KeyError(key)
            search=[found]
        if found is None:
            raise KeyError(key)
        # if subscopes: 
        #     return ( found, scopestack )
        # else:
        return found

    def force_define(self,key,value):
        names=splitkey(key)
        lval=self
        for i in xrange(len(names)-1):
            lval=lval.getlocal(names[i])
        lval.setlocal(names[-1],value)
        return value

    def check_define(self,key,value):
        names=splitkey(key)
        lval=self
        for i in xrange(len(names)-1):
            lval=lval.subscope(names[i])
        if lval.haslocal(value):
            raise Exception('Key %s already exists. (FIXME: Put better '
                            'exception class here.)'%(key,))
        #yell('setlocal %s = %s\n'%(names[-1],value))
        lval.setlocal(names[-1],value)
        return value

    def expand_string(self,string,con,scopes=None):
        stream=StringIO.StringIO()
        yell('Expand %s in %s\n'%(repr(string),repr(self)))
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
        stream.close()
        return val
            #print "Arg \"%s\" expands to \"%s\""%(string,val)

def make_params(defscopes,**kwargs):
    s=Scope(defscopes)
    for k,v in kwargs.iteritems():
        s.setlocal(k,v)
    return s.as_parameters()

def make_scope(defscopes,**kwargs):
    s=Scope(defscopes)
    for k,v in kwargs.iteritems():
        s.setlocal(k,v)
    return s

def call_scope(scope,con,defscopes,**kwargs):
    parms=make_scope(defscopes,**kwargs)
    assert(parms.no_nulls())
    s=scope.apply_parameters(parms,con)
    assert(s.no_nulls())
    return s
    
########################################################################

class Builtin(Scope):
    def __init__(self,defscopes,opname):
        super(Builtin,self).__init__(defscopes)
        self.__opname=opname
    def bash_context(self,con):
        raise TypeError('Cannot evaluate built-in operator %s in a '
                        'bash context.'%(self.__opname,))
    def string_context(self,con):
        raise TypeError('Cannot evaluate built-in operator %s in a '
                        'string context.'%(self.__opname,))
    def logical_context(self,con):
        raise TypeError('Cannot evaluate built-in operator %s in a '
                        'logical context.'%(self.__opname,))
    def numeric_context(self,con):
        raise TypeError('Cannot evaluate built-in operator %s in a '
                        'numeric context.'%(self.__opname,))
    def run(self,con):
        raise TypeError('Cannot run built-in operator %s.'%(self.__opname,))

    def new_empty(self):
        return Builtin(self.defscopes,self.__opname)

########################################################################

class Copy(Builtin):
    def __init__(self,defscopes,empty=False):
        super(Copy,self).__init__(defscopes,'.copy.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        return Copy(self.defscopes,empty=True)
    def run(self,con):
        assert(self.no_nulls())
        src=self.resolve('src').string_context(con)
        tgt=self.resolve('tgt').string_context(con)
        produtil.fileop.deliver_file(src,tgt)
    def bash_context(self,con):
        assert(self.no_nulls())
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').bash_context(con)
        return 'deliver_file %s %s\n'%(src,tgt)

########################################################################

class CopyDir(Builtin):
    def __init__(self,defscopes,empty=False):
        super(CopyDir,self).__init__(defscopes,'.copydir.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        return CopyDir(self.defscopes,empty=True)
    def run(self,con):
        raise NotImplementedError('CopyDir.run is not implemented yet.')
    def bash_context(self,con):
        assert(self.no_nulls())
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').bash_context(con)
        return '''for srcfile in %s/* ; do
  deliver_file "$srcfile" %s/.
done
'''%(src,tgt)

########################################################################

class Link(Builtin):
    def __init__(self,defscopes,empty=False):
        super(Link,self).__init__(defscopes,'.link.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        return Link(self.defscopes,empty=True)
    def run(self,con):
        assert(self.no_nulls())
        src=self.resolve('src').string_context(con)
        tgt=self.resolve('tgt').string_context(con)
        produtil.fileop.make_symlink(src,tgt)
    def bash_context(self,con):
        assert(self.no_nulls())
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').bash_context(con)
        return 'ln -sf %s %s\n'%(src,tgt)

########################################################################

class AtParse(Builtin):
    def __init__(self,defscopes,empty=False):
        super(AtParse,self).__init__(defscopes,'.atparse.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        return AtParse(self.defscopes,empty=True)
    def run(self,con):
        raise NotImplementedError("FIXME: Sam has not implemented AtParse.run")
    def bash_context(self,con):
        out=StringIO.StringIO()
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
        out.write("set -xe\n")
        ret=out.getvalue()
        out.close()
        return ret

########################################################################

class BitCmp(Builtin):
    def __init__(self,defscopes,empty=False):
        super(BitCmp,self).__init__(defscopes,'.bitcmp.')
        if not empty:
            self._set_parameters({'src':null_value, 'tgt':null_value})
    def new_empty(self):
        return BitCmp(self.defscopes,empty=True)
    def run(self,con):
        src=self.resolve('src').string_context(con)
        tgt=self.resolve('tgt').string_context(con)
        if run_mode==BASELINE:
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
        src=self.resolve('src').bash_context(con)
        tgt=self.resolve('tgt').bash_context(con)
        if run_mode==BASELINE:
            return 'deliver_file %s %s\n'%(tgt,src)
        else:
            return 'bitcmp %s %s\n'%(src,tgt)

########################################################################

class Criteria(TypelessObject):
    def __init__(self,defscopes):
        super(Criteria,self).__init__(defscopes)
        self.__opmap=collections.defaultdict(list)
        self.__tgtlist=list()
        self.is_criteria=True
    def add_binary_operator(self,tgt,op,src,con):
        if tgt not in self.__opmap:
            self.__tgtlist.append(tgt)
        callme=call_scope(op,con,self.defscopes,tgt=tgt,src=src)
        for mycall in self.__opmap[tgt]:
            assert mycall is not null_value
            if mycall==callme:
                return
        callme=self.__opmap[tgt].append(callme)
        assert callme is not null_value
    def use_from(self,criteria,only_scalars=False):
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
    def itercriteria(self):
        for tgt in self.__tgtlist:
            for callme in self.__opmap[tgt]:
                yield tgt,callme
    def bash_context(self,con):
        out=StringIO.StringIO()
        for tgt in self.__tgtlist:
            out.write('echo criteria for target %s:\n'%(
                    tgt.bash_context(con),))
            for callme in self.__opmap[tgt]:
                out.write(callme.bash_context(con))
                if run_mode==BASELINE: break
        ret=out.getvalue()
        out.close()
        return ret

########################################################################

class Filters(TypelessObject):
    def __init__(self,defscopes):
        super(Filters,self).__init__(defscopes)
        self.__opmap=dict()
        self.__tgtlist=list()
        self.is_filters=True
    def add_binary_operator(self,tgt,op,src,con):
        if tgt not in self.__opmap:
            self.__tgtlist.append(tgt)
        self.__opmap[tgt]=call_scope(op,con,self.defscopes,
                                     tgt=tgt,src=src)
        assert self.__opmap[tgt] is not null_value
    def use_from(self,filters,only_scalars=False):
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
        out=StringIO.StringIO()
        for tgt in self.__tgtlist:
            out.write('echo Filter for target %s:\n'%(
                    tgt.bash_context(con),))
            out.write(self.__opmap[tgt].bash_context(con))
        ret=out.getvalue()
        out.close()
        return ret

########################################################################

class Rank(TypelessObject):
    def __init__(self,args,opts):
        self.__args=args
        self.__opts=opts
    @property
    def args(self):
        return self.__args
    def argiter(self):
        for arg in self.__args:
            yield arg
    def ranks(self,con):
        if self.__opts is None or not self.__opts.haslocal('ranks'):
            return 0
        return int(self.__opts.getlocal('ranks').numeric_context(con))
    def threads(self,con):
        if self.__opts is None or not self.__opts.haslocal('threads'):
            return 0
        return int(self.__opts.getlocal('threads').numeric_context(con))

########################################################################

class SpawnProcess(TypelessObject):
    def __init__(self,defscopes):
        super(SpawnProcess,self).__init__(defscopes)
        self.__ranks=list()
    def add_rank(self,args,opts):
        self.__ranks.append(Rank(args,opts))
    def mpi_comm_size(self,con):
        size=0
        for rank in self.__ranks:
            size+=rank.ranks(con)
        return size
    def rocoto_resources(self,con):
        size=max(int(self.mpi_comm_size(con)),2)
        return '<cores>%d</cores>\n'%size
    def bash_context(self,con):
        out=StringIO.StringIO()
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
        nthreads=max(0,threads[0])
        out.write('export OMP_NUM_THREADS=%d MKL_NUM_THREADS=0\n'%(
                nthreads,))
        if not have_ranks:
            # Serial or openmp program.
            out.write(' '.join([r.bash_context(con) 
                                for r in self.__ranks[0].args]))
            out.write('\n')
        elif len(self.__ranks)==1:
            out.write('mpirun -np %d '%(int(self.__ranks[0].ranks(con))))
            out.write(' '.join([r.bash_context(con)
                                for r in self.__ranks[0].args]))
            out.write('\n')
        else:
            raise Exception("FIXME: Sam has not implemented MPMD yet.")
        out.write('# End of embedded process execution.\n')
        ret=out.getvalue()
        out.close()
        return ret

########################################################################

class EmbedBash(Scope):
    def __init__(self,defscopes):
        super(EmbedBash,self).__init__(defscopes)
        self.__template=None

    def validate_parameter(self,name):
        pass
        #if not re.match('(?s)^[a-zA-Z][a-zA-Z0-9_]*$',name):
            #raise ValueError('Invalid bash variable name $%s FIXME: use better exception here'%(name,))

    def bash_context(self,con):
        raise Exception("Cannot express a bash script in a bash string.")

    def __str__(self):
        return "bash script \"%s\" %s"%(
            elipses(repr(self.gettemplate())),
            super(EmbedBash,self).__str__())

    def __repr__(self):
        return "bash script \"%s\" %s"%(
            elipses(repr(self.gettemplate())),
            super(EmbedBash,self).__str__())

    def apply_parameters(self,scope,con):
        s=super(EmbedBash,self).apply_parameters(scope,con)
        s.__template=self.__template.rescope({self:s, scope:s})
        return s

    def is_valid_rvalue(self,con):
        return self.__template is not None

    def string_context(self,con): 
        return '%d'%(self.numeric_context(con),)

    def settemplate(self,template):
        assert(isinstance(template,String))
        self.__template=template

    def gettemplate(self):
        return self.__template

    def numeric_context(self,con):
        return self.run(con)

    def bash_context(self,con):
        template=self.gettemplate()
        template=template.string_context(con)
        expanded=self.expand_string(template,con)

        stream=StringIO.StringIO()
        env=dict()
        unset_me=list()
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
                stream.write('%s=%s\n'%(k,v.bash_context(con)))
        stream.write("# Embedded bash script:\n")
        stream.write(expanded)
        stream.write('\n# End of embedded bash script.\n')
        for k in unset_me:
            stream.write('unset %s\n'%(k,))
        stream.write('set -xe\n\n')
        script=stream.getvalue()
        stream.close()
        return script

    def run(self,con):
        script=self.bash_context(con)
        yell('%-7s %-7s %s\n'%("RUN","BASH",script))
        cmd=produtil.run.exe("bash")<<'set -xue\n'+script
        env=dict(self.iterlocal())
        if env: cmd.env(**env)
        return produtil.run.run(cmd)
            
    def logical_context(self,con): 
        return bool(self.numeric_context(con)==0)

    def new_empty(self):
        s=EmbedBash(self.defscopes)
        s.__template=self.__template
        return s

########################################################################

class Task(Scope):
    def __init__(self,defscopes,name,runvar='run'):
        super(Task,self).__init__(defscopes)
        self.__deps=list()
        self.__name=str(name)
        self.runvar=runvar
    @property
    def name(self):
        return self.__name
    def bash_context(self,con):
        assert(self.haslocal(self.runvar))
        return self.getlocal(self.runvar).bash_context(con)

    def iterdeps(self):
        for dep in self.__deps:
            yield dep

    def add_dependency(self,dep):
        self.__deps.append(dep)

    def is_valid_rvalue(self,con):
        return self.haslocal(self.runvar) and \
            self.getlocal(self.runvar) is not null_value

    def string_context(self,con): 
        return self.getlocal(self.runvar).string_context(con)

    def numeric_context(self,scopes,con):
        return self.getlocal(self.runvar).numeric_context(con)

    def run(self,con):
        return self.getlocal(self.runvar).run(con)
            
    def logical_context(self,con): 
        return self.getlocal(self.runvar).numeric_context(con)

    def new_empty(self):
        return Task(self.defscopes,self.__name,self.runvar)

########################################################################

class Build(Task):
    def __init__(self,defscopes,name):
        super(Build,self).__init__(defscopes,name,'build')
    def new_empty(self):
        return Build(self.defscopes,self.name)

########################################################################

class Platform(Task):
    def __init__(self,defscopes,name):
        super(Platform,self).__init__(defscopes,name,'detect')
    def new_empty(self):
        return Platform(self.defscopes,self.name)

########################################################################

class Test(Scope):
    def __init__(self,defscopes,name,mode):
        super(Test,self).__init__(defscopes)
        assert(mode in [ BASELINE, EXECUTION ])
        self.mode=mode
        self.__name=str(name)
        self.__deps=list()

    @property
    def name(self):
        return self.__name

    def bash_context(self,con):
        if self.mode==BASELINE:
            steps=['prep','input','execute','make_baseline']
        else:
            steps=['prep','input','execute','verify']

        out=StringIO.StringIO()
        for step in steps:
            try:
                stepobj=self.getlocal(step)
            except KeyError as ke:
                if step in [ 'make_baseline', 'verify' ]:
                    stepobj=self.getlocal('output')
                else:
                    raise
            out.write(stepobj.bash_context(con))
            out.write('\n')
        ret=out.getvalue()
        out.close()
        return ret

    def iterdeps(self):
        for dep in self.__deps:
            yield dep

    def add_dependency(self,dep):
        self.__deps.append(dep)

    def is_valid_rvalue(self,con):
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
            raise KeyError(step)
        return True

    def string_context(self,con): 
        raise TypeError('A Test cannot be evaluated in a string context.')

    def numeric_context(self,con):
        raise TypeError('A Test cannot be evaluated in a numeric context.')

    def run(self,con):
        raise TypeError('A Test cannot be run directly.')
            
    def logical_context(self,con): 
        raise TypeError('A Test cannot be evaluated in a logical context.')

    def new_empty(self):
        return Test(self.defscopes,self.name,self.mode)

########################################################################

class AutoDetectPlatform(object):
    def __init__(self):
        super(AutoDetectPlatform,self).__init__()
        self.__platforms=list()
    def add(self,platform):
        self.__platforms.append(platform)
    def detect(self,con):
        matches=list()
        names=list()
        for platform in self.__platforms:
            detecter=platform.resolve('detect')
            name=platform.resolve('PLATFORM_NAME')
            name=name.string_context(con)
            sys.stderr.write('%s: detection...\n'%(name,))
            detection=detecter.logical_context(con)
            if detection:
                sys.stderr.write('%s: PLATFORM DETECTED\n'%(name,))
                matches.append(platform)
                names.append(name)
            else:
                sys.stderr.write('%s: not detected\n'%(name,))
        sys.stderr.write('List of platforms detected: '+
                         ' '.join([ repr(s) for s in names ])+'\n')
        return matches

########################################################################

class Numeric(BaseObject):
    def __init__(self,value):
        super(Numeric,self).__init__([])
        self.is_scalar=True
        self.__value=value
    def string_context(self,con):
        return '%g'%self.__value
    def bash_context(self,con):
        return '"%g"'%self.__value
    def numeric_context(self,con):
        return self.__value
    def logical_context(self,con):
        return self.numeric_context(con)!=0
    def __str__(self):
        return str(self.__value)
    def __repr__(self):
        return repr(self.__value)
    def rescope(self,scopemap=None,prepend=None): 
        return Numeric(self.__value)
    
########################################################################

class String(BaseObject):
    def __init__(self,defscopes,value,should_expand):
        super(String,self).__init__(defscopes)
        self.__value=str(value)
        self.is_scalar=True
        self.should_expand=bool(should_expand)
    def rescope(self,scopemap=None,prepend=None):
        if prepend is None: prepend=[]
        if scopemap is None: scopemap={}
        return String(prepend+[ scopemap[s] if s in scopemap else s
                        for s in self.defscopes ],
                      self.__value,self.should_expand)
    def string_context(self,con):
        if self.should_expand:
            return self.defscopes[0].expand_string(
                self.__value,con,self.defscopes[1:])
        else:
            return self.__value
    def bash_context(self,con):
        string=self.string_context(con)
        output=StringIO.StringIO()
        for m in re.finditer('''(?xs)
            (
                (?P<quotes>'+)
              | (?P<printable>[!-&(-\[\]-~ ]+)
              | (?P<control>.)
            )''',string):
            if m.group('quotes'):
                output.write('"' + m.group('quotes') + '"')
            elif m.group('printable'):
                output.write("'"+m.group('printable')+"'")
            elif m.group('control'):
                output.write("$'\%03o'"%ord(m.group('control')))
        ret=output.getvalue()
        output.close()
        return ret
    def logical_context(self,con):
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
        s=self.string_context(con)
        return float(s)
    def __str__(self): return self.__value
    def __repr__(self): return 'String(%s)'%(repr(self.__value),)

########################################################################

class Environ(Scope):
    def __init__(self):
        super(Environ,self).__init__([])
        self.can_be_used=False
    def new_empty(self): return Environ()
    def bash_context(self,con):
        raise Exception('Cannot express the environment in a bash context.')
    def string_context(self,con):
        raise Exception('Cannot evaluate the environment in a string context.')
    def no_nulls(self): return True
    def _set_parameters(self,update):
        raise Exception('Cannot set parameters in the environment.')
    def numeric_context(self,con):
        raise Exception('Cannot evaluate the environment in a numeric context.')
    def logical_context(self,con):
        raise Exception('Cannot evaluate the environment in a logical context.')
    def as_parameters(self,con):
        raise Exception('Cannot turn the environment into a parameter list.')
    def rescope(self,scopemap=None,prepend=None):
        return self
    def has_parameters(self):
        return False
    def use_from(self,used_scope,only_scalars=False):
        raise Exception('Cannot use other scopes within the environment.')
    def apply_parameters(self,scope,con):
        raise Exception('Cannot call the environment.')
    def __str__(self):
        return 'Environ()'
    def __repr__(self):
        return 'Environ()'
    def subscope(self,key):
        raise TypeError('The environment has no subscopes.')
    def getlocal(self,key):
        return String([self],os.environ[key],False)
    def setlocal(self,key,value):
        raise Exception('Refusing to modify the environment.')
    def haslocal(self,key):
        return key in os.environ
    def iterlocal(self):
        for k,v in os.environ.iteritems():
            yield k,String([self],v,False)
    def resolve(self,key,scopes=None):
        if '.' in key or '%' in key:
            raise ValueError('Invalid environment variable \"%s\".'%(key,))
        return os.environ[key]
    def force_define(self,key,value):
        raise Exception('Refusing to modify the environment.')
    def check_define(self,key,value):
        raise Exception('Refusing to modify the environment.')

########################################################################

unknown_file='(**unknown**)'

class Token(object):
    def __init__(self,token_type,token_value,filename,lineno):
        super(Token,self).__init__()
        self.token_type=token_type
        self.filename=filename
        self.lineno=lineno
        self.token_value=token_value
    def __repr__(self):
        return 'Token(%s,%s,%s,%s)'%(
            repr(self.token_type),repr(self.token_value),
            repr(self.filename),repr(self.lineno))
    def __str__(self):
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
    def copy(self):
        return Tokenizer()
    def __init__(self):
        super(Tokenizer,self).__init__()
        #yell('compile\n')
        self.re=re.compile(r'''(?xs)
                (
                    \# (?P<comment>[^\r\n]+) (?: \r | \n )+
                  | \# (?P<commentend>[^\r\n]+) $
                  | (?P<varname> [A-Za-z_] [A-Za-z_0-9.]*
                       (?: % [A-Za-z_][A-Za-z_0-9.]* )* )
                  | (?P<number>
                        [+-]? [0-9]+\.[0-9]+ (?: [eE] [+-]? [0-9]+ )?
                      | [+-]?       \.[0-9]+ (?: [eE] [+-]? [0-9]+ )?
                      | [+-]? [0-9]+\.       (?: [eE] [+-]? [0-9]+ )?
                      | [+-]? [0-9]+         (?: [eE] [+-]? [0-9]+ )?
                    )
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
                  |   (?P<oper>\.[a-zA-Z_][a-zA-Z0-9_.]*\.)
                  |   (?P<error> . )
                )''')
    def tokenize(self,text,filename=unknown_file,first_line=1):
        lineno=first_line
        for m in self.re.finditer(text):
            if m is None: 
                raise ValueError('SHOULD NOT GET HERE: no match on "%s"'%(line,))
            # else:
            #     for dkey,dval in m.groupdict().iteritems():
            #         if dval is not None:
            #             yell("%10s = %s\n"%(dkey,repr(dval)))
            if m.group('comment'):
                yield Token(end_of_line_type,m.group('comment'),
                            filename,lineno)
            elif m.group('commentend'):
                yield Token(end_of_line_type,m.group('commentend'),
                            filename,lineno)
            elif m.group('endline'):
                yield Token(end_of_line_type,m.group('endline'),
                            filename,lineno)
            elif m.group('oper'):
                yield Token('oper',m.group('oper'),filename,lineno)
            elif m.group('varname'):
                yield Token('varname',m.group('varname'),filename,lineno)
            elif m.group('number'):
                yield Token('number',m.group('number'),filename,lineno)
            elif m.group('qstring'):
                yield Token('qstring',m.group('qstring'),filename,lineno)
            elif m.group('dqstring'):
                yield Token('dqstring',m.group('dqstring'),filename,lineno)
            elif m.group('bracestring'):
                yield Token('bracestring',m.group('bracestring'),
                            filename,lineno)
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
                raise ValueError('%s:%d: invalid text \"%s\"'%(
                        filename,lineno,m.group(0)))
            lineno+=m.group(0).count('\n')
        yield Token(end_of_text_type,'',filename,lineno)

class TokenizeFile(object):
    def __init__(self,tokenizer,fileobj,filename=unknown_file,first_line=1):
        self.tokenizer=tokenizer
        self.fileobj=fileobj
        self.filename=filename
        self.first_line=first_line
    def for_file(self,fileobj,filename,first_line=1):
        return TokenizeFile(self.tokenizer.copy(),fileobj,filename,first_line)
    def __iter__(self):
        text=self.fileobj.read()
        for token in self.tokenizer.tokenize(
            text,self.filename,self.first_line):
            yield token

########################################################################

class Parser(object):
    def __init__(self,run_mode=None,logger=None):
        super(Parser,self).__init__()
        if logger is None: logger=module_logger
        if run_mode is None: run_mode=EXECUTION
        if run_mode is not EXECUTION and run_mode is not BASELINE:
            raise ValueError(
                'The Parser.__init__ run_mode argument must be the '
                'special module constants EXECUTION or BASELINE.')
        self.__runset=set()
        self.__runlist=list()
        self.__run_mode=run_mode
        self.__logger=logger
    def iterrun(self):
        for runme,con in self.__runlist:
            yield runme,con
    def con(self,token,scopes=None):
        if scopes is None: scopes=[]
        return Context(scopes,token,self.__run_mode,self.__logger)
    def add_run(self,runme,con):
        assert(isinstance(runme,BaseObject))
        if runme in self.__runset:
            return # runme is already in the runlist
        addlist=[ [runme,con] ]
        addset=set([runme])
        for prereq in runme.iterdeps():
            if prereq==runme:
                raise Exception('ERROR: %s is dependent on itself.'%(
                        repr(prereq),))
            if prereq in self.__runset or prereq in addlist: 
                continue # skip things we already ran.
            assert(isinstance(prereq,BaseObject))
            addset.add(prereq)
            addlist.append([prereq,con])
        for r in addlist:
            assert(isinstance(r,list))
            assert(len(r)==2)
            assert(isinstance(r[0],BaseObject))
            assert(isinstance(r[1],Context))
        self.__runset.update(addset)
        self.__runlist.extend([r for r in reversed(addlist)])
    def parse(self,tokenizer,scope):
        tokiter=peekable(tokenizer)
        scope.setlocal('ENV',Environ())
        scope.setlocal('UNIQUE_ID',Numeric(os.getpid()))
        try:
            return self.parse_subscope(
                tokiter,[scope],[end_of_text_type],
                self.parse_between_assignments,
                allow_overwrite=False,
                allow_resolve=True,
                allow_run=True,
                allow_null=False,
                allow_use=False,
                allow_load=True,
                scope_name='global scope')
        except Exception as e: # FIXME: change exception type
            # try:
            #     peek=tokiter.peek()
            #     filename=peek.filename
            #     lineno=peek.lineno
            #     sys.stderr.write('%s:%d: uncaught exception: %s\n'%(
            #             filename,lineno,str(e)))
            # except StopIteration as se:
            #     sys.stderr.write('StopIteration while peeking: %s\n'%(
            #             str(se),))
            #     pass
            raise
    def parse_between_arguments(self,tokiter,ends=None):
        if ends is None: ends=[')']
        peek=tokiter.peek()
        yell('%-7s peek type=%s value=%s\n'%(
                'BETWEEN',str(peek.token_type),elipses(str(
                        peek.token_value))))
        while True:
            if peek.token_type == ',':
                tokiter.next()
                yell('%-7s consume ,\n'%('BETWEEN',))
                return True
            elif peek.token_type in ends:
                yell('%-7s stop at %s\n'%('BETWEEN',peek.token_type))
                return False
            elif peek.token_type==end_of_line_type:
                yell('%-7s saw \n'%('BETWEEN',))
                tokiter.next()
                peek=tokiter.peek()
            else:
                return False
    def parse_between_assignments(self,tokiter):
        peek=tokiter.peek()
        seen=False
        yell('%-7s peek type=%s value=%s in parse_between_assignments\n'%(
                'BETWEEN',str(peek.token_type),
                elipses(str(peek.token_value))))
        while True:
            seen=True
            if peek.token_type in [ ',', ';' ]:
                tokiter.next()
                yell('%-7s consume %s\n'%('BETWEEN',peek.token_type))
                return True
            elif peek.token_type in [ '}', end_of_text_type ]:
                yell('%-7s stop at %s\n'%('BETWEEN',peek.token_type))
                return True
            elif peek.token_type==end_of_line_type:
                yell('%-7s saw %s\n'%('BETWEEN',repr(peek.token_type)))
                seen=True
                tokiter.next()
                peek=tokiter.peek()
            else:
                break
        return seen
        self.error('between_assignments',peek)

    def parse_embed_script(self,tokiter,scopes,ends,parse_between=None):
        token=tokiter.next()
        if token.token_type != 'varname':
            self.error('embed',token)
        if token.token_value != 'bash':
            self.error('embed',token,'unknown language "%s"'%(
                    token.token_value,))
        nametoken=tokiter.next()
        if token.token_type != 'varname':
            self.error('embed script name',token)
        scope=EmbedBash(scopes)
        token=tokiter.next()

        while token.token_type==end_of_line_type: token=tokiter.next()
        if token.token_type=='(':
            self.parse_subscope(tokiter,[scope]+scopes,[')'],
                                self.parse_between_arguments,
                                allow_overwrite=False,
                                allow_resolve=False,
                                allow_null=True,
                                only_scalars=True,
                                scope_name='embed script parameters')
            scope=scope.as_parameters(self.con(token,scopes))
            token=tokiter.next()
        while token.token_type==end_of_line_type: token=tokiter.next()

        if token.token_type=='{':
            self.parse_subscope(tokiter,[scope]+scopes,['}'],
                                self.parse_between_assignments,
                                allow_overwrite=True,
                                allow_resolve=True,
                                allow_null=False,
                                allow_use=True,
                                only_scalars=True,
                                scope_name='embed script variables')
            token=tokiter.next()
        while token.token_type==end_of_line_type: token=tokiter.next()

        if token.token_type in [ 'qstring', 'dqstring', 'bracestring' ]:
            scope.settemplate(self.action_string([scope]+scopes,token))
        else:
            self.error('embed script contents',token)
        if parse_between: 
            parse_between(tokiter)
        return (nametoken.token_value,scope)
        
    def parse_deplist(self,tokiter,scopes,task,ends):
        allscopes=[task]+scopes
        peek=tokiter.peek()
        while not peek.token_type in ends:
            if peek.token_type=='varname':
                varname=peek
                tokiter.next()
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
                    tokiter.next()
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
        token=tokiter.next()
        strings=[ 'qstring', 'dqstring', 'bracestring' ]
        if token.token_type != '{':
            self.error('operation list',token)
        while True:
            # Get target of operation:
            token=tokiter.next()
            while token.token_type==end_of_line_type:
                token=tokiter.next()
 
            if token.token_type=='varname' and token.token_value=='use':
                peek=tokiter.peek()
                if peek.token_type!='varname':
                    self.error('operation list use statement',peek)
                tokiter.next()
                subscope.use_from(self.action_resolve(peek,scopes))
                self.parse_between_assignments(tokiter)
                peek=tokiter.peek()
                if peek.token_type=='}':
                    tokiter.next()
                    return subscope
                continue
            elif token.token_type=='}':
                return subscope
            elif token.token_type not in strings:
                self.error('operator target',token)
            tgt=self.action_string(scopes,token)

            # Get operator:
            token=tokiter.next()
            while token.token_type==end_of_line_type:
                token=tokiter.next()
            if token.token_type!='oper':
                self.error('oper',token)
            op=self.action_operator(scopes,token)

            # Get source of operation (input or baseline file)
            token=tokiter.next()
            while token.token_type==end_of_line_type:
                token=tokiter.next()
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
                tokiter.next()
                return subscope


    def parse_hash_define(self,tokiter,scopes,subscope,parse_between=None,
                          allow_deps=False,hash_type='hash'):
        token=tokiter.next()
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
            token=tokiter.next()

        if token.token_type=='{':
            tokiter.next()
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

        yell('%-7s define Scope@%s with %sparameters\n'%(
                hash_type.upper(),str(id(subscope)),
                ' ' if parameters else 'no '))
        return subscope

    def parse_spawn_element(self,tokiter,scopes,spawn,ends):
        token=tokiter.next()
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
                token=tokiter.next()
                continue
            elif token.token_type==end_of_line_type:
                token=tokiter.next()
                continue
            elif token.token_type=='varname':
                name=token.token_value
                peek=tokiter.peek()
                if peek.token_type != '=':
                    self.error('spawn process',token)
                tokiter.next()
            else:
                self.error('spawn process',token)
            # we're at the value in varname=value
            rvalue=self.parse_rvalue(
                tokiter,scopes,['}',','],
                only_scalars=True)
            self.parse_between_arguments(tokiter,ends)
            opts.append([name,rvalue])
            token=tokiter.next()
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
        token=tokiter.next()
        while token.token_type==end_of_line_type: 
            token=tokiter.next()
        while token.token_type not in ends:
            if token.token_type!='{':
                self.error('spawned process',token)
            (args,opts)=self.parse_spawn_element(
                    tokiter,scopes,spawn,['}'])
            spawn.add_rank(args,opts)
            if parse_between: parse_between(tokiter)
            token=tokiter.next()

    def parse_spawn(self,tokiter,scopes,name,spawn):
        token=tokiter.next()
        if token.token_type!='{':
            self.error('spawn block',token)
        while self.parse_spawn_block(tokiter,scopes,name,spawn,['}'],
                                     self.parse_between_assignments):
            continue
        return spawn

    def parse_autodetect(self,tokiter,scopes,taskname,task):
        # Check for the (/ and skip it:
        token=tokiter.next()
        while token.token_type==end_of_line_type:
            token=tokiter.next()
        if token.token_type!='(/':
            self.error('autodetect platform list',token)

        while True:
            peek=tokiter.peek()
            while peek.token_type==end_of_line_type:
                tokiter.next()
                peek=tokiter.peek()
            if peek.token_type=='/)':
                tokiter.next()
                return
            rvalue=self.parse_rvalue(tokiter,scopes,['/)'],
                                     self.parse_between_arguments,False)
            task.add(rvalue)
            peek=tokiter.peek()
            self.parse_between_arguments(tokiter)
            if peek.token_type=='/)':
                tokiter.next()
                return

    def parse_load(self,tokiter,scope,seen_run):
        filetoken=tokiter.next()
        if filetoken.token_type!='qstring':
            self.error('load',token,"load statements can only include "
                       "'single-quote strings'")
        eoln=tokiter.peek()
        if eoln.token_type not in [ end_of_line_type, end_of_text_type ]:
            self.error('load',eoln,"a load statement must be followed "
                       "by an end of line or the end of the script.")
        newfile=filetoken.token_value
        if os.path.isabs(newfile):
            newfile=os.path.join(filetoken.filename,newfile)
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
        
    def parse_subscope(self,tokiter,scopes,ends,parse_between,
                       allow_overwrite=True,allow_resolve=True,
                       allow_run=False,allow_null=False,
                       allow_use=False,scope_name='subscope',
                       only_scalars=False,allow_load=False,
                       seen_run=False):
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
            yell('%s:%s: define %s=%s\n'%(
                    token.filename,str(token.lineno),
                    str(key),repr(val)))
            if allow_overwrite:
                scopes[0].force_define(key,val)
            else:
                scopes[0].check_define(key,val)
        if allow_resolve:
            search_scopes=scopes
        else:
            search_scopes=scopes[1:]
        while go:
            token=tokiter.next()
            if token.token_type=='varname':
                peek=tokiter.peek()
                if peek.token_type=='=':
                    tokiter.next()
                    define(self.con(token,scopes),token.token_value,
                           self.parse_rvalue(tokiter,search_scopes,ends,
                                             parse_between,
                                             only_scalars=only_scalars))
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
                    tokiter.next() # consume the peeked value
                    self.action_use(scopes,peek,
                                    only_scalars=only_scalars)
                    if parse_between:  parse_between(tokiter)
                    continue
                elif allow_run and token.token_value=='run' \
                        and peek.token_type=='varname':
                    seen_run=True
                    self.action_run_obj(
                        self.parse_rvalue(tokiter,search_scopes,
                                          ends,parse_between),
                        self.con(peek,scopes))
                    if parse_between:  parse_between(tokiter)
                    continue
                elif not only_scalars and token.token_value=='spawn' \
                        and peek.token_type=='varname':
                    taskname=peek.token_value
                    tokiter.next()
                    task=self.parse_spawn(tokiter,scopes,peek.token_value,
                                          SpawnProcess(scopes))
                    define(self.con(peek,scopes),taskname,task)
                    if parse_between:  parse_between(tokiter)
                    del taskname,task
                    continue
                elif not only_scalars and token.token_value in [
                    'filters', 'criteria' ] and peek.token_type=='varname':
                    taskname=peek.token_value
                    tokiter.next()
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
                    tokiter.next() # Skip name token
                    task=AutoDetectPlatform()
                    self.parse_autodetect(tokiter,scopes,taskname,task)
                    task=self.action_autodetect(self.con(peek,scopes),
                                                tokiter,scopes,taskname,task)
                    define(self.con(peek,scopes),taskname,task)
                    del taskname, task
                    continue
                elif not only_scalars and token.token_value in [
                        'build', 'task', 'test', 'platform' ] \
                        and peek.token_type=='varname':
                    taskname=peek.token_value
                    yell('%-7s %-7s %s\n'%(
                            'PARSE',token.token_value,taskname))
                    tokiter.next() # consume the task name
                    yell('%-7s %-7s %s\n'%(
                            'INIT',token.token_value,taskname))
                    if token.token_value=='task':
                        raise AssertionError('Should never make a Task')
                        task=Task(scopes,taskname)
                    elif token.token_value=='test':
                        task=Test(scopes,taskname,run_mode)
                        task.setlocal('TEST_NAME',
                                      String(scopes,taskname,False))
                    elif token.token_value=='build':
                        task=Build(scopes,taskname)
                        task.setlocal('BUILD_NAME',
                                      String(scopes,taskname,False))
                    elif token.token_value=='platform':
                        task=Platform(scopes,taskname)
                        task.setlocal('PLATFORM_NAME',
                                      String(scopes,taskname,False))
                    else:
                        raise AssertionError(
                            'Unrecognized subscope type "%s".'%(
                                token.token_value,))
                    task=self.parse_hash_define(
                            tokiter,scopes,task,parse_between,
                            allow_deps=token.token_value!='platform')
                    yell('%-7s %-7s %s\n'%('DEFINE',token.token_value,
                                           taskname))
                    define(self.con(peek,scopes),taskname,task)
                    del taskname, task
                    if parse_between:  parse_between(tokiter)
                    continue
                elif not only_scalars \
                        and token.token_value=='hash' \
                        and peek.token_type=='varname':
                    hashname=peek.token_value
                    tokiter.next() # consume the hash name
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
                     only_scalars=False):
        token=tokiter.next()
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
                tokiter.next() # consume (
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
                return self.action_resolve(token,scopes)
            elif parse_between and parse_between(tokiter):
                return self.action_resolve(token,scopes)
        self.error('rvalue',token)
    def action_autodetect(self,con,tokiter,scopes,taskname,task):
        matches=task.detect(con)
        if len(matches)==0:
            raise Exception(
                'You are using an unknown platform.  Fixme: need better '
                'exception here.')
        elif len(matches)>1:
            raise Exception(
                'This machine can submit to multiple platforms: '+(
                    ' '.join([
                            s.resolve('PLATFORM_NAME').string_context() 
                            for s in matches
                ])))
        return matches[0]
    def action_dependency(self,task,scopes,dep):
        task.add_dependency(dep)
    def action_call(self,varname,token,scopes,parameters):
        yell('%-7s %s in parameter scope %s\n'%(
                'CALL',repr(varname),repr(parameters)))
        callme=scopes[0].resolve(varname)
        yell('CALL APPLY PARAMETERS\n')
        return callme.apply_parameters(parameters,self.con(token,scopes))
    def action_use(self,scopes,key_token,only_scalars=False):
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
        assert(isinstance(token,Token))
        if token.token_value=='.copy.':
            return Copy(scopes)
        elif token.token_value=='.copydir.':
            return CopyDir(scopes)
        elif token.token_value=='.bitcmp.':
            return BitCmp(scopes)
        elif token.token_value=='.link.':
            return Link(scopes)
        elif token.token_value=='.atparse.':
            return AtParse(scopes)
        else:
            self.error('operator name',token,'unknown operator '+
                       token.token_value)
    def action_numeric(self,scopes,token):
        value=float(token.token_value)
        return Numeric(value)
    def action_string(self,scopes,token):
        assert(isinstance(token,Token))
        if token.token_type=='qstring':
            s=String(scopes,token.token_value,False)
        elif token.token_type=='dqstring':
            s=String(scopes,dqstring2bracestring(token.token_value),True)
        elif token.token_type=='bracestring':
            s=String(scopes,token.token_value,True)
        else:
            raise ValueError('Invalid token for a string: '+repr(token))
        yell('%-7s %s = %s\n'%('STRING',repr(token.token_value),repr(s)))
        return s
    def action_resolve(self,varname_token,scopes):
        varname=varname_token.token_value
        for scope in scopes:
            try:
                return scope.getlocal(varname)
            except KeyError as ke:
                pass
        raise KeyError(varname)
    def action_null_param(self,varname,scope):
        if '%' in varname:
            raise ValueError('%s: cannot have "%" in a parameter name.'%(
                    varname,))
        scope.check_define(varname,null_value)
    def action_assign_var(self,toscope,tovar,fromvar,fromscopes,
                          allow_overwrite):
        if fromscopes:
            value=fromscopes[0].resolve(fromvar)
        else: # Global scope assignment
            value=toscope.resolve(fromvar)
        self.action_assign(toscope,tovar,value,allow_overwrite)
    def action_assign(self,scope,varname,value,allow_overwrite):
        assert(isinstance(scope,Scope))
        assert(isinstance(varname,basestring))
        assert(isinstance(value,BaseObject))
        if '%' in varname:
            raise ValueError('Cannot assign to %s; subscope definitions must be of syntax "var1 = { var2= { ...."'%(
                    varname,))
        yell('%-7s %s = %s IN %s\n'%(
            'ASSIGN', varname, repr(value),repr(scope) ))
        if allow_overwrite:
            scope.force_define(varname,value)
        else:
            scope.check_define(varname,value)
    def action_run_obj(self,obj,con):
        yell('%-7s %s\n'%(
            'RUN', repr(obj)))
        self.add_run(obj,con)
    def error(self,mode,token,reason=None):
        if token is None:
            raise Exception('Unexpected end of file.')
        elif reason:
            raise Exception('%s:%s: %s (%s token with value %s)'%(
                    token.filename,token.lineno,str(reason),
                    repr(token.token_type),
                    repr(elipses(str(token.token_value)))))
        else:
            raise Exception(
                '%s:%s: unexpected %s in %s (token value %s)'%(
                    token.filename, token.lineno, repr(token.token_type),
                    str(mode), repr(elipses(str(token.token_value)))))

########################################################################

class BashRunner(object):
    def __init__(self):
        super(BashRunner,self).__init__()
    def make_runner(self,parser):
        out=StringIO.StringIO()
        out.write(r'''#! /usr/bin/env bash

%s

set -xe

'''%(bash_functions,))

        seen=False
        for runme,con in parser.iterrun():
            seen=True
            out.write(runme.bash_context(con))
            out.write("\n\n")
        if not seen:
            raise ValueError('ERROR: No "run" statments seen; nothing to do.\n');
        print out.getvalue()
        out.close()

########################################################################

tokenizer=Tokenizer()
parser=Parser()
global_scope=Scope([])

def process_file(fileobj,filename,first_line,scope):
    parser.parse(TokenizeFile(tokenizer,fileobj,filename,first_line),
                 scope)

modestr=sys.argv[1]
if modestr=='BASELINE':
    run_mode=BASELINE
elif modestr=='EXECUTION':
    run_mode=EXECUTION

double_dash_seen=False
for arg in sys.argv[2:]:
    if double_dash_seen:
        with open(arg,'rt') as infile:
            process_file(infile,arg,1,global_scope)
    elif arg == '--':
        double_dash_seen=True
    elif arg == '-':
        process_file(sys.stdin,'(**stdin**)',1,global_scope)
    else:
        with open(arg,'rt') as infile:
            process_file(infile,arg,1,global_scope)

yell('DONE DEFINING; RUN NOW\n')

#BashRunner().make_runner(parser)
RocotoRunner().make_runner(parser)
