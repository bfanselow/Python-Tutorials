"""

 Class: MariaDB

 Python3 DB-access class for Maria (mysql) Databases

 Requires: 
   * mysql-connector-python
   * mysqlclient (typically require OS install of libmysqlclient-dev)
   * decorator  

 =====================================================================
 Public methods:

  === Class methods === 
  * create_connection_handle(d_db_args)
  * close_connection()
  
  === Instance methods === 
  * get_db_conn_handle()
  * set_db_conn_handle()

  * run_sql( <sql>, cursor_type=None):
  * run_sql_format_str(<sql>, l_vals, cursor_type=None )
  * run_transaction(l_statements, cursor_type=None )

  * getRecordsWhere( <table_name>, d_where )
  * getMaxRecordsPerGroup(<table_name>, <group_colname>, d_where )
  * getRecordsForGroupWithMax(<table_name>, <max_colname>, <group_colname>, d_where )
  * getMaxValueWhere(<table_name>, <max_colname>, d_where )
  * getLastRecordWhere(<table_name>, <timestamp_colname>, d_where )
  * getOldestRecordWhere(<table_name>, timestamp_colname, d_where )
  * getLastRecordFieldWhere( <table_name>, timestamp_colname, field_name, d_where )
  * getSingleRecord( <table_name>, d_where )
  * getRecordCount( <table_name> )
  * getRecordCountWhere( <table_name>, d_where )
  * getAllRecords( <table_name> )

  * update_single_record( <table_name>, d_updates, d_where ) 
  * update_multiple_records( <table_name>, l_data )
  * update_last_record(<table_name>, <timestamp_colname>, d_updates, d_where )
  * increment_value(<table_name>, <increment_colname>, d_where )
  * decrement_value(<table_name>, <decrement_colname>, d_where )

  * delete_single_record(<table_name> d_where )
  * delete_multiple_records(<table_name>, d_where )

  * submit_single_record( <table_name>, d_data )
  * submit_multiple_records( <table_name>, l_data )

  d_args = (
     'mdebug': <N>              (set debugging for method only)
     'cursor_type': <dict|...>  (set cursor-type: default=dict)
     'return': <data|default>   (set return-type)
              'default' for queries: d_return = { 'sql': <sql>, 'data': l_data, 'rows': <rows-returned> }
              'data' for queries: d_return = d_results['data']
              'default' for insert/update: d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': <affected-rows> }
              'data' for insert/updates: d_return = d_results['id']

      ## for queries only - get*()
     'select': l_select    (select keys for queries)
     'join': l_joins       ("join" information for queries)
     'orderby': l_orderby  ("orderby" data for queries)
     'limit': <N>          ("limit" information for queries)
    
     ## for inserts and updates only
     'validate': (0|1)     (validate affected rows matches expected inside method. Raise error if not) 
  )

 USAGE:  see TEST __main__ at bottom of file

"""

##----------------------------------------------------------------------------------------
import re
import sys
import time
import logging
import mysql.connector
from decorator import decorator 

from SqlBuilder import SqlBuilder

##----------------------------------------------------------------------------------------
##
## DEFAULTS: can be overridden by init()
##
DEBUG = 4 

## Connect on init() and leave open vs connect/disconnect on each transaction
PERSIST = 1 
 
##----------------------------------------------------------------------------------------
class InitError(Exception):
  pass

##----------------------------------------------------------------------------------------
class ConnectionError(Exception):
  pass

##----------------------------------------------------------------------------------------
class MissingAttributeError(Exception):
  pass

##----------------------------------------------------------------------------------------
class MethodInputError(Exception):
  pass

##----------------------------------------------------------------------------------------
class SchemaError(Exception):
  pass

##----------------------------------------------------------------------------------------
class QueryError(Exception):
  pass

##----------------------------------------------------------------------------------------
class SubmitError(Exception):
  pass

##----------------------------------------------------------------------------------------
class UpdateError(Exception):
  pass

##----------------------------------------------------------------------------------------
class DeleteError(Exception):
  pass

##----------------------------------------------------------------------------------------
class DBMethodDecorators(object):
  """
   Method decorator to ensure connection is up before a db call. 
   Close afterward if PERSIST=0
  """
  @decorator
  def connection_decorator(func, *args, **kwargs):
    self = args[0]
    if self.conn_handle is None: 
      self._log("DEBUG", "%s: Establishing new connection" % (self.oid))
      self.conn_handle = self.__class__.create_connection_handle(self.db_args) 
    d_results = func(*args, **kwargs)
    if not self.PERSIST: 
      self._log("DEBUG", "%s: [%s] Disconnecting non-persistant connection" % (self.oid, self.connection_id))
      self.__class__.close_connection(self.conn_handle)
    return (d_results)

