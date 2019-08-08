"""!This module provides a set of utility functions to do filesystem
operations.  It replaces or improves upon several os, stat, and sys
module functions by working around Python bugs, providing an API layer
that allows forward compatibility to future Python versions, and
adding logging capabilities."""

##@var __all__
# List of symbols exported by "from produtil.fileop import *"
__all__=['FileOpError','FileOpErrors','CannotLinkMulti',
         'UnexpectedAbsolutePath','InvalidExecutable',
         'FindExeInvalidExeName','CannotFindExe','RelativePathError',
         'DeliveryFailed','VerificationFailed','realcwd','chdir',
         'makedirs','remove_file','rmall','lstat_stat','isnonempty',
         'check_file','deliver_file','make_symlinks_in','find_exe',
         'make_symlink','replace_symlink','unblock','fortcopy',
         'norm_expand_path','norm_abs_path','check_last_lines',
         'wait_for_files','FileWaiter','call_fcntrl','gribver',
         'netcdfver','touch']

import os,tempfile,filecmp,stat,shutil,errno,random,time,fcntl,math,logging
import produtil.cluster, produtil.pipeline

module_logger=logging.getLogger('produtil.fileop')

########################################################################
class FileOpError(Exception):
    """!This is the superclass of several exceptions relating to
    multi-file operations in produtil.fileop."""
    def __init__(self,message,filename,more=[]):
        """!FileOpError constructor
        @param message the error message
        @param filename the name of the problematic file
        @param more a list of tuples, (from,to,message) where from is
          the source file, to is the destination file and message is a
          description of the problem with that pair."""
        self.message=message
        self.filename=filename
        self.more=more
    ##@var message
    # The error message

    ##@var filename
    # The name of the problematic file

    ##@var more
    # A list of tuples, (from,to,message) where from is the
    # source file, to is the destination file and message is a
    # description of the problem with that pair.

    def __str__(self):
        """!A string description of the problem."""
        return '%s: %s' % (self.filename,self.message)
    def __iter__(self):
        """!Iterates over a list of tuples, (from,to,message) where
        from is the source file, to is the destination file and
        message is a description of the problem with that pair."""
        for fromfile,tofile,message in self.more:
            yield fromfile,tofile,message
class FileOpErrors(FileOpError):
    """!This exception is raised when an operation that processes
    multiple files catches more than one exception."""
class CannotLinkMulti(FileOpError):
    """!This exception is raised when the caller tries to create
    multiple symlinks in a single target, but the target is not a
    directory."""
class UnexpectedAbsolutePath(FileOpError):
    """!This exception indicates that the renamer function sent to
    make_symlinks_in returned an absolute path."""
class InvalidExecutable(FileOpError):
    """!Thrown when a find_exe fails."""
class FindExeInvalidExeName(FileOpError):
    """!Thrown when find_exe is given an executable name that contains
    a directory path."""
class CannotFindExe(FileOpError):
    """!Thrown when find_exe cannot find an executable in the path or
    directory list."""
class RelativePathError(FileOpError):
    """!Raised when a relative path is given, but an absolute path is
    expected."""

class WrongSymlink(FileOpError):
    """!Raised when os.symlink makes a symlink to a target other than
    the one that was requested.  This is present to detect a bug in
    Cray where os.symlink randomly makes a symlink to the wrong
    place."""

class DeliveryFailed(Exception):
    """!This exception is raised when a file cannot be delivered."""
    def __init__(self,message,fromfile,tofile):
        """!DeliveryFailed constructor.
        @param message why the delivery failed
        @param fromfile what was being delivered
        @param tofile delivery destination"""
        self.message=message
        self.fromfile=fromfile
        self.tofile=tofile
    ##@var message
    # String description of the problem

    ##@var fromfile
    # The source file
 
    ##@var tofile
    # The target file 

    def __str__(self):
        """!Human-readable description of this error."""
        return '%s: cannot deliver (from %s): %s'%(
            self.tofile,self.fromfile,self.message)
    def __repr__(self):
        """!Pythonic representation of this error."""
        return 'DeliveryFailed(%s,%s,%s)' %  \
            (repr(self.message),repr(self.fromfile),repr(self.tofile))

class VerificationFailed(DeliveryFailed):
    """!This exception is raised when a copy of a file has different
    content than the original."""
    def __init__(self,message,fromfile,tofile,verifyfile):
        """!VerificationFailed constructor.
        @param message why the delivery failed
        @param fromfile what was being delivered
        @param tofile delivery destination
        @param verifyfile temporary file that failed verification"""
        DeliveryFailed.__init__(self,message,fromfile,tofile)
        self.verifyfile=verifyfile
    ##@var verifyfile
    # The file to verify

    def __str__(self):
        """!Human-readable description of this error."""
        return '%s: verification failed on temporary file %s (from %s): %s'%\
            (self.tofile,self.verifyfile,self.fromfile,self.message)
    def __repr__(self):
        """!Pythonic representation of this error."""
        return 'VerificationFailed(%s,%s,%s,%s)'%\
            (repr(self.message),repr(self.fromfile),repr(self.tofile),repr(self.verifyfile))

########################################################################
def realcwd():
    """!Returns the current working directory, expanding any symbolic
    links."""
    return os.path.realpath(os.getcwd())

