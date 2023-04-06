"""!Provides information about the cluster on which this job is running.""" 
"""Remove and clean WCOSS Cray and WCOSS Dell_p3 related logic and updating
prodcution machine identifying logic for WCOSS2 (Biju Thomas 10/12/2022)"""

##@var __all__
#List of symbols exported by "from produtil.cluster import *"
__all__=['Cluster','where','longname','name','group_quotas','acl_support',
         'no_access_control','use_acl_for_rstdata','ncepprod',
         'MSUOrion','NOAAJet','NOAAGAEA','NOAAHera','NOAAWCOSS']

import time, socket, os, re

##@var DO_NOT_SET
# Special values for parameters that should not be set.
DO_NOT_SET=object()

class Cluster(object):
    """!Stores information about a computer cluster.  """
    def __init__(self,group_quotas,acl_support,production,name,longname,
                 use_acl_for_rstdata=None):
        """!Sets all public member variables.  All are mandatory except
        use_acl_for_rstdata.  The default for use_acl_for_rstdata is
        the logical AND of group_quotas and acl_support."""
        self.group_quotas=bool(group_quotas)
        self.acl_support=bool(acl_support)
        if production is not DO_NOT_SET:
            self.production=bool(production)
        self.name=str(name)
        self.longname=str(longname)
        if use_acl_for_rstdata is None:
            use_acl_for_rstdata=self.group_quotas and self.acl_support
        self.use_acl_for_rstdata=use_acl_for_rstdata

    ##@var group_quotas
    #  True if group membership is used to manage disk
    #  quotas.  If this is True, then the scripts should never copy the
    #  group ID when copying files.

    ##@var acl_support
    #  True if the system uses Access Control Lists (ACLs)
    #  to control access to files.  

    ##@var use_acl_for_rstdata
    #  True if the scripts should use ACLs to
    #  protect restricted access data.  If this is True, the scripts
    #  should copy ACLs when copying files.  The produtil.acl supplies a
    #  way to do that on some Linux machines.

    ##@var  production
    #  True if this system is production (real-time
    #  forecasting) environment, and False otherwise.  Most systems
    #  should set this to False.  

    ##@var name
    #  a short name of this cluster.  Must be a valid Python
    #  identifier string.

    ##@var longname
    # a long name of this cluster.

    ##@var partition
    # What part of the cluster you are on; this information is
    # system-specific.  For example, on WCOSS, this may be "phase1" or
    # "phase2" or "cray"

    @property
    def partition(self):
        return self.name

##@var here
# The Cluster object for the local cluster.  Do not modify.
here=None

def set_cluster(there):
    """!Sets the current cluster (module-level "here" variable) to the
    given value.  Bad things may happen if this is not a subclass of
    Cluster.
    #@param there A Cluster object for this local cluster."""
    global here
    here=there

def where():
    """!Guesses what cluster the program is running on, and if it
    cannot, returns a cluster named "noname" with reasonable defaults.
    The result is stored in the module scope "here" variable."""
    global here
    if here is None:
        if os.path.exists('/lfs3'):
            here=NOAAJet()
        elif os.path.exists('/glade'):
            here=UCARYellowstone()
        elif os.path.exists('/data') and os.path.exists('/scratch') and \
                os.path.exists('/home'):
            here=WisconsinS4()
        elif os.path.exists('/scratch1'):
            here=NOAAHera()
            if os.path.exists('/scratch'):
                here=NOAATheia()
        elif os.path.exists('/lfs/h2/emc'):
            here=WCOSS2()
        elif os.path.exists('/lustre/f2'):
            here=NOAAGAEA()
        else:
            here=Cluster(False,False,False,'noname','noname')
    return here

def longname():
    """!Synonym for here.longname.  Will call the "where()" function if
    "here" is uninitialized."""
    if here is None: where()
    return here.longname

def name():
    """!Synonym for here.name.  Will call the "where()" function if
    "here" is uninitialized."""
    if here is None: where()
    return here.name

def group_quotas():
    """!Synonym for here.group_quotas.  Will call the "where()" function if
    "here" is uninitialized."""
    if here is None: where()
    return here.group_quotas

def acl_support():
    """!Synonym for here.acl_support.  Will call the "where()" function if
    "here" is uninitialized."""
    if here is None: where()
    return here.acl_support

def no_access_control():
    """!True if the cluster provides no means to control access to
    files.  This is true if the cluster uses group ids for quotas, and
    provides no access control list support."""
    if here is None: where()
    return here.group_quotas and not here.use_acl_for_rstdata

def use_acl_for_rstdata():
    """!Synonym for here.use_acl_for_rstdata.  Will call the "where()"
    function if "here" is uninitialized."""
    if here is None: where()
    return here.use_acl_for_rstdata

def ncepprod():
    """!Are we on NCEP production?

    @returns True if the present machine is the NCEP production
    machine.  Note that this function may read a text file when it is
    called, and the return value may change during the execution of
    the program if the program is running during a production switch."""
    if here is None: where()
    return here.production and 'ncep' in here.longname

def partition():
    """!Returns system-specific information about what part of the
    system you are on."""
    if here is None: where()
    return here.partition

