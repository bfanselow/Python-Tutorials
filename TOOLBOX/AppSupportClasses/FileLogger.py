"""
   A Python3 File-Logger Class 

   +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   For a BETTER implementation of this same functionality see
   LogFacility_file.py
   +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

   Instantiate a file-logger object which can be used to log to a file
   using the standard Python "logging" framework. Rather than returning
   a logging.logger object (which would expose all the methods supported
   by such an object) this Class returns a Class instance which exposes
   only  the method f_logger.log("<LOGLVL>", "<message>"). Therefore,
   the logging.logger object can only be manipulated upon instanatiation.

   Since we are working with files and file I/O the Class returns a
   a context-manager so that all file resources are properly released. 
   The __enter__() method returns the Class instance, so no "as"
   target is specified in the "with" statement.

  Usage:

  import utils
  import sys
  ## init FileLogger
  d_log_args = { 'log_filepath': <logpath>, 'min_log_level': logging.(DEBUG|INFO|ERROR), 'loghash': <32char-str> }
  try:
    f_logger = FileLogger(myname, d_log_args)
  except Exception as e:
    utils.stderr_notify(myname, "FileLogger().init() failed", {'exc':e, 'exit':2})

  ## Use context manager 
  with f_logger: 
    test_msg = "This is a test file-log message"
    f_logger.log('DEBUG', "%s: %s" % (myname, test_msg))

  sys.exit(0)

"""
import logging
import logging.handlers
import uuid
import sys

## custom libs
import utils

##------------------------------------------------------------------------------ 
##
## Defaults: can be overridden on instantiation
##

DEBUG = 3

## default log-rotation type (overwrite, rotate, hourlyrotate, dailyrotate)
DEFAULT_ROTATION = 'overwrite'

DEFAULT_PATH  = './fanselow_app.log'

## default minimum log level (i.e. if min_level=logging.INFO, logger.debug() does not log)
DEFAULT_MIN_LEVEL = logging.INFO ## Don't make this a string!!
##OTHER LEVELS: CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, NOTSET=0

##-----------------------------------------------------------------------------
class ReqArgError(Exception):
  pass

##-----------------------------------------------------------------------------
class InvalidLoggingType(Exception):
  pass

##-----------------------------------------------------------------------------
class InvalidLoggingLevel(Exception):
  pass

##------------------------------------------------------------------------------ 
class FileLogger(object):

  ## init(): Create application log-handler
  def __init__(self, caller, d_init_args):

    ## instance-name (don't want this overriden)
    self.__name = 'FileLogger'

    ## class-name
    cname = self.__class__.__name__
    self.cname = cname 

    self.log_handle_name = caller 
    self.DEBUG = DEBUG 

    self.loghash = None
    self.handler = None 
    
    self.logger = logging.getLogger(self.log_handle_name)

    self.min_log_level = DEFAULT_MIN_LEVEL 
    self.log_filepath = DEFAULT_PATH
    self.log_rotation = DEFAULT_ROTATION 

    ## min_log_level 
    if 'min_log_level' in d_init_args:
      self.min_log_level = d_init_args['min_log_level']
    
    ## log_filepath 
    if 'log_filepath' in d_init_args:
      self.log_filepath = d_init_args['log_filepath']

    ## log_rotation 
    if 'log_rotation' in d_init_args:
        self.log_rotation = d_init_args['log_rotation']

    ## debug 
    if 'debug' in d_init_args:
      self.DEBUG = d_init_args['debug']

    ## loghash
    if 'loghash' in d_init_args:
      self.loghash = d_init_args['loghash']
    else:
      self.loghash = uuid.uuid4().hex

    ##-----------------------------
    ## set level
    self.logger.setLevel(self.min_log_level) 

    ##-----------------------------
    ## Handler based on input (or default) "log_rotation" and "log_filepath"
    if self.log_rotation == 'overwrite':
      self.handler = logging.FileHandler(self.log_filepath)
    elif self.log_rotation == 'rotate':
      self.handler = logging.handlers.RotatingFileHandler(self.log_filepath, maxBytes=300000, backupCount=5)
    elif self.log_rotation == 'hourlyrotate':
      self.handler = logging.handlers.TimedRotatingFileHandler(self.log_filepath, when="h", backupCount=60)
    elif self.log_rotation == 'dailyrotate':
      self.handler = logging.handlers.TimedRotatingFileHandler(self.log_filepath, when="d", backupCount=60)
    else:
      raise InvalidLoggingType("%s: Log rotation-type (%s) is not supported" % (self.__name, self.log_rotation)) 
    
    ##-----------------------------
    ## Configure logging format 
    # formatter = logging.Formatter('%(asctime)-15s  %(loghash)s  %(process)-6d  %(levelname)-6s  %(name)s:  %(message)s')
    formatter = logging.Formatter('%(asctime)-15s  %(loghash)s %(levelname)-6s >>  %(message)s')
    self.handler.setFormatter(formatter)
    
    ##-----------------------------
    ## add handler 
    self.logger.addHandler(self.handler)

    ##-----------------------------
    ## Add hash as extra formatter 
    extra = {'loghash': self.loghash }
    self.logger = logging.LoggerAdapter(self.logger, extra)

    msg = "%s: init(): Initialization complete: minLevel=[%s] File=[%s] Rotation=[%s] LoggerName=[%s]" % \
        (self.__name, self.min_log_level, self.log_filepath, self.log_rotation, self.log_handle_name)
    if self.DEBUG > 2:
      print( msg )