def chdir(path,logger=None):
    """!Changes to the specified directory.  Please use
    produtil.cd.NamedDir instead.

    This is generally not a good idea since you will not cd back if an
    unhandled exception is raised.  It is better to use the
    produtil.cd module, which provides ways to enter a directory in a
    "with" block and optionally delete it afterwards.  Such
    functionality could also be implemented via a try...finally block.
    @param path the path to cd to
    @param logger a logging.Logger for log messages"""
    path=str(path)
    try:
        if logger is not None: logger.info(path+': cd here')
        os.chdir(path)
    except EnvironmentError as e:
        logger.warning(path+': cannot cd: '+str(e),exc_info=True)
        raise

def touch(filename, times=None):
    """!Open the file for append and set mtime and atime. 

    Opens the specified file in append mode, but writes nothing.  Sets
    the access and modification times. 

    @param filename the string filename
    @param times A 2-tuple of numbers, of the form (atime, mtime). 
      These are UNIX epoch times (seconds since 1970 began in UTC)."""
    with open(filename, 'a'):
        os.utime(filename, times)

########################################################################
def netcdfver(filename):
    """!What is the NetCDF version of this file?

    Returns one of three strings based on the NetCDF version of the
    given file, or returns None if the file is not NetCDF:
     *  "CDF1" = NetCDF classic format
     *  "CDF2" = NetCDF 64-bit offset format
     *  "HDF5" = HDF5 file, and hence possibly a NetCDF4 file.
     *  None   = Not NetCDF and not HDF5
    @param filename the name of the file to test"""
    with open(filename,'rb') as f:
        eight=f.read(8)
        if len(eight)<4:
            return None
        four=eight[0:4]
        if four=='CDF\x01':
            return "CDF1"
        elif four=='CDF\x02':
            return "CDF2"
        elif eight=='\x89\x48\x44\x46\x0d\x0a\x1a\x0a':
            return "HDF5"
    return None

########################################################################
def gribver(filename):
    """!What is the GRIB version of this file?

    Returns the GRIB file version: 1 or 2.  If the file is not a GRIB
    file, or if the answer is indeterminate, returns None.  Only the
    first GRIB record is tested.
    @param filename the path to the file to test"""
    if not isinstance(filename,str):
        raise TypeError('The first argument to gribver should be '
                        'a filename.  You provided a %s %s.'%
                        (type(filename).__name__,repr(filename)))
    if not isnonempty(filename):
        return None
    with open(filename,'rb') as f:
        eight=f.read(8)
        if eight=='GRIB\x00\x00\x00\x02':
            return 2
        elif eight[0:4]=='GRIB':
            return 1
        else:
            return None

########################################################################
def makedirs(filename,numtries=10,logger=None):
    """!Make a directory tree, working around filesystem bugs.

    This makedirs implementation works around a common bug: if two
    processes try to recursively make a directory tree simultaneously,
    makedirs can fail when two processes make the same path component
    at the same time.  This implementation automatically retries in
    that situation.
    @param filename the directory path
    @param numtries the number of times to retry
    @param logger a logging.Logger for log messages"""
    for n in range(numtries):
        try:
            if not os.path.isdir(filename):
                if logger is not None:
                    logger.info(filename+': make directory and parents')
                os.makedirs(filename)
        except EnvironmentError as e:
            if os.path.isdir(filename):
                return True
            elif os.path.exists(filename):
                raise
            elif n==numtries-1:
                continue
            raise

########################################################################    
def remove_file(filename,info=True,logger=None):
    """!Deletes the specified file.  

    Does nothing if the filename is None, is the empty string or
    already does not exist.  Otherwise, the file is deleted.
    @param filename The file to delete.
    @param info Optional: indicates that warnings about a file already
    not existing should be sent to the logger at INFO level
    (info=True) instead of WARNING (info=False).
    @param logger the logging.Logger for messages"""
    if filename is None or filename=='':
        return # nothing to do
    try:
        if logger is not None: logger.info('%s: remove file'%(filename,))
        os.unlink(filename)
    except EnvironmentError as e:
        if e.errno!=errno.ENOENT: # ENOENT = file does not exist
            if logger is not None: 
                logger.warning('%s: cannot remove: %s'%(filename,str(e)),
                               exc_info=True)
            raise
        if logger is not None: 
            log=logger.info if info else logger.warning
            log('%s: cannot remove; does not exist: %s'%(filename,str(e)))

def rmall(*args,**kwargs):
    """!Deletes the specified list of files.  

    Deletes files listed in "args".  Each one is passed to
    remove_file.  Exceptions that derive from EnvironmentError are
    collected, and will be raised at the end, thus allowing removal of
    later files to continue if earlier ones failed.  If only one file
    causes an exception, that exception will be raised, otherwise
    FileOpErrors will be raised
    @param args The files to delete.
    @param kwargs Keyword arguments passed to remove_file()."""
    logger=kwargs.get('logger',None)
    if logger is not None:
        logger.info('Removing %d files...'%(len(args),))
    ex=list()
    for arg in args:
        try:
            remove_file(arg,**kwargs)
        except EnvironmentError as e:
            ex.append( (arg,None,e) )
    if len(ex)==1:
        raise ex[0][1]
    elif len(ex)>1:
        msg='Multiple exceptions caught while deleting files in rmall.'
        if logger is not None: logger.warning(msg)
        raise FileOpErrors(msg,','.join(args),
                           [ (a,b,str(c)) for a,b,c in ex ] )
    if logger is not None:
        logger.info('Done removing %d files...'%(len(args),))

