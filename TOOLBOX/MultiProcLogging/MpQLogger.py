""" 

   File: MpQLogger.py 
   Class: MpQLogger.py 
   Author: Bill Fanselow
   Date: 11-10-2016

   Description:
     Python3 Class used to instantiate multiprocessing-queue logging objects. Such
     objects can then be passed to multiprocessing workers to provide a single,
     common file-logging facility for all the multiprocessing workers. 
        
   Usage: (see __main__ at bottom of page for details)
     1) Instantiate an MPQL object
     2) Spawn multiprocess workers, passing the MPQL object to each one.
     3) Each multiproc worker can log to shared logfile using syntax: mpql.log('<LEVEL>', <msg>)

   Background:
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
     processes. One method is to have all the processes log to a SocketHandler.  
     A simpler approach is to start up a multiprocessing Queue.  All sub-process 
     objects put() their log message onto this queue while a queue listener will 
     get() incoming messages off the queue write them to a single file using 
     Logger. Since all concurreny issues are handled by the Queue, there is no 
     danger of curruption. There are some gotchas associated with queue deadlocks
     which must be considered with this approach. I haven't considered all of 
     these scenarios yet.

"""

import multiprocessing
import traceback
import atexit 
import logging
import logging.handlers
import uuid
import time 
import sys 
import os 

DEFAULT_PATH  = './MPQL.log'
DEFAULT_LEVEL = logging.INFO
DEFAULT_LH_NAME = 'MPQL'

##--------------------------------------------------------------------------------
class MpQLogger(object):

  #----------------------------------------------------------
  ## init():
  def __init__(self, d_log_config, queue=None):

    ## class-name
    cname = self.__class__.__name__
    self.cname = cname 
    
    self.DEBUG = 1 

    print( "%s: Instantiating new..." % (cname))

    ## This is a multi-process safe method for debugging concurrency issues.
    ## Uncomment this for debugging
    ## multiprocessing.log_to_stderr(logging.DEBUG)

    if queue is None:
        queue = multiprocessing.Queue()   

    logger = self._init_logger(d_log_config)
    self.logger = logger  
    self.queue = queue 
    self.listener = None    ## set by qlistener_start()
    
    msg = "%s: Initialized MpQLogger..." % (cname)
    logger.debug(msg);

  #----------------------------------------------------------
  def __enter__(self):
    if self.DEBUG > 2:
      print("%s: __ENTER__" % (self.cname))
    return(self)

  #----------------------------------------------------------
  def __exit__(self, exc_type, exc_value, exc_traceback):
    if exc_value is None:
      msg = "%s: __EXIT__: Cleaning up on normal close with no exceptions" % (self.cname)
      self.logger.debug(msg)
    else:
      msg = "%s: __EXIT__: Cleaning up after exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.cname, exc_type,exc_value, exc_traceback)
      self.logger.error(msg)

    self.cleanup()

  #----------------------------------------------------------
  def _init_logger(self, d_log_config):

    hash = uuid.uuid4().hex
    extra = {'loghash': hash }

    log_level = DEFAULT_LEVEL
    log_filepath = DEFAULT_PATH
    log_handle_name =  DEFAULT_LH_NAME 
    log_type = 'overwrite'
    if  d_log_config:
      if 'log_level' in d_log_config:
        log_level = d_log_config['log_level']
      if 'log_filepath' in d_log_config:
        log_filepath = d_log_config['log_filepath']
      if 'lh_name' in d_log_config:
        log_handle_name = d_log_config['lh_name']
      if 'log_type' in d_log_config:
        log_type = d_log_config['log_type']
    
    logger = logging.getLogger(log_handle_name)
    logger.setLevel(log_level)

    if log_type == 'overwrite':
      lh = logging.FileHandler(log_filepath)
    elif log_type == 'rotate':
      lh = logging.handlers.RotatingFileHandler(log_filepath, maxBytes=300000, backupCount=5)
    elif log_type == 'hourlyrotate':
      lh = logging.handlers.TimedRotatingFileHandler(log_filepath, when="h", backupCount=60)
    elif log_type == 'dailyrotate':
      lh = logging.handlers.TimedRotatingFileHandler(log_filepath, when="d", backupCount=60)

    formatter = logging.Formatter('%(asctime)-15s  %(loghash)s %(levelname)-7s >>  %(message)s')
    lh.setFormatter(formatter)

    logger.addHandler(lh)
    logger = logging.LoggerAdapter(logger, extra)
    
    self.loghash = hash 
    self.log_filepath = log_filepath 
    self.log_handle_name = log_handle_name 

    return( logger )

  #----------------------------------------------------------
  def log(self, level, message):
    queue = self.queue
    d_record = {"level": level, "msg": message}
    queue.put(d_record)

  #----------------------------------------------------------
  def _log_record(self, d_record):
    ## Log to the named Python logging.Logger.

    logger = self.logger 
    msg = d_record['msg']

    s_level = d_record.get('level', 'DEBUG')

    int_level = getattr(logging, s_level.upper())
    if int_level:
      logger.log(int_level, msg)

    else:
      logger.log('ERROR', "(Invalid log-level: %s) - %s" % (s_level, msg))

  #----------------------------------------------------------
  def _listener(self):
    
    tag = self.cname + '._listener' 

    queue = self.queue
    logger = self.logger 
    msg_count = 0

    ## Read from the queue
    while True:
      try:
        d_record = queue.get()
        msg_count += 1
        if (d_record is None):
          logger.info("%s: qListener got termination message" % (tag))
          break

        self._log_record(d_record)
      except (KeyboardInterrupt, SystemExit) as e:
        logger.error("%s: qListener ABORTING on interrupt: %s" % (tag, e))
        break
      except EOFError as e:
        logger.error("%s: qListener ABORTING on error: %s" % (tag, e))
        break
      except:
        traceback.print_exc(file=sys.stderr)

    logger.info("%s: qListener stopped. Messages processed: %d" % (tag, msg_count))

  #----------------------------------------------------------
  def cleanup(self):
    
    tag = self.cname + '.cleanup' 

    ##print >> sys.stderr, "%s: Cleaning up" % (tag)
    self.listener.terminate

    return( 1 )

  #----------------------------------------------------------
  def check_listener(self, d_args=None):
    logger = self.logger 
    status = 0 
    q_listener = self.listener 
    if q_listener.is_alive(): 
      status = 1

    return( status )

  #----------------------------------------------------------
  def qlistener_start(self, d_args=None):

    tag = self.cname + '.qlistener_start' 

    logger = self.logger 
    queue = self.queue
    pid = None
    q_listener = multiprocessing.Process(target=self._listener, name="q_listener", args=())
    q_listener.daemon = True
    try:
      q_listener.start()
      pid = q_listener.pid
    except Exception as e:
      print >> sys.stderr, "%s: ERROR Failed to Start listener process: %s" % (tag, e)
      sys.exit(2)

    logger.info("%s: qListener started" % (tag))
    atexit.register(self.cleanup)

    self.listener = q_listener 

    return( pid )

  #----------------------------------------------------------
  def qlistener_stop(self, delay=None):
    
    tag = self.cname + '.qlistener_stop' 

    logger = self.logger 
    q_listener = self.listener 

    logger.info("%s: Request received to stop qListener" % (tag))
    if q_listener.is_alive(): 
      logger.info("%s: Stopping qListener" % (tag))
      if delay:
        time.sleep(delay)
      q_listener.terminate

    ecode = q_listener.exitcode
    logger.info("%s: qListener stopped with exitcode=%s" % (tag, ecode))

    return( ecode )

  #----------------------------------------------------------
  def getQListener(self):
    return(self.listener)   

  #----------------------------------------------------------
  def getLogHandler(self):
    return(self.logger)   
  
  #----------------------------------------------------------
  def getLogFilePath(self):
    return(self.log_filepath)   

  #----------------------------------------------------------
  def getLogHash(self):
    return(self.loghash)
  
  #----------------------------------------------------------
  def getLogHandlerName(self):
    return(self.log_handle_name)

