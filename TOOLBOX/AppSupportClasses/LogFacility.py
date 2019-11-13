"""

 LogFacility.py
 ABSTRACT Parent Class for the implementing various logging "facilties" provided
 by the LogFacility_* (concrete) sub-classes.

 Currently supported sub-classes:
  * LogFacility_file:   logging to file
  * LogFacility_db:     logging to a database
  * LogFacility_api:    logging to remote API
  * LogFacility_stdout: provides log-level-filtering and log-formatting for STDOUT and STDERR
  * LogFacility_multiChannel: logging to multiple facilities at once. 

 As an abstract class this Class cannot be instantiated. It is only
 intended to enforce the implementation behavior of its (child) sub-classes.
 All subclasses must implement these methods:
  * log()
  * resourceAllocation()
  * resourceCleanup()
 
 All subclasses must define these properties:
  * facility_name

 Instantiating a LogFacility_*() object provides a simple way to manage 
 sending log-messages to one or more logging facilties (a.k.a "channels") 
 such as file, database, remote-API, etc. with log-level-filtering, formatting, etc.
 See each facilitiy subclass file for more specific logging implementation info.

"""
import datetime
import logging
import getpass
import uuid
import sys
import abc

from CustomExceptions import ReqArgError, InitError
import utils
##----------------------------------------------------------------------------------------
##
## Defaults: can be overridden on instantiation with init() args
##
DEBUG = 2

## Log-level-threshhold. No message with level below this will get processed.
## Leave as string (not logging.INFO)!!
DEFAULT_MIN_LOG_LEVEL = 'DEBUG'

l_LOG_LEVELS = [ 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET' ]

##----------------------------------------------------------------------------------------
class LogFacilityError(Exception):
  pass

##----------------------------------------------------------------------------------------
class LogFacility(abc.ABC):
  def __init__(self, d_init_args):
    self.cname = self.__class__.__name__
     
    @abc.abstractproperty
    def facility_name(self):
        return 'unknown'

    self.user = getpass.getuser()
    
    self.caller = None 
    self.LOG_LEVELS = l_LOG_LEVELS 
 
    ## debug:
    self.DEBUG = DEBUG 
    if 'debug' in d_init_args:
      self.DEBUG = d_init_args['debug']
    
    ## caller:
    if 'caller' in d_init_args:
      self.caller = d_init_args['caller']

    ## "object-ID": (caller.cname)
    self.oid = self.cname
    if self.caller:
      self.oid = "%s.%s" % (self.caller, self.cname)

    ## dup_to_stdout:
    ## For testing: set dup_to_stdout=1 so all log messages also go to STDOUT
    self.dup_to_stdout = 0 
    if 'dup_to_stdout' in d_init_args:
      self.dup_to_stdout = d_init_args['dup_to_stdout']

    ## session_id
    self.session = None
    if 'session_id' in d_init_args:
      self.session_id = d_init_args['session_id']
    else:
      self.session_id = self.makeSessionId(uuid.uuid4()) 

    ## logging level
    ## This can be misleading: we pass in "min_log_level" as a string. We then
    ## convert to logging.loglevel int value and store this INT as self.min_level,
    ## and store the string as self.s_min_level
    s_min_level = DEFAULT_MIN_LOG_LEVEL

    if 'min_log_level' in d_init_args:
      s_min_level = d_init_args['min_log_level']
    if s_min_level not in l_LOG_LEVELS:
      raise InitError("%s: Invalid min-log-level: [%s]" % (self.cname, s_min_level))
    self.min_level = logging.getLevelName(s_min_level) ## integer
    self.s_min_level = s_min_level ## string 


  ##----------------------------------------------------------------------------------------
  @abc.abstractmethod
  def log(self, s_level, msg):

    ## This abtract method is called by sublass().log(). It takes the log-level and message
    ## and handles log-level filtering and message-formatting. It returns the formmated message
    ## (or None if not at/above min-log-level).  The subclass().log() then takes the return 
    ## and performs implementation-specific logging

    s_LEVEL = s_level.upper()
    if s_LEVEL not in l_LOG_LEVELS:
      raise LogFacilityError("Unspported log level: [%s]" % (s_LEVEL))
 
    loglvl = logging.getLevelName(s_LEVEL) ## integer

    fmtd_msg = None   
    if loglvl >= self.min_level:
      fmtd_msg = self.__formatMessage(s_level, msg) 
      if self.dup_to_stdout:
        print("%s: [%s] DUP-TO-STDOUT [%s]" % (self.cname, s_level, fmtd_msg))
 
    return(fmtd_msg)
  
  ##----------------------------------------------------------------------------------------
  @abc.abstractmethod
  def resourceCleanup(self):
    pass ## implemented entirely by subclass

  ##----------------------------------------------------------------------------------------
  @abc.abstractmethod
  def resourceAllocation(self):
    pass ## implemented entirely by subclass

  ##----------------------------------------------------------------------------------------
  def fields(self, s_level, msg):
    
    ## This method is similar to the above log() method. It takes the log-level and message
    ## and handles log-level filtering. However, instead of re-formatting the message, it
    ## returns a dict containing each of the main fileds of the formatted message (which 
    ## can be used by callers like the database logging facility).  It returns None 
    ## if not at/above min-log-level.  
    
    s_LEVEL = s_level.upper()
    loglvl = logging.getLevelName(s_LEVEL) ## integer
    
    d_fields = None   
    
    if loglvl >= self.min_level:
      d_fields = {
        "loglevel":   s_level,
        "session_id": self.session_id,
        "timestamp":  str(datetime.datetime.now()),
        "user":       self.user,
        "message":    msg
      }

    return(d_fields) 
  
  ##----------------------------------------------------------------------------------------
  @staticmethod
  def makeSessionId(input_text=None):
    hash = utils.makeUniqHash(input_text) 
    return(hash) 

  ##----------------------------------------------------------------------------------------
  def getSessionId(self):
    return(self.session_id) 
  
  ##----------------------------------------------------------------------------------------
  def getFacilityType(self):
    return(self.facility_name) 
  
  ##----------------------------------------------------------------------------------------
  def test(self, opt_text=None):
    ## Perfrom some testing of the logging resources
    msg = "%s: TESTING CHANNEL CONNECTION TO FACILITY=[%s]" % (self.cname, self.facility_name)
    if opt_text:
      msg += ": %s" % opt_text
    self.log('INFO', msg) 
  
  #-----------------------------------------------------------------------------
  def __formatMessage(self, s_level, msg):
    timestamp = str(datetime.datetime.now())
    fmtd_msg = "%-15s  %s %-8s %s >>  %s" % (timestamp, self.session_id, s_level, self.user, msg)
    return( fmtd_msg )

##----------------------------------------------------------------------------------------
## CLASS TEST (should fail as ABSTRACT class cannot be instantiated)
##----------------------------------------------------------------------------------------
if __name__ == "__main__":

  myname = 'abstract_tester'

  print("%s: Testing abstact class instantiation" % (myname) )
  logger = LogFacility( {} )
  ## should produce output:
  ## TypeError: Can't instantiate abstract class LogFacility with abstract methods ... 