########################################################################
def lstat_stat(filename,raise_nonexist=False):
    """!Runs lstat and stat on a file as efficiently as possible.

    Returns (lstat(filename),stat(filename)) where each is None if it
    fails due to non-existence.  Does this in as few filesystem
    metadata operations as possible.  Will raise an exception if the
    stat fails for any reason other than non-existence of a file, or
    if the file or linked file is non-existent and
    raise_nonexist=True.
    @param filename The file to test.
    @param raise_nonexist Should we raise an exception if the file does not exist?
    @returns a tuple (L,S) where L is the lstat return value, and S is
      the stat return value.  Each will be None if the file or link
      target do not exist."""
    assert(filename is not None)
    (xlstat,xstat)=(None,None)
    try:
        xlstat=os.lstat(filename)
        if not stat.S_ISLNK(xlstat.st_mode):
            return (xlstat,xlstat)
        xstat=os.stat(filename)
    except EnvironmentError as e:
        if raise_nonexist or e.errno!=errno.ENOENT:
            raise
    return (xlstat,xstat)

def isnonempty(filename):
    """!Returns True if the filename refers to an existent file that is
    non-empty, and False otherwise.
    @param filename The file to test."""
    if filename is None:           return None
    sfile=str(filename)
    if sfile is None or sfile=='': return None
    (l,s) = lstat_stat(filename)
    ret=s is not None and s.st_size>0
    return ret

