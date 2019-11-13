"""

 Class: StdApp()  a.k.a. "Standard-Application"

 Python3 class with provides some application-utility methods and attributes available 
 to all sub-classes that inherit from this class.  All subclasses have access to the 
 following methods and atributes:

 --------------------------------------------------------
 1) SESSION Attributes: Attributes providing unique application session variables
    (session_id, session_pid, session_user).
       Usage:
        * Child passes { 'session_id': <session_id> } to StdApp.init() or it will be created here.
        * Child references self.sessionn_id, self.session_pid, self.session_user

 --------------------------------------------------------
 2) OID: Attribute providing an "object-identication" which doesn't hide the child-class name. 
       Usage:
        * Child passes { 'caller': <caller-id> } to StdApp.init() or it will be created here.
        * Child references self.oid

 --------------------------------------------------------
 3) LOGGING: Logging method providing log-level-filtering, formatting with timestamp, 
    session-id, etc.
       Usage: 
        * Child passes passes d_init arg to specify which type of log-hander to use 
        * Child calls self.log("<level>", "<message>") 
       Three options for log-handler types based on log-handler-arg: 
        1) STDOUT (default): { 'log_h': None } or { 'log_h': 'STDOUT' }
        2) LogFacility() object: { 'log_h': LF } where LF is a LogFacility() object.
        3a) Python logging.Logger object args: {'logger': d_logger} where d_logger is a dict
            of logging.Logger config attributes. Logger will be created in this class.
        3b) Python logging.Logger object: {'logger': logger} where Logger is an already
            created logging.Logger object 
        
     Multi-processing file-logging can be achieved by passing a MultiProcessing queue (see notes below) 
 
 --------------------------------------------------------
 4) CUSTOMIZED MULTI-PROCESS Process(): Sub-classing the multiprocessing.Process() class with
    additional features such as the ability to catch and handle exceptions produced
    by the sub-process workers. 
      Usage:
       * StdApp child includes "from StdApp import Stdapp, CustomSubProc"
       * StdApp child assigns: spw = CustomSubProc(target=self.<worker-function>, name=<worker_name>, args=(arg-tuple,))
       * After spw.start(), can access worker exceptions (if spw.exception: e,tb = spw.exception) 

 --------------------------------------------------------
 5) MULTI-PROCESS QUEUE: General-purpose Queue() object to be used by multiprocess jobs who 
     all need access to a shared Queue. 
 
    Usage: 
      * StdApp child executes:
           a) MPQ = multiprocessing.Queue()     
              Optionally create a mp.Queue() to be passed to step-B. Can just execute step-B 
              which will create the MPQ.
           b) q_listener = startQueueLister(MPQ=None) 
              Create the MPQ (if None is passed) and start a queue listener on MPQ. Return a 
              reference to the listener.
      * Child now has access to the MPQ (self.MPQ) object and the q-listener (self.q_listener).

      Special Case: Multi-process-queue-logging 
        Logging to a single/shared file from multiple processes is not recommended in Python 
        since there is no standard way to serialize access to a single file across multiple 
        processes.  Passing a shared logger object to multiple sub-processes will appear 
        (on the surface) to work in simple low-load tests, but heavy logging from many 
        processes is vulnerable to corruption. To address this we can start a multiprocessing 
        Queue. All sub-process objects put() their log message onto this queue while a 
        queue-listener will get() incoming messages off the queue write them to a single 
        file using file-logging handler.

        HOWTO: Multi-process-queue-logging
         * StdApp child executes: qlistener = self.startQueueLister()
           This will create an MPQ object and start a multiprocess Queue listener on the MPQ. 
         * StdApp child spawns multiprocess.Process() workers and passes this self.MPQ to them.
           These sub-process workers can now safely log to a shared file via the qlistener by 
           executing:  self.MPQ.put( {"level":<loglvl>", "msg":"<msg>"} ).
           If sub-process workers initialize a StdApp() object with the init args: 
           {"log_h", LOG_H} or {"logger", d_logger} and then execute "configureMpqLogging(self.MPQ)", 
           these objects can now all safely log to a shared logfile using the standard logging 
           syntax: self.log("<lvl>", "<msg>").
         * StdApp child which started the qlistener needs to shut down the listening Queue using
           self.stopQueueListener(self, delay_secs) 
 
--------------------------------------------------------

"""

