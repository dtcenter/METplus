"""!Takes an object tree from produtil.parse.Parser and turns it into
a Rocoto workflow inside a valid Environmental Equivalence version 2
(EE2) compliant vertical structure."""

import sys, re, io, collections, os, datetime, logging
import produtil.run, produtil.log, produtil.setup

from produtil.testing.utilities import *
from produtil.testing.script import bash_functions
from produtil.testing.parsetree import Test, Build, BaseObject, SpawnProcess

def to_rocoto_walltime(seconds):
    return '%02d:%02d:%02d'%(
        seconds//3600, (seconds//60)%60, (seconds//1)%60)

def as_xml_attr(val):
    return val.replace('&','&amp;').replace('<','&lt;') \
              .replace('>','&gt;').replace('"','&quot;') \
              .replace("'",'&apos;').replace('\n',' ')

def as_xml_comment(val):
    return val.replace('--',' - ').replace('<','&lt;') \
        .replace('>','&gt;')

########################################################################

class RocotoTask(object):
    """!Represents one task in a Rocoto workflow document"""
    def __init__(self,name,obj,mode):
        """!Constructor for RocotoTask

        @param name the task name
        @param obj a produtil.testing.parsetree.Task containing 
          information about the task to run
        @param mode the run mode: produtil.testing.utilities.BASELINE
          or produtil.testing.utilities.EXECUTION"""
        super(RocotoTask,self).__init__()
        self.__name=name
        self.__obj=obj
        self.__mode=mode

    ##@property mode
    # The run mode: produtil.testing.utilities.BASELINE or
    # produtil.testing.utilities.EXECUTION

    @property
    def mode(self):
        """!The run mode: produtil.testing.utilities.BASELINE or
          produtil.testing.utilities.EXECUTION"""
        return self.__mode

    def get_test_resources(self,con):
        """!Get resource information for everything except cpus and
        time.

        Resolves the "test_size" variable to determine the test size.
        Then looks for "plat%rocoto%{test_size}_test_resources" for
        the resource information.  This is expected to contain
        everything except cpus and runtime.

        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @returns the resulting Rocoto XML code"""
        try:
            test_size=self.__obj.resolve('test_size')
        except KeyError:
            test_size='short'
        return self.__obj.defscopes[-1].resolve(
            'plat%rocoto%'+test_size+'_test_resources').string_context(con)
    def get_walltime(self,con):
        """!Gets walltime requirements from the "walltime" variable.

        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @returns the resulting Rocoto XML code"""
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
        """!Gets execution resources from the "execute" variable,
        resolving it in a rocoto_context.

        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @returns the resulting Rocoto XML code"""
        execute=self.__obj.resolve('execute')
        if isinstance(execute,SpawnProcess):
            s=execute.rocoto_resources(con)
        else:
            s='<cores>2</cores>'
        return s
    def j_job_name(self,workflow,con):
        """!Generates a path to the task's j-job

        Generates a path like "jobs/J{WORKFLOW}_{TASKNAME}" for the
        j-job portion of the task.

        @param workflow the RocotoWorkflow from which to obtain the
        workflow name
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @returns the resulting path."""
        return os.path.join(workflow.install_dir(con),'jobs',
                            'J%s_%s'%(workflow.NAME,self.__name.upper()))
    def ex_script_name(self,workflow,con):
        """!Generates a path to the task's ex-script

        Generates a path like "scripts/ex{workflow}_{taskname}" for the
        ex-script portion of the task.

        @param workflow the RocotoWorkflow from which to obtain the
        workflow name
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @returns the resulting path."""
        return os.path.join(workflow.install_dir(con),'scripts',
                            'ex%s_%s'%(workflow.name,self.__name.lower()))
    def j_job_contents(self,workflow,con):
        """!Generates the contents of the Task's j-job
        @param workflow the RocotoWorkflow from which to obtain the
        workflow name
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @returns the contents of the j-job as a string"""
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
        """!Generates the contents of the Task's ex-script
        @param workflow the RocotoWorkflow from which to obtain the
        workflow name
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @returns the contents of the ex-script as a string"""
        return r'''#! /usr/bin/env bash

# DO NOT EDIT THIS SCRIPT; IT IS AUTOMATICALLY GENERATED

source $HOME{workflow}/ush/functions.bash

set -xe

{SCRIPT}
'''.format(SCRIPT=self.__obj.bash_context(con),
           WORKFLOW=workflow.NAME,workflow=workflow.name)
    def generate_xml(self,out,workflow,con):
        """!Generates the Task's Rocoto XML element, writing it to
          a file-like stream.

        @param workflow the RocotoWorkflow from which to obtain the
        workflow name
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @param out a file-like stream in which to write
        @returns None"""
        obj=self.__obj
        if obj.haslocal('TEST_DESCR') and obj.haslocal('TEST_NAME'):
            descr=as_xml_comment(obj.resolve('TEST_DESCR').string_context(con))
            name=as_xml_comment(obj.resolve('TEST_NAME').string_context(con))
            out.write('  <!-- Test %s: %s -->\n'%(name,descr))
        out.write(r'''  <task name="{name}" maxtries="&TEST_MAXTRIES;">
    <command>"&INSTALL_DIR;/jobs/J{WORKFLOW}_{NAME}"</command>
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

        if len(deps)>1 or self.mode is BASELINE:
            out.write('    <dependency> <and>\n')
        else:
            out.write('    <dependency>\n')

        if self.mode is BASELINE:
            out.write('      <taskdep task="prep_baseline"/>\n')

        if len(deps)==0 and self.mode is not BASELINE:
            out.write('      <true/>\n')

        for dep in deps:
            if isinstance(dep,Build):
                out.write('      <taskdep task="build_%s"/>\n'%(dep.name,))
            elif isinstance(dep,Test):
                out.write('      <taskdep task="test_%s"/>\n'%(dep.name,))

        if len(deps)>1 or self.mode is BASELINE:
            out.write('    </and> </dependency>\n')
        else:
            out.write('    </dependency>\n')

        out.write(r'''  </task>

''')

########################################################################

NODEFAULT=object()

class RocotoWorkflow(object):
    """!Represents a Rocoto workflow, and creates the files needed to
    run one."""
    def __init__(self,name,scope,mode):
        """!Constructor for RocotoWorkflow

        @param name The name of the workflow.
        @param scope The global scope from produtil.testing.parser.Parse
        @param mode the run mode: produtil.testing.utilities.BASELINE
          or produtil.testing.utilities.EXECUTION
        """
        super(RocotoWorkflow,self).__init__()
        if not is_valid_workflow_name(name):
            raise PTParserError(
                '%s: not a valid workflow name; must begin with a letter '
                'and only contain alphanumerics and underscore.'%(name,))
        self.name=name.lower()
        self.mode=mode
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
        """!Generates the contents of the sorc/install.sh script.

        Constructs a script that knows how to build any of the
        possible build targets.  This is the contents of the
        sorc/install.sh script.

        @returns The resulting script, as a string."""
        assert(self.__install is not None)
        if self.__install is None:
            return ''
        else:
            return self.__install.getvalue()+self.__end_build
    def generate_uninstall_script(self):
        """!Generates the contents of the sorc/uninstall.sh script.

        Constructs a script that knows how to uninstall any of the
        possible build targets.  This is the contents of the
        sorc/uninstall.sh script.

        @returns The resulting script, as a string."""
        assert(self.__uninstall is not None)
        if self.__uninstall is None:
            return ''
        else:
            return self.__uninstall.getvalue()+self.__end_build
    def has_builds(self):
        """!Does this RocotoWorkflow contain any
        produtil.testing.parsetree.Build objects?"""
        return bool(self.__buildlist)
    def getvar(self,var,default=NODEFAULT):
        """!Resolves the specified variable reference within the
        global scope

        @param var A variable reference, such as "varname" or "scope1%scope2%varname" 
        @returns The value of the variable as a produtil.testing.parsetree.BaseObject
          or subclass thereof."""
        try:
            return self.__scope.resolve(var)
        except KeyError as ke:
            if default is not NODEFAULT:
                return default
            raise
    def as_attr(self,var,con):
        """!Resolves the specified variable reference in the given
        context and returns its value quoted for an XML attribute.

        Calls getvar() to resolve the variable, and expresses it
        within a string context.  Quotes the resulting string for an
        XML attribute.

        @see as_xml_attr()
        @see produtil.testing.parsetree.BaseObject.string_context()
        @see produtil.testing.parsetree.Context """
        val=self.getvar(var)
        if isinstance(val,BaseObject):
            val=val.string_context(con)
        return as_xml_attr(val)
    def run(self,obj,con):
        """!Adds a RocotoTask to the RocotoWorkflow

        @param obj a produtil.testing.parsetree.Test or
        produtil.testing.parsetree.Build for which the RocotoTask is
        to be constructed.
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables."""
        if isinstance(obj,Test):
            self.run_test(obj,con)
        elif isinstance(obj,Build):
            self.run_build(obj,con)
        else:
            raise PTParserError(
                'Rocoto can only run Test and Build objects, not a %s %s.'%(
                    type(obj).__name__,repr(obj)))
    def run_test(self,test,con):
        """!Adds the given produtil.testing.parsetree.Test to this
        RocotoWorkflow as a test to execute.

        @param test A produtil.testing.parsetree.Test representing the
        test to run.
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables."""
        self.add_test(test.name,test)
        # FIXME: INSERT CODE HERE
    def run_build(self,build,con):
        """!Adds a build from the given
        produtil.testing.parsetree.Build to this RocotoWorkflow as an
        executable to build.

        @param test The produtil.testing.parsetree.Build representing the
          executable to build
        @param con a produtil.testing.parsetree.Context to use when
          resolving variables."""
        self.add_build(build.name)

        kwargs={ 'install_if':'elif',
                 'uninstall_if':'elif',
                 'name':build.name,
                 'script':build.bash_context(con),
                 'target':build.resolve('target').bash_context(con)
                 }

        if not self.__install:
            self.__install=io.StringIO()
            self.__install.write(r'''#! /usr/bin/env bash

# DO NOT EDIT THIS SCRIPT; IT IS AUTOMATICALLY GENERATED
# This script installs executables in the build_* jobs.

set -xue

''')
            kwargs['install_if']='if'

        if not self.__uninstall:
            self.__uninstall=io.StringIO()
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
        """!Adds a file to the list of files that will be generated

        @param path the path to the file
        @param contents the text to write to the file"""
        path=os.path.normpath(path)
        if path in self.__files:
            raise PTParserError('%s: tried to redefine contents for this file.'%(path,))
        contents=str(contents)
        self.__files[path]=contents
    def add_build(self,buildname):
        """!Adds the given build name to the list of known build names.

        @param buildname the name of the build; this is used in the
          executable names, module name, and arguments to install.sh
          and uninstall.sh"""
        if buildname in self.__buildlist:
            raise PTParserError('%s: this build name is declared more than once.'%(buildname,))
        self.__buildlist.append(buildname)
    def add_test(self,taskname,obj):
        """!Adds the given produtil.testing.parsetree.Test to this
        RocotoWorkflow as a RocotoTask.

        @param testname The string name of the test.
        @param test A produtil.testing.parsetree.Test representing the
        test to run.
        @returns the resulting RocotoTask"""
        assert(taskname[0:5]!='test_')
        taskname='test_'+str(taskname)
        if taskname in self.__taskdict:
            raise PTParserError('%s: this task name is used more than once '%(taskname,))
        task=RocotoTask(taskname,obj,self.mode)
        self.__tasklist.append(taskname)
        self.__taskdict[taskname]=task
        return task
    def iter_buildnames(self):
        """!Iterates over build names."""
        for buildname in self.__buildlist:
            yield buildname
    def iter_paths(self):
        """!Iterates over paths to files that must be generated."""
        for path in self.__files.keys():
            yield path
    def iter_testnames(self):
        """!Iterates over names of tests."""
        for taskname in self.__tasklist:
            yield taskname
    def iter_files(self):
        """!Iterates over files to be generated, yielding tuples
        containing the path and contents."""
        for path,contents in self.__files.items():
            yield path,contents
    def iter_tests(self):
        """!Iterates over all RocotoTasks for tests to run, yielding a
        tuple containing the test name and RocotoTask."""
        for taskname in self.__tasklist:
            yield taskname,self.__taskdict[taskname]
    def as_walltime(self,time,con):
        """!Resolves the given numeric variable and turns it into a
        Rocoto-style wallclock time.

        @param time the variable reference
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables."""
        time=to_rocoto_walltime(self.getvar(time).numeric_context(con))
        assert(time is not None)
        return time
    def install_dir(self,con):
        """!Returns the directory in which to install the generated workflow.

        Gets the installation area for the created workflow from
        "plat%rocoto%install_dir", expressed in a string context.
        This is the top-level installation directory; the parent of
        ush/, jobs/, etc.

        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @return the directory in which to install the workflow"""
        idir=self.getvar('plat%rocoto%install_dir').string_context(con)
        assert(idir.find('@')<0)
        return idir
    def make_prep_baseline_sh(self,con):
        """!Creates a script that prepares the baseline when run in
        baseline generation mode.
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @returns the resulting script as a string"""
        baseline=self.getvar('plat%BASELINE').bash_context(con)
        template=self.getvar('plat%BASELINE_TEMPLATE').bash_context(con)
        return r'''#! /bin/sh

set -xue

baseline=%s
template=%s
mkdir -p "$baseline"
cd "$baseline"
rsync -arv "$template"/. .
'''%(baseline,template)

    def generate_xml(self,out,con):
        """!Generates the Rocoto workflow document.

        Writes the contents of the Rocoto XML document to the given
        file-like stream.

        @param out a file-like stream to which the document will be written.
        @param con a produtil.testing.parsetree.Context to use when
        resolving variables.
        @returns None"""
        default_task_throttle=produtil.testing.parsetree.String([],'55',False)
        one_max_try=produtil.testing.parsetree.String([],'1',False)
        try:
            walltime=self.as_walltime('walltime',con)
        except KeyError as ke:
            walltime=self.as_walltime('plat%BUILD_WALLTIME',con)
        kwargs={
            'account':self.as_attr('plat%CPU_ACCOUNT',con),
            'log_dir':self.as_attr('plat%rocoto%log_dir',con),
            'install_dir':self.as_attr('plat%rocoto%install_dir',con),
            'UNIQUE_ID':self.as_attr('UNIQUE_ID',con),
            'scheduler':self.as_attr('plat%rocoto%scheduler',con),
            'name':self.name,
            'cycle':'202012311830',
            'build_resources':self.getvar('plat%rocoto%build_resources').string_context(con),
            'build_walltime':walltime,
            'entities':self.getvar('plat%rocoto%entities').string_context(con),
            'baseline':self.getvar('plat%BASELINE').string_context(con),
            'template':self.getvar('plat%BASELINE_TEMPLATE').string_context(con),
            'build_deps':'',
            'build_maxtries':self.getvar('plat%BUILD_MAX_TRIES',one_max_try).string_context(con),
            'test_maxtries':self.getvar('plat%TEST_MAX_TRIES',one_max_try).string_context(con),
            'task_throttle':self.getvar('plat%TASK_THROTTLE',default_task_throttle) \
                           .string_context(con)
            }
        if self.mode is BASELINE:
            kwargs['build_deps']=r'''      <dependency>
        <taskdep task="prep_baseline"/>
      </dependency>'''
        out.write(r'''<?xml version="1.0"?>
<!DOCTYPE workflow
[
  <!ENTITY WORKFLOW_NAME "{name:s}">
  <!ENTITY LOG_DIR "{log_dir:s}">
  <!ENTITY INSTALL_DIR "{install_dir:s}">
  <!ENTITY ACCOUNT "{account:s}">
  <!ENTITY UNIQUE_ID "{UNIQUE_ID:s}">
  <!ENTITY BUILD_MAXTRIES "{build_maxtries}">
  <!ENTITY TEST_MAXTRIES "{test_maxtries}">
  <!ENTITY TASK_THROTTLE "{task_throttle}">
{entities:s}
]>

<!-- Workflow begins here -->

<!-- BASELINE = {baseline} -->
<!-- TEMPLATE = {template} -->

<workflow realtime="F" cyclethrottle="1"
          scheduler="{scheduler:s}"
          taskthrottle="&TASK_THROTTLE;">

  <!-- Rocoto is cycle-based, so we have to specify a cycle to run.
       This does NOT set the cycle to run in each regression test; it
       is only for Rocoto bookkeeping purposes. -->
  <cycledef>{cycle:s} {cycle:s} 01:00:00</cycledef>

  <!-- Tell Rocoto where to put Rocoto-specific log messages. -->
  <log><cyclestr>&LOG_DIR;/rocoto_@Y@m@d@H.log</cyclestr></log>

'''.format(**kwargs))

        if self.mode is BASELINE:
            out.write(r'''  <!-- Special task to copy baseline template -->
    <task name="prep_baseline" maxtries="&BUILD_MAXTRIES;">
      <command>sh -c 'cd &INSTALL_DIR; ; ./ush/prep_baseline.sh'</command>
      <jobname>prep_baseline</jobname>
      <account>&ACCOUNT;</account>
      <walltime>{build_walltime}</walltime>
      {build_resources:s}
      <envar>
        <name>RT_INSTALL_DIR</name>
        <value>&INSTALL_DIR;</value>
      </envar>
      <join>&LOG_DIR;/prep_baseline.log</join>
    </task>

'''.format(**kwargs))

        if self.has_builds():
            out.write(r'''  <!-- Build system definitions begin here -->
  <metatask name="builds" mode="serial">
    <var name="BUILD">'''.format(**kwargs))
            out.write(' '.join([ b for b in self.iter_buildnames()]))
            out.write(r'''</var>
    <task name="build_#BUILD#" maxtries="&BUILD_MAXTRIES;">
      <command>sh -c 'cd &INSTALL_DIR;/src ; ./install.sh #BUILD#'</command>
      <jobname>rt_build_#BUILD#</jobname>
      <account>&ACCOUNT;</account>
      <walltime>{build_walltime}</walltime>
      {build_resources:s}
      <envar>
        <name>RT_INSTALL_DIR</name>
        <value>&INSTALL_DIR;</value>
      </envar>
      <join>&LOG_DIR;/build_#BUILD#.log</join>
{build_deps:s}
      <rewind>
        <sh>set -xue ; cd "&INSTALL_DIR;/src" ; ./uninstall.sh "#BUILD#"</sh>
      </rewind>
    </task>
  </metatask>

'''.format(**kwargs))

        out.write('  <!-- Test definitions begin here. -->\n\n'.format(**kwargs))

        for testname,test in self.iter_tests():
            test.generate_xml(out,self,con)

        out.write(r'''
  <!-- End of test definitions. -->

''')


        out.write(r'''</workflow>

<!-- End of Rocoto workflow document -->
''')

########################################################################

def get_name(runcon):
    """!Gets the name of the test or build.

    @param runcon a produtil.testing.parse.RunConPair containing a
    build (produtil.testing.parsetree.Build) or test to run
    (produtil.testing.parsetree.Test).
    @returns the name of the build or test as a string"""
    try:
        return runcon.runnable.resolve('TEST_NAME').string_context(runcon.context)
    except KeyError as ke:
        return runcon.runnable.resolve('BUILD_NAME').string_context(runcon.context)

class RocotoRunner(object):
    """!Generates a three-tier NCEP EE2 structure to run a test suite
    in Rocoto."""
    def __init__(self):
        """!Constructor for RocotoRunner.

        Initializes the object so that make_runner() will be able to
        function properly.  Presently, this function does nothing."""
        super(RocotoRunner,self).__init__()
    def make_runner(self,parser,dry_run=False,setarith=None):
        """!Creates a Rocoto workflow for the given arguments.

        @param parser The produtil.testing.parse.Parser containing all
        needed information.  This is used to get the list of runnable
        tasks and builds, the sets of tasks and builds, and all
        configuration information.

        @param dry_run If True, the make_runner only logs what is to
        be done without actually doing it.

        @param setarith Optional: a string recognized by
        produtil.testing.setarith.arithparse().  This is used to
        generate the list of Tasks and Builds to run.  If no setarith
        is given, all Tests and Builds with "run" blocks are run."""
        dry_run=bool(dry_run)
        work=None
        con=None
        runset=parser.setarith(setarith)
        logger=parser.logger
        mode=parser.run_mode
        for runcon in runset:
            runme,raw_con=runcon.as_tuple
            runme_context=produtil.testing.script.runner_context_for(raw_con)
            if work is None:
                work=RocotoWorkflow('rt',runme.defscopes[-1],mode)
            work.run(runme,runme_context)
            if con is None:
                con=runme_context

        if work is None:
            raise ValueError('ERROR: No "run" statments seen; '
                             'nothing to do.\n');
        assert(con is not None)

        def here(path):
            here=os.path.normpath(os.path.join(work.install_dir(con),path))
            dir=os.path.normpath(os.path.dirname(here))
            if dir!=here and not dry_run and not os.path.isdir(dir):
                logger.info('%s: make directory'%(dir,))
                produtil.fileop.makedirs(dir)
            logger.info('%s: write file'%(here,))
            return here

        target=here('rocoto/workflow.xml')
        if not dry_run:
            with open(target,'wt') as f:
                work.generate_xml(f,con)
        target=here('src/install.sh')
        if not dry_run:
            with open(target,'wt') as f:
                f.write(work.generate_install_script())
                os.fchmod(f.fileno(),0o755)
        target=here('src/uninstall.sh')
        if not dry_run:
            with open(target,'wt') as f:
                f.write(work.generate_uninstall_script())
                os.fchmod(f.fileno(),0o755)
        if mode is BASELINE:
            target=here('ush/prep_baseline.sh')
            if not dry_run:
                with open(target,'wt') as f:
                    f.write(work.make_prep_baseline_sh(con))
                    os.fchmod(f.fileno(),0o755)
        for name,test in work.iter_tests():
            target=here(test.j_job_name(work,con))
            if not dry_run:
                with open(target,'wt') as f:
                    f.write(test.j_job_contents(work,con))
                    os.fchmod(f.fileno(),0o755)
            target=here(test.ex_script_name(work,con))
            if not dry_run:
                with open(target,'wt') as f:
                    f.write(test.ex_script_contents(work,con))
                    os.fchmod(f.fileno(),0o755)
        target=here('ush/functions.bash')
        if not dry_run:
            with open(target,'wt') as f:
                f.write('# DO NOT EDIT THIS SCRIPT; '
                        'IT IS AUTOMATICALLY GENERATED\n')
                f.write('# These are bash functions used '
                        'by the ex-scripts.\n\n')
                f.write(bash_functions)
