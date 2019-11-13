"""

 LogFacility_api.py
 Child class of ABSTRACT class LogFacility().

 All subclasses of LogFacility() must implement these methods:
  * log()
  * resourceAllocation()
  * resourceCleanup()

 All subclasses must define these properties:
  * facility_name

 Use this class as a simple way to manage sending log-messages to a (remote) API.
 Also can be used as one of multiple logging "facilities" to be accessed by
 the LogFacility_multiChannel() class (see LogFacility_multiChannel class
 for more details on how to do that).

 Pass in to init() a dict containing logging_api_url, a unique session_id, and the
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

##----------------------------------------------------------------------------------------
##
## Defaults: can be overridden on instantiation with init() args
##

##----------------------------------------------------------------------------------------
class LogFacility_api(LogFacility):
  def __init__(self, d_init_args):

    self.facility_name = 'Api' 

    super().__init__(d_init_args)
    ## Set by super()__init__():
    ##  debug  
    ##  session_id 
    ##  dup_to_stdout
    ##  logging-level
    ##  caller

    self.cname = self.__class__.__name__

    self.api_h = None 

    ## api_url
    if 'api_url' in d_init_args:
      self.api_url = d_init_args['api_url']
    else:
      raise InitError("%s: Missing required init() arg: [api_url]" % (self.cname) )
    
    ## Create the api log handle (This will be used by Class' log() method to manage logging to the API)
    try:
      self.resourceAllocation() ## sets self.api_h
    except Exception as e:
      raise

    if self.DEBUG > 1:
      print("%s: Initialization complete" % (self.cname) )
 
  ##----------------------------------------------------------------------------------------
  def log(self, s_level, msg):
    ## super().log does log-level-filtering and formatting and returns formatted message
    ## (or None if not passing level-filtering)

    fmtd_msg = super().log(s_level, msg)
    if fmtd_msg:
      print("PRETEND-API-LOG.%s: %s" % (self.api_url, fmtd_msg))
      ##self.api_logger()

    return( 1 )
 
 
  ##----------------------------------------------------------------------------------------
  def resourceCleanup(self):
    self.log("DEBUG", "%s: Cleaning up all logging resources..." % (self.cname))

  ##----------------------------------------------------------------------------------------
  def resourceAllocation(self):
    ## Return a log-handle attached to API which will be used by the Class' PUBLIC log() method
    if self.DEBUG > 2:
      print("%s: Allocating logging-resources..." % (self.cname))
    
    api_handle = None

    ## TODO: Bind api_handle to API

    self.api_h = api_handle
   
    msg = "Logging resource-allocation complete: API=[%s] minLogLevel=[%s] sessionId=[%s]" % (self.api_url, self.s_min_level, self.session_id)
    self.log("DEBUG", "%s: %s" % (self.cname, msg))

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
      msg = "%s: __EXIT__: Cleaning up API resources on normal close with no exceptions" % (self.cname)
      if self.DEBUG > 1:
        print("%s" % msg)
    else:
      msg = "%s: __EXIT__: Cleaning up API resources on exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.cname, exc_type,exc_value, exc_traceback)
      utils.stderr_notify(self.cname, msg)

    self.resourceCleanup()

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":
  
  myname = 'al_tester'

  api_url = 'http://some.random.api/logMsg' 
  ## POST payload { "message": <message> }

  d_log_config = {"api_url": api_url, "min_log_level": 'INFO', 'caller': myname }

  ## Instantiate with logging config
  a_logger = LogFacility_api(d_log_config)

  print("%s: Testing api-logging resources" % (myname) )
  with a_logger as log_h:
    try:
      log_h.test()
    except Exception as e:
      utils.stderr_notify(myname, "[Api] Resource test failed with exception",  {'exc':e, 'exit':2}) 

    ## send log messages to the API 
    msg = "%s: Sample log message to api=[%s]" % (myname, api_url)
    log_h.log("INFO", msg)
    log_h.log("DEBUG", msg)
    log_h.log("ERROR", msg)