import os 
import abc
import sys
import time
import logging
import getpass
import datetime 
import traceback
import atexit
import multiprocessing

## Custom classes
import utils
from LogFacility import LogFacility
from CustomExceptions import ReqArgError, InitError
##----------------------------------------------------------------------------------------

##----------------------------------------------------------------------------------------
##
## DEFAULTS: can be overridden by init()
##
DEBUG = 2 

## Duplicate non-STDOUT logging to stdout (useful during testing)
DUP_TO_STDOUT = 0 

##----------------------------------------------------------------------------------------
## Internal Exception classes
class InvalidLogFacility(Exception):
  pass

class MultiProcessQueueError(Exception):
  pass

##----------------------------------------------------------------------------------------
class CustomSubProc(multiprocessing.Process):
  ##
  ## Sub-classing the standard multiprocessing.Process class to provide ability to 
  ## catch/store exception created by the spawned sub-process workers.
  ##
  def __init__(self, *args, **kwargs):
    multiprocessing.Process.__init__(self, *args, **kwargs)
    self._pconn, self._cconn = multiprocessing.Pipe()
    self._exception = None

  def run(self):
    try:
      multiprocessing.Process.run(self)
      self._cconn.send(None)
    except Exception as e:
      tb = traceback.format_exc()
      self._cconn.send((e, tb))
      # raise e  # You can still rise this exception if you need to

  @property
  def exception(self):
    if self._pconn.poll():
      self._exception = self._pconn.recv()
    return self._exception

##----------------------------------------------------------------------------------------
class ContextFilter(logging.Filter):
  ## 
  ## This filter allows us to inject custom information into the log records.
  ## 

  def __init__(self, d_filter_args):

    ## session_id: Always added
    self.session_id = d_filter_args['session_id']

    ## Other attrs? 

  ##-----------------------------------------------------------------
  def filter(self, record):
    record.session_id = self.session_id

    ## other attrs? 

    return( True )

