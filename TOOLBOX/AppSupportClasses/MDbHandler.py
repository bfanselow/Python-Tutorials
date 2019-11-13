"""

 Class: MDbHandler
 Child-class of parent-class: StdApp()

 Python3 Parent DB-access class for Maria (mysql) Databases
 
 Usage:
  Create child class specific to some table in the DB (i.e. MDbHandler_my_table.py)
  In script which invokes this child-class:
    import DATABASE as config_db
    ...
    try:
      DBH = MDbHandler_my_table({ 'config_db': config_db, 'storage_id': <storage_id>})
    except Exception as e:
      raise
    ...
    with DBH:
      DBH.<func>()...
      ...
    

 Requires: 
   mysql-connector: (pip3 install mysql-connector)

 Uses the concept of "phases" to handle mutiple tables in same database
 with same table-name base, suffixed by what we refer to as the "phase".


 =====================================================================
 Public methods:

  1)  getDbConnHandle()
  2)  getSingleRecord( <table_name>, d_where, d_args=None)
  3)  getRecordsWhere( <table_name>, d_where, d_args=None)
  4)  getRecordCount( <table_name>, d_args=None)
  5)  getRecordCountWhere( <table_name>, d_where, d_args=None)
  6)  getAllRecords( <table_name>, d_args=None)
  7)  submitSingleRecord( <table_name>, d_data, d_args=None)
  8)  submitMultipleRecords( <table_name>, l_data, d_args=None)
  9)  updateSingleRecord( <table_name>, d_data, d_args=None)
  10) updateMultipleRecords( <table_name>, l_data, d_args=None)

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
import mysql.connector as mdb ## notice dot replaces dash on import
from decorator import decorator 

## custom imports  
import utils
from CustomExceptions import ReqArgError, InitError, InvalidLogHandle, PhaseError
from StdApp import StdApp 

##----------------------------------------------------------------------------------------
##
## DEFAULTS: can be overridden by init()
##
DEBUG = 4 

## Connect on init() and leave open vs connect/disconnect on each transaction
PERSIST = 1 
 
##----------------------------------------------------------------------------------------
class DbConnectError(Exception):
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

  ## Ensure connection is up before a db call. Close afterward if PERSIST=0
  @decorator
  def connection_decorator(func, *args, **kwargs):
    self = args[0]
    if self.conn_handle is None: 
      self.log("DEBUG", "%s: Establishing transaction-specific connection" % (self.oid))
      self.conn_handle = self.connect() 
    d_results = func(*args, **kwargs)
    if not self.PERSIST: 
      self.log("DEBUG", "%s: Disconnecting transaction-specific connection" % (self.oid))
      self.conn_handle = self.disConnect() 
    return (d_results)

##----------------------------------------------------------------------------------------
class MDbHandler(StdApp):

  def __init__(self, d_init_args):

    try:
      StdApp.__init__(self, d_init_args) ## sets up logging
    except Exception as e:
      raise
   
    ## class-name 
    self.cname = self.__class__.__name__

    ## "object" id (appended to by child class) 
    self.oid = self.cname
    if 'caller' in d_init_args:
      caller = d_init_args['caller']
      self.oid = "%s.%s" % (caller, self.cname)

    self.PERSIST = PERSIST 
    self.DEBUG = DEBUG
    self.all_phases = None 
    self.phase = None 

    if 'debug' in d_init_args: 
      self.DEBUG   = d_init_args['debug']
   
    if 'persist' in d_init_args: 
      self.PERSIST = d_init_args['persist']

    ################################################
    ##
    ## Configure multiprocess-queue logging in StdApp() using passed MPQ
    ##
    if 'mplq' in d_init_args:
      MPQ = d_init_args['mplq'] ## MPQ is multiprocessing.Queue created by a parent class
      try:
         self.configureMpqLogging(MPQ)
      except Exception as e:
        raise InitError("%s: configureMpqLogging() failed with exception: %s" % (self.cname,e))

    self.storage_id = None 
    self.d_db_args = None
    self.conn_handle = None 
    self.connection_id = None 

    ##################################################
    ## DATABASE Configuration and connection
    ## 

    ## DB-Connection handle passed in
    if 'conn_handle' in d_init_args: 
      self.conn_handle = d_init_args['conn_handle']
      self.connection_id = self.conn_handle.connection_id 
      self.log("INFO", "%s: Using established db connection: id=[%s], connection_id=[%s]" % (self.oid, self.connection_id))

    ## DB-Connection handle NOT passed in
    else:

      ## db-config-module 
      if 'config_module' in d_init_args: 
        config_module = d_init_args['config_module']
      else:
        raise InitError("%s: Missing required init() arg: [config_module]" % (self.oid))
   
      ## storge-id 
      if 'storage_id' in d_init_args: 
        storage_id = d_init_args['storage_id']
      else:
        raise InitError("%s: Missing required init() arg: [storage_id]" % (self.oid))
  
      self.log("DEBUG", "%s: Reading database args for db-id=[%s] from file [%s]" % (self.oid, storage_id, config_module.__file__))

      if hasattr(config_module, storage_id):
        d_db_args = getattr(config_module, storage_id) 
      else:
        raise InitError("%s: DB-config does not have storage_id: [%s]" % (self.oid, storage_id))

      if 'env' not in d_db_args:
        raise InitError("%s: Missing required (%s) DB arg: [env]" % (self.oid, storage_id))
      if 'host' not in d_db_args:
        raise InitError("%s: Missing required (%s) DB arg: [host]" % (self.oid, storage_id))
      if 'db_user' not in d_db_args:
        raise InitError("%s: Missing required (%s) DB arg: [db_user]" % (self.oid, storage_id))
      if 'db_pw' not in d_db_args:
        raise InitError("%s: Missing required (%s) DB arg: [db_pw]" % (self.oid, storage_id))
      if 'db_name' not in d_db_args:
        raise InitError("%s: Missing required (%s) DB arg: [db_name]" % (self.oid, storage_id))
    
      self.d_db_args = d_db_args 
      self.storage_id = storage_id 
   
      conn_handle = None
      try:   
        conn_handle = self.connect() 
      except Exception as e:
        raise
   
      if conn_handle: 
        self.conn_handle = conn_handle
        cid = conn_handle.connection_id 
        self.connection_id = cid 
        self.log("INFO", "%s: Database connection established for db-id=[%s], connection-id=[%s]" % (self.oid, storage_id, cid))
      else:
        raise InitError("%s: Failed to initialize/test) DB connection: db-id=[%s]" % (self.oid, storage_id))

    ###################################################################
    ## PERSISTANCE
    ## If PERSIST==1, establish connection and keep open
    ## If PERSIST==0, establish connection just for validation on init() and then close 
    ##  (will be reconnected/dicsonnected on each method call) 
    if self.PERSIST: 
      self.log("DEBUG", "%s: Maintaining persistant connection for db-id=[%s] (PERSIST=1)" % (self.oid, storage_id))
    else:
      self.log("DEBUG", "%s: NOT maintaining persistant connection for db-id=[%s] (PERSIST=0)" % (self.oid, storage_id))
      self.conn_handle.close()
      self.conn_handle = None

  ##-----------------------------------------------------------------------------
  ## "Hidden" methods intended for internal class use 
  ##-----------------------------------------------------------------------------

  def __enter__(self):
    ##
    ## Called when object enters a "with" block. 
    ##
    if self.DEBUG > 2:
      self.log("DEBUG", "%s: _ENTER_ - Returning self..." % (self.oid))
    return( self )

  #----------------------------------------------------------------------------- 
  def __exit__(self, exc_type, exc_value, exc_traceback):
    ##
    ## Called when object leaves a "with" block 
    ##
    if exc_value is None:
      msg = "%s: __EXIT__: Cleaning up on normal close with no exceptions" % (self.oid)
      self.log('DEBUG', msg)
    else:
      msg = "%s: __EXIT__: Cleaning up on exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.oid, exc_type,exc_value, exc_traceback)
      self.log('ERROR', msg)

    self.resourceCleanup() 

  #----------------------------------------------------------------------------- 
  def __sqlBuilder_SELECT(self, table_name, l_select):

    ##
    ## Builds the "SELECT ..." portion of an sql query "SELECT <select-list> from table"
    ## Return a text string
    ##

    if len(l_select) == 0:
      l_select = ['*']
    select_str = ",".join( l_select )

    text = "SELECT " + select_str + " FROM " + table_name
    return( text )
 
  #----------------------------------------------------------------------------- 
  def __sqlBuilder_JOIN(self, l_joins):

    ## Builds the "JOIN ..." portion of an sql query: "LEFTJOIN <jointable> ON (t1.id = t1.id), JOIN <j1> ON ...."
    ## Return a text string or None if no joins
    ##
    ##  l_joins = [
    ##             { "LEFT JOIN":  ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
    ##             { "JOIN":       ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
    ##             { "RIGHT JOIN": ["<join_to_table>", "<left_colname>", "<right_colname>" ] }
    ##           ]
    ##
    tag = self.oid + '.__sqlBuilder_JOIN' 

    text = None   

    ## { "join": ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
    if len(l_joins) > 0:
      l_join_statements = []
      join_str = None 
      for d_join in l_joins:
        for join_label,l_args in d_join.items():
          if (join_label != 'JOIN') and (join_label != 'LEFT JOIN') and (join_label != 'RIGHT JOIN'):
            raise MethodInputError("%s: Invalid JOIN-label syntax (%s)" % (tag, join_label))

          table = l_args[0]
          left_col = l_args[1]
          right_col = l_args[2]
          join_statement = join_label + ' ' + table + " ON (" + left_col + " = " + right_col + ")"
          l_join_statements.append(join_statement)
        text = " ".join( l_join_statements) 
 
    return( text )
  #----------------------------------------------------------------------------- 
  def __sqlBuilder_WHERE(self, d_where, raw=0):
    ## 
    ## Builds the "WHERE ..." portion of an sql query: "WHERE <k1> = <v1> AND <k1> = <v2> ...."
    ## and the actual WHERE text string (or None if no where clause to be used) 
    ## WHERE clause key/value pairs are passed in d_where.
    ## Values can be "NULL", "!NULL" or comma-sep-list, and will get translated to approprate sql.
    ## Numerical values preceeded by (>, <, >=, <=)  will get translated to approprate sql.
    ##
    ## By default, we return WHERE text as a formatting string and a list of values to associated
    ## with the formatting string.  If raw=1, we simple build the text string with its values in place. 
    ##
    ## To pass complex/grouped WHERE logic, use d_where['_COMPLEX_WHERE_'] = <complex-sql-statement> 
    ## This statement text does NOT include the word "WHERE"!! 
    ## Example: 
    ##   d_where['_COMPLEX_WHERE_'] = "(k1 = 'b' AND k2 = 'c') OR (j1 = 'b' AND j2 = 'c')"
    ##
    ## Return a dict containing a list of "prepared" values and the sql "WHERE ..." text 
    ## 
    
    tag = self.oid + '.__sqlBuilder_WHERE' 

    text = None   
    l_vals = []
     
    if len(d_where.keys()):
      ##utils.dataDump(d_where, "WHERE") 
      complex_where_sql = None
      if '_COMPLEX_WHERE_' in d_where:
        complex_where_sql = d_where['_COMPLEX_WHERE_']
        del d_where['_COMPLEX_WHERE_']
 
      where_str = None 
      l_where = []
      for k,v in d_where.items():

        ##dtype_value = utils.getDataType(v)
        ##print("-->%s: K=[%s]  V=[%s] TYPE=%s" % (tag, k,v, dtype_value))

        ## NULL or !NULL
        if v == 'NULL':
          l_where.append( k + " IS NULL" ) 
          ## do not append "v" to l_vals

        elif v == '!NULL':
          l_where.append( k + " IS NOT NULL" ) 
          ## do not append "v" to l_vals

        else:
          ## comma-sep-list
          m = re.match(",", str(v))
          if m:
            l_where.append( k + " IN (" + """%s""" + ")" ) 
            l_vals.append( v ) 

          else:
            ## identify assignment-operator
            op = '=' ## default operator is '='
            ## check for numerical operators
            m = re.match( "^([\>\<]=?)(\d.*)$", str(v))
            if m:
              op = m.group(1)
              v = m.group(2)
              if utils.getStrNumericType(v): 
                v = utils.castStrNumericType(v) 
            l_where.append( k + " " + op + " " + """%s""" ) 
            l_vals.append( v ) 

      ## add complex where logic statement if exists
      if complex_where_sql:
        l_where.append(complex_where_sql) 

      ## Join all the where pairs (including the complex segement) with AND logic
      text = " AND ".join( l_where )

    d_where_results = { 'prepare_values': l_vals, 'text': text }

    return( d_where_results )

  #----------------------------------------------------------------------------- 
  def __sqlBuilder_ORDER(self, l_orderby):

    ## Builds the "ORDER BY ..." portion of an sql query: "ORDER BY <k1> ASC, <k2> DESC ...."
    ## Return a text string or None if no joins
    ##    
    ## l_orderby syntax: 
    ##  l_orderby = [ {"col1": "<desc|asc>" }, ... {"colN": "<desc|asc>" } ]
    ##
    text = None   

    sep = "," ## comma separated joining of multiple column sorts
 
    if len(l_orderby) > 0:
      l_order_statements = []
      for d_orderby in l_orderby:
        for col,direction in d_orderby.items():
          order_statement =  "%s %s" % (col, direction)
          l_order_statements.append(order_statement)

      text = "ORDER BY " + sep.join(l_order_statements) 

    return( text )

  #----------------------------------------------------------------------------- 
  def __sqlBuilder_GROUP(self, l_groupby):

    ## Builds the "GROUP BY ..." portion of an sql query: "GROUP BY <k1>[, <k2> ....]"
    ## Return a text string or None if no joins
    ##    
    ## l_groupby syntax: 
    ##  l_groupby = [ "col1", "col2", ... ]
    ##
    text = None   
 
    sep = "," ## comma separated joining of multiple column grouping 

    if len(l_groupby) > 0:
      text = "GROUP BY " + sep.join(l_groupby) 

    return( text )


  ##--------------------------------------------------------------------------- 
  ## Simple public utility methods 
  #----------------------------------------------------------------------------- 
  def getAllPhases(self):
    ## self.all_phases defined by child classes
    return(self.all_phases)
  
  #----------------------------------------------------------------------------- 
  def getPhase(self):
    return(self.phase)

  #-----------------------------------------------------------------------------
  def getTableName(self, phase=None):
    table_name = None
    if phase is None:
      phase = self.phase
    if self.all_phases is None:
      table_name = self.table_name
    else: 
      if phase in self.all_phases:
        table_name = self.table_base_name + '_' + phase
      else:
        raise PhaseError("%s: Invalid table phase: [%s]" % (self.cname, phase))
    return(table_name)

  #-----------------------------------------------------------------------------
  def test(self):
    ## Execute a connection test: (describe <table_name>)
    table_name = self.table_name
    sql = "DESCRIBE %s" % (table_name)
    cursor_type = 'dict'

    d_results = None
    try:
      d_results = self.runSql(sql, cursor_type)
    except Exception as e:
      raise
    return( d_results )

  ##--------------------------------------------------------------------------- 
  ## Methods intended for internal use only, but NOT using __<method>() sytax.
  ## Would be nice to call use __<method>() syntax but then not accessible from 
  ## decorator
  ##---------------------------------------------------------------------------- 
 
  #----------------------------------------------------------------------------- 
  def connect(self):
    ##
    ## Connect and return DB connection handle 
    ##
    env =  self.d_db_args['env']
    host =  self.d_db_args['host']
    db_user =  self.d_db_args['db_user']
    db_pw =  self.d_db_args['db_pw']
    db_name = self.d_db_args['db_name']
    
    db_arg_str = "%s %s %s %s" % ( host, db_user, db_pw, db_name )

    secure_db_arg_str = "%s %s ***** %s" % ( host, db_user, db_name )
    self.log('DEBUG', "%s: Attempting DB-connection for db-id=[%s]: [%s]..." % (self.oid, self.storage_id, secure_db_arg_str))

    conn_handle = None
    try: 
      conn_handle = mdb.connect( host=host, user=db_user, password=db_pw, database=db_name )
    except Exception as e:   ## except (mdb.Error, mdb.Warning) as e:
      db_identity = host + ':' + db_user
      raise DbConnectError( "%s: Unable to connect to database: %s. %s" % (self.oid, db_identity, e))

    return( conn_handle )
 
  #----------------------------------------------------------------------------- 
  def resourceCleanup(self):
    ##
    ## Clean up all resources
    ##
    tag = "%s.resourceCleanup" % (self.cname)
    self.log('DEBUG', "%s: Cleaning up all class resources..." % (tag))
    self.disConnect()  ## close db-connection

  #----------------------------------------------------------------------------- 
  def disConnect(self):
    ##
    ## Dis-Connect  
    ##
    if self.conn_handle is not None:
      self.log('INFO', "%s: Closing OPEN DB-connection: db-id=[%s], connection-id=[%s]" % (self.oid, self.storage_id, self.connection_id))
      self.conn_handle.close()
 
  #----------------------------------------------------------------------------- 
  def getConnHandle(self):
    ##
    ## Return DB connection handle 
    ##
    return( self.conn_handle )
  
  ##----------------------------------------------------------------------------- 
  ## Decorated methods intended for internal use only
  ##----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def runSql(self, sql, cursor_type=None):

    ##
    ## Execute a passed SQL statement (can only be used for SELECT statements) 
    ## Used for complex SQL select statements
   
    tag = self.oid + '.runSql' 
    
    if cursor_type is None:
      cursor_type = 'dict'

    if re.match( "(update|insert|delete)", sql, re.I):
      raise MethodInputError("%s: Method cannot be used for (update|insert|delete)" % (tag))
      
    self.log("INFO", "%s: Executing SQL: %s" % (tag, sql))

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
  def runSqlFormatStr(self, sql, l_vals, cursor_type=None):

    ##
    ## Execute a passed SQL statement (can only be used for SELECT statements) 
    ## Used for complex SQL select statements
   
    tag = self.oid + '.runSqlFormatStr' 
    
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
  def runTransaction(self, l_statements, cursor_type=None):

    ##
    ## Execute a multiple SQL statements in an Atomic (all or nothing) transaction
    ## Passed SQL statements must be fully formatted strings.
    ##
   
    tag = self.oid + '.runTransaction' 
      
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
        self.log("INFO", "%s: Executing transaction statement (%d): [%s]" % (tag, N, sql))
        cur.execute(sql) 

      self.log("INFO", "%s: Commiting transaction..." % (tag))
      self.conn_handle.commit() 
      self.log("INFO", "%s: Transaction successful" % (tag))
      status = 1 
    except Exception as e:
      self.log("ERROR", "%s: Transaction failed. Rolling back..." % (tag))
      self.conn_handle.rollback() 
      status = 0
      raise 

    return( status )

  #----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def runPreparedSqlRead(self, sql, l_vals, cursor_type=None): 

    ##
    ## Execute a prepared SQL statement for SELECT statements 
    ##
   
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

      cur.execute(sql, tuple_vals) 
      l_rows = cur.fetchall()
      rowcount = cur.rowcount 
      sql = cur._executed.decode()
      d_results = { 'sql': sql, 'data': l_rows, 'rows': rowcount }
    except Exception as e:
      raise 
    
    self.log("DEBUG", "%s: Executed query: [%s]" % (tag, sql))

    return( d_results )

  #----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def runPreparedSqlInsert(self, sql, l_vals, cursor_type=None): 

    ##
    ## Execute a prepared SQL statement for INSERT statements 
    ##
   
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

    ##
    ## Execute a prepared SQL statement for UPDATE statements 
    ##
   
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
      utils.dataDump(tuple_vals, "TUPLE-VALUES")
      raise 

    return( d_results )

  #----------------------------------------------------------------------------- 
  @DBMethodDecorators.connection_decorator
  def runPreparedSqlDelete(self, sql, l_vals, cursor_type=None): 

    ##
    ## Execute a prepared SQL statement for DELETE statements 
    ##
   
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
    ## Insert a single row 
    ## Key/Value pairs are passed in d_kv
    ## Return DB id
    ## By default we do not check affected-rows here to identify successful submit.
    ## Optionally, (d_args['validate']=1) we can raise error inside this method if 
    ## submit does not result in affected rows = 1
   
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
        self.log("INFO", "%s: Inserted new record: SQL=[%s]" % (tag, sql))
 
      if rowcount != 1:
        msg = "%s: Affected rows (%s) does not match expected (1)" % (tag, rowcount)
        if validate == 1:
          raise SubmitError("%s. SQL=[%s]" % (msg, sql))
        else:
          self.log("WARNING", "%s" % (msg))
 
    if db_id is None:
      raise SubmitError("%s: Invalid DB id returned" % (tag))
 
    return( db_id )

  #----------------------------------------------------------------------------- 
  def __updateRecords(self, table_name, d_updates, d_where, d_args=None): 
    ## Update one or more rows 
    ## Key/Value updates are passed in d_updates
    ## Return d_results dict. 
    ## By default we do not check affected-rows here to identify successful update.
    ## Optionally, (d_args['validate']=1 and d_args['expected']=<N>) we can raise 
    ## error inside this method if delete does not result in afftected rows = <N>
   
    tag = self.oid + '.__updateRecords' 
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
    d_where_results = self.__sqlBuilder_WHERE(d_where)
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
        self.log("INFO", "%s: Updated records: [%s]: SQL=[%s]" % (tag, rowcount, sql))
    
    if expected:
      if expected != rowcount:
        msg = "%s: Affected rows (%s) does not match expected (%s)" % (tag, rowcount, expected)
        if validate == 1:
          self.log("ERROR", "%s" % (msg))
          raise UpdateError("%s. SQL=[%s]" % (msg, sql))
        else:
          self.log("WARNING", "%s" % (msg))
    
    return( d_results )

  #----------------------------------------------------------------------------- 
  def __deleteRecords(self, table_name, d_where, d_args=None): 
    ## DELETE one or more rows 
    ## Key/Value pairs are passed in d_kv
    ## Return d_results dict. 
    ## By default we do not check affected-rows here to identify successful delete.
    ## Optionally, (d_args['validate']=1 and d_args['expected']=<N>) we can raise 
    ## error inside this method if delete does not result in afftected rows = <N>
   
    tag = self.oid + '.__deleteRecords' 
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
    d_where_results = self.__sqlBuilder_WHERE(d_where)
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
        self.log("INFO", "%s: Deleted records: [%s]: SQL=[%s]" % (tag, rowcount, sql))
    
    if expected:
      msg = "%s: Affected rows (%s) does not match expected (%s)" % (tag, rowcount, expected)
      if validate == 1:
        if expected != rowcount:
          self.log("ERROR", "%s" % (msg))
          raise DeleteError("%s. SQL=[%s]" % (msg, sql))
      else:
        self.log("WARNING", "%s" % (msg))
    
    return( d_results )

  #----------------------------------------------------------------------------- 
  def __getRecords(self, table_name, d_where, d_args=None): 
  
    ## Return one or more rows
    ## Optionally, with d_args['expected']=<N> and validate=1, we can raise error inside 
    ## this method if affected rows != <N> 
    ## SELECT fields are passed in l_select (default: l_select=['*'] to select ALL)
    ## WHERE clause is created by self.__sqlBuilder_WHERE() 
    ##
    ## d_where = {"key1": "val1", ... "keyN": "valN" }
    ##
    ## d_args = ( 
    ##            'select':  l_select, 
    ##            'join':    d_join, 
    ##            'orderby': l_orderby, 
    ##            'limit':   <N>: 
    ##          )
    ##
    ##  l_join = [
    ##             { "LEFT JOIN":  ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
    ##             { "JOIN":       ["<join_to_table>", "<left_colname>", "<right_colname>" ] },
    ##             { "RIGHT JOIN": ["<join_to_table>", "<left_colname>", "<right_colname>" ] }
    ##           ]
    ##
    ##  l_orderby = [ {"col1": "<desc|asc>" }, ... {"colN": "<desc|asc>" } ]
    ##
    ##
    ## RETURN (one of two possible formats):
    ##  full-results (default):           d_results = { 'sql': sql, 'data': l_rows, 'rows': rowcount }
    ##  data-only (d_args['dataonly']=1): d_data = d_results['data']
    ##
 
    tag = self.oid + '.__getRecords' 
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
    sql = self.__sqlBuilder_SELECT(table_name, l_select)

    ## JOIN
    join_str = self.__sqlBuilder_JOIN(l_joins)
    if join_str:
      sql += " " + join_str

    ## WHERE
    d_where_results = self.__sqlBuilder_WHERE(d_where)
    l_prepare_values = d_where_results['prepare_values']
    where_str = d_where_results['text']
    if where_str:
      sql += " WHERE " + where_str

    ## ORDER BY 
    order_str = self.__sqlBuilder_ORDER(l_orderby)
    if order_str:
      sql += " " + order_str

    ## GROUP BY (careful, you may need an aggregate function!)
    group_str = self.__sqlBuilder_GROUP(l_groupby)
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
      self.log("INFO", "No records returned from query: [%s]" % (sql))  
    else:
      self.log("INFO", "Records returned from query (%s): [%s]" % (rows,sql))  
      ##utils.dataDump(d_results) ## uncomment for troubleshooting

    if expected:
      if rows != expected: 
        msg = "Records returned (%s) does not match expected=(%s) for query: [%s]" % (rows, expected, sql)
        self.log("WARNING", msg)  
        if validate == 1:
          self.log("ERROR", msg)  
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

    ## Execute a connection test (show tables) 
    sql = "show tables"

    d_results = None
    try:
      d_results = self.runSql(sql)
    except Exception as e:
      raise 
    return( d_results )
 
  #----------------------------------------------------------------------------- 
  def getSingleRecord(self, d_where, d_args=None): 

    ## Query for single row. Raise exception if more than one row is returned (unless validate=0). 
    ## RETURN: full-results or data-only
    
    tag = self.oid + '.getSingleRecord' 

    return_type = 'default'
    table_name = self.table_name
      
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

    ## override default table_name?
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise
    elif 'table_name' in d_args:
      table_name = d_args['table_name']

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
  def getRecordsWhere(self, d_where, d_args=None):

    ## Get specific records in a table
    ## RETURN: full-results or data-only

    tag = self.oid + '.getRecordsWhere'

    table_name = self.table_name

    if not d_args:
      d_args = {}
   
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raie
    ## must have this to provide for table aliasing
    if 'table_name' in d_args:
      table_name = d_args['table_name'] 

    o_return = None
    try:
      o_return = self.__getRecords(table_name, d_where, d_args)
    except Exception as e:
      raise 
    
    return( o_return )
  
  #-----------------------------------------------------------------------------
  def getMaxRecordsPerGroup(self, group_colname, d_where, d_args=None):
    ##
    ## Get the max value of a column for each grouping (of another column)
    ## Example, suppose we want to know each students highest score from
    ## a table of all the scores for all students.
    ##   SELECT MAX(score), name FROM student_scores 
    ##     [WHERE name in ("bill","joe","bob")] # optional
    ##   GROUP by name 
    ##
    ## RETURN: list of matching records, or [] if no match 
    ##
    tag = self.oid + '.getMaxRecordsPerGroup'

    if not d_args:
      d_args = {}
     
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

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
  def getRecordsForGroupWithMax(self, max_colname, group_colname, d_where, d_args=None):
    ##
    ## Get all the records for the "group" which has the largest value of a column.
    ## Example, suppose we want to know ALL the scores for the student which has
    ## the highest score (from a table of all the scores for all students).
    ##   SELECT * FROM student_scores where name = 
    ##     (select name from student_scores 
    ##       [WHERE name in ("bill","joe","bob")] 
    ##      ORDER BY score DESC LIMIT 1); 
    ##
    ## RETURN: list of matching records, or [] if no match 
    ##

    tag = self.oid + '.getRecordsForGroupWithMax'
    
    if not d_args:
      d_args = {}
    
    table_name = self.table_name
     
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise
   
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
    d_where_results = self.__sqlBuilder_WHERE(d_where)
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
      d_results = self.runSqlFormatStr(sql, l_where_values)
    except Exception as e:
      raise 

    l_records = []
    if d_results: 
      l_records = d_results['data'] 

    print("DONE: %s\n" % (l_records))

    return( l_records )

  #-----------------------------------------------------------------------------
  def getMaxValueWhere(self, max_colname, d_where, d_args=None):
    ##
    ## Simple query for max value of a column 
    ## Example, suppose we want to know the highese score of all students scores
    ##   SELECT * FROM student_scores 
    ##     [WHERE name in ("bill","joe","bob")] # optional
    ##   ORDER BY score DESC LIMIT 1; 
    ##
    ## RETURN: dict record, or None if no match 
    ##

    tag = self.oid + '.getMaxValueWhere'
    
    if not d_args:
      d_args = {}
     
    table_name = self.table_name

    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

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
  def getLastRecordWhere(self, d_where, timestamp_colname, d_args=None):
    ##
    ## Essentially synonomous with getMaxValueWhere().
    ##
    ## Get the LAST (i.e. most-recent) record in a table.
    ## Depending on the timestamp_colname this may not be the most recently
    ## inserted record. It could be an update-timestamp in which case it
    ## returns the record with the most-recent update. 
    ## RETURN: dict - d_record
    ##

    tag = self.oid + '.getLastRecordWhere'
    
    table_name = self.table_name

    if not d_args:
      d_args = {}
      
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise
    ## must have this to provide for table aliasing
    if 'table_name' in d_args:
      table_name = d_args['table_name'] 

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
      self.log("INFO", "%s: NO records found in table=[%s] for %s" % (self.oid, table_name, d_where))  
    else:
      if count == 1:
        d_record = l_data[0] 
      else:
        raise QueryError("%s: Invalid record count: [%s]" % (tag, count))

    return( d_record )

  #-----------------------------------------------------------------------------
  def getOldestRecordWhere(self, d_where, timestamp_colname, d_args=None):
    ##
    ## Similar to getLastRecordWhere() but reversed timestamp ordering.
    ## Get the "OLDEST" record in a table.
    ## Depending on the timestamp_colname this may not be the "oldest" in
    ## terms of insert. It could be an update-timestamp in which case it
    ## returns the record with the oldest update. 
    ## RETURN: dict - d_record
    ##

    tag = self.oid + '.getOldestRecordWhere'
    
    table_name = self.table_name

    if not d_args:
      d_args = {}
      
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

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
      self.log("INFO", "%s: NO records found in table=[%s] for %s" % (self.oid, table_name, d_where))  
    else:
      if count == 1:
        d_record = l_data[0] 
      else:
        raise QueryError("%s: Invalid record count: [%s]" % (tag, count))

    return( d_record )

  #-----------------------------------------------------------------------------
  def getLastRecordFieldWhere(self, d_where, timestamp_colname, field_name, d_args=None):

    ## Get LAST (most-recent) record in a table and return a specified field from that record
    ## RETURN: value of field_name 

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
  def getRecordCountWhere(self, d_where, d_args=None):

    ## Get record count of specific records in a table
    ## RETURN: <count> 

    tag = self.oid + '.getRecordCountWhere'

    table_name = self.table_name

    if not d_args:
      d_args = {}
    
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

    sql = "SELECT count(*) as count from %s" % (table_name)
    cursor_type = 'dict'
  
    ## WHERE
    l_prepare_values = []
    where_str = None
    d_where_results = self.__sqlBuilder_WHERE(d_where)
    l_prepare_values = d_where_results['prepare_values']
    where_str = d_where_results['text']
    if where_str:
      sql += " WHERE " + where_str
 
    count = -1
    d_results = None

    try:
      if where_str is None:
        d_results = self.runSql(sql, cursor_type)
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

    ## Get record count of all records in a table
    ## RETURN: <count> 

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
  def getAllRecords(self, d_args=None):

    ## Get all records in a table
    ## RETURN: full-results or data-only

    tag = self.oid + '.getAllRecords'

    table_name = self.table_name

    if not d_args:
      d_args = {}

    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise
    ## must have this to provide for table aliasing
    if 'table_name' in d_args:
      table_name = d_args['table_name'] 

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
  def submitSingleRecord(self, d_data, d_args=None):

    ##
    ## Submit one new record. 
    ## RETURN: new database id 
    ##
    
    tag = self.oid + '.submitSingleRecord'

    if not isinstance(d_data, dict):
      raise MethodInputError("%s: Method requires input data dict" % (tag))

    table_name = self.table_name
    
    if not d_args:
      d_args = {}

    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

    db_id = None
    try:
      db_id = self.__insertRecord(table_name, d_data, d_args)
    except Exception as e:
      raise 

    return( db_id )

  #-----------------------------------------------------------------------------
  def submitMultipleRecords(self, l_data, d_args=None):

    ## Submit multiple new records. 
    ## RETURN: list of new database ids:  l_dbids = [] 
    ## If persist==0, set persist=1 for all row inserts and then reset persist=0 
    
    tag = self.oid + '.submitMultipleRecords'

    if not isinstance(l_data, list):
      raise MethodInputError("%s: Method requires input data list" % (tag))
    
    table_name = self.table_name
    mdebug = 0 

    if not d_args:
      d_args = {}
    
    if 'debug' in d_args:
      mdebug = d_args['debug']
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise
    
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
  def incrementValue(self, increment_colname, d_where, d_args=None):
    ##
    ## Update a record with an incremented value (update <table> set <value> = <value> + 1 WHERE...)
    ## RETURN: 
    ##   default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
    ##   data-only:  N = d_results['rows']
    ##
    
    tag = self.oid + '.incrementValue'
    
    if not isinstance(d_where, dict):
      raise MethodInputError("%s: Method requires input data dict: d_where" % (tag))

    table_name = self.table_name
    return_type = 'rows'

    if not d_args:
      d_args = {}

    if 'return_type' in d_args:
      return_type = d_args['return_type']
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

    new_value = "%s + 1" % (increment_colname) ## must have single space around "+"
    d_updates = { increment_colname: new_value } 

    d_results = None 
    try:
      d_results = self.__updateRecords(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def decrementValue(self, decrement_colname, d_where, d_args=None):
    ##
    ## Update a record with an decremented value (update <table> set <value> = <value> - 1 WHERE...)
    ## RETURN: 
    ##   default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
    ##   data-only:  N = d_results['rows']
    ##
    
    tag = self.oid + '.decrementValue'
    
    if not isinstance(d_where, dict):
      raise MethodInputError("%s: Method requires input data dict: d_where" % (tag))

    table_name = self.table_name
    return_type = 'rows'

    if not d_args:
      d_args = {}

    if 'return_type' in d_args:
      return_type = d_args['return_type']
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

    new_value = "%s - 1" % (decrement_colname) ## must have single space around "-"
    d_updates = { decrement_colname: new_value } 

    d_results = None 
    try:
      d_results = self.__updateRecords(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def updateMultipleRecords(self, d_updates, d_where, d_args=None):
    ##
    ## Update one or more records. 
    ## RETURN: 
    ##   default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
    ##   data-only:  N = d_results['rows']
    ##
    
    tag = self.oid + '.updateMultipleRecords'
    
    if not isinstance(d_updates, dict):
      raise MethodInputError("%s: Method requires input data dict: d_updates" % (tag))
    if not isinstance(d_where, dict):
      raise MethodInputError("%s: Method requires input data dict: d_where" % (tag))

    table_name = self.table_name
    return_type = 'rows'

    if not d_args:
      d_args = {}

    if 'return_type' in d_args:
      return_type = d_args['return_type']
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

    d_results = None 
    try:
      d_results = self.__updateRecords(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def updateSingleRecord(self, d_updates, d_where, d_args=None):
    ##
    ## Update single record. 
    ## RETURN: 
    ##   default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
    ##   data-only:  N = d_results['rows']
    ##
    
    tag = self.oid + '.updateSingleRecord'
    
    if not isinstance(d_updates, dict):
      raise MethodInputError("%s: Method requires input data dict: d_updates" % (tag))
    if not isinstance(d_where, dict):
      raise MethodInputError("%s: Method requires input data dict: d_where" % (tag))

    table_name = self.table_name
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
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

    d_results = None 
    try:
      d_results = self.__updateRecords(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def updateLastRecord(self, d_updates, d_where, timestamp_colname, d_args=None):
    ##
    ## Update the LAST record based on a timestamp column. 
    ## RETURN: 
    ##   default-return:  d_results = { 'sql': <sql>, 'id': <db-id>, 'rows': 1 }
    ##   data-only:  N = d_results['rows']
    ##
    tag = self.oid + '.updateLastRecord'
    
    if not isinstance(d_updates, dict):
      raise MethodInputError("%s: Method requires input data dict" % (tag))

    table_name = self.table_name

    return_type = 'rows'
    if not d_args:
      d_args = {}

    if 'return_type' in d_args:
      return_type = d_args['return_type']
    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise
    
    d_args['expected'] = 1 
    d_args['validate'] = 1 
    d_args['limit'] = 1 
    d_args['orderby'] = [ {timestamp_colname: 'desc'} ]
   
    d_results = None 
    try:
      d_results = self.__updateRecords(table_name, d_updates, d_where, d_args)
    except Exception as e:
      raise error 
    
    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def deleteSingleRecord(self, d_where, d_args=None):
    ##
    ## Delete single record. 
    ## RETURN: d_results, or affected-rows (if return_type=rows) 
    ##

    tag = self.oid + '.deleteSingleRecord'
    
    table_name = self.table_name
    
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

    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise
 
    d_results = None 
    try:
      d_results = self.__deleteRecords(table_name, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def deleteMultipleRecords(self, d_where, d_args=None):
    ##
    ## Delete multiple records. 
    ## RETURN: d_results, or affected-rows (if return_type=rows) 
    ##

    tag = self.oid + '.deleteMutlipleRecords'
    
    table_name = self.table_name

    return_type = 'rows'
    if not d_args:
      d_args = {}
    
    if 'return_type' in d_args:
      return_type = d_args['return_type']

    if 'phase' in d_args:
      phase = d_args['phase']
      try:
        table_name = self.getTableName( phase )
      except Exception as e:
        raise

    d_results = None 
    try:
      d_results = self.__deleteRecords(table_name, d_where, d_args)
    except Exception as e:
      raise 

    o_return = None
    if d_results:
      o_return = d_results
      if return_type == 'rows':
        o_return = d_results['rows'] 

    return(o_return)

  #-----------------------------------------------------------------------------
  def getColNames(self):
    ## return list of column names as defined by child classes
    return(self.col_names)

  #-----------------------------------------------------------------------------
  def getRecordId(self):
    ## return the primary "id" column name as defined by child classes
    return(self.record_id)

  #-----------------------------------------------------------------------------
  @DBMethodDecorators.connection_decorator
  def getDbConnHandle(self):
    ## return self.conn_handle
    return(self.conn_handle)

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":

  sys.path.append('./config')
  import DATABASE as config_db

  myname = 'mdb_tester'

  storage_id = 'workflow_applog'
  
  ## Args for init(): config_file is an IMPORTED module, NOT a PATH
  d_db_args = {"config_module": config_db, "storage_id": storage_id }

  ## Instantiate Db_handler
  try:
    db_h = MDbHandler(d_db_args)
  except Exception as e:
    errmsg = "%s: MDbHandler().init() failed with exception" % (myname)
    utils.stderr_notify(myname, errmsg,  {'exc':e, 'exit':1} )

  with db_h:
    print("%s: TESTING DB connection for storage-id: [%s]" % (myname, storage_id))
    try:
      d_results = db_h.test()
      sql = d_results['sql']
      rows = d_results['rows']
      data = d_results['data']
      print("%s: SQL: [%s]" % (myname, sql))
      print("%s: ROWS-RETURNED: [%d]" % (myname, rows))
      print("%s: DATA: %s" % (myname, data))
    except Exception as e:
      errmsg = "%s: MDbHandler().test() failed with exception" % (myname)
      utils.stderr_notify(myname, errmsg,  {'exc':e, 'exit':1} )
