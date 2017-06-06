"""!Handles data restriction classes.

Implements access control mechanisms for NOAA data.  Although this was
written for the NOAA Restricted Data (rstprod), it can be used for
general access control.  It is also more general than NOAA, so long as
one correctly initializes the produtil.cluster module.  The mechanism
used depends on the cluster, due to varying capabilities throughout.
Some do not implement access control mechanisms that are usable for
the restricted data (such as NOAA Jet).  For those systems,
RstNoAccessControl is raised if one attempts to restrict a file."""

##@var __all__ 
# List of symbols exported by "from produtil.rstprod import *"
__all__= [ 'RestrictionClass', 'tag_rstprod', 'rstprod_tagger', 
           'make_rstprod_tagger' ]

class RstprodError(Exception):
    """!The base class of all exceptions specific to the rstprod module"""
class RstNoAccessControl(RstprodError):
    """!Raised when the cluster has no access control mechanisms."""
class RstBadGroup(RstprodError):
    """!Raised when a group's id or name could not be determined."""

import os, stat, grp
import produtil.cluster, produtil.acl

from produtil.acl import ACL, ACL_TYPE_ACCESS, ACL_TYPE_DEFAULT

##@var okay_mode
# File permission bits (from the stat module) that are allowed to be
# set on restricted access data.  When Access Control List (ACL) based
# access control is used, the group bits refer to the rstprod's
# permissions in the ACL, rather than the owning group.
okay_mode = stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR | \
            stat.S_IRGRP|stat.S_IWGRP|stat.S_IXGRP

def acl_text_for_rstclass(groupname,mode):
    """!Generates the access control list for the specified restriction
    class (groupname) and nine bit access permissions (mode).
    @param groupname the restricted file unix group
    @param mode required access mode (world access will be removed even
       if it is present in mode)"""
    if not isinstance(mode,int):
        raise TypeError(
            'In acl_text_for_rstclass, the mode must be the integer access mode, not a %s %s'
            %(type(groupname).__name__,repr(groupname)))
    imode=int(mode)&0770
    if not isinstance(groupname,basestring):
        raise TypeError(
            'In acl_text_for_rstclass, the groupname must be the string name of a unix group, not a %s %s'
            %(type(groupname).__name__,repr(groupname)))
    return "u::%c%c%c,g::---,g:%s:%c%c%c,o::---,m::rwx" % (
        ( 'r' if 0!=imode&stat.S_IRUSR else '-' ),
        ( 'w' if 0!=imode&stat.S_IWUSR else '-' ),
        ( 'x' if 0!=imode&stat.S_IXUSR else '-' ),
        groupname,
        ( 'r' if 0!=imode&stat.S_IRGRP else '-' ),
        ( 'w' if 0!=imode&stat.S_IWGRP else '-' ),
        ( 'x' if 0!=imode&stat.S_IXGRP else '-' ) )

