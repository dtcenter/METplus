"""!Change directory, handle temporary directories

This module provides a means by which to change to a different
directory in a Python "with" block and change back out afterwards,
regardless of what happens inside the block.  It can, optionally,
create a new directory, and optionally delete it at the end of the
block.  There are two classes:

*  TempDir - creates a temporary directory with a randomly-generated
     name, chdirs to the directory, and chdirs back out afterwards.
     It can be configured to delete the directory afterwards (the
     default) or not.  

*  NamedDir - a subclass of TempDir that uses a specific directory
     rather than a randomly-generated one.  By default, the directory
     is NOT deleted at the end of the block.  That can be configured."""

import tempfile, os, re, logging, sys, shutil, errno, stat
import produtil.listing

##@var __all__
# List of symbols to export by "from produtil.cd import *"
__all__=['TempDir','NamedDir','perm_remove','perm_add']

##@var perm_add
# Default permissions to add to new directories created by TempDir:
# user has all possible access.  Group and other can read and execute.
# @private
perm_add = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | \
    stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH

##@var perm_remove
# Permissions to remove from all directories: world write and setuid.
# This overrides perm_add.
# @private
perm_remove = stat.S_IWOTH|stat.S_ISUID

class TempDir(object):
    """!This class is intended to be used with the Python "with TempDir() as t" syntax.
    Example:
    @code
         with TempDir() as t:
             # we're now in the temporary directory
             ...do things...
         # the temporary directory has been deleted now
    @endcode
    """
    def __init__(self,suffix='.tmp',prefix='tempdir.',dir=None,keep=False,
                 logger=None,print_on_exception=True,add_perms=perm_add,
                 remove_perms=perm_remove,keep_on_error=True,cd=True):
        """!Creates a TempDir.

        @param  suffix,prefix,dir Passed to the tempfile.mkdtemp to
            generate the directory name.  Meanings are the same as in
            that constructor.  See the Python documentation for
            details.
        @param  keep Controls directory deletion if the "with" block
            returns without an exception.  If False, the directory is
            deleted.  Default: keep=False
        @param logger A logging.logger for log messages
        @param print_on_exception Print exceptions before leaving the dir
        @param add_perms Permissions to add to the directory.  Default: 755.
        @param remove_perms Permissions to remove from the directory.
            Default: setuid and world write.
        @param  keep_on_error Controls directory deletion if the "with"
            block raises an Exception or GeneratorExit, or subclass
            thereof.  If False, the directory is deleted under those
            circumstances.  Default: keep_on_error=True.
        @param cd If True (default), cd to the directory in the "with"
            block and cd back out afterwards.  If False, then only 
            directory creation and deletion happens.  """
        self.dirname=None
        self.suffix=suffix
        self.prefix=prefix
        self.print_on_exception=print_on_exception
        if dir is None:
            dir='.'
        self.dir=dir
        self.olddir=None
        self._keep=keep
        self._logger=logger
        self._add_perms=int(add_perms)
        self._remove_perms=int(remove_perms)
        self._keep_on_error=keep_on_error
        self._cd=bool(cd)
        assert(dir is not None)
        if not os.path.isabs(self.dir):
            self.dir=os.path.join(os.getcwd(),self.dir)
        assert(os.path.isabs(self.dir))
    ##@var dirname
    # The name of the target directory.

    ##@var olddir
    # The name of the directory we came from.

    ##@var suffix
    # Temporary directory name suffix

    ##@var prefix
    # Temporary directory name prefix

    ##@var print_on_exception
    # Should we print exceptions before exiting the directory?

    ##@var dir
    # The directory object.

    def name_make_dir(self):
        """!Decide the name of the directory, and create the directory.
        Also create any path components leading up to the
        directory."""
        if self.prefix is not None:
            try:
                d=os.path.dirname(self.prefix)
                if d is not None and d!='':
                    os.makedirs(d)
            except EnvironmentError as e:
                if e.errno != errno.EEXIST:
                    raise
        self.dirname=tempfile.mkdtemp(suffix=self.suffix,prefix=self.prefix,
                                      dir=self.dir)
        # Add requested permissions to the directory.  Remove world write.
        s=os.stat(self.dirname)
        os.chmod(self.dirname, (s.st_mode | int(self._add_perms)) 
                 & ~self._remove_perms )
    def mkdir_cd(self):
        """!Creates the temporary directory and chdirs the current
        process into that directory.  It calls self.name_make_dir() to
        do the naming and directory creation."""
        self.olddir=os.getcwd()
        self.name_make_dir()
        if self._cd: os.chdir(self.dirname)
        if self._logger is not None:
            self._logger.info('chdir to temporary directory '+self.dirname)
    def cd_out(self):
        """!Exit the temporary directory created by mkdir_cd and
        return to the original directory, if possible."""
        if self._logger is not None:
            self._logger.info('chdir to old directory '+self.olddir)
        if self._cd: os.chdir(self.olddir)
    def cd_rmdir(self):
        """!CD out and remove the old directory.

        This subroutine exits the temporary directory created by
        mkdir_cd, and then deletes that temporary directory.  After
        this routine, the process will be in its original directory
        (from before the call to mkdir_cd) if possible, or otherwise
        it will be in the root directory (/).

        It is the caller's responsibility to ensure this function is
        not called if keep_on_error=True and an error occurs."""
        try:
            if self._cd: self.cd_out()
        except(Exception) as e:
            if self._logger is not None:
                self._logger.critical('could not chdir, so chdir to root '
                                      'because of exception: '+repr(e))
            if self._cd: os.chdir('/')
        finally:
            if self.dirname is not None and not self._keep \
                    and os.path.isabs(self.dirname):
                if self._logger is not None:
                    self._logger.info('%s: delete temporary directory'
                                      %(self.dirname,))
                if self._logger is not None:
                    shutil.rmtree(self.dirname,onerror=self._rmerror)
                else:
                    shutil.rmtree(self.dirname,True)
                if self._logger is not None and os.path.exists(self.dirname):
                    self._logger.warning('%s: could not delete directory'
                                         %(self.dirname,))
            elif self.dirname is not None and self._logger is not None:
                self._logger.info('%s: not deleting temporary directory'
                                  %(self.dirname,))
        return False
    def _rmerror(self,function,path,excinfo):
        """!Called when a file removal error happens.
        @param function,path,excinfo exception information"""
        if self._logger is not None:
            self._logger('%s: cannot remove'%(str(path),),exc_info=excinfo)
    def exception_info(self):
        """!Called to dump information to a log, or failing that, the
        terminal if an unexpected exception is caught."""
        if self._logger is not None:
            self._logger.warning(self.dirname
                                 +': leaving temp directory due to exception')
            self._logger.info('%s: listing current directory (%s) via ls -l',
                              self.dirname,os.getcwd())
        else:
            logging.getLogger('produtil.tempdir').warning(
                self.dirname+': leaving temp directory due to exception')
        print produtil.listing.Listing('.')
    def __enter__(self):
        """!This is a simple wrapper around mkdir_cd that is intended
        to be used with in a "with" block.  This subroutine is
        automatically called at the beginning of the block."""
        self.mkdir_cd()
        return self
    def __exit__(self,etype,value,traceback):
        """!Exit the 'with' block.

        This is a simple wrapper around cd_rmdir that is intended to
        be used with in a "with" block.  This subroutine is
        automatically called at the end of the block.  It will call
        cd_rmdir to delete the directory unless an exception is thrown
        that is NOT a subclass of Exception or GeneratorExit.  The
        removal is skipped to allow the program to exit quickly in
        case of a fatal signal (ie.: SIGQUIT, SIGTERM, SIGINT,
        SIGHUP).
        @param etype,value,traceback exception information"""
        if value is None or isinstance(value,GeneratorExit):
            # Normal exit
            self.cd_rmdir() # will not delete if self.keep
        elif isinstance(value,Exception):
            # Exception thrown, but not a fatal exception and not a
            # break statement (GeneratorExit)
            if isinstance(value,Exception) and self.print_on_exception:
                self.exception_info()
            if self._keep_on_error:
                self.cd_out()
            else:
                self.cd_rmdir()
        else:
            # Fatal error such as KeyboardInterrupt or SystemExit.  Do
            # as little as is safe:
            self.cd_out() # no rmdir