########################################################################    
def deliver_file(infile,outfile,keep=True,verify=False,blocksize=1048576,
                 tempprefix=None,permmask=0o002,removefailed=True,
                 logger=None,preserve_perms=True,preserve_times=True,
                 preserve_group=None,copy_acl=None,moveok=True, 
                 force=True, copier=None):
    """!This moves or copies the file "infile" to "outfile" in a unit
    operation; outfile will never be seen in an incomplete state.

    If the caller specifies keep=False (default is True) and
    moveok=True, and the source and destination are on the same
    filesystem then the delivery is done with a simple move.
    Otherwise a copy is done to a temporary file on the same
    filesystem as the target.  If verification is requested
    (verify=True) then the temporary file is verified by filecmp.cmp,
    before moving the temporary file to the final location.

    When requested, and when possible, the permissions and ownership
    are preserved.  Both copy_acl and preserve_group have defaults set
    by the produtil.cluster module.  If the cluster uses access
    control lists for data restriction classes, then copy_acl will be
    set to True, otherwise it is false.  If group quotas are enabled,
    preserve_group is False, otherwise it is True.

    @note The original file is never deleted, but it may be moved to
    the target if keep=False.  If a copy is done instead, the original
    file is still present.

    @param infile the origin file
    @param outfile the destination file or its parent directory
    @param keep If False, the original file is no longer needed.  If False
      and moveok=True, the file might be delivered by a "mv"
      operation, avoiding any data duplication (no "cp").
    @param verify If a "cp" is done, reopen the target and source and
      verify they are the same.  Note that providing a copier will 
      break the verification functionality if the copier changes the
      contents of the destination file (such as a copier that compresses).
    @param blocksize block size during copy operations
    @param tempprefix Prefix for temporary files during copy operations.
      Do not include directory paths in the tempprefix.
    @param permmask Permission bits to remove Default: world write (002)
    @param removefailed If True, delete temporary files if the delivery fails
    @param logger the logging.Logger for log messages.
    @param preserve_perms If True, copy the old file's permissions to
      the new file
    @param preserve_times If True, copy the old file's timestamps to
      the new file
    @param preserve_group If True, copy the old file's group ID to the
      new file
    @param copy_acl If True, copy the access control lists from one file 
      to another
    @param moveok If True, delivery by "mv" is allowed.  Must also set
      keep=False.
    @param force If False, delivery will be aborted (raise
      TargetFileExists) if the target file already exists.
    @param copier If present, this function or callable object is used to
      copy data from the source file to the temporary file before moving
      it to the target.  The copier is called as 
           copier(infile,temp_file_name,temp_file_object)
      Where the temp_file_name is the name of the destination file and
      the temp_file_object is an object that can be used to write to 
      the file.  The copier should NOT close the temp_file_object. """
    if preserve_group is None:
        preserve_group = not produtil.cluster.group_quotas()
    if copy_acl is None:
        copy_acl = produtil.cluster.use_acl_for_rstdata()
    if copier is not None:
        # Cannot simply do a "move" if we are using an external
        # function to copy.
        keep=True

    assert(infile is not None)
    assert(outfile is not None)
    inbase=os.path.basename(infile)
    (ilstat,istat)=lstat_stat(infile,raise_nonexist=True)

    if stat.S_ISDIR(istat.st_mode):
        raise DeliveryFailed('This subroutine cannot deliver directories.',
                             infile,outfile)

    # The outfile may be a directory, in which case we copy to a file
    # with the same name as the source, in that directory:
    actual_outfile=outfile # actual path of target file
    outdir=None # parent directory of target file
    (oflstat,ofstat)=lstat_stat(actual_outfile) # stat on target file
    (odlstat,odstat)=(None,None) # stat on target file's parent directory
    if ofstat is not None:
        if stat.S_ISDIR(ofstat.st_mode):
            outdir=actual_outfile
            actual_outfile=os.path.join(outfile,inbase)
            (odlstat,odstat)=(oflstat,ofstat)
            if logger is not None:
                logger.debug('%s: is a directory; file is %s'
                             %(outfile,inbase))
            (oflstat,ofstat)=lstat_stat(actual_outfile)
    if odlstat is None:
        outdir=os.path.dirname(outfile)
        if len(outdir)<1: outdir='.'
        if logger is not None:
            logger.debug('%s: exists, so parent %s must exist and be a '
                         'directory'%(outfile,outdir))
        (odlstat,odstat)=lstat_stat(outdir,raise_nonexist=True)
        if odstat is None:
            raise DeliveryFailed('Target does not exist, and parent of '
                                 'target does not exist.',infile,outfile)
        if not stat.S_ISDIR(odstat.st_mode):
            raise DeliveryFailed('Target does not exist, and parent of '
                                 'target is not a directory.',infile,outfile)

    if odstat is not None and not force:
        if logger is  not None:
            logger.debug('%s: exists and overwrite (force) is disabled.  '
                         'Aborting delivery.'%(actual_outfile,))

    # Handle a special case: the source and destination are the same
    # and the destination is not a symlink.  In that case, we have
    # nothing to do and can simply return.
    if ofstat is not None:
        if stat.S_ISLNK(ofstat.st_mode):
            if logger is not None:
                logger.info('%s: destination is a link, will recopy as '
                            'a non-link.'%(actual_outfile,))
        elif os.path.samestat(istat,ofstat):
            if logger is not None:
                logger.info('%s: same as %s'%(actual_outfile,infile))
            return # nothing to do
        if logger is not None:
            logger.info('%s: exists, replacing with %s'%(
                    actual_outfile,infile))
    elif logger is not None:
        logger.debug('%s: does not exist'%(actual_outfile))

    # Handle another case: if we're not required to keep the origin,
    # the origin is in the same file as the target, and the origin is
    # not a link, and moveok=True, we can deliver the file by an
    # os.rename
    samefs = (istat.st_dev == odstat.st_dev)
    if samefs and not keep and moveok:
        if stat.S_ISLNK(ilstat.st_mode):
            if logger is not None:
                logger.info('%s: cannot deliver via "os.rename" since '
                            'source is a link.'%(infile,))
        else:
            if logger is not None:
                logger.info('%s: move from %s'%(actual_outfile,infile))
            try:
                os.rename(infile,actual_outfile)
                return
            except EnvironmentError as e:
                if logger is not None:
                    logger.info('%s: could not deliver by os.rename: %s'
                                %(actual_outfile,str(e)))
                                
    # If we get here, then the files are in different filesystems or
    # we're being asked to keep a copy or os.rename failed.  That
    # means we need to copy to a temporary file and move it to the
    # destination.
    temp=None
    tempname=None
    try:
        # Copy to a temporary file:
        if tempprefix is None:
            tempprefix="tmp."+inbase+".part."
        temp=tempfile.NamedTemporaryFile(prefix=tempprefix,
                                         delete=False,dir=outdir)
        tempname=temp.name
        if logger is not None:
            logger.info('%s: copy to temporary %s'%(infile,tempname))
        if copier is None:
            with open(infile,'rb') as indata:
                shutil.copyfileobj(indata,temp,length=blocksize)
        else:
            copier(infile,tempname,temp)
        temp.close()
        temp=None

        if verify:
            if logger is not None:
                logger.info('%s: verify copy %s'%(infile,tempname))
            if not filecmp.cmp(infile,tempname):
                raise VerificationFailed('filecmp.cmp returned False',
                                         infile,actual_outfile,tempname)
        if logger is not None:
            logger.info('%s: copy group ID and permissions to %s'
                        %(infile,tempname,))
        # Copy group ID and permissions:
        if preserve_group:
            try:
                os.chown(tempname,-1,istat.st_gid)
            except(IOError,OSError) as e:
                # Usually this is not an error: it means the user is
                # not in the group
                if logger is not None:
                    logger.warning('%s: cannot copy groupid to %s: %s' 
                                   % (infile,tempname,str(e)))
        if preserve_perms:
            os.chmod(tempname,istat.st_mode&~permmask)
        #FIXME: COPY ACLS HERE
        # Move to the final location:
        if logger is not None:
            logger.info('%s: move from %s'%(actual_outfile,tempname))
        if preserve_times:
            os.utime(tempname,(istat.st_atime,istat.st_mtime))
        os.rename(tempname,actual_outfile)
        tempname=None
    except Exception as e:
        if logger is not None:
            logger.error('%s: delivery failed: %s'%(infile,str(e)))
        raise
    finally:
        try:
            if temp is not None:
                temp.close()
            if removefailed and tempname is not None:
                os.unlink(tempname)
        except EnvironmentError as e:
            pass