##----------------------------------------------------------------------------------------
## CLASS TEST
##----------------------------------------------------------------------------------------
if __name__ == "__main__":

  myname = 'MpQLogger_test'

  ## Logging configurations (pass to MpQLogger class init)
  MIN_LOG_LEVEL = "DEBUG"  ## min-log-level for Logger (will be converted to INT)
  LOGFILE_PATH = "./%s.log" % (myname)

  ##========================
  def worker1(mpql):
    proc_name = multiprocessing.current_process().name
    pid = os.getpid()
    msg_count = 0
    print( "%s pid=[%s]: Starting..." % (proc_name, pid) )
    limit = 40
    sleep_time = 1.2
    ## Write to the queue
    for i in range(0, limit):
      msg = "[%s] %s %s" % (pid, proc_name, i)
      if i % 5 == 0:
        mpql.log('DEBUG', msg)
        print("  %s: Still working..." % (proc_name) )
      else:
        mpql.log('INFO', msg)
      msg_count += 1
      time.sleep(sleep_time)
    print( "%s: Finished. Messages sent: %d" % (proc_name, msg_count) )

  ##========================
  def worker2(mpql):
    proc_name = multiprocessing.current_process().name
    pid = os.getpid()
    msg_count = 0
    print( "%s pid=[%s]: Starting..." % (proc_name, pid) )
    limit = 90
    sleep_time = 0.7
    ## Write to the queue
    for i in range(0, limit):
      msg = "[%s] %s %s" % (pid, proc_name, i)
      if i % 7 == 0:
        print("  %s: Still working..." % (proc_name) )
        mpql.log('WARNING', msg)
      else:
        mpql.log('INFO', msg)
      msg_count += 1
      time.sleep(sleep_time)
    print( "%s: Finished. Messages sent: %d" % (proc_name, msg_count) )


  pid = os.getpid()
  print( "%s: Starting pid=[%s]" % (myname, pid) )
  print( "%s: Logging to file: [%s]" % (myname, LOGFILE_PATH) )

  ## instantiate MpQLogger()
  INT_LOG_LEVEL = getattr(logging, MIN_LOG_LEVEL)
  d_log_config = { "log_filepath": LOGFILE_PATH, "log_level": INT_LOG_LEVEL, "type": "dailyrotate" }
  try:
    mpql = MpQLogger( d_log_config )
  except Exception as e:
    print( "%s: ERROR - MpQLogger.init() failed with exception: %s" % (myname, e) )
    raise

  with mpql:
    pid = mpql.qlistener_start() ## start the listener

    logger = mpql.getLogHandler()
    logger.debug("%s: Starting workers with main pid=%s" %(myname,pid))

    ## start workers
    w1 = multiprocessing.Process(target=worker1, name="worker-1", args=(mpql,))
    w2 = multiprocessing.Process(target=worker2, name="worker-2", args=(mpql,))
    w1.start()
    w2.start()
    atexit.register(w1.terminate)
    atexit.register(w2.terminate)

    w1.join()
    w2.join()

    ecode = mpql.qlistener_stop() ## stop the listener

    logger.debug("%s: FINISHED with main" %(myname))
    print( "%s: Finished with script\n" % (myname) )

  sys.exit(0)
