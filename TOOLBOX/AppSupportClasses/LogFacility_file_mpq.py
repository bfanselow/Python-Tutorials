"""

 LogFacility_file_mpq.py
 Child class of ABSTRACT class LogFacility().
 All subclasses of LogFacility() must implement these methods:
  * log()
  * resourceAllocation()
  * resourceCleanup()

 All subclasses must define these properties:
  * facility_name

 This class is similar to the LogFacility_file() class, but provides the 
 ability for sending log-messages to a single log file from multiple processes.

 Using python (stdlib) logging is thread-safe, allowing mulitple threads (running 
 in a single process) to write to single file. However, logging to a single file 
 from multiple processes is not supported since there is no standard way to 
 serialize access to a single file across multiple processes in Python. Passing a 
 shared logger object to multiple sub-processes will appear (on the surface) to work 
 just fine in simple low-load tests, but heavy logging from many processes 
 (particularly with a RotatingFileHandler) is vulnerable to logfile corruption as 
 multiple processes will invariably attempt to write to the file concurrently
 leading to interleaved writes by different processes.

 There are a few options if you need to log to a single file from multiple 
 processes.  This class uses the simple approach of start up a multiprocessing 
 Queue.  All sub-process objects put() their log message onto this queue while 
 a queue listener will get() incoming messages off the queue write them to a 
 single file using Logger. Since all concurreny issues are handled by the Queue, 
 there is no danger of curruption. There are some gotchas associated with queue 
 deadlocks which must be considered with this approach, though I haven't considered 
 all of these scenarios yet.

 USAGE: see TEST __main__ at bottom of file

"""

import os 
import sys 
import time 
import logging
import logging.handlers
import multiprocessing
import atexit 

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

DEFAULT_LOG_PATH  = './wfanselow_app.log'

##----------------------------------------------------------------------------------------

l_VALID_ROTATION_TYPES = ['overwrite', 'rotate', 'hourlyrotate', 'dailyrotate']

##----------------------------------------------------------------------------------------
class InvalidRotationType(Exception):
  pass