########################################################################
def find_exe(name,dirlist=None,raise_missing=True):
    """!Searches the $PATH or a specified iterable of directory names
    to find an executable file with the given name.  

    Returns the executable's location.  If the executable cannot be
    found, and raise_missing=True, raises CannotFindExe, otherwise
    returns None.  Raises FindExeInvalidExeName if "name" is not the
    same as its os.path.basename.

    @param name The name of the executable to find.
    @param dirlist The list of directories to search, or None to search $PATH
    @param raise_missing If True, the CannotFindExe exception is
      raised for executables that cannot be found.  If False, return
      None in that situation."""
    bn=os.path.basename(name)
    if bn != name:
        raise FindExeInvalidExeName(
            'executable name is not the same as its basename in '
            'find_exe (basename=%s)'%(bn,),name)
    if dirlist is None:
        dirlist=os.environ['PATH'].split(':')
    for dirname in dirlist:
        if dirname=='': dirname='.'
        exename=os.path.join(dirname,name)
        if os.path.isfile(exename) and os.access(exename,os.X_OK):
            return exename
    if not raise_missing: return None
    raise CannotFindExe('cannot find executable',name)

########################################################################

def symlink_read_test(filename,readsize=40,logger=None):
    """!Opens the specified file for reading and attempts to read data
    to it.  Logs the process.  Will NOT raise any I/O or system
    errors; they are ignored.  This is a workaround for a bug in Cray:
    symlinks to recently created files cannot be read by the compute
    node unless the batch node reads from them first (or unless you
    wait a while)."""
    try:
        with open(filename,'rt') as f:
            buf=f.read(readsize)
            if logger is not None:
                logger.info('%s: read %s'%(filename,repr(buf)))
    except EnvironmentError as e:
        pass # ignore I/O and OS errors

def make_symlinks_in(sources,targetdir,force=False,renamer=None,logger=None,
                     copy=False):
    """!Creates symbolic links from a set of source files to a target
    directory.  If "force" is True, then any existing files will first
    be deleted.

    The "renamer" can be a function that generates paths of the
    symlinks, relative to targetdir, for each symlink in "sources".
    If the return value from "renamer" is an absolute path, an
    exception will be thrown.  If the return value is None, then no
    link will be made.

    Example:
    make_symlinks_in(['/path/to/a','/path/to/b'],'.',
      renamer=lambda s: os.path.basename(s)+'.linkified')

    will create a.linkified, linked to /path/to/a, and b.linkified,
    linked to /path/to/b in directory "." 
    @param sources The list of files to link to.
    @param targetdir The directory in which to place the links.
    @param force Remove existing files if needed.
    @param renamer Function to generate link names.
    @param logger A logging.Logger for log messages.
    @param copy If True, files are copied instead of linked."""
    (tlstat,tstat)=lstat_stat(targetdir,raise_nonexist=True)
    if not stat.S_ISDIR(tstat.st_mode):
        raise CannotLinkMulti('target is not a directory',targetdir)
    errors=[]
    for source in sources:
        target=None
        try:
            if renamer is not None:
                target=renamer(source)
                if target is None: continue
                if os.path.isabs(target):
                    raise UnexpectedAbsolutePath(
                        'renamed path is absolute',renamed)
                target=os.path.join(targetdir,target)
            else:
                target=os.path.join(targetdir,os.path.basename(source))
            if copy:
                if os.path.exists(source):
                    if force and os.path.exists(target):
                        os.unlink(target)
                    deliver_file(source,target,keep=True,logger=logger)
                elif logger is not None:
                    logger.warning(
                        '%s: skip.  Am in copy mode, and source does not exist (%s)'%(
                            target,source))
            else:
                make_symlink(source,target,force=force,logger=logger)
        except EnvironmentError as e:
            errors.append( (source,str(target),str(e)) )
            if logger is not None:
                logger.warning(str(e),exc_info=True)
    if len(errors)>0:
        raise FileOpError('cannot link files',targetdir,errors)

def make_symlink(source,target,force=False,logger=None,max_tries=20):
    """!Creates a symbolic link "target" that points to "source".  If
    the target already exists and is NOT a directory, then the file
    will be replaced.  The replacement is done in a unit operation so
    that the target will always exist (unless the operation fails).
    @param source The file to link to.
    @param target The name of the link.
    @param force If True, and target exists, delete it first.
    @param logger a logging.Logger for log messages."""
    if logger is None: logger=module_logger
    if logger is not None:
        logger.info('link %s -> %s'%(target,source))
    if os.path.isdir(target):
        target=os.path.join(target,os.path.basename(source))
        if logger is not None:
            logger.info('Target is a directory.  Symlink to %s instead'%(target,))
    try:
        os.symlink(source,target)
        content=os.readlink(target)
        if content!=source:
            msg="FILESYSTEM FAILURE: Cannot symlink \"%s\" -> \"%s\".  Instead, the symlink is to \"%s\"."%(target,source,content)
            if logger is not None:
                logger.critical(msg)
            raise WrongSymlink(msg,target)
        else:
            pass # symlink_read_test(target,logger=logger)
    except EnvironmentError as e:
        if not e.errno==errno.EEXIST or not force:
            raise
        # The file already exists
        if logger is not None:
            logger.info('target exists - using replace_symlink instead')
        return replace_symlink(source,target,logger=logger)

