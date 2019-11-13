"""

 LogFacility_db.py
 Child class of ABSTRACT class LogFacility().

 All subclasses of LogFacility() must implement these methods:
  * log()
  * resourceAllocation()
  * resourceCleanup()

 All subclasses must define these properties:
  * facility_name


 Use this class as a simple way to manage sending log-messages to a database.
 Also can be used as one of multiple logging "facilities" to be accessed by
 the LogFacility_multiChannel() class (see LogFacility_multiChannel class
 for more details on how to do that).

 Pass in to init() a dict containing db_storage_id, a unique session_id, and the
 minimum-logging-level (messages with logging-level below this are not processed).

 Since we are working with files and file I/O the Class returns a
 context-manager so that all file resources are properly released.
 The __enter__() method returns the Class instance

 USAGE: see TEST __main__ at bottom of page 

"""

import sys

## custom libs
import utils
from CustomExceptions import InitError
from LogFacility import LogFacility ##(parent)

##
## TODO: import dynamically on instantiation using storage_id
##
## import all avialable handler classes
sys.path.append('./lib')
from MDbHandler_workflow_applog import MDbHandler_workflow_applog

##----------------------------------------------------------------------------------------
## Provide all supported log storage_id names and their associated Class
d_AVAILABLE_DB_HANDLERS = {
  "workflow_applog": MDbHandler_workflow_applog
}

##----------------------------------------------------------------------------------------
##
## Defaults: can be overridden on instantiation with init() args
##

DEBUG = 0

## Connect on DbHandler init() and leave open vs connect/disconnect on each transaction
DEFAULT_PERSIST = 1