##--------------------------------------------------------------------------------
class LogFacility_file_mpq(LogFacility):
  def __init__(self, d_init_args):
    
    self.facility_name = 'FileMPQ'
    self.logger = None

    super().__init__(d_init_args)
    ## Set by super()__init__():
    ##  debug 
    ##  session_id 
    ##  dup_to_stdout
    ##  logging-level
    ##  caller
    ##  oid 

    self.cname = self.__class__.__name__

    ## This is a multi-process safe method for debugging concurrency issues.
    ## Uncomment this for debugging
    ## multiprocessing.log_to_stderr(logging.DEBUG)
   
    ## Queue 
    self.queue = None 
    if 'queue' in d_init_args:
      self.queue = d_init_args['queue']
    else: 
      self.queue = multiprocessing.Queue()   

    ## Listener 
    self.listener = None    ## set by qlistenerStart()

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
    self.resourceAllocation() ## sets self.logger

    ## Start Queue listener
    pid = self.__qlistenerStart()

    if self.DEBUG > 1:
      self.__dlog("DEBUG", "%s: Initialization complete" % (self.cname) )

  ##----------------------------------------------------------
  def log(self, s_level, msg):

    ## This bascially does a put(msg) onto the queue. Queue-listener will get() and write to file.
    ## super().log does log-level-filtering and formatting and returns formatted message
    ## (or None if not passing level-filtering)

    if msg == 'QSTOP!':
      self.queue.put(None)
    else:

      fmtd_msg = super().log(s_level, msg)
      if fmtd_msg:
        LVL = s_level.upper()
        d_record = {"level": LVL, "msg": fmtd_msg}
        self.queue.put(d_record)

  ##----------------------------------------------------------------------------------------
  def resourceCleanup(self):
    tag = self.cname + '.resourceCleanup' 
    self.__dlog("DEBUG", "%s: Terminating queue-listener..." % (tag))
    self.__qlistenerStop(1)
    self.__dlog("DEBUG", "%s: Cleaning up all logger handlers..." % (tag))
    self.logger.handlers = []

  ##----------------------------------------------------------------------------------------
  def resourceAllocation(self):
    ## Return a logging.logger which will be used by the Class' PUBLIC log() method
    
    tag = self.cname + '.resourceAllocation' 

    if self.DEBUG > 1:
      print("%s: Allocating logging-resources..." % (tag))

    handler = None
    log_handle_name = self.oid

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

    self.__dlog("DEBUG", "%s: %s" % (tag, msg))

    return(1)

  ##--------------------------------------------------------------------------------
  def checkListener(self):
    status = 0 
    q_listener = self.listener 
    if q_listener.is_alive(): 
      status = 1
    return( status )

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
      msg = "%s: __EXIT__: Cleaning up on normal close with no exceptions" % (self.cname)
      self.__dlog("DEBUG", msg)
    else:
      msg = "%s: __EXIT__: Cleaning up on exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.cname, exc_type,exc_value, exc_traceback)
      self.__dlog("ERROR", msg)
      utils.stderr_notify(self.cname, msg)

    self.resourceCleanup()

  ##----------------------------------------------------------
  def __log_to_file(self, d_record):

    ## Write the message to file (called by qlistener, NOT directly by processes)

    msg = d_record['msg']
    LVL = d_record['level']

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

    return( 1 )

  ##----------------------------------------------------------
  def __dlog(self, s_level, msg):

    ## This method does a "direct" log to file, without putting message on queue. 
    ## This is used for internal class messages that may occur after the queue 
    ## listener has stopped.

    fmtd_msg = super().log(s_level, msg)
    if fmtd_msg:
      LVL = s_level.upper()
      d_record = {"level": LVL, "msg": fmtd_msg}
      self.__log_to_file(d_record)

  ##----------------------------------------------------------
  def __listener(self):
    
    tag = self.cname + '.__listener' 

    msg_count = 0

    ## Read from the queue
    while True:
      try:
        d_record = self.queue.get()
        msg_count += 1
        if (d_record is None):
          self.__dlog("INFO", "%s: qListener got STOP message. Messages processed=[%d]" % (tag, msg_count))
          break
        self.__log_to_file(d_record)

      except (KeyboardInterrupt, SystemExit) as e:
        self.__dlog("CRITICAL", "%s: qListener ABORTING on interrupt: %s" % (tag, e))
        break
      except EOFError as e:
        self.__dlog("CRITICAL", "%s: qListener ABORTING on EOF error: %s" % (tag, e))
        break
      except Exception as e:
        self.__dlog("CRITICAL", "%s: qListener ABORTING on exception: %s" % (tag, e))
        break
        
    self.__dlog("INFO", "%s: qListener stopped. Messages processed: %d" % (tag, msg_count))

  ##--------------------------------------------------------------------------------
  def __qlistenerStart(self, d_args=None):

    tag = self.cname + '.__qlistenerStart' 

    pid = None
    q_listener = multiprocessing.Process(target=self.__listener, name="q_listener", args=())
    q_listener.daemon = True
    try:
      q_listener.start()
      pid = q_listener.pid
    except Exception as e:
      utils.stderr_notify(tag, "Failed to Start listener process",  {'exc':e, 'exit':2})

    self.__dlog("INFO", "%s: qListener started..." % (tag))
    atexit.register(self.__qlistenerStop)

    self.listener = q_listener 

    return( pid )

  ##--------------------------------------------------------------------------------
  def __qlistenerStop(self, delay=None):
    
    tag = self.cname + '.__qlistenerStop' 

    q_listener = self.listener 

    self.__dlog("INFO", "%s: Request received to stop qListener" % (tag))

    if q_listener.is_alive(): 
      self.__dlog("INFO", "%s: Stopping qListener" % (tag))
      if delay:
        time.sleep(delay)
      q_listener.terminate
    else: 
      self.__dlog("INFO", "%s: qListener is no longer alive" % (tag))

    ecode = q_listener.exitcode
    self.__dlog("INFO", "%s: qListener stopped with exitcode=%s" % (tag, ecode))

    return( ecode )

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
## The following sample script illustrates spawning 2 multiprocessing workers 
## which will both log information to the same shared log facility using a
## queue.
if __name__ == "__main__":

  myname = 'flmpq_tester'

  log_filepath = "./%s.log" % myname
  d_log_config = {"debug": 3, "log_filepath": log_filepath, "min_log_level": 'DEBUG', 'caller': myname }
   
  ##-------------------------- 
  ## Random functions 
  ## 
  def do_some_stuff(fl_mpq):
    tag = "%s.do_some_stuff" % (myname)
    print("%s: Starting..." % (tag))
    fl_mpq.log('INFO', "[%s] Yo, starting method..." % (tag))
    for x in range(10):
      fl_mpq.log('INFO', "[%s] Yo, still in method: (%d)" % (tag, x))
      time.sleep(2)
    fl_mpq.log('INFO', "[%s] Yo, done with method..." % (tag))
    print("%s: Stopping !!" % (tag))
    return( 1 )

  def find_something_bad(fl_mpq):
    tag = "%s.find_something_bad" % (myname)
    print("%s: Starting..." % (tag))
    fl_mpq.log('INFO', "[%s] I'm starting method..." % (tag))
    for x in range(14):
      fl_mpq.log('INFO', "[%s] I'm still in method: (%d)" % (tag, x))
      time.sleep(1.2)
    fl_mpq.log('INFO', "[%s] I'm done with method..." % (tag))
    print("%s: Finished" % (tag))
    return( -1 )
  
  ##-------------------------- 
  ## Multiprocessing Workers 
  ## 
  def worker_job_A(fl_mpq):
    tag = "%s.worker_job_A" % (myname)
    pid = os.getpid()
    found = do_some_stuff(fl_mpq)
    fl_mpq.log('INFO', "%s: [%s] Found=(%d)" % (tag, pid, found))
    if found:
      fl_mpq.log('WARNING', "%s: [%s] Something found" % (tag, pid))

  def worker_job_B(fl_mpq):
    tag = "%s.worker_job_B" % (myname)
    pid = os.getpid()
    status = find_something_bad(fl_mpq)
    if status < 0: 
      fl_mpq.log('CRITICAL', "%s: [%s] Failure detected" % (tag, pid))

  ##-------------------------- 
  ## Main()
  ## 
  fl_mpq = LogFacility_file_mpq( d_log_config )

  with fl_mpq:
    ## start workers
    workerA = multiprocessing.Process(target=worker_job_A, name="worker_A", args=(fl_mpq,))
    workerA.start()
    workerB = multiprocessing.Process(target=worker_job_B, name="worker_B", args=(fl_mpq,))
    workerB.start()

    ## main() continues
    ## send log messages to the file
    if fl_mpq.checkListener():
      msg = "%s: Listener is up: Sample INFO message to file=[%s]" % (myname, log_filepath)
      fl_mpq.log("INFO", msg)
      time.sleep(1)
    if fl_mpq.checkListener():
      msg = "%s: Listener is up: Sample DEBUG message to file=[%s]" % (myname, log_filepath)
      fl_mpq.log("DEBUG", msg)
      time.sleep(1)
    if fl_mpq.checkListener():
      msg = "%s: Listener is up: Sample ERROR message to file=[%s]" % (myname, log_filepath)
      fl_mpq.log("ERROR", msg)

    workerA.join()
    workerB.join()
  
      
  sys.exit(0)         