def replace_symlink(source,target,logger=None,max_tries=20):
    """!Do not call this routine directly: you want make_symlink
    instead.  This routine creates a new symbolic link and renames
    that link to "target."  That always replaces target with a
    symbolic link to source, even if target did not already exist.
    @param source the file to link from
    @param target the file to link to
    @param logger a logging.Logger for messages"""
    if logger is None: logger=module_logger
    tempname=os.path.join(os.path.dirname(target),
       'tmp.%s.%06x.%06x.tmp' % ( os.path.basename(target),
           random.getrandbits(32),random.getrandbits(32)))
    try:
        if logger is not None:
            logger.info('link %s -> %s'%(tempname,source))
        os.symlink(source,tempname)
        content=os.readlink(tempname)
        if content!=source:
            msg="FILESYSTEM FAILURE: Cannot symlink \"%s\" -> \"%s\".  Instead, the symlink is to \"%s\"."%(tempname,source,content)
            if logger is not None:
                logger.critical(msg)
            raise WrongSymlink(msg,tempname)
        if logger is not None:
            logger.info('rename %s to %s'%(tempname,target))
        os.rename(tempname,target)
        # symlink_read_test(tempname,logger=logger)
    except Exception as e:
        if isinstance(e,WrongSymlink): raise
        try:
            if logger is not None:
                logger.info('failed: delete %s'%(tempname,))
            os.remove(tempname)
        except EnvironmentError: pass
        raise e

########################################################################
def unblock(stream,logger=None):
    """!Attempts to modify the given stream to be non-blocking.  This
    only works with streams that have an underlying POSIX fileno, such
    as those from open.  

    Will re-raise any exception received, other than AttributeError
    and EnvironmentError.  Hence, I/O errors and attempts to make a
    non-fileno stream non-blocking will produce a False return value,
    while anything else will raise an exception.

    @param stream the stream to unblock
    @param logger a logging.Logger for log messages
    @returns True on success, False otherwise."""
    call_fcntrl(os.O_NONBLOCK,0,logger)

def call_fcntrl(stream,on,off,logger=None):
    """!Internal function that implements unblock()
    @param stream the stream to modify
    @param on flags to turn on
    @param off flags to turn off
    @param logger a logging.Logger for messages
    @returns True on success, False otherwise."""
    try:
        if isinstance(stream,int):
            fd=stream
        else:
            fd=stream.fileno()
    except (AttributeError,EnvironmentError) as ee: 
        if logger is not None:
            logger.warning('%s: stream has no fileno, cannot switch to '
                           'non-blocking I/O: %s'%
                           (repr(stream),str(ee)),exc_info=True)
        return False
    
    try:
        flags=fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, (flags|on) & ~off)
        return True
    except EnvironmentError as ee:
        if logger is not None:
            logger.error('%s: cannot switch to non-blocking I/O: %s'%
                         (repr(stream),str(ee)),exc_info=True)
        return False

########################################################################
def fortlink(forts,force=False,basedir=None,logger=None):
    """!This is a convenience routine that makes many symbolic links to
    fort.N files for various integers N using make_symlink.  It works
    similarly to fortcopy.  The optional basedir is the relative
    directory.  The optional force argument is passed on to
    make_symlink and has the usual meaning: replace existing files.

    Call like this:
    @code
      fortlink({ 15:"/usr/local/share/file1",
                 23:"./file2"})
    @endcode

    And you will create these symbolic links:
    @code{.unformatted}
      ./fort.15 -> /usr/local/share/file1
      ./fort.23 -> ./file2
    @endcode

    as with other symlink routines in this module, set force=True to
    remove target fort.N files if they already exist.
    @param forts Mapping from Fortran unit number to link target.
    @param force Remove target files if they exist.
    @param basedir Where to make the links instead of the current directory.
    @param logger A logging.Logger for log messages."""
    if logger is not None:
        logger.debug('in fortlink, forts=%s force=%s basedir=%s logger=%s'%(
                repr(forts),repr(force),repr(basedir),repr(logger)))
    for (i,filename) in forts.items():
        assert(isinstance(filename,str))
        link='fort.%d'%(int(i),)
        if basedir is not None: link=os.path.join(basedir,where)
        make_symlink(filename,link,force=force,logger=logger)

def fortcopy(forts,basedir=None,logger=None,only_log_errors=False,**kwargs):
    """!A convenience function for copying files to local fort.N files
    for various integers N using deliver_file(...,keep=True).  It
    works similarly to fortlink.  The force= argument tells fortcopy
    to overwrite existing files.  Otherwise, an exception will be
    raised if the destination file already exists.  The optional
    basedir argument is the parent directory of the fort.N.

    Call like this:
    @code
      fortcopy({ 15:"/usr/local/share/file1",
                 23:"./file2"})
    @endcode

    And you will create files:
    @code{.unformatted}
      ./fort.15 (copied from /usr/local/share/file1)
      ./fort.23 (copied from ./file2)
    @endcode

    All other keyword arguments are sent to deliver_file.
    @param forts Mapping from Fortran unit number to copy target.
    @param basedir Where to put the files instead of the current directory.
    @param logger A logging.Logger for log messages.    
    @param only_log_errors Only log failed operations instead of logging everything.
    @param kwargs All other keyword arguments are passed to deliver_file()"""
    for (i,filename) in forts.items():
        newfile='fort.%d'%(int(i),)
        if basedir is not None: newfile=os.path.join(basedir,where)
        try:
            deliver_file(filename,newfile,logger=logger,**kwargs)
        except (EnvironmentError) as ee:
            if logger is not None:
                logger.warning('%s: fortcopy could not copy to %s: %s'
                               %(filename,newfile,str(ee)))
                if not only_log_errors:
                    raise
            else:
                # Cannot log errors, so ignore the only_log_errors flag
                raise

