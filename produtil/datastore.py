"""!Stores products and tasks in an sqlite3 database file.

This module maintains an sqlite3 database file that stores information
about Products and Tasks.  A Product is a file or group of files
created by some Task.  Both Product and Task classes derive from
Datum, which is the base class of anything that can be stored in the
Datastore."""

import sqlite3, threading, collections, re, contextlib, time, random,\
    traceback, datetime, logging, os, time
import produtil.fileop, produtil.locking, produtil.sigsafety, produtil.log

##@var __all__
# Symbols exported by "from produtil.datastore import *"
__all__=['DatumException','DatumLockHeld','InvalidID','InvalidOperation',
         'UnknownLocation','FAILED','UNSTARTED','RUNNING','PARTIAL',
         'COMPLETED','Datastore','Transaction','Datum','CallbackExceptions',
         'Product','Task']

class FakeException(Exception):
    """!This is a fake exception used to get a stack trace.  It will
    never be raised outside this module."""

class DatumException(Exception):
    """!Superclass of all exceptions local to produtil.datastore."""

class DatumLockHeld(Exception):
    """!Raised when a LockDatum is held by another Worker."""
    def __init__(self,did,owner,owninfo,ownseen,ownlegacy,checktime):
        """!DatumLockHeld constructor.
        
        @param did the database ID  of the datum whose lock is held
        @param owner the owner of the lock
        @param owninfo implementation-defined information about the owner
        @param ownseen last time the owner checked in
        @param ownlegacy length of time the lock is valid
        @param checktime suggestion of how often to check the lock"""
        self.did=str(did)
        self.owner=int(owner)
        self.owninfo=str(owninfo)
        self.ownseen=int(ownseen)
        self.ownlegacy=int(ownlegacy)
        self.checktime=int(checktime)
    ##@var did
    # The database ID  of the datum whose lock is held

    ##@var owner
    # The owner of the lock

    ##@var owninfo
    # implementation-defined information about the owner

    ##@var ownseen 
    # last time the owner checked in

    ##@var ownlegacy
    # length of time the lock is valid

    ##@var checktime
    # suggestion of how often to check the lock
    def __str__(self):
        """!Human-readable representation of this exception."""
        return '''Cannot lock Datum %s at %d (%s)
Was locked by worker %d (info %s)
Last seen %d = %s
Lock legacy time %d
Time left: %d''' % (self.did,self.checktime,
                    datetime.datetime.utcfromtimestamp(self.checktime).ctime(),
                    self.owner,self.owninfo,self.ownseen,
                    datetime.datetime.utcfromtimestamp(self.ownseen).ctime(),
                    self.ownlegacy,self.ownseen+self.ownlegacy-self.checktime)
    def __repr__(self):
        """!String representation of this object."""
        return '%s(%s,%s,%s,%s,%s,%s)' % \
            ( type(self).__name__, repr(self.did), repr(self.owner), repr(self.owninfo),
              repr(self.ownseen), repr(self.ownlegacy), repr(self.checktime) )

class InvalidID(DatumException):
    """!Raised when a Datum or subclass receives a prodname or category name that is invalid."""
class InvalidOperation(DatumException):
    """!Raised when an invalid Datum operation is requested, such as delivering an UpstreamProduct."""
class UnknownLocation(DatumException):
    """!Raised when delivering data, but no location is provided."""

##@var _has_dcolon
# Regular expression to detect a database ID with a double colon in it.
_has_dcolon=re.compile(r'\A.*::.*\Z')

##@var _has_dstar
# Regular expression to detect a database ID with a double asterisk in it.
_has_dstar=re.compile(r'\A.*\*\*.*\Z')

##@var TASK_CATEGORY
# Special product category used for Tasks.
TASK_CATEGORY='**task**'

# Constants used by the Task class:

##@var FAILED
# Constant used for Task.state to indicate a run was attempted but failed.
FAILED=-10
"""Constant for use in Task.state: indicates a run was attempted but
failed."""

##@var UNSTARTED
# Constant used for Task.state to indicate no attempt was made to run.
UNSTARTED=0
"""Constant for use in Task.state: indicates a run was never
attempted, or a run was attempted but the task was cleaned up."""

##@var RUNNING
# Constant used for Task.state to indicate the task is presently running.
RUNNING=10
"""Constant for use in Task.state: indicates the Task is presently
running."""

##@var PARTIAL
# Constant used for Task.state to indicate the task was attempted but
# exited prematurely. Practically speaking, there is no way to tell
# the difference between RUNNING and PARTIAL since the job cannot
# ensure that it resets the state before unexpectedly exiting.
PARTIAL=20
"""Constant for use in Task.state: indicates the Task was running but
exited prematurely.  Practically speaking, there is no way to tell the
difference between RUNNING and PARTIAL since the job cannot ensure
that it resets the state before unexpectedly exiting."""

##@var COMPLETED
# Constant used for Task.state to indicate the task completed successfully.
COMPLETED=30
"""Constant for use in Task.state: indicates the task ran to
completion successfully."""