##----------------------------------------------------------------------------------------
class MariaDB():
  ##-----------------------------------------------------------------------------

  def __init__(self, d_init_args):

    ## class-name 
    self.cname = self.__class__.__name__

    ## "object" id (appended to by child class) 
    self.oid = self.cname
    if 'caller' in d_init_args:
      caller = d_init_args['caller']
      self.oid = "%s.%s" % (caller, self.cname)

    self.PERSIST = PERSIST 
    self.DEBUG = DEBUG
    
    self.logger = None 
    if 'logger' in d_init_args: 
      self.logger   = d_init_args['logger']

    if 'debug' in d_init_args: 
      self.DEBUG   = d_init_args['debug']
   
    if 'persist' in d_init_args: 
      self.PERSIST = d_init_args['persist']

    self.db_args = None
    self.conn_handle = None 
    self.connection_id = None 

    ##################################################
    ## DATABASE connection
    ##################################################
    ## DB-Connection handle passed in
    if 'conn_handle' in d_init_args: 
      ch = d_init_args['conn_handle']
      if not isinstance(ch, mysql.connector.connection.MySQLConnection):
        raise InitError("%s: Input DB connection handle does not have valid type" % (self.oid))
      
      self.conn_handle = ch 
      self.connection_id = self.conn_handle.connection_id 
      self._log("INFO", "%s: Using established db connection - connection_id=[%s]" % (self.oid, self.connection_id))

    ## DB-args passed in
    else:
      self._log("INFO", "%s: Creating NEW db connection..." % (self.oid))
      ## database args 
      if 'db_args' not in d_init_args: 
        raise InitError("%s: Missing required init() arg: [db_args]" % (self.oid))
     
      d_db_args = d_init_args['db_args']
      self.db_args = d_db_args
   
      self._log('DEBUG', "%s: Attempting DB-connection: [%s]..." % (self.oid, str(d_db_args)))
      conn_handle = None
      try:
        conn_handle = self.__class__.create_connection_handle(d_db_args) 
      except Exception as e:
        raise InitError("%s: create_connection_handle() failed with exception: %s" % (self.oid, e))
   
      if conn_handle: 
        self.conn_handle = conn_handle
        cid = conn_handle.connection_id 
        self.connection_id = cid 
        self._log("INFO", "%s: Database connection successfully established - connection-id=[%s]" % (self.oid, cid))
      else:
        raise InitError("%s: Failed to initialize/test) DB connection" % (self.oid))

    ###################################################################
    ## PERSISTANCE
    ## If PERSIST==1, establish connection and keep open
    ## If PERSIST==0, establish connection just for validation on init() and then close 
    ##  (will be reconnected/dicsonnected on each method call) 
    if self.PERSIST: 
      self._log("DEBUG", "%s: [%s] Maintaining persistant connection (PERSIST=1)" % (self.oid, self.connection_id))
    else:
      self._log("DEBUG", "%s: [%s] NOT maintaining persistant connection (PERSIST=0)" % (self.oid, self.connection_id))
      self.conn_handle.close()
      self.conn_handle = None

  ##-----------------------------------------------------------------------------
  ## Class methods 
  ##-----------------------------------------------------------------------------
  @classmethod
  def create_connection_handle(cls, d_db_args):
    """ 
     Connect to database using passed DB args.
     Return the DB connection-handler. 
    """ 
    tag = "%s.create_connection_handle" % (cls.__name__)

    l_required = ['host', 'database', 'user', 'password' ]
    for arg in l_required:
      if arg not in d_db_args:
        raise KeyError("%s: Missing required database arg: [%s]" % (tag, arg)) 

    host =  d_db_args['host']
    database = d_db_args['database']
    user =  d_db_args['user']
    password =  d_db_args['password']

    conn_handle = None
    try: 
      conn_handle = mysql.connector.connect( host=host, user=user, password=password, database=database )
    except Exception as e: 
      raise ConnectionError("%s: mysql.connector.connect() failed with exception: %s" % (tag, e))

    return( conn_handle )
  
  ##-----------------------------------------------------------------------------
  @classmethod
  def close_connection(cls, conn_handle):
    """ 
     Dis-Connect from the passed database-connection 
     Return the DB connection-handler. 
    """ 
    if conn_handle is not None:
      conn_handle.close()
 
  ##-----------------------------------------------------------------------------
  ## Context-handler methods (with...) 
  ##-----------------------------------------------------------------------------
  def __enter__(self):
    """ 
     Called when object enters a "with" block. 
     Return "self"
    """ 
    if self.DEBUG > 2:
      self._log("DEBUG", "%s: _ENTER_ - Returning self..." % (self.oid))
    return( self )

  #----------------------------------------------------------------------------- 
  def __exit__(self, exc_type, exc_value, exc_traceback):
    """ Called when object leaves a "with" block """ 
    if exc_value is None:
      msg = "%s: __EXIT__: Cleaning up on normal close with no exceptions" % (self.oid)
      self._log('DEBUG', msg)
    else:
      msg = "%s: __EXIT__: Cleaning up on exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.oid, exc_type,exc_value, exc_traceback)
      self._log('ERROR', msg)

    ## Dis-Connect from DB 
    if self.conn_handle is not None:
      self._log('INFO', "%s: Closing OPEN DB-connection - connection-id=[%s]" % (self.oid, self.connection_id))
      self.__class__.close_connection(self.conn_handle)
 
  
  ##-----------------------------------------------------------------------------
  ## "Hidden" methods (intended for internal class use) 
  ##-----------------------------------------------------------------------------
  def __data_dump(self, data, title=None):
    """ Mimic Perl's data Dumper() """
    if title is None:
      title = 'DataDump'
    print("--START: %s-----------------" % (title) )
    print(data)
    print("--END-----------------------" )

  #----------------------------------------------------------------------------- 
  def _log(self, s_level, msg ):
    """Internal logging functionality"""
    if self.logger is None:
      print("%s: %s" % (s_level, msg))
    else:
      numeric_level = getattr(logging, s_level.upper(), None)
      if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
      self.logger.log( numeric_level, msg)

  ##--------------------------------------------------------------------------- 
  ## "Public" methods 
  #----------------------------------------------------------------------------- 
  def test(self):
    """ Execute a connection test: (describe <table_name>)"""
    table_name = self.table_name
    sql = "DESCRIBE %s" % (table_name)
    cursor_type = 'dict'

    d_results = None
    try:
      d_results = self.run_sql(sql, cursor_type)
    except Exception as e:
      raise
    return( d_results )

  ##----------------------------------------------------------------------------- 
  ## Decorated methods intended for internal use only
  ##----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def run_sql(self, sql, cursor_type=None):
    """
     Execute a passed SQL statement (can only be used for SELECT statements). 
     Used for complex SQL select statements.
     Return dict of results.
    """ 
    tag = self.oid + '.run_sql' 
    
    if cursor_type is None:
      cursor_type = 'dict'

    if re.match( "(update|insert|delete)", sql, re.I):
      raise MethodInputError("%s: Method cannot be used for (update|insert|delete)" % (tag))
      
    self._log("INFO", "%s: Executing SQL: %s" % (tag, sql))

    d_results = None 
    l_rows = [] 
    try:
      if cursor_type == 'dict':
        cur = self.conn_handle.cursor(dictionary=True) ## return data as a list of dictionaries
      else:
        cur = self.conn_handle.cursor() ## default cursor returns the data in a tuple of tuples
      cur.execute(sql) 
      l_rows = cur.fetchall()
      rowcount = cur.rowcount 
      desc = cur.description
      d_results = { 'sql': sql, 'data': l_rows, 'rows': rowcount, 'col_names': desc }
    except Exception as e:
      raise 

    return( d_results )

  ##----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def run_sql_format_str(self, sql, l_vals, cursor_type=None):
    """ 
     Execute a passed SQL statement (can only be used for SELECT statements) 
     Used for complex SQL select statements
     Return dict of results.
    """ 
    tag = self.oid + '.run_sql_format_str' 
    
    if cursor_type is None:
      cursor_type = 'dict'
    
    tuple_vals = tuple(l_vals)

    if re.match( "(update|insert|delete)", sql, re.I):
      raise MethodInputError("%s: Method cannot be used for (update|insert|delete)" % (tag))

    d_results = None 
    l_rows = [] 
    try:
      if cursor_type == 'dict':
        cur = self.conn_handle.cursor(dictionary=True) ## return data as a list of dictionaries
      else:
        cur = self.conn_handle.cursor() ## default cursor returns the data in a tuple of tuples
      cur.execute(sql, tuple_vals) 
      l_rows = cur.fetchall()
      rowcount = cur.rowcount 
      sql = cur._executed.decode() 
      desc = cur.description
      d_results = { 'sql': sql, 'data': l_rows, 'rows': rowcount, 'col_names': desc }
    except Exception as e:
      raise 

    return( d_results )

  ##----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def run_transaction(self, l_statements, cursor_type=None):
    """ 
     Execute a multiple SQL statements in an Atomic (all or nothing) transaction.
     Passed SQL statements must be fully formatted strings.
     Return dict of results.
    """ 
   
    tag = self.oid + '.run_transaction' 
      
    status = 0 

    try:
      if cursor_type == 'dict':
        cur = self.conn_handle.cursor(dictionary=True) ## return data as a list of dictionaries
      else:
        cur = self.conn_handle.cursor() ## default cursor returns the data in a tuple of tuples
      self.conn_handle.autocommit = false

      N = 0
      for sql in l_statements:
        ++N
        self._log("INFO", "%s: Executing transaction statement (%d): [%s]" % (tag, N, sql))
        cur.execute(sql) 

      self._log("INFO", "%s: Commiting transaction..." % (tag))
      self.conn_handle.commit() 
      self._log("INFO", "%s: Transaction successful" % (tag))
      status = 1 
    except Exception as e:
      self._log("ERROR", "%s: Transaction failed. Rolling back..." % (tag))
      self.conn_handle.rollback() 
      status = 0
      raise 

    return( status )

  #----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def runPreparedSqlRead(self, sql, l_vals, cursor_type=None): 
    """ 
     Execute a prepared SQL statement for SELECT statements.
     Return dict of results.
    """ 
   
    tag = self.oid + '.runPreparedSqlRead' 

    if cursor_type is None:
      cursor_type = 'dict'
    
    tuple_vals = tuple(l_vals)
 
    d_results = None 
    l_rows = [] 

    try:
      if cursor_type == 'dict':
        cur = self.conn_handle.cursor(dictionary=True) ## return data as a list of dictionaries
      else:
        cur = self.conn_handle.cursor() ## default cursor returns the data in a tuple of tuples
      ts_1 = time.perf_counter()
      cur.execute(sql, tuple_vals) 
      l_rows = cur.fetchall()
      ts_2 = time.perf_counter()
      rowcount = cur.rowcount 
      sql = cur._executed.decode()
      ts_elapsed = ts_2 - ts_1
      d_results = { 'sql': sql, 'data': l_rows, 'rows': rowcount, 'elapsed': ts_elapsed }
    except Exception as e:
      raise 
    
    self._log("DEBUG", "%s: Executed query: [%s]" % (tag, sql))

    return( d_results )

  #----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def runPreparedSqlInsert(self, sql, l_vals, cursor_type=None): 
    """ 
     Execute a prepared SQL statement for INSERT statements.
     Return dict of results.
    """ 
   
    tag = self.oid + '.runPreparedSqlInsert' 

    if cursor_type is None:
      cursor_type = 'dict'
    
    tuple_vals = tuple(l_vals)

    d_results = None 
    l_rows = [] 

    try:
      if cursor_type == 'dict':
        cur = self.conn_handle.cursor(dictionary=True) ## return data as a list of dictionaries
      else:
        cur = self.conn_handle.cursor() ## default cursor returns the data in a tuple of tuples
      cur.execute(sql, tuple_vals) 
      self.conn_handle.commit() 
      db_id = cur.lastrowid 
      rowcount = cur.rowcount 
      sql = cur._executed.decode()
      d_results = { 'sql': sql, 'id': db_id, 'rows': rowcount }
    except Exception as e:
      raise 

    return( d_results )

  #----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def runPreparedSqlUpdate(self, sql, l_vals, cursor_type=None): 
    """ 
     Execute a prepared SQL statement for UPDATE statements 
     Return dict of results.
    """ 
   
    tag = self.oid + '.runPreparedSqlUpdate' 

    if cursor_type is None:
      cursor_type = 'dict'
    
    tuple_vals = tuple(l_vals)

    d_results = None 

    try:
      if cursor_type == 'dict':
        cur = self.conn_handle.cursor(dictionary=True) ## return data as a list of dictionaries
      else:
        cur = self.conn_handle.cursor() ## default cursor returns the data in a tuple of tuples
      cur.execute(sql, tuple_vals) 
      self.conn_handle.commit() 
      rowcount = cur.rowcount 
      sql = cur._executed.decode()
      d_results = { 'sql': sql, 'rows': rowcount }
    except Exception as e:
      print(">>SQL: %s" % sql)
      ##self.__data_dump(tuple_vals, "TUPLE-VALUES")
      raise 

    return( d_results )

  #----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def runPreparedSqlDelete(self, sql, l_vals, cursor_type=None): 
    """ 
     Execute a prepared SQL statement for DELETE statements 
     Return dict of results.
    """ 
   
    tag = self.oid + '.runPreparedSqlDelete' 

    if cursor_type is None:
      cursor_type = 'dict'
    
    tuple_vals = tuple(l_vals)
 
    d_results = None 

    try:
      if cursor_type == 'dict':
        cur = self.conn_handle.cursor(dictionary=True) ## return data as a list of dictionaries
      else:
        cur = self.conn_handle.cursor() ## default cursor returns the data in a tuple of tuples
      cur.execute(sql, tuple_vals) 
      self.conn_handle.commit() 
      sql = cur._executed.decode()
      db_id = cur.lastrowid 
      rowcount = cur.rowcount 
      d_results = { 'sql': sql, 'id': db_id, 'rows': rowcount }
    except Exception as e:
      raise 

    return( d_results )

  ##----------------------------------------------------------------------------- 
  ## Methods intended for internal use
  ##-----------------------------------------------------------------------------
  def __insertRecord(self, table_name, d_kv, d_args=None): 
    """
     Insert a single row. Key/Value pairs are passed in d_kv.
     By default we do not check affected-rows here to identify successful submit.
     Optionally, (d_args['validate']=1) we can raise error inside this method if 
     submit does not result in affected rows = 1.
     Return DB record id
    """ 
    tag = self.oid + '.__insertRecord' 
    cursor_type = 'dict' 
    validate = 1 
    log = 1 
    
    if d_args is not None:  
      if 'validate' in d_args:
        validate = d_args['validate'] 
      if 'log' in d_args:
        log = d_args['log'] 

    l_select = []
    l_prepare_values = []
    l_fmts = []
    for k,v in d_kv.items():
      l_select.append(k) 
      l_prepare_values.append(v) 
      l_fmts.append('%s') 

    select_str = ",".join( l_select )
    val_fmt_str = ",".join( l_fmts )
    tuple_vals = tuple(l_prepare_values)

    sql = 'INSERT into ' + table_name + ' (' + select_str + ') VALUES (' + val_fmt_str + ')'
      
    db_id = None 
    try:
      d_results = self.runPreparedSqlInsert(sql, l_prepare_values, cursor_type)
      db_id = d_results['id'] 
      rowcount = d_results['rows'] 
      sql = d_results['sql'] 
    except Exception as e:
      raise 
   
    if d_results: 
      if log == 1:
        self._log("INFO", "%s: Inserted new record: SQL=[%s]" % (tag, sql))
 
      if rowcount != 1:
        msg = "%s: Affected rows (%s) does not match expected (1)" % (tag, rowcount)
        if validate == 1:
          raise SubmitError("%s. SQL=[%s]" % (msg, sql))
        else:
          self._log("WARNING", "%s" % (msg))
 
    if db_id is None:
      raise SubmitError("%s: Invalid DB id returned" % (tag))
 
    return( db_id )

  #----------------------------------------------------------------------------- 
  def __update_records(self, table_name, d_updates, d_where, d_args=None): 
    """
     Update one or more rows. Key/Value updates are passed in d_updates.
     By default we do not check affected-rows here to identify successful update.
     Optionally, (d_args['validate']=1 and d_args['expected']=<N>) we can raise 
     error inside this method if delete does not result in afftected rows = <N>.
     Return dict of results. 
    """
 
    tag = self.oid + '.__update_records' 
    cursor_type = 'dict' 
    validate = 1 
    log = 1 
    expected = None

    l_prepare_values = []
   
    if d_args:
      if 'expected' in d_args:
        expected = d_args['expected']
      if 'validate' in d_args:
        validate = d_args['validate'] 
      if 'log' in d_args:
        log = d_args['log'] 
    
    sql = 'UPDATE ' + table_name
    
    ## UPDATE string
    update_str = None 
    l_updates = []
    if len(d_updates.keys()) == 0:
      raise MethodInputError("%s: Zero updates passed in" % (tag))
    for k,v in d_updates.items():
      if v == 'NULL':
        l_updates.append( k + " = NULL" ) 
        ## do NOT append to l_prepare_values!
      else:

        ## check for increment/decrement expression ( update <table> set <value> = <value> + 1... )
        m = re.search("\s([+-])\s1", str(v)) 
        if m:
          op = m.group(1)
          inc_dec = "%s = %s %s 1" % (k, k, op) ## <value> = <value> + 1
          l_updates.append( inc_dec ) ## <value> = <value> + 1
 
        else: ## all other formats
          ## NOTE: "%s" is required regardless of the datatype of v. DO NOT change this!!!
          l_updates.append( k + """ = %s""" ) 
          l_prepare_values.append( v ) 

    update_str = ", ".join( l_updates )
    sql += " set " + update_str 
 
    ## WHERE clause - ABSOULTELY MUST have, else we update ALL rows!
    if len(d_where.keys()) == 0:
      raise MethodInputError("%s: No records specified for update" % (tag))
    d_where_results = SqlBuilder.sql_build_WHERE(d_where)
    l_prepare_values.extend( d_where_results['prepare_values'] )
    where_str = d_where_results['text']
    sql += " WHERE " + where_str 
  
    rowcount = 0 
    d_results = None  
    try:
      d_results = self.runPreparedSqlUpdate(sql, l_prepare_values, cursor_type)
      rowcount = d_results['rows'] 
      sql = d_results['sql'] 
    except Exception as e:
      raise 
   
    if d_results: 
      if log == 1:
        self._log("INFO", "%s: Updated records: [%s]: SQL=[%s]" % (tag, rowcount, sql))
    
    if expected:
      if expected != rowcount:
        msg = "%s: Affected rows (%s) does not match expected (%s)" % (tag, rowcount, expected)
        if validate == 1:
          self._log("ERROR", "%s" % (msg))
          raise UpdateError("%s. SQL=[%s]" % (msg, sql))
        else:
          self._log("WARNING", "%s" % (msg))
    
    return( d_results )

  #----------------------------------------------------------------------------- 
  def __delete_records(self, table_name, d_where, d_args=None): 
    """
     DELETE one or more rows.  Key/Value pairs are passed in d_kv.
     By default we do not check affected-rows here to identify successful delete.
     Optionally, (d_args['validate']=1 and d_args['expected']=<N>) we can raise 
     error inside this method if delete does not result in afftected rows = <N>.
     Return dict of results. 
    """ 
    tag = self.oid + '.__delete_records' 
    cursor_type = 'dict' 
    validate = 1 
    log = 1 
    expected = None 

    l_prepare_values = []
   
    if d_args:
      if 'expected' in d_args:
        expected = d_args['expected']
      if 'validate' in d_args:
        validate = d_args['validate'] 
      if 'log' in d_args:
        log = d_args['log'] 
   
    sql = 'DELETE from ' + table_name
    
    ## WHERE clause - ABSOULTELY MUST have, else we DELETE ALL rows!
    if len(d_where.keys()) == 0:
      raise MethodInputError("%s: No records specified for delete" % (tag))
    d_where_results = SqlBuilder.sql_build_WHERE(d_where)
    l_prepare_values.extend( d_where_results['prepare_values'] )
    where_str = d_where_results['text']
    sql += " WHERE " + where_str 
    
    rowcount = 0
    d_results = None  
    try:
      d_results = self.runPreparedSqlDelete(sql, l_prepare_values, cursor_type)
      db_id = d_results['id'] 
      rowcount = d_results['rows'] 
      sql = d_results['sql'] 
    except Exception as e:
      raise 
     
    if d_results:
      if log == 1: 
        self._log("INFO", "%s: Deleted records: [%s]: SQL=[%s]" % (tag, rowcount, sql))
    
    if expected:
      msg = "%s: Affected rows (%s) does not match expected (%s)" % (tag, rowcount, expected)
      if validate == 1:
        if expected != rowcount:
          self._log("ERROR", "%s" % (msg))
          raise DeleteError("%s. SQL=[%s]" % (msg, sql))
      else:
        self._log("WARNING", "%s" % (msg))
    
    return( d_results )

  #----------------------------------------------------------------------------- 
  def __getRecords(self, table_name, d_where, d_args=None): 
    """ 
     Return one or more rows.
     Optionally, with d_args['expected']=<N> and validate=1, we can raise error inside 
     this method if affected rows != <N> 
     SELECT fields are passed in l_select (default: l_select=['*'] to select ALL)
     WHERE clause is created by SqlBuilder.sql_build_WHERE() 
    
      d_where = {"key1": "val1", ... "keyN": "valN" }
    
      d_args = ( 
                'select':  l_select, 
                'join':    d_join, 
                'orderby': l_orderby, 
                'limit':   <N>: 
              )
    
      l_joins = [
                  { "LEFT JOIN":  ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
                  { "JOIN":       ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
                  { "RIGHT JOIN": ["<join_to_table>", "<left_colname>", "<right_colname>" ] }
                ]
    
      l_orderby = [ {"col1": "<desc|asc>" }, ... {"colN": "<desc|asc>" } ]
    
    
     RETURN (one of two possible formats):
      full-results (default):           d_results = { 'sql': sql, 'data': l_rows, 'rows': rowcount }
      data-only (d_args['dataonly']=1): d_data = d_results['data']
    """ 
 
    tag = self.oid + '.__getRecords' 

    self._log("INFO", "Getting records: [%s]" % (tag))  
 
    cursor_type = 'dict'
    validate = 1 
    expected = None 

    l_prepare_values = []
   
    l_select = []
    l_joins = [] 
    l_orderby = [] 
    l_groupby = [] 
    limit = None
    return_type = 'default'
 
    if d_args is not None: 

      ## Args for SQL statement 
      if 'select' in d_args:
        l_select = d_args['select'] 
      if 'join' in d_args:
        l_joins = d_args['join'] 
      if 'orderby' in d_args:
        l_orderby = d_args['orderby'] 
      if 'groupby' in d_args:
        l_groupby = d_args['groupby'] 
      if 'limit' in d_args:
        limit = d_args['limit'] 

      ## Args for processing 
      if 'expected' in d_args:
        expected = d_args['expected'] 
      if 'validate' in d_args:
        validate = d_args['validate'] 
      if 'cursor_type' in d_args:
        cursor_type = d_args['cursor_type'] 
      if 'return_type' in d_args:
        return_type = d_args['return_type'] 
      if 'dataonly' in d_args:
        return_type = 'data' 

    ##=====================
    ## Build SQL statement

    ## SELECT
    sql = SqlBuilder.sql_build_SELECT(table_name, l_select)

    ## JOIN
    join_str = SqlBuilder.sql_build_JOIN(l_joins)
    if join_str:
      sql += " " + join_str

    ## WHERE
    d_where_results = SqlBuilder.sql_build_WHERE(d_where)
    l_prepare_values = d_where_results['prepare_values']
    where_str = d_where_results['text']
    if where_str:
      sql += " WHERE " + where_str

    ## ORDER BY 
    order_str = SqlBuilder.sql_build_ORDER(l_orderby)
    if order_str:
      sql += " " + order_str

    ## GROUP BY (careful, you may need an aggregate function!)
    group_str = SqlBuilder.sql_build_GROUP(l_groupby)
    if group_str:
      sql += " " + group_str

    ## LIMIT 
    if limit is not None:
      try:
        limit = int(limit)
      except ValueError:
        raise 
      sql += " LIMIT %d" % limit
 
    ##=====================
    ## Execute
    
    ##print("\nSQL: %s\n" % (sql))
    ##print("\nPREPARE %s" % (l_prepare_values))
 
    o_return = None  
    d_results = None  
    try:
      d_results = self.runPreparedSqlRead(sql, l_prepare_values, cursor_type)
    except Exception as e:
      raise 
     
    rows = d_results['rows']
    sql = d_results['sql']
    
    ##=====================
    ## Process results 

    if rows == 0:
      self._log("INFO", "No records returned from query: [%s]" % (sql))  
    else:
      self._log("INFO", "Records returned from query (%s): [%s]" % (rows,sql))  
      ##self.__data_dump(d_results) ## uncomment for troubleshooting

    if expected:
      if rows != expected: 
        msg = "Records returned (%s) does not match expected=(%s) for query: [%s]" % (rows, expected, sql)
        self._log("WARNING", msg)  
        if validate == 1:
          self._log("ERROR", msg)  
          raise QueryError(msg)
 
    if return_type == 'data':
      o_return = d_results['data']
    else:
      o_return = d_results

    return( o_return )

  ##----------------------------------------------------------------------------- 
  ## Methods intended for PUBLIC use
  ##-----------------------------------------------------------------------------
  def test(self):
    """ Execute a connection test (show tables)""" 
    sql = "show tables"

    d_results = None
    try:
      d_results = self.run_sql(sql)
    except Exception as e:
      raise 
    return( d_results )
 
  #----------------------------------------------------------------------------- 
  def getSingleRecord(self, table_name, d_where, d_args=None): 
    """
     Query for single row. Raise exception if more than one row is returned (unless validate=0). 
     RETURN: full-results or data-only
    """ 
    tag = self.oid + '.getSingleRecord' 

    return_type = 'default' 
    validate = 0 
    
    if not d_args:
      d_args = {}
        
    if 'dataonly' in d_args:
      return_type = 'data' 
    if 'return_type' in d_args:
      return_type = d_args['return_type'] 
    if 'validate' in d_args:
      validate = d_args['validate'] 

    if validate == 1:
      d_args['expected'] = 1
    
    o_return = None
    try:
      o_return = self.__getRecords(table_name, d_where, d_args)
    except Exception as e:
      raise 
        
    if o_return is not None:    ## o_return could be [] if "datonly".
      if return_type == 'data': 
        ## since we are querying for a single record, we return first element only 
        if len(o_return) == 1:   ## we've already validated that len() is not > 1
          o_return = o_return[0] ## this is a dict
        else:
          o_return = None        ## rather than returning []

    return( o_return )

  #-----------------------------------------------------------------------------
  def getRecordsWhere(self, table_name, d_where, d_args=None):
    """
     Get specific records in a table
     RETURN: full-results or data-only
    """
    tag = self.oid + '.getRecordsWhere'

    if not d_args:
      d_args = {}
   
    o_return = None
    try:
      o_return = self.__getRecords(table_name, d_where, d_args)
    except Exception as e:
      raise 
    
    return( o_return )
  
  #-----------------------------------------------------------------------------
  def getMaxRecordsPerGroup(self, table_name, group_colname, d_where, d_args=None):
    """ 
     Get the max value of a column for each grouping (of another column)
     Example, suppose we want to know each students highest score from
     a table of all the scores for all students.
       SELECT MAX(score), name FROM student_scores 
         [WHERE name in ("bill","joe","bob")] # optional
       GROUP by name 
    
      RETURN: list of matching records, or [] if no match 
    """ 
    tag = self.oid + '.getMaxRecordsPerGroup'

    if not d_args:
      d_args = {}
     
    ## One might be tempted to pass these to this method. 
    if 'groupby' in d_args:
      raise QueryError("%s: This method does not support a GROUP-BY clause" % (tag))
    
    d_args['orderby'] = [ {max_colname: 'desc'} ]
    d_args['dataonly'] = 1 

    l_records = [] 
    try:
      l_records = self.__getRecordsWhere(table_name, d_where, d_args)
    except Exception as e:
      raise 

    return( l_records )

  #-----------------------------------------------------------------------------
  def getRecordsForGroupWithMax(self, table_name, max_colname, group_colname, d_where, d_args=None):
    """ 
     Get all the records for the "group" which has the largest value of a column.
     Example, suppose we want to know ALL the scores for the student which has
     the highest score (from a table of all the scores for all students).
       SELECT * FROM student_scores where name = 
         (select name from student_scores 
           [WHERE name in ("bill","joe","bob")] 
          ORDER BY score DESC LIMIT 1); 
     RETURN: list of matching records, or [] if no match 
    """ 

    tag = self.oid + '.getRecordsForGroupWithMax'
    
    if not d_args:
      d_args = {}
    
    ## One might be tempted to pass these to this method. 
    if 'groupby' in d_args:
      raise QueryError("%s: This method does not support a GROUP-BY clause" % (tag))
    if 'orderby' in d_args:
      raise QueryError("%s: This method does not support a ORDER-BY clause" % (tag))
   
    ## First build sub-query which creates our grouping 
    sub_select = "SELECT " + group_colname + " FROM " + table_name 

    print("\n\nSUB-SELECT: %s\n\n" % sub_select)
   
    ## WHERE
    l_where_values = []
    where_str = None
    d_where_results = SqlBuilder.sql_build_WHERE(d_where)
    l_where_values = d_where_results['prepare_values']
    where_str = d_where_results['text']
    
    if where_str:
      sub_select += " WHERE " + where_str

    sub_query = sub_select + " ORDER BY " + max_colname + " DESC LIMIT 1"
    
    ## Now the full sql in which we select all fields from the records in the sub-query results 
    sql = "SELECT * FROM " + table_name + " WHERE " + group_colname + " = (" + sub_query + ")" 

    ## d_results = { 'sql': sql, 'data': l_rows, 'rows': rowcount, 'col_names': desc }
    d_results = None 
    try:
      d_results = self.run_sql_format_str(sql, l_where_values)
    except Exception as e:
      raise 

    l_records = []
    if d_results: 
      l_records = d_results['data'] 

    print("DONE: %s\n" % (l_records))

    return( l_records )

  #-----------------------------------------------------------------------------
  def getMaxValueWhere(self, table_name, max_colname, d_where, d_args=None):
    """ 
     Simple query for max value of a column 
     Example, suppose we want to know the highese score of all students scores
       SELECT * FROM student_scores 
         [WHERE name in ("bill","joe","bob")] # optional
       ORDER BY score DESC LIMIT 1; 
     RETURN: dict record, or None if no match 
    """ 

    tag = self.oid + '.getMaxValueWhere'
    
    if not d_args:
      d_args = {}
     
    ## One might be tempted to pass these to this method. 
    if 'groupby' in d_args:
      raise QueryError("%s: This method does not support a GROUP-BY clause" % (tag))
    if 'orderby' in d_args:
      raise QueryError("%s: This method does not support a ORDER-BY clause" % (tag))

    d_args['dataonly'] = 1 
    d_args['orderby'] = [ {max_colname: 'desc'} ]
    d_args['limit'] = 1 

    d_record = None 
    try:
      d_record = self.__getSingleRecord(table_name, d_where, d_args)
    except Exception as e:
      raise 

    return( d_record )

  #-----------------------------------------------------------------------------
  def getLastRecordWhere(self, table_name, timestamp_colname, d_where, d_args=None):
    """ 
     Get the LAST (i.e. most-recent) record in a table.
     Essentially synonomous with getMaxValueWhere().
     Depending on the timestamp_colname this may not be the most recently
     inserted record. It could be an update-timestamp in which case it
     returns the record with the most-recent update. 
     RETURN: dict - d_record
    """ 

    tag = self.oid + '.getLastRecordWhere'
    
    table_name = self.table_name

    if not d_args:
      d_args = {}
      
    d_where[timestamp_colname] = '!NULL'

    d_args['limit'] = 1 
    d_args['dataonly'] = 1 
    d_args['orderby'] = [ {timestamp_colname: 'desc'} ]

    l_data = [] 
    try:
      l_data = self.__getRecords(table_name, d_where, d_args)
    except Exception as e:
      raise 
   
    d_record = None 
    count = len(l_data)
    if count == 0:
      self._log("INFO", "%s: NO records found in table=[%s] for %s" % (self.oid, table_name, d_where))  
    else:
      if count == 1:
        d_record = l_data[0] 
      else:
        raise QueryError("%s: Invalid record count: [%s]" % (tag, count))

    return( d_record )

  #-----------------------------------------------------------------------------
  def getOldestRecordWhere(self, table_name, timestamp_colname, d_where, d_args=None):
    """ 
     Similar to getLastRecordWhere() but reversed timestamp ordering.
     Get the "OLDEST" record in a table.
     Depending on the timestamp_colname this may not be the "oldest" in
     terms of insert. It could be an update-timestamp in which case it
     returns the record with the oldest update. 
     RETURN: dict - d_record
    """ 

    tag = self.oid + '.getOldestRecordWhere'
    
    if not d_args:
      d_args = {}
      
    d_args['limit'] = 1 
    d_args['dataonly'] = 1 
    d_args['orderby'] = [ {timestamp_colname: 'asc'} ]

    l_data = [] 
    try:
      l_data = self.__getRecords(table_name, d_where, d_args)
    except Exception as e:
      raise 
   
    d_record = None 
    count = len(l_data)
    if count == 0:
      self._log("INFO", "%s: NO records found in table=[%s] for %s" % (self.oid, table_name, d_where))  
    else:
      if count == 1:
        d_record = l_data[0] 
      else:
        raise QueryError("%s: Invalid record count: [%s]" % (tag, count))

    return( d_record )

  #-----------------------------------------------------------------------------
  def getLastRecordFieldWhere(self, table_name, timestamp_colname, field_name, d_where, d_args=None):
    """
     Get LAST (most-recent) record in a table and return a specified field from that record
     RETURN: value of field_name 
    """
    tag = self.oid + '.getLastRecordFieldWhere'

    if not d_args:
      d_args = {}
    d_args['select'] = [ field_name ] 

    value = None
    try:
      d_record = self.getLastRecordWhere(d_where, timestamp_colname, d_args)
    except Exception as e:
      raise

    if d_record:
      if field_name in d_record:
        value = d_record[field_name]
      else:
        raise SchemaError("Unknown column: [%s]" % field_name)

    return( value )

  #-----------------------------------------------------------------------------
  def getRecordCountWhere(self, table_name,  d_where, d_args=None):
    """
     Get record count of specific records in a table
     RETURN: <count> 
    """
    tag = self.oid + '.getRecordCountWhere'

    if not d_args:
      d_args = {}
    
    sql = "SELECT count(*) as count from %s" % (table_name)
    cursor_type = 'dict'
  
    ## WHERE
    l_prepare_values = []
    where_str = None
    d_where_results = SqlBuilder.sql_build_WHERE(d_where)
    l_prepare_values = d_where_results['prepare_values']
    where_str = d_where_results['text']
    if where_str:
      sql += " WHERE " + where_str
 
    count = -1
    d_results = None

    try:
      if where_str is None:
        d_results = self.run_ql(sql, cursor_type)
      else:
        d_results = self.runPreparedSqlRead(sql, l_prepare_values, cursor_type)
    except Exception as e:
      raise

    if d_results is not None:
      l_data = d_results['data']
      d_data = l_data[0]
      count = d_data['count']

    if count < 0:
      raise QueryError("%s: Invalid record count: [%s]" % (tag, count))

    return( count )

  #-----------------------------------------------------------------------------
  def getRecordCount(self, d_args=None):
    """
     Get record count of all records in a table
     RETURN: <count> 
    """
    tag = self.oid + '.getRecordCount'

    if not d_args:
      d_args = {}

    d_where = {}
    try:
      count = self.getRecordCountWhere(d_where, d_args)
    except Exception as e:
      raise

    return( count )

  #-----------------------------------------------------------------------------
  def getAllRecords(self, table_name, d_args=None):
    """
     Get all records in a table
     RETURN: full-results or data-only
    """
    tag = self.oid + '.getAllRecords'

    if not d_args:
      d_args = {}

    if 'limit' in d_args:
      raise MethodInputError("%s: Incorrect use of method: getAllRecords() - LIMIT unsupported" % (tag))

    d_where = {}
    o_return = None
    try:
      o_return = self.__getRecords(table_name, d_where, d_args)
    except Exception as e:
      raise 

    return( o_return )

  #-----------------------------------------------------------------------------
  def submit_single_record(self, table_name, d_data, d_args=None):
    """ 
     Submit one new record. 
     RETURN: new database id 
    """ 
    
    tag = self.oid + '.submit_single_record'

    if not isinstance(d_data, dict):
      raise MethodInputError("%s: Method requires input data dict" % (tag))

    if not d_args:
      d_args = {}

    db_id = None
    try:
      db_id = self.__insertRecord(table_name, d_data, d_args)
    except Exception as e:
      raise 

    return( db_id )

  #-----------------------------------------------------------------------------
  def submit_multiple_records(self, table_name, l_data, d_args=None):
    """
     Submit multiple new records. 
     RETURN: list of new database ids:  l_dbids = [] 
     If persist==0, set persist=1 for all row inserts and then reset persist=0 
    """ 
    tag = self.oid + '.submit_multiple_records'

    if not isinstance(l_data, list):
      raise MethodInputError("%s: Method requires input data list" % (tag))
    
    mdebug = 0 

    if not d_args:
      d_args = {}
    
    if 'debug' in d_args:
      mdebug = d_args['debug']
   
    l_db_ids = []
   
    persist_reset = 0 
    if self.persist == 0:
      persist_reset = 1 
      self.persist = 1
    for d_data in l_data:
      try:
        db_id = self.__insertRecord(table_name, d_data, d_args)
        l_db_ids.append(db_id) 
      except Exception as e:
        raise 

    if persist_reset == 1:
      self.persist = 0 

    return( l_db_ids )

  #-----------------------------------------------------------------------------
  def increment_value(self, table_name, increment_colname, d_where, d_args=None):
    """ 
     Update a record with an incremented value (update <table> set <value> = <value> + 1 WHERE...)
     RETURN: 
       default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
       data-only:  N = d_results['rows']
    """ 
    
    tag = self.oid + '.increment_value'
    
    if not isinstance(d_where, dict):
      raise MethodInputError("%s: Method requires input data dict: d_where" % (tag))

    return_type = 'rows'

    if not d_args:
      d_args = {}

    if 'return_type' in d_args:
      return_type = d_args['return_type']

    new_value = "%s + 1" % (increment_colname) ## must have single space around "+"
    d_updates = { increment_colname: new_value } 

    d_results = None 
    try:
      d_results = self.__update_records(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def decrement_value(self, table_name, decrement_colname, d_where, d_args=None):
    """ 
     Update a record with an decremented value (update <table> set <value> = <value> - 1 WHERE...)
     RETURN: 
       default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
       data-only:  N = d_results['rows']
    """ 
    
    tag = self.oid + '.decrement_value'
    
    if not isinstance(d_where, dict):
      raise MethodInputError("%s: Method requires input data dict: d_where" % (tag))

    return_type = 'rows'

    if not d_args:
      d_args = {}

    if 'return_type' in d_args:
      return_type = d_args['return_type']

    new_value = "%s - 1" % (decrement_colname) ## must have single space around "-"
    d_updates = { decrement_colname: new_value } 

    d_results = None 
    try:
      d_results = self.__update_records(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def update_multiple_records(self, table_name, d_updates, d_where, d_args=None):
    """ 
     Update one or more records. 
     RETURN: 
       default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
       data-only:  N = d_results['rows']
    """ 
    
    tag = self.oid + '.update_multiple_records'
    
    if not isinstance(d_updates, dict):
      raise MethodInputError("%s: Method requires input data dict: d_updates" % (tag))
    if not isinstance(d_where, dict):
      raise MethodInputError("%s: Method requires input data dict: d_where" % (tag))

    return_type = 'rows'

    if not d_args:
      d_args = {}

    if 'return_type' in d_args:
      return_type = d_args['return_type']

    d_results = None 
    try:
      d_results = self.__update_records(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def update_single_record(self, table_name, d_updates, d_where, d_args=None):
    """ 
     Update single record. 
     RETURN: 
      default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
       data-only:  N = d_results['rows']
    """ 
    
    tag = self.oid + '.update_single_record'
    
    if not isinstance(d_updates, dict):
      raise MethodInputError("%s: Method requires input data dict: d_updates" % (tag))
    if not isinstance(d_where, dict):
      raise MethodInputError("%s: Method requires input data dict: d_where" % (tag))

    return_type = 'rows'
    
    if not d_args:
      d_args = {}
 
    ## By default we assume the record exists so consider it an error if not 
    expected = 1
    validate = 1

    d_args['limit'] = 1 

    if 'return_type' in d_args:
      return_type = d_args['return_type']
    if 'expected' in d_args:
      expected = d_args['expected']
    if 'validate' in d_args:
      validate = d_args['validate']

    d_results = None 
    try:
      d_results = self.__update_records(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def update_last_record(self, table_name, timestamp_colname, d_updates, d_where, d_args=None):
    """ 
     Update the LAST record based on a timestamp column. 
     RETURN: 
       default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
       data-only:  N = d_results['rows']
    """ 
    tag = self.oid + '.update_last_record'
    
    if not isinstance(d_updates, dict):
      raise MethodInputError("%s: Method requires input data dict" % (tag))

    return_type = 'rows'
    if not d_args:
      d_args = {}

    if 'return_type' in d_args:
      return_type = d_args['return_type']
    
    d_args['expected'] = 1 
    d_args['validate'] = 1 
    d_args['limit'] = 1 
    d_args['orderby'] = [ {timestamp_colname: 'desc'} ]
   
    d_results = None 
    try:
      d_results = self.__update_records(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise error 
    
    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def delete_single_record(self, table_name, d_where, d_args=None):
    """ 
     Delete single record. 
     RETURN: d_results, or affected-rows (if return_type=rows) 
    """ 

    tag = self.oid + '.delete_single_record'
    
    return_type = 'rows'
   
    ## By default we assume the record exists so consider it an error if not 
    validate = 1
    expected = 1

    if not d_args:
      d_args = {}
    if 'validate' in d_args:
      validate = d_args['validate']
    if 'expected' in d_args:
      expected = d_args['expected']

    if 'return_type' in d_args:
      return_type = d_args['return_type']

    d_results = None 
    try:
      d_results = self.__delete_records(table_name, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def delete_multiple_records(self, table_name, d_where, d_args=None):
    """ 
     Delete multiple records. 
     RETURN: d_results, or affected-rows (if return_type=rows) 
    """ 

    tag = self.oid + '.delete_mutliple_records'
    
    return_type = 'rows'
    if not d_args:
      d_args = {}
    
    if 'return_type' in d_args:
      return_type = d_args['return_type']

    d_results = None 
    try:
      d_results = self.__delete_records(table_name, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def get_db_conn_handle(self):
    """ return self.conn_handle (could be None) """
    return(self.conn_handle)

  #-----------------------------------------------------------------------------
  def set_db_conn_handle(self, conn_handle):
    """ set self.conn_handle """

    if not isinstance(ch, mysql.connector.connection.MySQLConnection):
      raise MethodInputError("%s: Input DB connection handle does not have valid type" % (self.oid))

    self.conn_handle = conn_handle

    return(1)

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":

  myname = 'mdb_tester'

  d_db_args = {
    'env':      'test',
    'host':     'localhost', 
    'database': 'sars',
    'user':     'sars_ro',
    'password': '!SarS_RO!'
  } 

  d_init_args = { 'db_args': d_db_args }

  ## Instantiate MariaDB handler
  try:
    db_h = MariaDB(d_init_args)
  except Exception as e:
    print("%s: MariaDB().init() failed with exception: %s" % (myname, e))
    sys.exit(1) 


  with db_h:
    print("%s: TESTING DB connection for db_args: [%s]" % (myname, str(d_db_args)))
    try:
      d_results = db_h.test()
      sql = d_results['sql']
      rows = d_results['rows']
      data = d_results['data']
      print("%s: SQL: [%s]" % (myname, sql))
      print("%s: ROWS-RETURNED: [%d]" % (myname, rows))
      print("%s: DATA: %s" % (myname, data))
    except Exception as e:
      print("%s: MariaDB().test() failed with exception: %s" % (myname, e))
      sys.exit(1) 