class NOAAJet(Cluster):
    """!The NOAA Jet Cluster

    Represents the NOAA Jet cluster, which has non-functional ACL
    support.  Will report that ACLs are supported, but should not be
    used.  Also, group quotas are in use.  That means that there is no
    means by which to restrict access control, so no_access_control()
    will return True."""
    def __init__(self):
        """!constructor for NOAAJet"""
        super(NOAAJet,self).__init__(True,True,False,'jet',
                                     'jet.rdhpcs.noaa.gov',False)

class NOAAGAEA(Cluster):
    """!Represents the NOAA GAEA cluster.  Allows ACLs to be used for
    restricted data, and specifies that group quotas are not in use."""
    def __init__(self):
        """!constructor for NOAAGAEA"""
        super(NOAAGAEA,self).__init__(False,True,False,'gaea',
                                      'gaea.rdhpcs.noaa.gov')

class NOAAHera(Cluster):
    """!Represents the NOAA Hera cluster.  Does not allow ACLs,
    assumes no group quotas (fileset quotas instead)."""
    def __init__(self):
        super(NOAAHera,self).__init__(False,False,False,'hera',
                                      'hera.rdhpcs.noaa.gov')

class UCARYellowstone(Cluster):
    """!Represents the Yellowstone cluster.  Does not allow ACLs,
    assumes group quotas."""
    def __init__(self):
        """!Constructor for UCARYellowstone"""
        super(UCARYellowstone,self).__init__(
            True,False,False,'yellowstone','yellowstone.ucar.edu')

class WisconsinS4(Cluster):
    """!Represents the S4 cluster.  Does not allow ACLs, assumes group
    quotas."""
    def __init__(self):
        """!Constructor for WisconsinS4"""
        super(WisconsinS4,self).__init__(
            True,False,False,'s4','s4.ssec.wisc.edu')

class MSUOrion(Cluster):
    """Represents the MSU Orion cluster.  Does not allow ACLs,
    assumes no group quotas (fileset quotas instead)."""
    def __init__(self):
        super(MSUOrion,self).__init__(
            False,False,False,'orion','orion.hpc.msstate.edu')

class NOAAWCOSS(Cluster):
    """!Represents the NOAA WCOSS clusters, Tide, Gyre and the test
    system Eddy.  

    Automatically determines which WCOSS the program is on based on
    the first letter of socket.gethostname().  Will report no ACL
    support, and no group quotas.  Hence, the cluster should use group
    IDs for access control.

    The production accessor is no longer a public member variable: it
    is now a property, which may open the /etc/prod file.  The result
    of the self.production property is cached for up to
    prod_cache_time seconds.  That time can be specified in the
    constructor, and defaults to 30 seconds."""
    def __init__(self,prod_cache_time=30,name=None,phase=None):
        """!Creates a NOAAWCOSS object, and optionally specifies the
        time for which the result of self.production should be cached.
        Default: 30 seconds.
        @param prod_cache_time how long to cache the prod vs. dev information, in seconds"""

        super(NOAAWCOSS,self).__init__(False,False,DO_NOT_SET,name,
                                       name+'.ncep.noaa.gov')
        self._phase=phase
        self._production=None
        self._lastprod=0
        self._prod_cache_time=int(prod_cache_time)
    def uncache(self):
        """!Clears the cached value of self.production so the next call
        will return up-to-date information."""
        self._production=None
        self._lastprod=0
        self._phase=0;

    @property
    def production(self):
        """!Is this the WCOSS2 production machine?  

        The name of the WCOSS2 production machine: cactus or dogwood
        luna as determined by the /lfs/h1/ops/prod/config/prodmachinefile file.

        @returns True or False: is this the WCOSS2 production machine?

        @note The return value may change during the execution of this
        program if a production switch happened.  A cached value is
        returned if the values is not too old.  To force a refresh,
        call uncache() first.

        @warning The check requires opening and parsing the /etc/prod
        file, so the runtime is likely several milliseconds when the
        cache times out."""
        now=int(time.time())
        if self._production is None or \
                now-self._lastprod>self._prod_cache_time:
            prod=False
            if os.path.exists('/lfs/h1/ops/prod/config/prodmachinefile'):
                with open('/lfs/h1/ops/prod/config/prodmachinefile','rt') as f:
                    for line in f:
                        if re.match('[a-z]+',line):
                            if line.strip().split(':')[0]=='primary':
                                prod = line.strip().split(':')[1].strip()==self.name
                                break
            self._production=prod
            self._lastprod=int(time.time())
            return prod
        else:
            return self._production

class WCOSS2(NOAAWCOSS):
    """!This subclass of NOAAWCOSS handles the new Cray portions of
    WCOSS: Luna and Surge."""
    def __init__(self,name=None):
        """!Create a new WCOSS2 object describing this cluster as a
        Cray machine.

        @property name The name of the cluster.  Default is to check
        the hostname with socket.gethosname() and decide "dogwood"
        vs. "cactus" based on the first letter of the hostname. """
        if name is None:
            host1=socket.gethostname()[0:1]
            if host1=='c':          name='cactus'
            elif host1=='s':        name='dogwood'
            else:                   name='cactus'
        super(WCOSS2,self).__init__(name=name)