class Datastore(object):
    """!Stores information about Datum objects in a database.  

    Stores and retrieves Datum objects from an sqlite3 database.  Uses
    file locking workarounds for bugs in RedHat Enterprise Linux's
    sqlite3 library, which is compiled without proper locking.  Has
    support for caching, and multithreading.  Each object in this
    database has a type, a string location, an integer "available"
    parameter, and an arbitrary list of (key,value) metadata pairs.
    This object can safely be accessed by multiple threads in the
    local process, and handles concurrency between processes via file
    locking."""
    def __init__(self,filename,logger=None,locking=True):
        """!Datastore constructor

        Creates a Datastore for the specified sqlite3 file.  Uses the
        given logging.Logger object for logging messages.  Set
        locking=False to disable all file locking.  That is generally
        unwise, and should only be used when reading the database.
        That functionality is supplied, and critical, for monitoring
        another user's jobs.  One cannot lock another user's file, so
        the "no locking" option is the only way to analyze the other
        user's simulation.
        @param filename the filename passed to sqlite3.connect
        @param logger a logging.Logger to use for logging messages
        @param locking should file locking be used?  It is unwise to
          turn off file locking.
        @warning Setting locking=False will disable file locking at
          both the Datastore level, and within sqlite3 itself.  This
          can lead to database corruption if two processes try to
          write at the same time.  This functionality is provided
          for the rare situation where you are unable to write to
          a database, such as when reading other users' sqlite3 
          database files."""
        self._logger=logger
        self.filename=filename
        self.db=None
        self._locking=locking
        self._connections=dict()
        self._map_lock=threading.Lock()
        self._db_lock=threading.Lock()
        lockfile=filename+'.lock'
        if logger is not None:
            logger.debug('Lockfile is %s for database %s'%(lockfile,filename))
        self._file_lock=produtil.locking.LockFile(
            lockfile,logger=logger,max_tries=300,sleep_time=0.1,first_warn=50)
        self._transtack=collections.defaultdict(list)
        with self.transaction() as tx:
            self._createdb(self._connection())
    ##@var db 
    # The underlying sqlite3 database object

    ##@var filename
    # The path to the sqlite3 database file

    def _connection(self):
        """!Gets the current thread's database connection.  Each thread
        has its own connection."""
        tid=threading.current_thread().ident
        with self._map_lock:
            if tid in self._connections:
                return self._connections[tid]
            else:
                c=sqlite3.connect(self.filename)
                self._connections[tid]=c
                return c
    @contextlib.contextmanager
    def _mystack(self):
        """!Gets the transaction stack for the current thread."""
        tid=threading.current_thread().ident
        with self._map_lock:
            yield self._transtack[tid]
    def _lock(self):
        """!Acquires the database lock for the current thread."""
        if not self._locking: return
        self._db_lock.acquire()
        try:
            self._file_lock.acquire()
        except:
            self._db_lock.release()
            raise
    def _unlock(self):
        """!Releases the database lock from the current thread.  If the
        current thread does not have the lock, the results are
        undefined."""
        if not self._locking: return
        self._file_lock.release()
        self._db_lock.release()
        #if self._logger is not None:
        #        self._logger.info('db lock release: '+\
        #          (''.join(traceback.format_list(traceback.extract_stack(limit=10)))))
    def transaction(self):
        """!Starts a transaction on the database in the current thread."""
        return Transaction(self)
    def _createdb(self,con):
        """!Creates the tables used by this Datastore.  

        Runs "CREATE TABLE" commands in the sqlite3 database to create
        all tables needed by this class.  This code must be executed
        inside a transaction() and should only be executed on initial
        opening of the file, in the Datastore constructor.  It is safe
        to run this command twice on the same file --- the "IF NOT
        EXISTS" SQLite modifier is used to ensure the table will not
        be replaced."""
        con.execute('''CREATE TABLE IF NOT EXISTS products ( id TEXT NOT NULL, available INTEGER DEFAULT 0, location TEXT DEFAULT "", type TEXT DEFAULT "Product", PRIMARY KEY(id))''')
        con.execute('''CREATE TABLE IF NOT EXISTS metadata ( id TEXT NOT NULL, key TEXT NOT NULL, value TEXT, CONSTRAINT id_metakey PRIMARY KEY(id,key))''')
        con.execute('''CREATE TABLE IF NOT EXISTS workers ( info TEXT NOT NULL, lastseen INTEGER NOT NULL)''')
    def dump(self):
        """!Print database contents to the terminal.

        This function is only meant for debugging.  It dumps to the
        terminal an arguably human-readable display of the complete
        database state via the print command."""
        with self.transaction() as t:
            products=t.query('SELECT id,available,location,type FROM products')
            meta=t.query('SELECT id,key,value FROM metadata')
        print('TABLE products:')
        taskmap={UNSTARTED:'UNSTARTED',FAILED:'FAILED',RUNNING:'RUNNING',
                 PARTIAL:'PARTIAL',COMPLETED:'COMPLETED'}
        for row in products:
            (what,avail,loc,typ)=row
            if typ=='Task' and avail in taskmap:
                print("id=%s available=%s (%s) location=%s type=%s" % \
                    ( what,avail,taskmap[avail],loc,typ ))
            elif typ=='Product':
                print("id=%s available=%s (%s) location=%s type=%s" % \
                    ( what,avail,repr(bool(avail)),loc,typ ))
            else:
                print("id=%s available=%s location=%s type=%s" % \
                    (what,avail,loc,typ))
        print('TABLE metadata:')
        for row in meta:
            print('%s[%s]=%s' % row)

########################################################################

