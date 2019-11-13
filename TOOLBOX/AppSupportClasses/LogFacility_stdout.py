"""

 LogFacility_stdout.py
 Child class of ABSTRACT class LogFacility().

 All subclasses of LogFacility() must implement these methods:
  * resourceAllocation()
  * resourceCleanup()

 All subclasses must define these properties:
  * facility_name


 Use this class as a simple way to print messages to STDOUT and/or
 STDERR after performing the same log-level-filtering and message formatting
 used by the other LogFacility_* classes.

 Also can be used as one of multiple logging "facilities" to be accessed by
 the LogFacility_multiChannel() class (see LogFacility_multiChannel class
 for more details on how to do that).

 Pass in to init() a dict containing "targets" (STDOUT and/or STDERR), a 
 unique session_id, and the minimum-logging-level (messages with logging-level 
 below this are not processed).

 Options for "targets":
  * Print messages above min-log-level to STDOUT: {'targets': 'STDOUT' }
  * Same as above and also print ERROR message to STDERR: { 'targets': 'STDOUT,STDERR' }
  * DEFAULT if not specified: ('targets': 'STDOUT' }

 USAGE: see TEST __main__ at bottom of page 

"""

import sys

## custom libs
import utils
from CustomExceptions import ReqArgError, InitError
from LogFacility import LogFacility ##(parent)

##----------------------------------------------------------------------------------------
##
## Defaults: can be overridden on instantiation with init() args
##

##----------------------------------------------------------------------------------------
class LogFacility_stdout(LogFacility):
  def __init__(self, d_init_args):

    self.facility_name = 'Stdout' 
    
    super().__init__(d_init_args)
    ## Set by super()__init__():
    ##  debug 
    ##  session_id 
    ##  dup_to_stdout 
    ##  logging-level 
    ##  caller
    
    self.cname = self.__class__.__name__

    ## targets 
    if 'targets' in d_init_args:
      self.targets = d_init_args['targets']
    else:
      self.targets = 'STDOUT' 

    if self.DEBUG > 1:
      print("%s: Initialization complete" % (self.cname) )

  ##----------------------------------------------------------------------------------------
  def log(self, s_level, msg):
    ## super().log does log-level-filtering and formatting and returns formatted message
    ## (or None if not passing level-filtering)

    fmtd_msg = super().log(s_level, msg)
    if fmtd_msg:
      if self.targets == 'STDOUT':
        print(fmtd_msg)
      elif self.targets == 'STDOUT,STDERR':
        print(fmtd_msg)
        if s_level == 'ERROR':
          utils.stderr_notify(self.cname, fmtd_msg)

    return( 1 )
 
  ##----------------------------------------------------------------------------------------
  def resourceCleanup(self):
    pass ## "dummy" method to obey abstract parent class 

  ##----------------------------------------------------------------------------------------
  def resourceAllocation(self):
    pass ## "dummy" method to obey abstract parent class 

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":
 
  myname = 'lp_tester'

  targets = 'STDOUT,STDERR'

  d_log_config = {"targets": targets, "min_log_level": 'INFO', 'caller': myname }

  ## Instantiate with logging config.
  ## NOTICE: Here, our returned object is the log-handle since we don't use a contect manager
  log_h = LogFacility_stdout(d_log_config)

  print("%s: Testing stdout-logging resources" % (myname) )
  try:
    log_h.test()
  except Exception as e:
    errmsg = "%s: ERROR - [Stdout] Resource test failed" % (myname)
    utils.stderr_notify(myname, errmsg,  {'exc':e, 'exit':2})

  ## send log messages
  msg = "%s: LOG-TEST to stdout. Targets=[%s]" % (myname, targets)
  log_h.log("INFO", msg)
  log_h.log("DEBUG", msg)
  log_h.log("ERROR", msg)