########################################################################
def norm_expand_path(path=None,fullnorm=False):
    """!Normalizes path and expand home directories.

    Calls os.path.normpath and os.path.expanduser on its argument, or
    on os.getcwd() if no argument is supplied (or if path=None).  This
    removes extraneous a/./b, a/../b, expands ~username and ~, and
    other system-specific expansions.  See the Python documentation of
    normpath and expanduser for details.  Will also call realpath and
    normcase if fullnorm=True.  Raises RelativePathError if the
    resulting path is not absolute.
    @param path the path to expand
    @param fullnorm If True, call os.path.normcase() and
      os.path.realpath() normapth and expanduser."""
    if path is None:
        path=os.getcwd()
    normpath=os.path.normpath(os.path.expanduser(path))
    if fullnorm:
        normpath=os.path.normcase(os.path.realpath(normpath))
    if not os.path.isabs(normpath):
        raise RelativePathError(
            '%s: path is relative, not absolute (expands to %s)'%
                (path,normpath))
    return normpath

def norm_abs_path(rel,fromdir=None):
    """!Return relative path.

    This routine generates relative file paths (using os.path.relpath)
    that are relative to the specified "from" directory fromdir.  The
    fromdir will be first sent through norm_expand_path to eliminate
    system-specific weirdness, such as a/./b, a/../b, ~username and so
    on.  This will raise RelativePathError if the resulting path is
    not absolute.
    @param rel the path 
    @param fromdir the directory from which we want the relative path"""
    return os.path.relpath(rel,norm_expand_path(fromdir))

########################################################################
def check_last_lines(filename,searchstr,lastbytes=10000,logger=None):
    """!Checks the last few bytes of a file to see if the specified
    search string is present.  Returns True if the string is present
    or False if the file existed but the string was not present.  Will
    raise an exception if the file is non-existent or cannot be read.

    @param filename The file to search (a string).
    @param searchstr The string to search for.  Must not contain 
        end-of-line chars.
    @param lastbytes The number of bytes at the end of the file to check.
        Can be larger than the file size.
    @param logger A logging.Logger for log messages.
    @returns True if the file contains the given string, False otherwise"""
    with open(str(filename),'rt') as f:
        try:
            f.seek(-lastbytes,os.SEEK_END)
        except EnvironmentError as e:
            if logger is not None:
                logger.info('%s: probably not an error: %s'
                            %(filename,str(e)))
        i=0
        for line in f:
            i+=1
            #print '%s: search line "%s" for "%s"'%(
            #               filename,line,searchstr)
            if line.find(searchstr)>=0:
                return True
        if logger is not None:
            logger.info('%s: read %d lines'%(filename,i))
        return False

########################################################################

def check_file(filename,min_size=None,min_mtime_age=None,
               min_atime_age=None,min_ctime_age=None,logger=None):
    """!Determines whether the specified file exists, and meets
    additional requirements.
    @param filename The file to analyze.
    @param min_size If present, the file must be at least this many bytes.
    @param min_mtime_age If specified, the file must have been modified
        more than this many seconds in the past.
    @param min_atime_age if specified, the file atime must be at least
        this many seconds old.  The meaning of atime varies, but
        usually means the last access time.
    @param min_ctime_age If specified, the file ctime must be at least
        this many seconds old.  The meaning of ctime varies between
        platforms and file types, but usually means the file creation
        or inode change time.  See stat(2) for details.
    @param logger a logging.Logger for log messages.
    @note This routine can also be used on directories, but one should avoid
    the min_size option when doing that.
    @returns True if requirements are met, False otherwise.    """
    try:
        s=os.stat(filename)
        if s.st_size<min_size: 
            if logger is not None:
                logger.info('%s: too small'%(filename,))
            return False
        if min_mtime_age is not None or min_atime_age is not None \
                or min_ctime_age is not None:
            now=int(time.time())
            if min_mtime_age is not None:
                if not now-s.st_mtime>min_mtime_age: 
                    if logger is not None:
                        logger.info('%s: not old enough (modification time)'
                                    %(filename,))
                    return False
            if min_atime_age is not None:
                if not now-s.st_atime>min_atime_age: 
                    if logger is not None:
                        logger.info('%s: not old enough (access time)'
                                    %(filename,))
                    return False
            if min_ctime_age is not None:
                if not now-s.st_ctime>min_ctime_age: 
                    if logger is not None:
                        logger.info('%s: not old enough (inode change time)'
                                    %(filename,))
                    return False
        if logger is not None:
            logger.info('%s: file meets requirements'%(filename,))
        return True
    except EnvironmentError as e:
        if e.errno==errno.ENOENT:
            if logger is not None:
                logger.info('%s: does not exist (ENOENT)'%(filename,))
            return False
        raise