class RestrictionClass(object):
    """!This is a python class intended to be used to automate
    restricting data to a specific restriction class using access
    control lists or group ownership

    Example:
    @code
      rc=RestrictionClass("rstprod")
      rc.restrict_file("/path/to/some/dangerous/file")
    @endcode

    It can also set the Default Access Control List if supplied a directory:
    @code
      rc.restrict_file("/path/to/some/dangerous/directory/")
    @endcode"""
    def __init__(self,group,use_acl=None,logger=None):
        """!Create a new RestrictionClass object for the specified
        group.  
        @param group The group may be the string group name, or the numeric
        group id.  
        @param use_acl If use_acl is unspecified, then
        produtil.cluster.use_acl_for_rstdata() is used to decide.
        @param logger a logging.Logger for log messages"""
        assert(use_acl is None)
        if use_acl is None:
            # We are being asked to automatically decide what type of
            # access control mechanism to use.
            if produtil.cluster.no_access_control():
                raise RstNoAccessControl(
                    "This cluster cannot be used for NOAA restricted data.  It "
                    "uses group quotas, so I cannot control access through "
                    "group IDs.  It does not have a functional access control "
                    "list (ACL) mechanism, so I cannot use ACLs.")
            use_acl=produtil.cluster.use_acl_for_rstdata()
        self.__use_acl=bool(use_acl)
        if isinstance(group,basestring):
            self.__groupname=group
            try:
                grent=grp.getgrnam(group)
                self.__groupid=grent[2]
            except (EnvironmentError,KeyError) as e:
                raise RstBadGroup('%s: could not get group id for group: %s'
                                  %(group,str(e)))
            if not isinstance(self.__groupid,int):
                raise RstBadGroup(
                    '%s: could not get group id for group.  The grp.getgrnam'
                    '(...)[2] returned something that was not an int: a %s %s'
                    %(group,type(self.__groupid).__name__,repr(self.__groupid)))
        elif isinstance(group,int):
            try:
                grent=grp.getgrgid(group)
                self.__groupname=grent[0]
                self.__groupid=group
            except (EnvironmentError,KeyError) as e:
                raise RstBadGroup('%s: could not get group id for group: %s'
                                  %(group,str(e)))
            if not isinstance(self.__groupname,basestring):
                raise RstBadGroup(
                    '%d: could not get group name for group.  The grp.getgrgid'
                    '(...)[0] returned something that was not an int: a %s %s'
                    %(group,type(self.__groupid).__name__,
                      repr(self.__groupid)))

        else:
            raise TypeError(
                "In produtil.rstprod.RestrictionClass.__init__, the group parameter must be the string group name or integer group id.  You provided a %s %s"
                %(type(group).__name__,repr(group)))
        self.__allowed=stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR | \
                       stat.S_IRGRP|stat.S_IWGRP|stat.S_IXGRP
        if use_acl:
            self.__acls=self.make_acl_dict()
    def make_acl_dict(self):
        """!Internal function that generates the ACL dictionary.

        @protected
        This is part of the internal implementation of
        RestrictionClass and should not be used directly.  It returns
        a dict() that maps from integer permission to an ACL object
        that will set an access control list appropriate for that
        permission.  The user and restriction group will match the old
        user and group permissions, but other groups will have no
        permissions, and the "world" permissions will be 0."""
        acls=dict()
        mode=010
        for IRUSR in ( 0, stat.S_IRUSR ):
            for IWUSR in ( 0, stat.S_IWUSR ):
                for IXUSR in ( 0, stat.S_IXUSR ):
                    for IRGRP in ( 0, stat.S_IRGRP ):
                        for IWGRP in ( 0, stat.S_IWGRP ):
                            for IXGRP in ( 0, stat.S_IXGRP ):
                                mode=IRUSR|IWUSR|IXUSR|IRGRP|IWGRP|IXGRP
                                txt=acl_text_for_rstclass(self.groupname,mode)
                                acl=ACL()
                                acl.from_text(txt)
                                acls[mode]=acl
        return acls
    @property
    def groupname(self):
        """!The name of the group used for the restriction class"""
        return self.__groupname
    @property
    def groupid(self):
        """!The numeric ID of the group used for the restriction class"""
        return self.__groupid
    @property
    def use_acl(self):
        """!True if ACLs are used for access permission, False if
        setgid and chgrp are used."""
        return self.__use_acl

    def acl_for(self,st_mode):
        """!Returns an produtil.acl.ACL object for the specified access
        mode.  Will raise an exception if self.use_acl is False.
        @param st_mode desired access mode"""
        imode = stat.S_IMODE(st_mode)
        amode = imode & self.__allowed # limit to allowed permissions
        return self.__acls[amode]

    def chgrp_restrict(self,target,st_mode,chown,chmod,logger):
        """!Internal function that uses chgrp to restrict a file's access.

        This is an internal implementation function that should not be
        called directly.  It handles the non-ACL (chgrp+setgid) case
        of restrict_file and restrict_gid.
        @param target the target file
        @param st_mode the desired mode
        @param chown chowning function
        @param chmod chmodding function
        @param logger a logging.Logger for log messages
        @protected """
        if logger is not None: 
            logger.info('%s: chgrp to %s'%(str(target),self.__groupname))
        chown(target,-1,self.__groupid)
        if stat.S_ISDIR(st_mode):
            smode = stat.S_ISGID | (stat.S_IMODE(st_mode)&okay_mode)
            if logger is not None:
                logger.info('%s: set mode on directory to 0%o'
                            %(str(target),smode))
            chmod( target, smode )
        else:
            smode = stat.S_IMODE(st_mode)&okay_mode
            if logger is not None:
                logger.info('%s: set mode on file to 0%o'%(str(target),smode))
            chmod( target, smode )

    def acl_restrict_file(self,target,st_mode,set_acl,logger):
        """!Internal function that restricts files using ACLs

        This is an internal implementation function that should not be
        called directly.  It handles the ACL case of restrict_file.
        @protected
        @param target the target file
        @param st_mode the desired access
        @param set_acl the acl-setting function
        @param logger a logging.Logger for log messages        """
        if stat.S_ISDIR(st_mode):
            if logger is not None:
                logger.info('%s: use acl to restrict dir to group %s'
                            %(str(target),self.groupname))
            set_acl(target,ACL_TYPE_ACCESS)
            set_acl(target,ACL_TYPE_DEFAULT)
        else:
            if logger is not None:
                logger.info('%s: use acl to restrict file to group %s'
                            %(str(target),self.groupname))
            set_acl(target,ACL_TYPE_ACCESS)

    def restrict_file(self,filename,st_mode=None,logger=None):
        """!Adds the requested restrictions to the specified file or
        directory.  This routine needs to stat the opened file to get
        the stat.st_mode.  
        @param st_mode To avoid a stat call, send st_mode into the
        optional argument.
        @param filename the target file
        @param logger a logging.Logger for log messages"""
        if st_mode is None:
            if logger is not None:
                logger.info(filename+': stat file')
            s=os.stat(filename)
            st_mode=s.st_mode
        if self.__use_acl:
            acl=self.acl_for(stat.S_IMODE(st_mode))
            self.acl_restrict_file(filename,st_mode,acl.to_file,logger)
        else:
            self.chgrp_restrict(filename,st_mode,os.chown,os.chmod,logger)

    def restrict_fd(self,fd,st_mode=None,logger=None):
        """Adds the requested restrictions to an opened file.  This
        routine needs to stat the opened file to get the stat.st_mode.
        @param st_mode To avoid a stat call, send st_mode into the optional argument.
        @param fd the target file descriptor
        @param logger a logging.Logger for log messages"""
        if hasattr(fd,'fileno'): 
            fd=fd.fileno()
        if st_mode is None:
            if logger is not None:
                logger.info(str(fd)+': stat fileno')
            s=os.fstat(fd)
            st_mode=s.st_mode
        if self.__use_acl:
            acl=self.acl_for(stat.S_IMODE(st_mode))
            if logger is not None:
                logger.info('%s: set acl of fileno to restrict to group %s'
                            %(str(fd),self.__groupname))
            acl.to_fd(fd)
        else:
            self.chgrp_restrict(fd,st_mode,os.fchown,os.fchmod,logger)