class Transaction(object):
    """!Datastore transaction support.

    Implements sqlite3 transactions on a Datastore.  A transaction is
    a set of reads and updates that should either ALL be done, or NONE
    at all.  Transactions also speed up the script, sometimes by as
    much of a factor of 300, by grouping I/O operations to the
    database into one large chunk.  However, one must be careful in
    using them since it keeps the database locked for an extended
    period of time.

    This class should not be used directly.  Instead, one should do
    this to a Datum (Task or Product) object:

    with datum_object.transaction() as t:
        ... do things to the datum object ...
    transaction is now complete, database is updated."""
    def __init__(self,ds):
        """!Transaction constructor.

        Creates the Transaction object but does NOT initiate the
        transaction."""
        self.ds=ds

    def __enter__(self):
        """!Locks the database for the current thread, if it isn't
        already locked."""
        with self.ds._mystack() as s:
            first=not s # True = first transaction from this thread
            s.append(self)
        if first:
            self.ds._lock()
        return self
    def __exit__(self,etype,evalue,traceback):
        """!Releases the database lock if this is the last Transaction
        released for the current thread.
        @param etype,evalue Exception type and value, if any.
        @param traceback Exception traceback, if any."""
        with self.ds._mystack() as s:
            assert(s.pop() is self)
            unlock=not s
        if unlock:
            self.ds._connection().commit()
            self.ds._unlock()
    def query(self,stmt,subvals=()):
        """!Performs an SQL query returning the result of cursor.fetchall()
        @param stmt the SQL query
        @param subvals the substitution values"""
        cursor=self.ds._connection().execute(stmt,subvals)
        return cursor.fetchall()
    def mutate(self,stmt,subvals=()):
        """!Performs an SQL database modification, returning the result
        of cursor.lastrowid
        @param stmt the SQL query
        @param subvals the substitution values"""
        cursor=self.ds._connection().execute(stmt,subvals)
        return cursor.lastrowid
    def init_datum(self,d,meta=True):
        """!Add a Datum to the database if it is not there already.

        Given a Datum, add the object to the database if it is not
        there already and fill the object with data from the database.
        @param d the Datum
        @param meta If True, also initialize metadata."""
        prodtype=type(d).__name__
        av = d._meta['available'] if ('available' in d._meta) else 0
        loc = d._meta['location'] if ('location' in d._meta) else ''
        #print 'INIT_DATUM with location=%s'%(repr(loc),)
        self.mutate('INSERT OR IGNORE INTO products VALUES (?,?,?,?)',(d.did,av,loc,prodtype))
        if loc is not None and loc!='':
            # Update the location if it is not set in the product
            # table, but is set in the initial values.
            #print 'UPDATE LOCATION...'
            for (did,oloc) in \
                    self.query('SELECT id,location FROM products WHERE id = ?',(d.did,)):
                #print 'LOCATION currently %s'%(oloc,)
                if did==d.did and (oloc is None or oloc==''):
                    self.mutate('UPDATE products SET location=? WHERE id=?',
                                (loc,d.did))
                    break

        if meta and d._meta is not None and d._meta: 
            for k,v in d._meta.items():
                if k!='location' and k!='available':
                    self.mutate('INSERT OR IGNORE INTO metadata VALUES (?,?,?)',(d.did,k,v))
        if meta:
            self.refresh_meta(d,or_add=False)
    def update_datum(self,d):
        """!Update database availability and location records.

        Given a Datum whose location and availability is set, update
        that information in the database, adding the Datum if
        necessary.
        @param d the Datum"""
        loc=str(d._meta['location'])
        av=int(d._meta['available'])
        self.mutate('INSERT OR REPLACE INTO products VALUES (?,?,?,?)',
                    (d.did,av,loc,type(d).__name__))
    def refresh_meta(self,d,or_add=True):
        """!Replace Datum metadata with database values, add new metadata to database.

        Given a Datum d, discards and replaces d._meta with the
        current metadata, location and availability.  Will raise an
        exception if the product does not exist in the database.
        @param d The Datum.
        @param or_add If True, then any metadata that does not exist in the 
          database is created from values in d."""
        found=False
        meta=dict()
        for (did,av,loc) in \
                self.query('SELECT id, available, location FROM products WHERE id = ?',(d.did,)):
            found=True
            meta['available']=av
            meta['location']=loc
            #print 'refresh_meta update location=%s'%(repr(loc),)
            break
        if not found:
            if or_add:
                self.init_datum(d,meta=False)
            meta['available']=0
            meta['location']=''
            #print 'refresh_meta not found so location=""'
        for (did,k,v) in self.query('SELECT id, key, value FROM metadata WHERE id = ?',(d.did,)):
            meta[k]=v
        d._meta=meta
    def set_meta(self,d,k,v):
        """!Sets metadata key k to value v for the given Datum.  

        Modifies the database entries for key k and datum d to have
        the value v.  If k is location or available, then the product
        table will be updated instead.
        @param d The Datum
        @param k The metadata key.
        @param v The value, a string."""
        if k=='location':
            self.mutate('UPDATE OR IGNORE products SET location = ? WHERE id = ?',(v,d.did))
        elif k=='available':
            self.mutate('UPDATE OR IGNORE products SET available = ? WHERE id = ?',(int(v),d.did))
        else:
            self.mutate('INSERT OR REPLACE INTO metadata VALUES (?,?,?)',(d.did,k,v))
    def del_meta(self,d,k):
        """!Delete metadata from the database.

        Deletes the specified metadata key k, which must not be
        "location" or "available".
        @param d The Datum whose metadata is being deleted.
        @param k The metadata key, which cannot be "available" or "location"."""
        assert(k != 'available' and k != 'location')
        self.mutate('DELETE FROM metadata WHERE id=? AND key=?',(d.did,k))

    ##@var ds
    # The Datastore containing the database for which this is a transaction.

########################################################################