##------------------------------------------------------------------------------ 
  def __enter__(self):
    msg = "%s: __ENTER__: Returning Context-Manager type=SELF..." %  (self.__name)
    if self.DEBUG > 2:
      print(msg)
    self.log('DEBUG', msg)
    return( self )

  def __exit__(self, exc_type, exc_value, exc_traceback):
    if exc_value is None:
      msg = "%s: __EXIT__: Cleaning up logger=[%s] on normal close with no exceptions" % (self.__name, self.log_handle_name)
    else:
      msg = "%s: __EXIT__: Cleaning up logger=[%s] on exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.__name, self.log_handle_name, exc_type,exc_value, exc_traceback)

    if self.DEBUG > 2:
      print(msg)
    self.log('DEBUG', msg)
 
    self.logger.handlers = [] 

  #-----------------------------------------------------------------------------
  def log(self, loglvl, msg):
    LVL = loglvl.upper()
    if LVL == 'DEBUG':
      self.logger.debug(msg) 
    elif LVL == 'INFO':
      self.logger.info(msg) 
    elif LVL == 'WARNING':
      self.logger.warning(msg) 
    elif LVL == 'ERROR':
      self.logger.error(msg) 
    elif LVL == 'CRITICAL':
      self.logger.critical(msg) 
    else:
      raise InvalidLoggingLevel("%s: Logging-level (%s) is not supported" % (self.__name, LVL)) 
    return( 1 )

##------------------------------------------------------------------------------ 
  def getLogFilePath(self):
    return(self.log_filepath)   

##------------------------------------------------------------------------------ 
  def getLogHash(self):
    return(self.loghash)
  
##------------------------------------------------------------------------------ 
  def getLogRotation(self):
    return(self.log_rotation)
##------------------------------------------------------------------------------ 


##------------------------------------------------------------------------------ 
##------------------------------------------------------------------------------ 
## TEST
if __name__ == '__main__':

  myname = 'flog_test'
  filepath = "./%s.log" % (myname)
  d_log_args = {'log_filepath': filepath, 'min_log_level': logging.DEBUG}
  try:
    f_logger = FileLogger(myname, d_log_args)
  except Exception as e:
    utils.stderr_notify(self.cname, "FileLogger().init() failed", {'exc':e, 'exit':2})

  with f_logger: 
    test_msg = "This is a debug file-log message"
    f_logger.log('DEBUG', "%s: %s" % (myname, test_msg))
    test_msg = "This is an information file-log message"
    f_logger.log('INFO', "%s: %s" % (myname, test_msg))

