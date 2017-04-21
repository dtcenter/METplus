"""!Manipulates Access Control Lists (ACL)

This module is a wrapper around the C libacl library, which provides
support for POSIX Access Control Lists, as defined by the abandoned
draft standard "IEEE 1003.1e draft 17".  Only the widely-supported
features are implemented.  It is intended to be used with the Linux
libacl, but might be portable to other versions if the module-scope
acl_library variable is changed to the name of your "dll" or "so" file
for libacl and values of ACL_TYPE_ACCESS and ACL_TYPE_DEFAULT are
changed.  In addition, one must change the means by which errno is
accessed if switching from glibc to another C library."""

import ctypes, os, stat

class ACLError(EnvironmentError):
    """!Superclass of any ACL errors"""
    def __init__(self,message,errno):
        """!ACLError constructor
        @param message the description of the error
        @param errno the system errno from the error"""
        super(ACLError,self).__init__(message)
        self.errno=errno
    ##@var errno
    # The errno value when the error happened.

class ACLLibraryError(ACLError):
    """!Raised when the libacl library could not be loaded."""
class ACLMissingError(ACLError):
    """!Raised when a function that requires an ACL object received
    None, or an invalid ACL."""
class ACLCannotStringify(ACLError):
    """!Raised when libacl cannot convert an ACL to text."""
class ACLCannotGet(ACLError):
    """!Raised when the libacl library could not get a file's ACL."""
class ACLCannotSet(ACLError):
    """!Raised when the libacl library could not set a file's ACL."""

##@var  libacl
# The loaded libacl library from ctypes.cdll.LoadLibrary.
libacl=None

##@var libc
# The loaded libc library from ctypes.cdll.LoadLibrary.
libc=None

##@var ACL_TYPE_ACCESS
# The ACL_TYPE for Access Control Lists, defined in the libacl header
# files.  This must match the value in the header.
ACL_TYPE_ACCESS=32768

##@var ACL_TYPE_DEFAULT
# The ACL_TYPE for Default Access Control Lists defined in the libacl
# header files.  This must match the value in the header.
ACL_TYPE_DEFAULT=16384

##@var acl_library
# The ACL library name or path for input to ctypes.cdll.LoadLibrary.
# This is intended to be modified externally from this module if needed
# before using the produtil.acl module.
acl_library='libacl.so.1'

##@var c_library
# The C library name for input to ctypes.cdll.LoadLibrary.  This is
# intended to be modified externally from this module if needed before
# using the produtil.acl module.
c_library='libc.so.6'

##@var get_errno
# Function that returns the value of errno.  Used for testing for
# errors in libacl routines.
get_errno=None

########################################################################
# Library loading routine:

def load_libc():
    """!Loads the libc library.

    Loads the standard C library, which is needed to test the value of
    errno in order to report errors.  This function is called
    automatically when needed; you should never need to call it
    directly."""
    global libc,get_errno
    try:
        libc=ctypes.cdll.LoadLibrary(c_library)
        get_errno_loc = libc.__errno_location
        get_errno_loc.restype = ctypes.POINTER(ctypes.c_int)
    except EnvironmentError as e:
        raise ACLLibraryError('Cannot load libc: '+str(e),e.errno)
    if libc is None:
        raise ACLLibraryError(
            'Cannot find libc.  The ctypes.cdll.LoadLibrary(%s) returned None.'
            %(repr(c_library),))

    get_errno=lambda: get_errno_loc()[0]

def load_libacl():
    """!Loads the libacl library.

    Loads the libacl library whose name is specified in the module
    scope acl_library variable.  This function is called automatically
    when needed; you should never need to call it directly."""
    global libacl, libc
    if libc is None:
        load_libc()
    # Load the library:
    try:
        libacl=ctypes.cdll.LoadLibrary(acl_library)
    except EnvironmentError as e:
        raise ACLLibraryError('Cannot load libacl: '+str(e),e.errno)
    if libacl is None:
        raise ACLLibraryError('Cannot find libacl.  The ctypes.cdll.LoadLibrary(%s) returned None.'%(repr(acl_library),))

    # Set the function prototypes:
    libacl.acl_get_fd.argtypes=[ ctypes.c_int ]
    libacl.acl_get_fd.restype=ctypes.c_void_p

    libacl.acl_get_file.argtypes=[ ctypes.c_char_p, ctypes.c_int ]
    libacl.acl_get_file.restype=ctypes.c_void_p

    libacl.acl_from_text.argtypes=[ ctypes.c_char_p ]
    libacl.acl_from_text.restype=ctypes.c_void_p

    libacl.acl_to_text.argtypes=[ ctypes.c_int, ctypes.c_void_p ]
    libacl.acl_to_text.restype=ctypes.c_char_p

    libacl.acl_set_fd.argtypes=[ ctypes.c_int, ctypes.c_void_p ]
    libacl.acl_set_fd.restype=ctypes.c_int

    libacl.acl_set_file.argtypes=[ ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p ]
    libacl.acl_set_file.restype=ctypes.c_int

    libacl.acl_free.argtypes=[ ctypes.c_void_p ]
    libacl.acl_free.restype=ctypes.c_int