class Datum(object):
    """!Superclass of anything that can be stored in a Datastore.

    This is the superclass of anything that can be placed in a
    datastore.  It has a category, a product name (prodname for
    short), a location, availability (an int) and arbitrary metadata
    (key,value) pairs.  It caches database metadata in self._meta,
    which is directly accessed by the Datastore class.  Cache data
    will be discarded once its age is older than self._cacheage."""
    def __init__(self,dstore,prodname,category,meta=None,cache=30,location=None,**kwargs):
        """!Datum constructor.

        Creates a Datum in the given Datastore dstore, under the
        specified category and product name prodname.  The datastore
        id used is "category::prodname".  The value for "cache" is the
        number of seconds to retain cached metadata before going back
        to disk to reread it.  That only applies to data "get"
        operations: setting a data or metadata value will cause an
        immediate write to the database.  Also, __contains__ ("var" in
        self) will force a fetch from the database if the requested
        metadata variable is not in the cached copy of the database.

        Values for location and meta are only the DEFAULT values, and
        will be ignored if other values are already set in the
        database.  The location is only used if the product is not
        already in the database: its location will be set to the
        provided values upon entry.  Similarly, the metadata is only
        set in this call if there isn't already metadata for the
        product with the given metadata keys.
        @param dstore The Datastore for this Datum.
        @param prodname The product name portion of the Datum ID
        @param category The category part of the Datum ID
        @param meta A dict of metadata values.
        @param cache Metadata cache lifetime in seconds.
        @param location The initial value for location, if it is not set already in the database.
        @param kwargs Ignored."""
        #print 'INIT WITH location=%s prodname=%s category=%s'% \
        #    (repr(location),repr(prodname),repr(category))
        (self._dstore,self._prodname,self._category) = (dstore,str(prodname),str(category))
        self._id=self._category+'::'+self._prodname
        self._cachetime=time.time()
        self._cacheage=30
        if not cache:
            self._cacheage=-1
        self.validate()
        if (meta is None):
            self._meta=dict()
        else:
            self._meta=dict(meta)
        if location is not None:
            self._meta['location']=str(location)
        if 'available' in self._meta:
            self._meta['available']=int(self._meta['available'])
        self._lock=threading.RLock()
        with self._dstore.transaction() as t:
            t.init_datum(self)

    # Lock/unlock self:
    def __enter__(self):
        """!Acquires this object's thread lock.  This is used to manage cached data."""
        self._lock.acquire()
        return self
    def __exit__(self,etype,evalue,traceback):
        """!Releases this object's thread lock.  This is used to manage cached data.
        @param etype,evalue,traceback Exception information."""
        self._lock.release()

    def validate(self):
        """!Validates this object's Datastore, prodname and category."""
        if _has_dcolon.match(self._prodname):
            raise InvalidID('%s: the prodname cannot contain a double colon (::)'%(self._id))
        if _has_dcolon.match(self._category):
            raise InvalidID('%s: the category cannot contain a double colon (::)'%(self._id))

    # Getter/setters to implement the properties:
    def getid(self):
        """!Returns the database ID of this datum."""
        return self._id
    def getdatastore(self):
        """!Returns the datastore of this datum."""
        return self._dstore
    def transaction(self):
        """!Creates, but does not lock, a Transaction for this datum's datastore."""
        return self._dstore.transaction()
    def getprodtype(self):
        """!Returns the product type of this Datum.  

        Returns the product type of this Datum.  This is generally the
        name of the Python class that created the entry in the
        database."""
        return type(self).__name__
    def getprodname(self):
        """!Returns the product name part of the database ID."""
        return self._prodname
    def getcategory(self):  
        """!Returns the product category part of the database ID."""
        return self._category

    def getlocation(self):
        """!Returns the "location" field of this Datum's database entry."""
        return self['location']
    def setlocation(self,v): 
        """!Sets the "location" field of this Datum's database entry.
        @param v the new location"""
        self['location']=v

    ##@property prodname
    # Read-only property, an alias for getprodname(): the product name
    # part of the database ID.
    prodname=property(getprodname,None,None,"""the product name (read-only)""")

    ##@property category
    # Read-only property, an alias for getcategory(), the category
    # name part of the database ID.
    category=property(getcategory,None,None,"""the category (read-only)""")

    ##@property prodtype
    # Read-only property, an alias for getprodtype(), the product
    # type.  This is generally the name of the Python class that
    # created the entry in the database.
    prodtype=property(getprodtype,None,None,
                      """Returns the prodtype for this Datum: its class name (read-only)""")

    ##@property did
    # Read-only property, an alias for getid().  The full database ID.
    did=property(getid,None,None,
                 """Returns the database id for this Datum (read-only)""")

    ## @property dstore
    # Read-only property, an alias for getdatastore(), the Datastore
    # in which this Datum resides.
    dstore=property(getdatastore,None,None,
                    """Gets the Datastore object that contains this Datum (read-only)""")

    ## @property location
    # Read-write property, an alias for getlocation() and
    # setlocation().  The location on disk of this Datum.
    location=property(getlocation,setlocation,None,
                      """The location of this product (read/write)""")

    def __hash__(self): 
        """!Integer hash function."""
        return hash(self._prodname)^hash(self._category)
    def __str__(self): 
        """!Human-readable description of this Datum."""
        return '%s with id %s'%(self.prodtype,self.did)
    def __repr__(self): 
        """!Python code-like description of this Datum."""
        return '%s(%s,%s,%s)' % \
            (self.prodtype,repr(self.dstore),repr(self._prodname),repr(self._category))
    def __lt__(self,other):
        """!Compares two Datums' prodnames and categories.
        @param other the other datum to compare against"""
        if self._prodname < other._prodname:
            return True
        if self._category < other._category:
            return True
        return False
    def __gt__(self,other):
        """!Compares two Datums' prodnames and categories.
        @param other the other datum to compare against"""
        if self._prodname > other._prodname:
            return True
        if self._category > other._category:
            return True
        return False
    def __eq__(self,other):
        """!Compares two Datums' prodnames and categories.
        @param other the other datum to compare against"""
        return not (self>other or self<other)
    def __ne__(self,other):
        """!Compares two Datums' prodnames and categories.
        @param other the other datum to compare against"""
        return self>other or self<other
    def __ge__(self,other):
        """!Compares two Datums' prodnames and categories.
        @param other the other datum to compare against"""
        return not (self<other)
    def __le__(self,other):
        """!Compares two Datums' prodnames and categories.
        @param other the other datum to compare against"""
        return not (self>other)
    def set_loc_avail(self,loc,avail):
        """!Sets the location and availability of this Datum in a
        single transaction.
        @param loc the new location, a string
        @param avail the new availability, an int"""
        with self:
            self._meta['location']=str(loc)
            self._meta['available']=int(avail)
            with self.transaction() as t:
                t.update_datum(self)
    def _getcache(self,k=None,force=False):
        """!Requests or forces a cache update.
        This is the implementation of metadata/location/available
        caching.  It returns self._meta if the cache has not aged out
        (and k, if provided, is in self._meta) or goes to the
        Datastore to update the cache, and then returns the resulting
        self._meta.  This MUST be called from within a "with self".
        @param k The key of interest.
        @param force If True, forces a cache update even if the
          cache is not expired."""
        logger=self.dstore._logger
        did=self.did
        if not force:
            age=time.time()-self._cachetime
            if age<self._cacheage:
                if k is None or k in self._meta:
                    return self._meta
        with self.transaction() as t:
            t.refresh_meta(self)
            self._cachetime=time.time()
        return self._meta
    def update(self):
        """!Discards all cached metadata and refreshes it from the
        Datastore."""
        with self:
            self._getcache(force=True)
    def __getitem__(self,k):
        """!Returns the value of the specified metadata key or raises
        KeyError.  Forces a cache update if k is not in the cache."""
        with self:
            meta=self._getcache(k)
            return meta[k]
    def meta(self,k,default=None):
        """!Return the value of a metadata key

        Returns the value of the specified metadata key or returns
        default if it is unset.  Does NOT force a cache update if k is
        missing from the cache.  To force a cache update, use
        __getitem__ instead.
        @param k The key of interest.
        @param default The value to return if no value is seen.
        @returns The metadata value or the default."""
        with self:
            return self._getcache().get(k,default)
    def get(self,k,default=None):
        """!Alias for self.meta()
        Returns the value of the specified metadata key or returns
        default if it is unset.  Does NOT force a cache update if k is
        missing from the cache.  To force a cache update, use
        __getitem__ instead.
        @param k The key of interest.
        @param default The value to return if no value is seen.
        @returns The metadata value or the default."""
        with self:
            return self._getcache().get(k,default)

    def __setitem__(self,k,v):
        """!Sets the value of the specified metadata key.
        @param k the key
        @param v the value"""
        with self:
            with self.transaction() as t:
                t.set_meta(self,k,v)
            self._meta[k]=v
    def __delitem__(self,k):
        """!Deletes the specified metadata key, which must not be
        "available" or "location".
        @param k the key to delete"""
        assert(k != 'available' and k != 'location')
        with self:
            with self.transaction() as t:
                t.del_meta(self,k)
                if k in self._meta:
                    del self._meta[k]
    def __contains__(self,k):
        """!Determines if a metadata key is set.
        @returns True if the specified metadata key is set, and False
          otherwise.  Immediately returns True for 'available' and
          'location' without checking the metadata cache.
        @param k the key of interest"""
        if k=='available' or k=='location':
            return True
        with self:
            return k in self._getcache()
    def iteritems(self):
        """!Alias for items() for backward compatibility"""
        for k,v in self.items():
            yield k,v
    def items(self):
        """!Iterates over all metadata (key,value) pairs for this
        Datum, including "available" and "location"."""
        with self:
            meta=dict(self._getcache())
        assert('available' in meta)
        assert('location' in meta)
        yield 'available',meta['available']
        yield 'location',meta['location']
        for k,v in meta.items():
            if k!='location' and k!='available':
                yield k,v

