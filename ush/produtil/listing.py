"""!Contains the Listing class, which emulates "ls -l"."""

##@var __all__
# Symbols exported by "from produtil.listing import *"
__all__=['Listing']

import os,stat,StringIO,grp,pwd,time

class Listing(object):
    """!Imitates the shell "ls -l" program.

    Imitate ls -l, but with a longer mtime string:
    @code
       print Listing("/usr/local")
    @endcode

    To include files whose names begin with "."  add hidden=True:
    @code
       print Listing("/usr/local",hidden=True)
    @endcode

    To log messages related to failures of lstat and readlink, pass 
    a logging.Logger:
    @code
       print Listing("/usr/local",hidden=True,logger=logger)
    @endcode"""
    def __init__(self,path=".",hidden=False,logger=None):
        """!Constructor for Listing:
        @param path The directory path to list.
        @param hidden If True, files with names beginning with "." are listed.
        @param logger A logging.Logger for error messages."""
        self.__path=path
        self.__contents=dict()
        self.list(hidden=bool(hidden),logger=logger)
    def __iter__(self):
        """!Iterates over filenames in the listed directory."""
        for name in self.contents.iterkeys():
            yield name
    def iteritems(self):
        """!Iterates over name,data pairs in the listed directory.  The
        "data" will be a tuple containing the output of lstat and the
        output of readlink."""
        for (name,data) in self.contents.iteritems():
            yield name,data
    def iterkeys(self):
        """!Iterates over filenames in the listed directory."""
        for name in self.contents.iterkeys():
            yield name

    def list(self,hidden=False,logger=None):
        """!Updates the internal data structures with a new listing of
        the directory.  Arguments are the same as for the constructor.
        @param hidden If True, files with names beginning with "." are listed.
        @param logger A logging.Logger for error messages."""
        hidden=bool(hidden)
        path=self.__path
        listing=os.listdir(path)
        contents=dict()
        for item in listing:
            if item[0]=='.' and not hidden: 
                # Skip "hidden" files.
                continue
            loc=os.path.join(path,item)
            try:
                lstat=os.lstat(loc)
            except EnvironmentError as e:
                if logger is not None:
                    logger.info(
                        "%s: cannot lstat: %s"%(loc,str(e)),exc_info=True)
                continue
            if not stat.S_ISLNK(lstat.st_mode):
                contents[item]=(lstat,None)
                continue
            try:
                linkpath=os.readlink(loc)
            except EnvironmentError as e:
                if logger is not None:
                    logger.info(
                        "%s: cannot readlink: %s"%(loc,str(e)),exc_info=True)
                contents[item]=(lstat,"(**UNKNOWN**)")
                continue
            contents[item]=(lstat,linkpath)
        self.__contents=contents
    def __str__(self):
        """!Generates an ls -l style listing of the directory."""
        c=self.__contents
        sizes=[0,0,0,0,0,0]
        rows=list()
        for (name,item) in c.iteritems():
            row=self._stritem(name,item)
            for col in xrange(len(row)-1):
                sizes[col]=max(sizes[col],len(row[col]))
            rows.append(row)
        format=' %%%ds'*6+' %%s\n'
        format=format[1:]
        format=format%tuple(sizes)

        s=StringIO.StringIO()
        for row in rows:
            s.write(format%row)
        st=s.getvalue()
        s.close()
        return st
    def _stritem(self,name,item):
        """!This is an internal implementation function.  Do not call
        it directly.  It generates one line of ls output as a tuple of
        strings, one string per column of information (the mtime is
        one column).  The __str__ turns the lines into one big string.
        @param name the filename
        @param item details about the file
        @returns data for each column of the listing"""
        lstat=item[0]
        linkpath=item[1]
        if linkpath is None: linkpath='(**UNKNOWN**)'
        mode=lstat.st_mode

        s=''

        # file type character
        if   stat.S_ISDIR(mode):  s+='d'
        elif stat.S_ISCHR(mode):  s+='c'
        elif stat.S_ISBLK(mode):  s+='b'
        elif stat.S_ISFIFO(mode): s+='p'
        elif stat.S_ISLNK(mode):  s+='l'
        elif stat.S_ISSOCK(mode): s+='s'
        else:                     s+='-'

        # User permissions
        s+=('r' if mode&stat.S_IRUSR else '-')
        s+=('w' if mode&stat.S_IWUSR else '-')
        if mode&stat.S_IXUSR:
            if mode&stat.S_ISUID:
                s+='s'
            else:
                s+='x'
        elif mode&stat.S_ISUID:
            s+='S'
        else:
            s+='-'

        # Group permissions
        s+=('r' if mode&stat.S_IRGRP else '-')
        s+=('w' if mode&stat.S_IWGRP else '-')
        if mode&stat.S_IXGRP:
            if mode&stat.S_ISGID:
                s+='s'
            else:
                s+='x'
        elif mode&stat.S_ISGID:
            s+='S'
        else:
            s+='-'


        # Other permissions
        s+=('r' if mode&stat.S_IROTH else '-')
        s+=('w' if mode&stat.S_IWOTH else '-')
        if mode&stat.S_IXOTH:
            if mode&stat.S_ISVTX:
                s+='t'
            else:
                s+='x'
        elif mode&stat.S_ISVTX:
            s+='T'
        else:
            s+='-'

        nlink=str(int(lstat.st_nlink))
        username=self._username(lstat.st_uid)
        groupname=self._groupname(lstat.st_gid)
        size=str(int(lstat.st_size))
        when=time.asctime(time.localtime(lstat.st_mtime))
        if stat.S_ISLNK(lstat.st_mode):
            return (s,nlink,username,groupname,size,when,name+' -> '+linkpath)
        else:
            return (s,nlink,username,groupname,size,when,name)


    def _groupname(self,gid):
        """!Return the group name for a group ID from getgrgid."""
        try:
            gr=grp.getgrgid(gid)
            return str(gr.gr_name)
        except (KeyError,ValueError,EnvironmentError):
            return str(gid)

    def _username(self,uid):
        """!Return the user name for a group ID from getpwuid."""
        try:
            pw=pwd.getpwuid(uid)
            return str(pw.pw_name)
        except (KeyError,ValueError,EnvironmentError):
            return str(uid)