##@var rstprod_tagger
#The RestrictionClass object used for tag_rstprod.  Create this with
#make_rstprod_tagger
rstprod_tagger=None

def make_rstprod_tagger(group='rstprod',use_acl=None,logger=None):
    """!Creates the rstprod_tagger object for use by tag_rstprod"""
    global rstprod_tagger
    rstprod_tagger=RestrictionClass(group,use_acl,logger)

def tag_rstprod(target,logger=None):
    """!Places a file or directory under the rstprod restriction class.
    This command will attempt to raise RstprodForbidden if it is run
    on a cluster that is not supposed to have rstprod data (only
    GAEA, Zeus and WCOSS are allowed).  

    This routine uses the approved rstprod protection mechanisms on
    each cluster:

    *  Zeus --- place the file in the rstprod access control list, and
             make it unreadable to anyone else.
      
    *  WCOSS --- place the file in group rstprod and remove permissions
              for others.

    *  GAEA --- same as WCOSS

    Note that the NOAA Jet cluster is not allowed to contain
    restricted data, so this routine will raise RstprodForbidden on
    that cluster."""
    if rstprod_tagger is None:
        make_rstprod_tagger(logger=logger)
    if isinstance(target,basestring):
        rstprod_tagger.restrict_file(target,logger=logger)
    elif isinstance(target,file) or isinstance(target,int):
        rstprod_tagger.restrict_fd(target,logger=logger)
    else:
        raise TypeError('The tag_rstprod target argument must be an int, a file '
                        'or a basestring.  You supplied a %s %s'
                        %(type(target).__name__,repr(target)))
        