########################################################################

class CallbackExceptions(Exception):
    """!Exception raised when a Product class encounters
    exceptions while calling its callback functions in
    Product.call_callbacks."""
    def __init__(self,message,exlist):
        """!CallbackExceptions constructor.
        @param message The beginning of the exception message.  Each
          exception's message will be appended to this.
        @param exlist The list of exceptions."""
        self.messagebase=message
        self.exlist=exlist
        for ex in exlist:
            message+="\n  %s"%(str(ex),)
        Exception.__init__(self,message,exlist)

    ##@var exlist
    # The list of exceptions raised.
    
    ##@var messagebase
    # The original message sent to the constructor before
    # per-exception messages were appended.

########################################################################

class Product(Datum):
    """!A piece of data produced by a Task.

    A Product is a piece of data that can be produced by a Task.  Once
    the product is available, self.available or self.is_available()
    will be True, and the self.location will be valid.  The meaning of
    self.location is up to the implementer to decide, but it should be
    a full path to a location on disk for file products.  As with all
    Datum objects, a Product also has arbitrary metadata."""
    def add_callback(self,callback,args=None,states=None):
        """!Adds a delivery callback function.  

        Adds a delivery callback that is called when the product is
        delivered.  This is intended to do such tasks as running an
        NCO dbn_alert, or copying to a website, or emailing someone.
        This function is only added in this local Python instance, not
        in the database file.  Also, it is the responsibility of the
        subclasses to call self.call_callbacks() from self.deliver()
        to ensure the callbacks are run.

        Example:
        @code{.py}
          def callback(name,*args,**kwargs):
            print "My fancy product %s was delivered!"%(name,)
          product.add_callback(callback,[product.prodname])
        @endcode

        @param callback The callback function, which must be able to
          take any keyword or indexed arguments.
        @param args The indexed arguments to send.
        @param states Presently unused."""
        if args is None: 
            largs=list()
        else:
            largs=list(args)
        calldata=[callback,largs]
        if '_callbacks' not in self.__dict__: setattr(self,'_callbacks',list())
        self._callbacks.append(calldata)
    def has_callbacks(self):
        """!Returns True if this Product has any callback functions
        and False otherwise"""
        if '_callbacks' not in self.__dict__: return False
        return len(self._callbacks)>0
    def call_callbacks(self,logger=None):
        """!Calls all delivery callback functions.

        Calls all data delivery callbacks for this Product.  Collects
        any raised Exception subclasses until after all callbacks are
        called.  Will raise CallbackExceptions if any exceptions are
        caught.

        Subclasses should call this from either check, or deliver, as
        appropriate for the product type.
        @param logger Optional: the logging.Logger for logging messages."""
        if '_callbacks' not in self.__dict__: return
        if not self._callbacks: return
        if logger is None and len(self._callbacks)>0:
            logger=logging.getLogger('produtil.datastore')
        exlist=None
        meta=self._getcache()
        for (callback,args) in self._callbacks:
            try:
                callback(*args,**meta)
            except Exception as e:
                if exlist is None: exlist=list()
                exlist.append(e)
                if logger is not None:
                    logger.warning(str(e),exc_info=True)
        if exlist is not None:
            raise CallbackExceptions('%s: exceptions caught when delivering this product'%(self.did,),exlist)
    def check(self,**kwargs):
        """!Asks the product to check its own availability and update
        the database.

        Checks to see if this product is available.  This is generally
        not a cheap operation, as it can take seconds or minutes and
        may fail.  One should call "available" instead if cached
        information is sufficient.
        @param kwargs Additional keyword arguments are unused.  This is
          for use by subclasses."""
        self.update()
        return self.available
    def deliver(self,**kwargs):
        """!Asks the Product to deliver itself.

        Delivers a product to its destination.  This is not
        implemented by the base class.  Note that this is generally an
        expensive operation which may take seconds or minutes, and may
        fail.  It may involve copying many files, network access, or
        even pulling tapes from a silo.  In the end, the location and
        availability are expected to be updated in the database.
        @param kwargs Unused, to be used by subclasses.
        @post available=True and location is non-empty."""
        raise InvalidOperation('The Product base class does not implement deliver')
    def undeliver(self,**kwargs):
        """!"Undelivers" a product.  

        The meaning of this function is implementation-dependent: it
        could mean deleting an output file, or any number of other
        actions.  Regardless, it should result in self.available=False
        or an exception being thrown.  Note that this is generally an
        expensive operation that could take seconds or minutes, and
        may fail.  The default implementation simply sets available to
        False.

        @post available=False"""
        self.available=False
    def setavailable(self,val):
        """!Sets the availability to the specified value.

        Sets the "available" attribute of this Product in the database
        after converting the given value to a bool and then int
        (int(bool(val))).
        @param val the new availability"""
        self['available']=int(bool(val))
    def is_available(self):
        """!Is the product available?

        Returns the "available" attribute of this Product in the
        database, converted to a boolean value via bool()"""
        return bool(int(self['available']))

    ##@property available
    # Read-write property: is the product available?
    available=property(is_available,setavailable,None,
                       """The availability of this product as a bool (read/write)""")

    def validate(self):
        """!Validates this object's Datastore, prodname and category.

        Validates the Datastore, prodname and category of this
        Product.  In addition to the requirements made by Datum, this
        function requires that the category not contain any double
        stars ("**")."""
        if _has_dstar.match(self._category):
            raise InvalidID('%s: Product categories cannot contain double stars (**)'%(self._id))
        super(Product,self).validate()

