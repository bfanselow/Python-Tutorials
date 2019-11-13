"""

 LogFacility_file.py
 Child class of ABSTRACT class LogFacility().

 All subclasses of LogFacility() must implement these methods:
  * log()
  * resourceAllocation()
  * resourceCleanup()

 All subclasses must define these properties:
  * facility_name

 Use this class as a simple way to manage sending log-messages to a file.  
 Also can be used as one of multiple logging "facilities" to be accessed by 
 the LogFacility_multiChannel() class (see LogFacility_multiChannel class
 for more details on how to do that).

 Pass in to init() a dict containing log-file-path, a unique session_id, file-roatation
 beavior and the minimum-logging-level (messages with logging-level below this are not 
 processed). 

 NOTICE: Rather than returning a logging.logger object (which would expose all 
 the methods supported by such an object) this Class returns a Class instance 
 object which exposes only the method log("<LOGLVL>", "<message>"). Therefore, 
 the logging.logger object can only be manipulated upon instanatiation.

 Since we are working with files and file I/O the Class returns a
 context-manager so that all file resources are properly released.
 The __enter__() method returns the Class instance

 USAGE: see TEST __main__ at bottom of file 


"""

##----------------------------------------------------------------------------------------
import sys
import logging
import logging.handlers

## custom libs
import utils
from CustomExceptions import ReqArgError, InitError
from LogFacility import LogFacility ##(parent)

##----------------------------------------------------------------------------------------
##
## Defaults: can be overridden on instantiation with init() args
##
DEBUG = 1

## default log-rotation type (overwrite, rotate, hourlyrotate, dailyrotate)
DEFAULT_ROTATION = 'overwrite'

DEFAULT_LOG_PATH  = './fanselow_app.log'

##----------------------------------------------------------------------------------------

l_VALID_ROTATION_TYPES = ['overwrite', 'rotate', 'hourlyrotate', 'dailyrotate']

##----------------------------------------------------------------------------------------
class InvalidRotationType(Exception):
  pass

##----------------------------------------------------------------------------------------
class LogFacility_file(LogFacility):
  def __init__(self, d_init_args):

    self.facility_name = 'File'

    super().__init__(d_init_args)
    ## Set by super()__init__():
    ##  debug  
    ##  session_id 
    ##  dup_to_stdout
    ##  logging-level
    ##  caller
    ##  oid 

    self.cname = self.__class__.__name__

    self.logger = None 

    ## log_filepath
    self.log_filepath = DEFAULT_LOG_PATH
    if 'log_filepath' in d_init_args:
      self.log_filepath = d_init_args['log_filepath']

    ## log_rotation
    self.log_rotation = DEFAULT_ROTATION
    if 'log_rotation' in d_init_args:
        self.log_rotation = d_init_args['log_rotation']
    if self.log_rotation not in l_VALID_ROTATION_TYPES:
      raise InvalidLogRotationType("%s: Log rotation-type (%s) is not supported" % (self.cname, self.log_rotation))

    ## Create logging.logger (This will be used by Class' log() method to manage logging to file) 
    try:
      self.resourceAllocation() ## sets self.logger
    except Exception as e:
      raise

    self.log("DEBUG", "%s: Initialization complete" % (self.cname))
  
  ##----------------------------------------------------------------------------------------
  def log(self, s_level, msg):
    ## super().log does log-level-filtering and formatting and returns formatted message
    ## (or None if not passing level-filtering) 
 
    fmtd_msg = super().log(s_level, msg) 
    if fmtd_msg:
      LVL = s_level.upper()
      if LVL == 'DEBUG':
        self.logger.debug(fmtd_msg)
      elif LVL == 'INFO':
        self.logger.info(fmtd_msg)
      elif LVL == 'WARNING':
        self.logger.warning(fmtd_msg)
      elif LVL == 'ERROR':
        self.logger.error(fmtd_msg)
      elif LVL == 'CRITICAL':
        self.logger.critical(fmtd_msg)

    return( 1 )
 
  ##----------------------------------------------------------------------------------------
  def resourceCleanup(self):
    self.log("DEBUG", "%s: Cleaning up all logging resources (logger.handlers)..." % (self.cname))
    self.logger.handlers = []
 
  ##----------------------------------------------------------------------------------------
  def resourceAllocation(self):
    ## Return a logging.logger which will be used by the Class' PUBLIC log() method
  
    if self.DEBUG > 1:
      print("%s: Allocating logging-resources..." % (self.cname))
    
    handler = None
    log_handle_name = self.caller 
    
    logger = logging.getLogger(log_handle_name)

    ## set level
    logger.setLevel(self.min_level)

    ## Handler based on input (or default) "log_rotation" and "log_filepath"
    if self.log_rotation == 'overwrite':
      handler = logging.FileHandler(self.log_filepath)
    elif self.log_rotation == 'rotate':
      handler = logging.handlers.RotatingFileHandler(self.log_filepath, maxBytes=300000, backupCount=5)
    elif self.log_rotation == 'hourlyrotate':
      handler = logging.handlers.TimedRotatingFileHandler(self.log_filepath, when="h", backupCount=60)
    elif self.log_rotation == 'dailyrotate':
      handler = logging.handlers.TimedRotatingFileHandler(self.log_filepath, when="d", backupCount=60)

    ##-----------------------------
    ## Configure logging format is NOT done with logging.Formatter() since we want formatting
    ## to be a consistent method across all Logging facility classes

    ##-----------------------------
    ## add handler
    logger.addHandler(handler)

    self.logger = logger

    msg = "Logging resource-allocation complete: File=[%s] minLogLevel=[%s] sessionId=[%s] Rotation=[%s] LoggerName=[%s]" % \
        (self.log_filepath, self.s_min_level, self.session_id, self.log_rotation, log_handle_name)

    self.log("DEBUG", "%s: %s" % (self.cname, msg))

    return(1)

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
      msg = "%s: __EXIT__: Cleaning up logging-handlers on normal close with no exceptions" % (self.cname)
      self.log('DEBUG', msg)
    else:
      msg = "%s: __EXIT__: Cleaning up logging-handlers on exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.cname, exc_type,exc_value, exc_traceback)
      self.log('ERROR', msg)
      utils.stderr_notify(self.cname, msg)

    self.resourceCleanup()
 
  ##----------------------------------------------------------------------------------------


##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":

  myname = 'fl_tester'

  log_filepath = "./%s.log" % myname
 
  d_log_config = {"debug": 3, "log_filepath": log_filepath, "min_log_level": 'DEBUG', 'caller': myname }

  ## Instantiate with logging config
  f_logger = LogFacility_file(d_log_config)

  print("%s: Testing file-logging resources" % (myname) )
  with f_logger as log_h:
    try:
      log_h.test()
    except Exception as e:
      utils.stderr_notify(myname, "[File] Resource test failed with exception",  {'exc':e, 'exit':2})   

    ## send log messages to the file
    msg = "%s: Sample log message to file=[%s]" % (myname, log_filepath)
    log_h.log("INFO", msg)
    log_h.log("DEBUG", msg)
    log_h.log("ERROR", msg)