class NamedDir(TempDir):
    """!This subclass of TempDir takes a directory name, instead of
    generating one automatically.  By default, it will NOT delete the
    directory upon __exit__.  That can be overridden by specifying
    keep=False."""
    def __init__(self,dirname,keep=True,logger=None,keep_on_error=True,
                 add_perms=0,remove_perms=0,rm_first=False):
        """!Create a NamedDir for the specified directory.  The given
        logger is used to log messages.  There are two deletion
        vs. non-deletion options:

        @param dirname The directory name
        @param keep If False, the file is deleted upon successful return
             of the "with" block.  If True, the file is kept upon
             successful return.
        @param logger A logging.logger for log messages
        @param add_perms Permissions to add to the directory after cding
             into it.  Default: none.
        @param remove_perms Permissions to remove from the directory after
             cding into it.  Default: none.
        @param keep_on_error Controls deletion upon catching of an
             Exception or GeneratorException (or subclass thereof).
        @param rm_first If the directory already exists, delete it first
           and make a new one before cding to it."""
        if not isinstance(dirname,basestring):
            raise TypeError(
                'NamedDir requires a string name as its first argument.')
        super(NamedDir,self).__init__(
            keep=keep,logger=logger,keep_on_error=keep_on_error,
            add_perms=add_perms,remove_perms=remove_perms)
        self.dirname=dirname
        self._rm_first=bool(rm_first)
    ##@var dirname 
    # The directory name specified in the constructor.
    def name_make_dir(self):
        """!Replacement for the TempDir.name_make_dir.  Uses the
        directory name specified in the constructor."""
        if not self._cd: return
        if self._rm_first:
            if os.path.exists(self.dirname):
                if self._logger is not None:
                    self._logger.warning('%s: delete directory tree'%(
                            self.dirname,))
                    shutil.rmtree(self.dirname,onerror=self._rmerror)
                else:
                    shutil.rmtree(self.dirname,True)
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)
        # If requested, modify the directory permissions:
        if self._add_perms!=0 or self._remove_perms!=0:
            s=os.stat(self.dirname)
            os.chmod(self.dirname, (s.st_mode | int(self._add_perms)) 
                     & ~self._remove_perms )