##----------------------------------------------------------------------------------------
class StdApp(object):

  def __init__(self, d_init_args):

    self.name = 'StdApp' 
    self.cname = self.__class__.__name__

    self.d_init_args = d_init_args

    self.DEBUG = DEBUG
    if 'debug' in d_init_args:
      self.DEBUG   = d_init_args['debug']
 
    ## Logging defaults 
    self.LOGGING = 1  ## Supress all logging when set to 0
    if 'logging' in d_init_args:
      self.LOGGING = d_init_args['logging']
    self.LOG_H = 'STDOUT'               ## default log handle if no 'log_h' is passed. 
    self.lh_type = 'STDOUT'             ## default logging type 
    self.dup_to_stdout = DUP_TO_STDOUT  ## duplicate log messages to stdout if lh_type is not stdout
    self.mplq = 0                       ## log via the multi-process Queue
    
    ## MPQ defaults 
    self.MPQ = None        ## Reference to mp.Queue() object passed in with method startQueueListener(MPQ)
    self.q_listener = None ## Reference to Queue listener object created by startQueueListener(MPQ)

    ###################################################################### 
    ##
    ## "Session" attributes (session_id, session_pid, session_user)
    ##
    ###################################################################### 
    self.session_pid =  os.getpid() 
    self.session_user = getpass.getuser()

    if 'session_id' in d_init_args:
      self.session_id  = d_init_args['session_id']
    else:
      seed = "%s %s" % (self.session_pid, self.session_user)
      self.session_id = utils.makeUniqHash(seed) 

    ###################################################################### 
    ##
    ## "object-ID": (caller.cname)
    ##
    ###################################################################### 
    self.caller = None
    self.oid = "%s.%s" % (self.name, self.cname)
    if 'caller' in d_init_args:
      self.caller  = d_init_args['caller']
      self.oid = "%s.%s" % (self.cname, self.caller)

    ###################################################################### 
    ##
    ## Logging functionality
    ##
    ###################################################################### 

    ##
    ## dup_to_stderr: Set this =1 for nice troubleshooting of log-handling 
    ##
    if 'dup_to_stdout' in d_init_args:
      self.dup_to_stdout = d_init_args['dup_to_stdout']
    
    ##
    ## Logging "handler": either STDOUT (default), or python logging.Logger, or LogFacility handler.
    ## If self.mplq=1, q-listener will log to this handler.
    ## Child objects that pass this in can then simply call self.log(). 
    ##
    if 'log_h' in d_init_args:
      log_h = d_init_args['log_h']
      if str(log_h) != 'STDOUT':
        if isinstance( log_h, LogFacility ):
          #self.__log_to_so("DEBUG", "%s: Logging configured with LogFacility type=(%s)" % (self.oid, self.lh_type))
          self.LOG_H = log_h
          self.lh_type = log_h.getFacilityType()

    elif 'logger' in d_init_args:
      self.lh_type = 'logger'
      o_logger = d_init_args['logger']
      if isinstance( o_logger, logging.Logger ):
        self.LOG_H = o_logger
        self.__log_to_so("DEBUG", "%s: Logging configured with custom python logging.Logger: (%s)" % (self.oid, self.LOG_H))
      elif isinstance( o_logger, dict ):
        if 'name' not in  o_logger:
          raise InitError("%s: Missing logging.Logger name" % (self.cname))
        logger_name = o_logger['name']
        try:
          self.LOG_H = self.__configurePythonLogger(o_logger) 
        except Exception as e:
          raise InitError("%s: __configurePythonLogger() failed with exception: %s" % (self.cname, e))
        self.__log_to_so("DEBUG", "%s: Logging configured with default python logging.Logger: (%s)" % (self.oid, self.LOG_H))
      else:
        raise InitError("%s: Invalid logger value. Must be dict or Logger" % (self.cname))

    else: ## STDOUT
      self.__log_to_so("DEBUG", "%s: Logging configured with DEFAULT STDOUT logging" % (self.oid)) 

    self.log("DEBUG", "%s: Finished StdApp initialization. Logging with LOG_H: (%s)" % (self.oid, self.LOG_H)) 
    
    ##print(self.__dict__)

  #-----------------------------------------------------------------------------
  def startQueueListener(self, MPQ=None):

    tag = "%s.startQueueListener" % (self.oid)

    q_listener = None

    if MPQ is None:
      try:
        MPQ = multiprocessing.Queue() 
      except Exception as e:
        self.log("ERROR", "%s: multiprocessing.Queue() failed with exception: %s" % (tag, e))
        raise
      self.log("DEBUG", "%s: Created new multiprocess Queue object: (%s)" % (tag, MPQ)) 
    
    else: 
      if isinstance(self.MPQ, multiprocessing.queues.Queue):
        raise MultiProcessQueueError("%s: Invalid multiprocessing.Queue object" % (tag))
      self.log("DEBUG", "%s: Configuring pre-created multiprocess Queue object: (%s)" % (tag, MPQ)) 

    self.MPQ = MPQ

    pid = None
    self.log("DEBUG", "%s: Starting MP.Process() worker for Queue listener..." % (tag))
    q_listener = multiprocessing.Process(target=self.__qlistener, name="Queue_listener", args=(MPQ,))
    q_listener.daemon = True
    try:
      q_listener.start()
      atexit.register(q_listener.terminate)
      pid = q_listener.pid
      self.log("INFO", "%s: qListener started with PID=(%s)" % (tag, pid))
    except Exception as e:
      self.log("ERROR", "%s: qListener.start() failed with exception: %s" % (tag, e))
      raise

    if q_listener.is_alive():
      self.log("INFO", "%s: qListener has started" % (tag))
      d_log = {"level": "INFO", "msg": "%s: qListener has started (delivered to QL)" % (tag)}
      MPQ.put(d_log)
    else:
      self.log("ERROR", "%s: qListener failed to start" % (tag))
      raise MultiProcessQueueError("%s: qListener failed to start" % (tag))

    return( q_listener )

  #-----------------------------------------------------------------------------
  def stopQueueListener(self, delay=None):

    tag = "%s.stopQueueListener" % (self.oid)

    MPQ = self.MPQ

    if MPQ:
      q_listener = self.q_listener

      msg =  "%s: Received request to stop qListener" % (tag)
      self.log("INFO", msg)

      d_log = {"level": "INFO", "msg": msg}
      MPQ.put(d_log)

      if not q_listener:
        self.log("WARNING", "%s: qListener no longer exists" % (tag))
      else:
        if q_listener.is_alive():
          self.log("DEBUG", "%s: qListener is alive. Terminating..." % (tag))
          if delay:
            time.sleep(delay)
          q_listener.terminate
        else:
          self.log("DEBUG", "%s: qListener is no longer alive" % (tag))

        ecode = q_listener.exitcode
        self.log("INFO", "%s: qListener stopped with exitcode=%s" % (tag, ecode))
    else:
      self.log("WARNING", "%s: Multi-process Queue is not defined" % (tag))

    return( ecode )

  #-----------------------------------------------------------------------------
  def configureMpqLogging(self, MPQ):

    tag = "%s.configureMpqLogging" % (self.oid)

    if isinstance(MPQ, multiprocessing.queues.Queue):
      self.MPQ = MPQ 
      self.mplq = 1 
      self.log("INFO", "%s: Configured MPLQ from passed Queue object: (%s)" % (tag, MPQ)) 
    else:
      raise MultiProcessQueueError("%s: Invalid multiprocessing.Queue object" % (tag))

  #-----------------------------------------------------------------------------
  def __qlistener(self, o_mpq):

    tag = "%s.__qlistener" % (self.oid)

    msg_count = 0

    self.log("DEBUG", "%s: qListener is LISTENING on MP queue: %s" % (tag, o_mpq))

    ## Read from the queue
    while True:
      try:
        d_item = o_mpq.get() ## get next item from Queue
        msg_count += 1
        if (d_item is None):
          self.log("DEBUG", "%s: qListener got STOP message. Messages processed=[%d]" % (tag, msg_count))
          break
        else:
          ##
          ## Handle the item pulled from the Queue.
          ## There are different ways of handling the item based on what the item is, and what configurations are set.
          ##
          ##>> Multi-process-queue logging
          if ('level' in d_item) and ('msg' in d_item):
            self.__log_from_queue(d_item)

          ##>> Other operations TBD... 

      except (KeyboardInterrupt, SystemExit) as e:
        raise MultiProcessQueueError("%s: qListener ABORTING on interrupt: %s" % (tag, e))
      except EOFError as e:
        raise MultiProcessQueueError("%s: qListener ABORTING on EOF error: %s" % (tag, e))
      except Exception as e:
        self.log("ERROR", "%s: __qlistener() failed with exception: %s" % (tag, e))
        raise

    self.log("DEBUG", "%s: qListener stopped. Messages processed: %d" % (tag, msg_count))

  #-----------------------------------------------------------------------------
  def __configurePythonLogger(self, d_logger): 
    ##
    ## Configure a Python logging.Logger with a BasicConfig()
    ## Can pass in filename, min-level, format and format-filter 
    ##
    
    logger_name = d_logger['name']
 
    def_fname = "./%s.log" % (self.oid)
    def_min_level = 'DEBUG'

    my_fname = def_fname
    if 'logfile_path' in d_logger:
      my_fname = d_logger['logfile_path']
   
    my_min_level = def_min_level
    if 'min_level' in d_logger:
      my_min_level = d_logger['min_level'] ## this is NOT a string!
    str_min_level = my_min_level.upper()
    int_min_level =  getattr(logging, str_min_level) ## convert string to corresponding logging int

    d_config = {'datefmt': '%Y-%m-%d %H:%M:%S', 'level': int_min_level, 'filename': my_fname }

    ## Default formatting (can be altered by "filter" args)
    d_config['format'] = '%(asctime)s  %(session_id)s  %(levelname)-8s %(message)s'

    ## apply some custom filters for formatting including session_id
    d_filter = {'session_id': self.session_id } 
    logging.basicConfig( **d_config )
    
    logger = logging.getLogger(logger_name)

    try:
      log_filter = ContextFilter(d_filter)
    except Exception as e:
      raise InitError("%s: ContextFilter.init() failed with exception: %s" % (self.cname, e))
    logger.addFilter(log_filter)

    return(logger)

  #-----------------------------------------------------------------------------
  def getLogHandler(self):
    ##
    ## Return the configured logging handler 
    ##
    return( self.LOG_H )

  #-----------------------------------------------------------------------------
  def log(self, s_level, msg, d_args=None):
    ##
    ## Subclasses of StdApp execute self.log() to utilize this method.
    ## Uses either STDOUT, logging.Logger, or LogFacility.log_h (with the
    ## latter two available directly or via mp-logging-queue).
    ##

    ## Logging Queue
    if self.mplq and self.MPQ and self.q_listener:
      d_log = {'level': s_level, 'msg': msg}
      self.MPQ.put(d_log) 

    else:
      if self.lh_type == 'STDOUT':
        self.__log_to_so(s_level, msg)
      elif self.lh_type == 'logger':
        self.__log_to_logger(s_level, msg, d_args)
      else: ## .lh_type == 'log_h'
        self.__log_to_facility(s_level, msg)

    ## Duplicate message to STDOUT. 
    if self.dup_to_stdout:
      if self.lh_type != 'STDOUT':
        self.__log_to_so(s_level, msg)

  #-----------------------------------------------------------------------------
  def __log_to_so(self, s_level, msg):
    ##
    ## Simple STDOUT with no level-filtering
    ##
    if self.LOGGING: 
      timestamp = str(datetime.datetime.now())
      print("%s  %s %-8s %s >> (stdout): %s" % (timestamp, self.session_id, s_level, self.session_user, msg))

  #-----------------------------------------------------------------------------
  def __log_to_facility(self, s_level, msg):

    ## Log to the log-facility created by one of the LogFacility() classes. 

    if self.lh_type == 'MultiChannel':
      self.LOG_H.log('*', s_level, msg)
    else: ## SingleChannel
      self.LOG_H.log(s_level, msg)
 
  #-----------------------------------------------------------------------------
  def __log_to_logger(self, s_level, msg, d_extra=None):

    ## Log to the named Python logging.Logger. 
    LVL_int = getattr(logging, s_level.upper())

    if not LVL_int:
      msg = "(Invalid log-level: %s) - %s" % (s_level, msg)
      self.__log_to_so('ERROR', msg)

    self.LOG_H.log(LVL_int, msg, extra=d_extra)

  #-----------------------------------------------------------------------------
  def __log_from_queue(self, d_log):
    ##       
    ## Log messages put on the Queue to either STDOUT or one of the LogFacility() classes. 
    ##       
    
    ##print(">>>>>>>>>>>>>>QPRINT (%s): >> %s" % (self.lh_type, d_log))
    s_level = d_log['level']
    msg = d_log['msg']
    msg = "(mplq): %s" % (msg)
    if self.lh_type == 'STDOUT':
      self.__log_to_so(s_level, msg)
    else:
      self.__log_to_facility(s_level, msg)
  