class FileWaiter:
    """!A class that waits for files to meet some requirements."""
    def __init__(self,flist=None,min_size=None,
                 min_mtime_age=None,min_atime_age=None,
                 min_ctime_age=None,
                 min_fraction=1.0):
        """!Constructor for the FileWaiter.  Most arguments have the same
        meaning as check_file()
        @param flist the file or list of files to wait for.  This is simply
              sent into self.add.
        @param min_size minimum file size
        @param min_mtime_age minimum modification time age, 
        @param min_atime_age minimum access time age.
        @param min_ctime_age time since last file status change (see stat(2))
        @param min_fraction the minimum fraction of the provided files
            that must match the above requirements in order for
            FileWaiter.wait to return True. Default is 1.0, which
            means all of them."""
        self._flist=list()
        self._fset=set()
        self._found=set()
        self.min_size=min_size
        self.min_mtime_age=min_mtime_age
        self.min_atime_age=min_atime_age
        self.min_ctime_age=min_ctime_age
        self.min_fraction=float(min_fraction)
        if flist is not None: self.add(flist)
    ##@var min_size
    # The minimum file size

    ##@var min_mtime_age
    # Minimum age of the modification time

    ##@var min_atime_age
    # Minimum age of the access time

    ##@var min_ctime_age
    # Minimum age of the creation and/or inode access time

    ##@var min_fraction
    # The minimum fraction of files that must meet the requirements

    def add(self,flist):
        """!Adds a file, or iterable that iterates over files, to the
        list of files to wait for.  If the same filename is received a
        second time, it is ignored.
        @param flist a filename (string) or list of filenames"""
        if isinstance(flist,str):
            if flist in self._fset:
                return # already have this file
            self._flist.append(flist)
            self._fset.add(flist)
        else:
            for file in flist:
                self.add(file)
    def check(self,filename,logger=None):
        """!Checks to see if one file meets the requirements set in the
        constructor.  This default implementation calls check_file.
        This is in a separate member function so that a subclass can
        override the file checking method.  
        @returns True if the file is "ready," and False if it is not.
        @param filename the path to the file to check
        @param logger a logging.Logger for messages"""
        return check_file(filename,self.min_size,self.min_mtime_age,
                          self.min_atime_age,self.min_ctime_age,
                          logger=logger)
    def reset(self):
        """!Resets internal information about which files have been
        seen."""
        self._found=set()
        
    def iterfound(self):
        """!Iterates over all files that were found."""
        for filename in self._found: yield filename

    def countfound(self):
        """!Returns the number of files that were found."""
        return len(self._found)
    def countmissing(self):
        """!Returns the number of files that were NOT found."""
        return len(self._fset)-len(self._found)

    def checkfiles(self,maxwait=1800,sleeptime=20,logger=None,
                   log_each_file=True):
        """!Looks for the requested files.  Will loop, checking over
        and over up to maxwait seconds, sleeping sleeptime seconds
        between checks.
        @param maxwait maximum seconds to wait
        @param sleeptime sleep time in seconds between checks
        @param logger a logging.Logger for messages
        @param log_each_file log messages about each file checked"""
        maxwait=int(maxwait)
        start=int(time.time())
        now=start
        first=True
        if log_each_file:
            flogger=logger
        else:
            flogger=None
        while None is None:
            if len(self._fset)<=0: 
                if logger is not None:
                    logger.info('No files to check.')
                return True

            left=len(self._fset)-len(self._found)
            now=int(time.time())
            nfiles=len(self._fset)
            nfound=len(self._found)
            frac=float(nfound)/nfiles
            needfiles=math.ceil(self.min_fraction*nfiles)

            if frac>=self.min_fraction-1e-5: 
                logger.info('Have required fraction of files.')
                return True
            if now-start>=maxwait: 
                logger.info('Waited too long.  Giving up.')
                return False
            
            if not first:
                sleepnow=max(0,min(sleeptime,start+maxwait-now-1))
                if sleepnow<1e-3:
                    logger.info('Waited too long.  Giving up.')
                    return False
                if logger is not None:
                    logger.info('Still need files: have %d of %d, '
                                'but need %g%% of them (%g file%s).'
                                %(len(self._found),len(self._fset),
                                  self.min_fraction*100.0,needfiles,
                                  's' if (needfiles>1) else ''))
                    logfun=logger.info if (sleepnow>=5) else logger.debug
                    logfun('Sleeping %g seconds...'%(float(sleepnow),))
                time.sleep(sleepnow)
                if logger is not None:
                    logfun('Done sleeping.')

            first=False

            for filename in self._flist:
                if filename in self._found: continue
                if self.check(filename,logger=flogger):
                    self._found.add(filename)
                    if flogger is not None:
                        flogger.info('%s: found this one (%d of %d found).'
                                    %(filename,len(self._found),
                                      len(self._fset)))
                
        return len(self._found)>=len(self._fset)

def wait_for_files(flist,logger=None,maxwait=1800,sleeptime=20,
                   min_size=1,min_mtime_age=30,min_atime_age=None,
                   min_ctime_age=None,min_fraction=1.0,
                   log_each_file=True):
    """!Waits for files to meet requirements.  This is a simple
    wrapper around the FileWaiter class for convenience.  It is
    equivalent to creating a FileWaiter with the provided arguments,
    and calling its checkfiles routine.
        @param flist the file or list of files to wait for.  This is simply
              sent into self.add.
        @param logger a logging.Logger for messages
        @param maxwait maximum seconds to wait
        @param sleeptime sleep time in seconds between checks
        @param min_size minimum file size
        @param min_mtime_age minimum modification time age, 
        @param min_atime_age minimum access time age.
        @param min_ctime_age time since last file status change (see stat(2))
        @param min_fraction the minimum fraction of the provided files
            that must match the above requirements in order for
            FileWaiter.wait to return True. Default is 1.0, which
            means all of them.
        @param log_each_file log messages about each file checked  """
    waiter=FileWaiter(flist,min_size,min_mtime_age,min_atime_age,
                      min_ctime_age,min_fraction)
    return waiter.checkfiles(maxwait,sleeptime,logger,log_each_file)
