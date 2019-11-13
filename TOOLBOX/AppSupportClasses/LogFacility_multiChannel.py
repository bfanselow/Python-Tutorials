"""

 LogFacility_MultiChannel.py
 Sub-class of ABSTRACT LogFacility() class

 All subclasses of LogFacility() must implement these methods:
  * resourceAllocation()
  * resourceCleanup()

 All subclasses must define these properties:
  * facility_name

 This Python3 class is used to broadcast log messages to multiple backend
 logging "channels" (i.e. imported LogFacility() sub-classes which implement
 the log() method.
 Currently supported: 
  * LogFacility_file   - logging to file
  * LogFacility_db     - logging to a database
  * LogFacility_api    - logging to remote API
  * LogFacility_stdout - provides log-level-filtering and log-formatting for STDOUT and STDERR 
 
 Each facility is intitialized with its own configuration including 
 logging-level.
 
 This class is implemented as a Context-Manager so that backend logging 
 resources are thoroughly/properly released.  Instantiation returns 
 a single logging "handle" which  can be used to dispatch a single log 
 message to ALL of the configured logging channels using the standard 
 python logging-level logic. 

 Implement a context-manager using: "with LogFac as lf": ...
 (__enter__ returns self).

 USAGE: see TEST __main__ at bottom of page
  
"""

import sys

## custom libs
import utils
from CustomExceptions import ReqArgError, InitError
from LogFacility import LogFacility               ## Abstract parent
from LogFacility_file import LogFacility_file     ## File-logging
from LogFacility_db import LogFacility_db         ## Database logging
from LogFacility_api import LogFacility_api       ## Api logging
from LogFacility_stdout import LogFacility_stdout ## Level-filtered and formatted "print" to stdout/stderr 

##----------------------------------------------------------------------------------------
## Provide all supported Logging facility names and the associated Class  
d_AVAILABLE_FACILITIES = {
  "File": LogFacility_file, 
  "Db": LogFacility_db, 
  "Api": LogFacility_api,  
  "Stdout": LogFacility_stdout
}