##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":

  myname = 'StdApp_test'

  ## Test using a logging.Logger 

  ## Create session-id/logging hash
  session_id = utils.makeUniqHash(myname)

  min_level = "INFO"
  logfile_path = "%s.log" % (myname)
  
  #d_logger = {'name': myname } ## empty args (use defaults)
  #print("\n%s: Testing with default logging.Logger setup..." % (myname))

  d_logger = {'name': myname, 'min_level': min_level, 'logfile_path': logfile_path } ## custom level filepath
  print("\n%s: Testing with logging.Logger setup with logfile: %s..." % (myname, logfile_path))

  d_init_args = {'caller': myname, 'session_id': session_id, 'logger': d_logger}
  try:
    SA = StdApp(d_init_args)
  except Exception as e:
    errmsg = "%s: StdApp.init() failed with exception." % (myname)
    utils.stderr_notify(myname, errmsg,  {'exc':e, 'exit':1} )

  log_h = SA.getLogHandler()
  print("LOGGER: %s" % (log_h))

  ## Log to the logger object directly (this requires conversion of log-level to its integer equivlent)
  INFO_int = getattr(logging, 'INFO')
  log_h.log(INFO_int, "This is an INFO message using the log-handler object")

  ## Log to the logger object via the simpler StdApp method
  SA.log("WARNING", "This is a WARNING message using the StdApp.log() method")

  print("%s: DONE Testing\n\n" % (myname))