########################################################################
# ACL class wrapped around the libacl library:

class ACL(object):
    """!Inquire and manipulate access control lists (ACLs).

    Represents a POSIX Access Control List (ACL).  This is a wrapper
    around the libacl library, and implements only widely-supported
    ACL features.  Data is stored internally in C structures, which
    are allocated and freed automatically as needed."""
    def __init__(self):    
        """!Create a blank, invalid, ACL.  You should use the various
        from_* routines to fill it with valid data."""
        if libacl is None: load_libacl()
        self.__libacl=libacl # to ensure libacl is not freed before the ACL
        self.__acl=None
    def __del__(self): 
        """!Free the memory used by the ACL in libacl."""
        self.free()
    def free(self):
        """!Frees resources used by the libacl library to store this
        ACL's underlying C structures."""
        if self.__acl is not None and self.__acl!=0:
            # We use self.__libacl here because we know it has not
            # been freed.
            self.__libacl.acl_free(self.__acl)
        self.__acl=None
        return self
    def have_acl(self):
        """!Returns True if this ACL has data, and False otherwise."""
        return self.__acl is not None and self.__acl!=0
    def from_text(self,acl):
        """!Attempts to convert the given string to an ACL, storing the
        result in this object.  Any prior ACL information in this
        object will be freed.
        @param acl the access control list description"""
        if self.__acl is not None: self.free()
        sacl=str(acl)
        cacl=ctypes.c_char_p(sacl)
        self.__acl=self.__libacl.acl_from_text(cacl)
        errno=get_errno()
        if self.__acl is None or self.__acl==0:
            self.__acl=None
            shortacl=sacl
            if len(sacl)>20:
                shortacl=sacl[0:17]+'...'
            raise ACLCannotGet('Cannot convert to acl: %s.  String: %s'
                               %(os.strerror(errno),repr(shortacl)),errno)
        return self
    def from_file(self,filename,which=ACL_TYPE_ACCESS):
        """!Copies the files's ACL into this object.  

        Specify which type of access control list via the second
        argument: ACL_TYPE_ACCESS or ACL_TYPE_DEFAULT.  Any prior ACL
        information in this object will be freed.
        @param filename the name of the file whose ACL is desired
        @param which which access control list is desired;
        ACL_TYPE_ACCESS or ACL_TYPE_DEFAULT.
        @returns self"""
        if self.__acl is not None: self.free()
        sfilename=str(filename)
        cfilename=ctypes.c_char_p(sfilename)
        self.__acl=self.__libacl.acl_get_file(filename,which)
        errno=get_errno()
        if self.__acl is None or self.__acl==0:
            self.__acl=None
            raise ACLCannotGet('%s: cannot get acl: %s'
                               %(sfilename,os.strerror(errno)),errno)
        return self
    def from_fd(self,fd):
        """!Get an access control list from a file descriptor.

        Obtains an Access Control List from the specified file object
        or file descriptor number.  You can also pass any object that
        has a "fileno()" member function.  Any prior ACL information
        in this object will be freed.
        @param fd an integer file descriptor or a file object.
        @returns self"""
        if hasattr(fd,'fileno'): fd=fd.fileno()
        ifd=int(fd)
        cfd=ctypes.c_int(ifd)
        self.__acl=self.__libacl.acl_get_fd(cfd)
        errno=get_errno()
        if self.__acl is None or self.__acl==0:
            self.__acl=None
            raise ACLCannotGet('file descriptor %d: cannot get acl: %s'
                               %(ifd,os.strerror(errno)),errno)
        return self
    def to_fd(self,fd):
        """!Updates a file's file descriptor.

        Sets the ACL for the specified file descriptor to the ACL
        stored in this object.  Raises ACLMissingError if this object
        has no ACL information.
        @param fd an integer file descriptor or open file object"""
        if self.__acl is None or self.__acl==0:
            raise ACLMissingError(
                "to_fd: caller tried to set a file descriptor's ACL to an invalid ACL: %s"
                %(os.strerror(errno),),errno)
        if hasattr(fd,'fileno'):
            fd=fd.fileno()
        ifd=int(fd)
        cfd=ctypes.c_int(ifd)
        r=self.__libacl.acl_set_fd(cfd,self.__acl)
        errno=get_errno()
        if r is not None and r!=0:
            raise ACLCannotSet('file descriptor %d: cannot set acl: %s'
                               %(ifd,os.strerror(errno)),errno)
        return self
    def to_file(self,filename,access=ACL_TYPE_ACCESS):
        """!Updates a file's access control list.

        Sets the ACL for the specified file to the ACL stored in this
        object.  Specify access=ACL_TYPE_DEFAULT to obtain the default
        access control list (Default ACL) or ACL_TYPE_ACCESS for the
        access control list.  Raises ACLMissingError if this object
        has no ACL information.

        @param filename the name of the file whose ACL is to be updated
        @param access ACL_TYPE_ACCESS or ACL_TYPE_DEFAULT"""
        if self.__acl is None or self.__acl==0:
            raise ACLMissingError(
                "Tried to set a file's ACL, while providing an invalid ACL.",
                errno)
        sfn=str(filename)
        cfn=ctypes.c_char_p(sfn)
        r=self.__libacl.acl_set_file(cfn,access,self.__acl)
        errno=get_errno()
        if r is not None and r!=0:
            raise ACLCannotSet('%s: cannot set acl: %s'
                               %(sfn,os.strerror(errno)),errno)
        return self
    def to_text(self):
        """!Converts an ACL to text.

        Returns a string representation of this ACL from acl_to_text.
        Returns the empty string ('') if this ACL has no data."""
        if self.__acl is None or self.__acl==0: return ''
        size=ctypes.c_ulonglong(0)
        textified=self.__libacl.acl_to_text(self.__acl,ctypes.byref(size))
        errno=get_errno()
        if textified==0 or textified is None:
            raise ACLCannotStringify(
                'Cannot convert ACL to a string: acl_to_text returned NULL: %s'
                %(os.strerror(errno),), errno)
        if size<=0:
            raise ACLCannotStringify(
                ('Cannot convert ACL to a string: acl_to_text size was %d'
                 ' (but return value was non-NULL): %s')
                %(int(size),os.strerror(errno)), errno)
        retstr=ctypes.string_at(textified)
        self.__libacl.acl_free(textified)
        return retstr

    def __str__(self):
        """! => self.to_text() """
        return self.to_text()

