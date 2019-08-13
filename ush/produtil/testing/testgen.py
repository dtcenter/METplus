"""!Utility package for making programs that are wrapped around the
produtil.testing package."""

import os, logging

import produtil.fileop

from produtil.testing.utilities import BASELINE, EXECUTION
from produtil.testing.tokenize import Tokenizer, TokenizeFile
from produtil.testing.parse import Parser
from produtil.testing.rocoto import RocotoRunner
from produtil.testing.script import BashRunner
from produtil.testing.parsetree import fileless_context
from produtil.testing.setarith import arithparse

__all__=[ 'TestGen' ]

class TestGen(object):
    """!"""
    def __init__(self, run_mode, OutputType, outloc, inloc, dry_run, 
                 unique_id, logger=None, verbose=True, PWD=None,
                 setarith=None, platform_name=None):
        """!Constructor for TestGen

        @param run_mode Run mode: baseline or execution.  Must be
        produtil.testing.utilities.BASELINE or
        produtil.testing.utilities.EXECUTION

        @param OutputType the class that generates the workflow script
        or scripts.  This should be
        produtil.testing.rocoto.RocotoRunner or
        produtil.testing.script.BashRunner

        @param outloc The output directory or script filename for the workflow

        @param inloc The input file to send to the parser and tokenizer

        @param dry_run If True, then the test suite will not be
        generated.  Instead, the functions will just log what they
        would have done.

        @param unique_id Optional.  Integer ID for the workflow.  By
        default, Null is sent into the OutputType's constructor, to
        indicate that it should choose one for you.

        @param logger a logging.Logger to log messages

        @param verbose If True, send verbose log messages.

        @param PWD The directory to use for PWD in the script
        generator.  The default is the top of the produtil package
        installation area (parent of the testing/ directory.)

        @param setarith Optional.  A produtil.testing.setarith style
        set arithmetic expression to select which tests and builds to
        run.  By default, all known tests are run."""
        if PWD is None:
            # Default PWD is produtil:
            PWD=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        if logger is None:
            logger=logging.getLogger('testgen')
        self.setarith=setarith
        self.logger=logger
        self.run_mode=run_mode
        self.OutputType=OutputType
        self.outloc=outloc
        self.inloc=inloc
        self.dry_run=dry_run
        self.unique_id=unique_id
        self.platform_name=platform_name
        self.verbose=bool(verbose)
        self.PWD=PWD
        self.scope=None
        self.parser=None
        self.parse_result=None
        assert(isinstance(self.unique_id,int))

    def get_string(self,varname):
        """!Resolves the given variable reference within the global scope

        @param varname a variable reference, such as "plat%BASELINE"
        to send to self.scope.resolve().  

        @returns the string value of the varname

        @raise KeyError if the variable does not exist"""
        var=self.scope.resolve(varname)
        con=fileless_context(verbose=self.verbose)
        return var.string_context(con)

    def make_vars(self):
        """!Generates global scope constants for the parser's global scope.

        Creates and returns a dict with global constants.

        - OUTPUT_PATH: the target directory or file where the workflow
          scripts or script should be placed

        - PWD: the ush/ directory in which produtil is installed

        - PWD_UP1, PWD_UP2, ...: 1, 2, etc. directories above PWD

        @returns the dict with the constants"""
        here=self.PWD
        PWD_UP1=os.path.dirname(here)
        PWD_UP2=os.path.dirname(PWD_UP1)
        PWD_UP3=os.path.dirname(PWD_UP2)
        PWD_UP4=os.path.dirname(PWD_UP3)
        PWD_UP5=os.path.dirname(PWD_UP4)
        return { 'PWD_UP1':PWD_UP1, 'PWD_UP2':PWD_UP2,
                 'PWD_UP3':PWD_UP3, 'PWD_UP4':PWD_UP4,
                 'PWD_UP5':PWD_UP5, 'OUTPUT_PATH':self.outloc,
                 'PWD': here }
    def make_more(self,result,con):
        """!This routine is used by subclasses to make any additional
        files from within testgen().  The default implementation does
        nothing.

        @param result the produtil.testing.parsetree.Scope for the
        global scope of the parsed files

        @param con the produtil.testing.parsetree.Context to use when
        expanding strings or other objects from result."""
    def override(self,scope):
        """!Allows subclasses to override variables in the scope
        before parsing.  The default implementation does nothing.

        @param scope The global scope in which to override variables."""
    def parse(self):
        """!Parses the provided files and creates parser result variables.

        Creates these variables by parsing the inloc

        - scope: the produtil.testing.parsetree.Scope for the global scope

        - parser: the produtil.testing.parsetree.Parser used to parse
          the input files.

        - parse_result: the return value from the Parser's parse
          function (presently None)

        @returns None"""
        logger=self.logger
        tokenizer=Tokenizer()
        self.scope=produtil.testing.parsetree.Scope()
        self.override(self.scope)
        self.parser=Parser(self.run_mode,logger,self.verbose)
        self.parser.requested_platform_name=self.platform_name
        morevars=self.make_vars()
        with open(self.inloc,'rt') as fileobj:
            self.parse_result=self.parser.parse(
                TokenizeFile(tokenizer,fileobj,self.inloc,1),self.scope,
                unique_id=self.unique_id,morevars=morevars)
    def generate(self):
        """!Generates the on-disk files used to run the workflow."""
        logger=self.logger
        outputter=self.OutputType()
        outputter.make_runner(parser=self.parser,dry_run=self.dry_run,
                              setarith=self.setarith)
        con=fileless_context(
            scopes=[self.parse_result],verbose=self.verbose,logger=logger,
            run_mode=self.run_mode)
        self.make_more(self.parse_result,con)
    def testgen(self):
        """!Parses input files and generates the workflow scripts.

        @see parse()
        @see generate()"""
        self.parse()
        self.generate()
            