########################################################################

class FileProduct(Product):
    """!A subclass of Product that represents file delivery.

    This subclass of Product represents a file that is delivered by
    this workflow.  The deliver() subroutine actually copies the file,
    and undeliver() deletes it.  The produtil.fileop.remove_file() and
    produtil.fileop.deliver_file() are used for this purpose."""
    def undeliver(self,delete=True,logger=None):
        """!Undoes the effect of deliver()

        Sets this Product's available attribute to False.  If
        delete=True, will also delete the specified file.
        @param delete if True, the file is deleted
        @param logger a logging.Logger for log messages"""
        loc=self.location
        if loc and delete:
            produtil.fileop.remove_file(filename=loc,logger=logger,info=True)
        self.available=False
    def deliver(self,location=None,frominfo=None,keep=True,logger=None,
                copier=None):
        """!Delivers the file to a destination.

        Delivers the file to a destination location specified.  The
        origin is in the "frominfo" argument.  Delivery is done by
        produtil.fileop.deliver_file.  The keep, copier and logger
        arguments are passed on unmodified.
        @param location The new location.
        @param frominfo Where to get the file from.
        @param keep If True, the original file is always kept.  If False,
           the original file may be moved to the destination instead of copied.
        @param logger a logging.Logger for log messages

        @param copier Passed to the copier argument of
          produtil.fileop.deliver_file()
        @post The file is at the location specified, and the database
          location and availability are updated accordingly."""
        if not isinstance(frominfo,str):
            raise TypeError('FileProduct.deliver requires a string filename as its frominfo argument.  You provided an object of type %s.'%(type(frominfo).__name__))
        if location is not None and not isinstance(location,str):
            raise TypeError('FileProduct.deliver requires a location argument that is None or a string filename.  You provided an object of type %s.'%(type(frominfo).__name__))
        loc=location
        setloc=True
        if loc is None:
            setloc=False
            loc=self.location
        if loc is None:
            raise UnknownLocation(
                '%s: no location known when delivering product.  Specify a '
                'location to deliver().'%(self.did))
        produtil.fileop.deliver_file(frominfo,loc,keep=keep,logger=logger,
                                     copier=copier)
        if setloc:
            self.set_loc_avail(loc,True)
        else:
            self.available=True
        self.call_callbacks(logger=logger)