##----------------------------------------------------------------------------------------
class LogFacility_db(LogFacility):
  def __init__(self, d_init_args):

    self.facility_name = 'Db'

    super().__init__(d_init_args)
    ## Set by super()__init__():
    ##  debug  
    ##  session_id 
    ##  dup_to_stdout
    ##  logging-level
    ##  caller

    self.cname = self.__class__.__name__

    self.d_available_dbhandlers = d_AVAILABLE_DB_HANDLERS

    self.INIT_ARGS = d_init_args 
    self.DBH = None

    self.DEBUG = DEBUG
    if 'debug' in d_init_args:
      self.DEBUG   = d_init_args['debug']

    self.PERSIST = DEFAULT_PERSIST
    if 'persist' in d_init_args:
      self.PERSIST = d_init_args['persist']

    ## database config module 
    if 'config_module' in d_init_args:
      config_db = d_init_args['config_module']
    else:
      raise InitError("%s: Missing required init() arg: [config_module]" % (self.cname))

    ## database storage_id
    if 'storage_id' in d_init_args:
      self.storage_id = d_init_args['storage_id']
    else:
      raise InitError("%s: Missing required init() arg: [storage_id]" % (self.cname) )

    if self.storage_id not in self.d_available_dbhandlers:
      raise InitError("%s: Unsupported storage_id: [%s]" % (self.cname, self.storage_id) )

    ##
    ## Create the database logging handle (This will be used by Class' log() method to manage logging to the API)
    ##
    try:
      self.resourceAllocation(config_db) ## sets self.DBH
    except Exception as e:
      raise
    
    if self.DBH:
      self.log("DEBUG", "%s: Initialization complete" % (self.cname))
    else:
      errmsg = "%s: Initialization() failed" % (self.cname)
      utils.stderr_notify(self.cname, errmsg )  ## DON'T EXIT!!

  ##----------------------------------------------------------------------------------------
  def log(self, s_level, msg):
    ##
    ## super().log does log-level-filtering and formatting and returns formatted message
    ## (or None if not passing level-filtering)

    d_fields = super().fields(s_level, msg)
    if d_fields:
      try:
        row_id = self.__db_logger(d_fields)
      except Exception as e:
        errmsg = "%s: DB-Log-msg failed with exception" % (self.cname)
        utils.stderr_notify(self.cname, errmsg,  {'exc':e} )  ## DON'T EXIT!!

  ##--------------------------------------------------------------------------------------
  def getAvailableDbHandlers(self):
    return(self.d_available_dbhandlers)

  ##----------------------------------------------------------------------------------------
  def resourceCleanup(self):
    self.log("DEBUG", "%s: Cleaning up all class resources..." % (self.cname))
    
    self.log("INFO", "%s: Cleaning up db-logging resources..." % (self.cname))
    self.DBH.resourceCleanup()

  ##----------------------------------------------------------------------------------------
  def resourceAllocation(self, config_db):
    ##
    ## Return a log-handle attached to database connection which will be used by the Class' PUBLIC log() method
    ##
    if self.DEBUG > 2:
      print("%s: Allocating logging-resources..." % (self.cname))

    DbHandlerClass = self.d_available_dbhandlers[self.storage_id]

    d_db_args = self.INIT_ARGS 
    d_db_args['persist'] = self.PERSIST ## this was an optional arg, so possbile override with class default

    db_h = None
    try:
      db_h = DbHandlerClass(d_db_args)
    except Exception as e:
      raise 

    if db_h:
      self.DBH = db_h
      msg = "Logging resource-allocation complete: Storage-id=[%s] minLogLevel=[%s] sessionId=[%s]" % (self.storage_id, self.s_min_level, self.session_id)
      self.log("INFO", "%s: %s" % (self.cname, msg))

    return( 1 )

  ##----------------------------------------------------------------------------------------
  ## PRIVATE METHODS
  ##----------------------------------------------------------------------------------------
  def __enter__(self):
    if self.DEBUG > 2:
      print("%s: __ENTER__" % (self.cname))
    return(self)

  ##----------------------------------------------------------------------------------------
  def __exit__(self, exc_type, exc_value, exc_traceback):
    if exc_value is None:
      msg = "%s: __EXIT__: Cleaning up DB resources on normal close with no exceptions" % (self.cname)
      self.log("INFO", "%s: %s" % (self.cname, msg))
    else:
      msg = "%s: __EXIT__: Cleaning up DB resources on exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.cname, exc_type,exc_value, exc_traceback)
      self.log("WARNING", "%s: %s" % (self.cname, msg))
      utils.stderr_notify(self.cname, msg)
    self.resourceCleanup()

  ##----------------------------------------------------------------------------------------
  def __db_logger(self, d_log_record):
    ## Actual submit of record to database (level-filtering has already been done) 

    try:
      row_id = self.DBH.newLogRecord(d_log_record) 
    except Exception as e:
      raise

    return( row_id )

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":

  sys.path.append('./config')
  import DATABASE as config_db
  
  myname = 'dbl_tester'

  session_id = utils.makeUniqHash(myname)
  storage_id = "workflow_applog"

  d_log_config = {"config_module": config_db, "storage_id": storage_id, "min_log_level": 'INFO', 'caller': myname, 'session_id':session_id }

  db_logger = None
  ## Instantiate with logging config
  try:
    db_logger = LogFacility_db(d_log_config)
  except Exception as e:
    utils.stderr_notify(myname, "LogFacility_db().init() failed with exception",  {'exc':e, 'exit':2})

  if db_logger:
    print("%s: Testing db-logging resources" % (myname) )
    with db_logger as log_h:
      try:
        log_h.test()
      except Exception as e:
        utils.stderr_notify(myname, "[Db] Resource test failed with exception",  {'exc':e, 'exit':2})

      ## send log messages to the DB 
      msg = "%s: LOG-TEST to db=[%s]" % (myname, storage_id)
      log_h.log("INFO", msg)
      log_h.log("DEBUG", msg)
      log_h.log("ERROR", msg)
  else:
    utils.stderr_notify(myname, "LogFacility_db().init() failed",  {'exit':2})