##----------------------------------------------------------------------------------------
class LogFacility_multiChannel(LogFacility):
  def __init__(self, d_init_args):

    self.facility_name = 'MultiChannel'
    
    super().__init__(d_init_args)
    ## Set by super()__init__():
    ##  debug 
    ##  session_id 
    ##  dup_to_stdout 
    ##  logging-level 
    ##  caller
    ##  oid 
   
    self.cname = self.__class__.__name__

    self.d_available_facilities = d_AVAILABLE_FACILITIES 
    self.d_active_facilities = {}

    ## Instantiate each facility class and store associated facility object 
    for fname in self.d_available_facilities:
      if fname in d_init_args: 
        if self.DEBUG > 2:
          print("%s: init(): Requested facility [%s]" % (self.oid, fname))
        d_log_args = d_init_args[fname] 

        ## pass session_id thru to each instantiated facility 
        if 'session_id' not in d_log_args:
          d_log_args['session_id'] = self.session_id

        ## pass caller thru to each instantiated facility (if != self.cname) 
        if 'caller' not in d_log_args:
          if self.caller != self.cname:
            d_log_args['caller'] = self.caller

        LogFacilityClass = self.d_available_facilities[fname] 

        try:
          o_lf = LogFacilityClass(d_log_args)
        except Exception as e:
          err_msg = "%s: %s().init() failed with exception: %s" % (self.oid, str(LogFacilityClass), e)
          raise InitError(err_msg)

        self.d_active_facilities[fname] = o_lf
        if self.DEBUG >2:
          print("%s: init(): Instantiated/stored logging object for facility-name: [%s]" % (self.oid, fname))

    N_facilities = len(self.d_active_facilities.keys())
    if N_facilities == 0: 
      raise InitError("%s: No logging facilities provided" % (self.oid))
 
    if self.DEBUG > 1:
      print("%s: Initialization complete" % (self.oid) )
 
  ##--------------------------------------------------------------------------------------
  def log(self, facility, s_level, msg):
    ## super().log does log-level-filtering and formatting and returns formatted message
    ## (or None if not passing level-filtering)

    l_facilities = list( self.d_available_facilities.keys() )
    l_facilities.append( '*' )

    ## Just in case this method was called with log(<level>, <msg>) as for other facilities
    ## in which case <facility> which actually be <level>
    ## Warn and set facility to "*"
    if facility in self.LOG_LEVELS:
      facility = '*'
      LFH.log('ERROR', "Missing required facility for multiChannel log()" % (self.oid)) 

    fmtd_msg = super().log(s_level, msg)
    if fmtd_msg:
      if facility in l_facilities:

        ## all facilities 
        if facility == '*':
          for fname in self.d_active_facilities: 
            LFH = self.d_active_facilities[fname]
            LFH.log(s_level, msg) 

        ## specific facility 
        else:
          if facility in self.d_active_facilities: 
            LFH = self.d_active_facilities[facility]
            LFH.log(s_level, msg) 

      ## unsupported facility name - notify of this on all active facilities
      else: 
        for fname in self.d_active_facilities: 
          LFH = self.d_active_facilities[fname]
          LFH.log('ERROR', "%s: Invalid logging facility: (%s)" % (self.oid, fname)) 
          LFH.log(s_level, msg) 

  ##--------------------------------------------------------------------------------------
  def getActiveFacilities(self):
    return(self.d_active_facilities) 
 
  ##--------------------------------------------------------------------------------------
  def getAllFacilities(self):
    return(self.d_available_facilities) 
 
  ##--------------------------------------------------------------------------------------
  def resourceAllocation(self):
    pass ## implemented by each facility's same method 
 
  ##--------------------------------------------------------------------------------------
  def resourceCleanup(self, caller=None):
    self.log('*', "DEBUG", "%s: Cleaning up all logging resources on request of [%s]..." % (self.oid, caller))
    for fname in self.d_active_facilities: 
      self.log('*', "DEBUG", "%s: Cleaning up all logging resources for [%s] on request of [%s]..." % (self.oid, fname, caller))
      LFH = self.d_active_facilities[fname]
      LFH.resourceCleanup() 

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
      msg = "%s: __EXIT__: Cleaning up ALL facility resources on normal close with no exceptions" % (self.oid)
      if self.DEBUG: 
        print("%s" % msg)  
    else:
      msg = "%s: __EXIT__: Cleaning up ALL facility resources on exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.oid, exc_type,exc_value, exc_traceback)
      utils.stderr_notify(self.oid, msg)

    self.resourceCleanup('self')

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":
 
  sys.path.append('./config')
  import DATABASE as config_db

  myname = "mcl_tester"
  session_id = '3e9gjsdkjlsk993klskjge9dsfkdjsel' 
  
  db_storage_id = "workflow_applog"  
  log_filepath = "./%s.log" % (myname)
  
  print("%s: STARTING CLASS-TEST" % (myname))
  
  ## Configure each backend log-facilities and associated parameters (level, etc.) 
  ## Here, we configure file, database and STDOUT facilities 
  d_log_config = {
    "caller": myname, 
    "File":   {"log_filepath":  log_filepath, "min_log_level": 'DEBUG', "session_id": session_id}, 
    "Db":     {"storage_id":db_storage_id, "config_module":config_db, "min_log_level":'INFO', "session_id":session_id}, 
    "Stdout": {"target": 'STDOUT,STDERR',  "min_log_level": 'ERROR', "session_id": session_id} 
  }

  ## Instantiate the LogFacility_multiChannel()
  LFmC = LogFacility_multiChannel(d_log_config) 

  ## Implement context-manager
  with LFmC as lf:
    for fname in lf.d_active_facilities:
      log_h = lf.d_active_facilities[fname]

      ## test connections
      print("%s: Testing logging resources on facility: %s" % (myname, fname) )
      try:
        log_h.test()
      except Exception as e:
        errmsg = "ERROR - Init test failed with exception on logging facility [%s]" % (fname)
        utils.stderr_notify(myname, errmsg,  {'exc':e, 'exit':2})

      ## send log messages directly to each facility 
      msg = "%s: LOG-TEST direct to facility=[%s]" % (myname,fname)
      log_h.log("INFO", msg)

    ## dispatch to a specific facility using the LogFacility_multiChannel object 
    lf.log("Db", "INFO", "This is an info-level test msg for Db facility via LogFacility_multiChannel")
    lf.log("File", "INFO", "This is an info-level test msg for File facility via LogFacility_multiChannel")
    lf.log("File", "DEBUG", "This is a debug-level test msg for File facility via LogFacility_multiChannel")
   
    ## dispatch to a ALL facilities at once using the LogFacility_multiChannel object 
    lf.log("*", "ERROR", "This is an error-level test msg sent to ALL facilities")
    
  print("%s: FINISHED CLASS-TEST" % (myname))