########################################################################

class UpstreamFile(Product):
    """!Represents a Product created by an external workflow.

    This subclass of Product represents a file that is created by an
    external workflow.  It implements a check() call that determines
    if the file is larger than a minimum size and older than a minimum
    age.  Once the file is large enough and old enough, it sets the
    location and availability.  Any calls to undeliver() or deliver()
    raise InvalidOperation."""
    def check(self,frominfo=None,minsize=None,minage=None,logger=None):
        """!Checks the specified file to see if it is available.

        Looks for the file on disk.  Updates the "available" and
        "location" attributes of this Product.  Uses two metadata
        values to decide whether the file is "available" if it exists:

        self["minsize"] - minimum size in bytes.  Default: 0
        self["minage"] - minimum age in seconds.  Default: 20

        Both can be overridden by corresponding arguments.  Note that
        one must be careful with the minimum age on poorly-maintained
        clusters due to clock skews.
        @param frominfo Optional: where to look for the file instead of
          looking at self.location
        @param minsize Optional: the minimum file size in bytes
        @param minage Optional: the minimum file modification time in seconds.
        @param logger Optional: a logging.Logger for log messages."""
        loc=frominfo
        setloc=True
        if loc is None:
            setloc=False
            loc=self.location
        elif not isinstance(loc,str):
            raise TypeError('UpstreamFile.check requires a frominfo argument that is either None or a string filename.  You provided an object of type %s.'%(type(frominfo).__name__))
        assert(loc is not None)
        if minsize is None:
            minsize=int(self.get('minsize',0))
        if minage is None:
            minage=int(self.get('minage',20))
        if not produtil.fileop.check_file(loc,min_size=minsize,
                min_mtime_age=minage):
            if self.available:
                self.available=False
            return False
        if setloc:
            self.set_loc_avail(loc,True)
        else:
            self.available=True
        self.call_callbacks(logger=logger)
        return True
    def undeliver(self):
        """!Undelivering an UpstreamFile merely sets the internal
        "available" flag to False.  It does not remove the data."""
        self.available=False
    def deliver(self,location=None,frominfo=None):
        """!Raises InvalidOperation.  You cannot deliver an upstream
        file.  The upstream workflow must do that for you.  Call
        check() instead to see if the file has been delivered."""
        raise InvalidOperation('Internal error: the scripts attempted to deliver an upstream product.')

########################################################################

def wait_for_products(plist,logger,renamer=None,action=None,
                      renamer_args=None,action_args=None,sleeptime=20,
                      maxtime=1800):
    """!Waits for products to be available and performs an action on them.

    Waits for a specified list of products to be available, and
    performs some action on each product when it becomes available.
    Sleeps sleeptime seconds between checks.  Returns the number of
    products that were found before the maxtime was reached.

    @param plist A Product or a list of Product objects.
    @param logger A logging.Logger object in which to log messages.
    @param renamer Optional: a function or callable object that
       provides a new name for each product.  This is passed the
       product, the logger and the contents of *renamer_args.
       Default: os.path.basename(p.location)
    @param action Optional: an action to perform on each product.
       This is passed the product, the output of renamer, the logger
       and the contents of *action_args.  Default: perform no action.
    @param renamer_args Optional: arguments to renamer.
    @param action_args Optional: arguments to action.
    @param sleeptime - after checking availability of all products, if
       at least one is unavailable, the code will sleep for this much
       time before rechecking.  Will be overridden by 0.01 if it is
       set to something lower than that.  Default: 20
    @param maxtime - maximum amount of time to spend in this routine
       before giving up.
    @returns the number of products that became available before the
       maximum wait time was hit.    """
    if renamer is None:
        renamer=lambda p,l: os.path.basename(p.location)
    if isinstance(plist,Product):
        plist=[plist]
    if not ( isinstance(plist,tuple) or isinstance(plist,list) ):
        raise TypeError('In wait_for_products, plist must be a '
                        'list or tuple, not a '+type(plist).__name__)
    now=int(time.time())
    start=now
    seen=set()
    for p in plist:
        if not isinstance(p,Product):
            raise TypeError('In wait_for_products, plist must only '
                            'contain Product objects.')
    if renamer_args is None: renamer_args=list()
    if action_args is None: action_args=list()
    logger.info('Waiting for %d products.'%(int(len(plist)),))
    while len(seen)<len(plist) and now<start+maxtime:
        now=int(time.time())
        for p in plist:
            if p in seen: continue
            if not p.available: p.check()
            if p.available:
                logger.info('Product %s is available at location %s'
                            %(repr(p.did),repr(p.location)))
                seen.add(p)
                if action is not None:
                    name=renamer(p,logger,*renamer_args)
                    action(p,name,logger,*action_args)
            else:
                logger.info(
                    'Product %s not available (available=%s location=%s).'
                    %(repr(p.did),repr(p.available),repr(p.location)))
        now=int(time.time())
        if now<start+maxtime and len(seen)<len(plist):
            sleepnow=max(0.01,min(sleeptime,start+maxtime-now-1))
            logfun=logger.info if (sleepnow>=5) else logger.debug
            logfun('Sleeping %g seconds...'%(float(sleepnow),))
            time.sleep(sleepnow)
            logfun('Done sleeping.')
    logger.info('Done waiting for products: found %d of %d products.'
                %(int(len(seen)),int(len(plist))))
    return len(seen)