########################################################################
# Pythonic wrapper functions that mimic the C routines:

def acl_to_text(acl):
    """!Returns a string representation of the given access control
    list object.
    @param acl an ACL object
    @returns the string equivalent"""
    return acl.to_text()

def acl_get_file(filename,access=ACL_TYPE_ACCESS):
    """!Returns an object that represents the access control list for
    the specified file.
    @param filename the name of the file of interest
    @param access ACL_TYPE_ACCESS or ACL_TYPE_DEFAULT
    @return a new ACL"""
    return ACL().from_file(filename,access)

def acl_get_fd(fd):
    """!Returns an object that represents the access control list for
    an open file descriptor.
    @param fd the integer file descriptor or open file object
    @returns a new ACL object"""
    return ACL().from_fd(fd)

def acl_set_file(filename,acl,access=ACL_TYPE_ACCESS):
    """!Sets the named file's access control list.
    @param filename the name of the file of interest
    @param acl the destination ACL object
    @param access ACL_TYPE_ACCESS or ACL_TYPE_DEFAULT
    @returns acl"""
    return acl.to_file(filename)

def acl_set_fd(fd,acl):
    """!Given an open file descriptor, sets the corresponding file's
    access control list.
    @param fd the file descriptor or file object
    @param acl the ACL object to change
    @returns acl"""
    return acl.to_fd(fd)

def acl_from_text(txt):
    """!Converts text to an access control list.
    @param txt a text access control list
    @returns a new ACL object"""
    return ACL().from_text(txt)

########################################################################
# Simplified wrappers that perform common tasks:

def copy_acl_fd(fromfd,tofd):
    """!Copy an access control list from one object to another

    Copies a POSIX Access Control List (ACL) from one open file to
    another.  The arguments should be either UNIX file descriptors, or
    the return values from open().  This routine is quicker than using
    the ACL() object due to avoidance of creating unnecessary Python
    objects.  However, the access control list information is
    discarded in this routine, so it can only be used when the sole
    need is to copy the information from one file to another.
    @param fromfd the source file descriptor
    @param tofd the target file descriptor"""
    if hasattr(fromfd,'fileno'): fromfd=fromfd.fileno()
    if hasattr(tofd,'fileno'): tofd=tofd.fileno()
    if libacl is None: load_libacl()
    acl=None
    try:
        cfrom=ctypes.c_int(int(fromfd))
        cdto=ctypes.c_int(int(tofd))
        acl=libacl.acl_get_fd(cfrom)
        errno=get_errno()
        if acl is None or acl==0:
            raise ACLCannotGet(
                'Cannot read acl from descriptor %s: acl_get_fd returned NULL: %s'
                %(repr(fromfd),os.strerror(errno)), errno)
        res=libacl.acl_set_fd(cto,acl)
        errno=get_errno()
        if res is None or res!=0:
            raise ACLCannotSet('Cannot set acl to descriptor %s: %s'
                               %(repr(getfd),os.strerror(errno)),  errno)
    finally:
        if acl is not None and acl!=0:
            libacl.acl_free(acl)
            acl=None