########################################################################

class Task(Datum):
    """!Represents a process or actor that makes a Product.

    A Task represents some work that needs to be done to produce
    Products.  A task has a state (stored in the "available" metadata
    attribute), a location, whose meaning is up to the implementer to
    decide, and a logger.Logger.  As with all Datum subclasses, a Task
    also has arbitrary metadata."""
    def __init__(self,dstore,taskname,logger=None,**kwargs):
        """!Task constructor

        Creates a new Task from the given dataset and with the given
        task name.
        @param dstore the Datastore where this Task will live
        @param taskname the task name, passed to the Datum as prodname
        @param logger a logging.Logger for this task to use for log messages
        @param kwargs other keyword arguments are passed to Datum.__init__"""
        if logger is None:
            logger=logging.getLogger(taskname)
        self._logger=logger
        Datum.__init__(self,dstore=dstore,prodname=taskname,category=TASK_CATEGORY,**kwargs)

    @property
    def jlogfile(self):
        """!returns the jlogfile logger.  

        Returns a logging.Logger for the jlogfile.  The jlogfile is
        intended to receive only major errors, and per-job start and
        completion information.  This is equivalent to simply
        accessing produtil.log.jlogger."""
        return produtil.log.jlogger

    def postmsg(self,message,*args,**kwargs):
        """!same as produtil.log.jlogger.info()

        Sends a message to the multi-job shared log file at level
        INFO.
        @param message the message
        @param args positional arguments for string replacement
        @param kwargs keyword arguments for string replacement."""
        produtil.log.jlogger.info(message,*args,**kwargs)

    def setstate(self,val):
        """!Sets the state of this job.

        Sets the job stat to the specified value.  This works by
        setting the "available" attribute to the specified integer.
        For compatibility with other scripts, this should be FAILED,
        UNSTARTED, RUNNING, PARTIAL or COMPLETED.
        @param val the new job state, an int"""
        self['available']=int(val)
    def getstate(self): 
        """!Returns the job state.
        
        Returns the "available" attribute as an integer.  This is used
        as the state of the Task.  Typically, the return value should
        be one of: FAILED, UNSTARTED, RUNNING, PARTIAL, or COMPLETED."""
        return int(self['available'])

    ##@property produtil.datastore.Product.state
    # Read-write property: the job state.  Can be FAILED, UNSTARTED,
    # RUNNING, PARTIAL or COMPLETED.
    state=property(getstate,setstate,None,
        """The state of this Task as an int (read/write)""")

    @property
    def strstate(self):
        """!A string representation of the job state."""
        s=int(self['available'])
        if s==FAILED:         return 'FAILED'
        elif s==UNSTARTED:    return 'UNSTARTED'
        elif s==RUNNING:      return 'RUNNING'
        elif s==PARTIAL:      return 'PARTIAL'
        elif s==COMPLETED:    return 'COMPLETED'
        else:                 return 'UNRECOGNIZED(%d)'%s
    def gettaskname(self):
        """!Returns the task name part of the database ID, which is the
        same as the prodname."""
        return self._prodname

    ##@property taskname
    # Read-only property: the name of this task.  Same as self.prodname.
    taskname=property(gettaskname,None,None,
        """!The task name (read-only, same as prodname)""")
    def products(self,*args,**kwargs):
        """!Iterate over the products this task produces.

        Iterates over some or all of the products produced by this
        task.  The arguments are used to select subsets of the total
        set of products.  Provide no arguments to get the full list of
        products.  All subclasses should re-implement this method, and
        interpret the arguments in a way that makes sense to that
        class.  The default implementation returns immediately without
        doing anything.
        @param args,kwargs Implementation-defined, used by subclasses."""
        return
        for x in []: yield x  # ensures this is an iterator
    def log(self):
        """!Returns the logger object for this task."""
        return self._logger
    def clean(self):
        """!Cleans up any unneeded data used by this task.  

        Subclasses should override this function to clean up any
        unneeded temporary files or other unused resources consumed by
        the run() function.  This default implementation does nothing."""
        pass
    def unrun(self):
        """!Undoes the effect of run().

        Cleans up this Task's work areas, "undelivers" all
        deliverables, and makes it look like the task has never been
        run.  All subclasses should re-implement this method, and must
        also "unrun" everything their parent class runs.  The default
        implementation simply calls self.clean() and sets the state to
        UNSTARTED.
        @post self.state=UNSTARTED"""
        self.clean()
        self.state=UNSTARTED
    def run(self):
        """!Performs the work this Task should do and generates all products.
        
        Performs the work that this task is supposed to do.  All
        subclasses should re-implement this method, and should set the
        state to COMPLETED the end.  This implementation simply calls
        self.setstate(COMPLETED)
        @post self.state=COMPLETED"""
        self.setstate(COMPLETED)
    def is_completed(self):
        """!Is this task complete?

        Returns True if this task's state is COMPLETED, and False
        otherwise."""
        return self.state==COMPLETED

    ##Read-only property: is this task completed?  Same as is_completed()
    @property
    def completed(self):
        """!True if self.state==COMPLETED, False otherwise."""
        return self.state==COMPLETED

    def runpart(self):
        """!Run some of this task's work, deliver some products.

        Performs a subset of the work that this task is supposed to do
        and returns.  This is intended to be used for tasks that can
        be broken up into small pieces, such as post-processing all
        output files from a NWP simulation one by one.  The default
        implementation simply calls self.run()"""
        self.run()

