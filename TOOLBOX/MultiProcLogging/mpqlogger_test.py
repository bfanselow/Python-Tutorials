#!/usr/bin/env python3

"""

 mpqlogger_test.py
 fanselow.william
 6-30-2017

 This script tests MpQLogger.py class which allows multiple processes to write
 to to a single log-file.

 See MpQLogger.py for importance of mp-queue logging!!

"""

import os
import multiprocessing
import time
import sys
import atexit 
import logging 
from MpQLogger import MpQLogger

myname = 'mpqlogger_test.py'

DEBUG = 2

## Logging configurations (pass to MpQLogger class init)
MIN_LOG_LEVEL = 'DEBUG'  ## min-log-level for Logger (will be converted to int) 
LOGFILE_PATH = "./%s.log" % (myname)

#----------------------------------------------------------

def worker1(mpql):
    proc_name = multiprocessing.current_process().name
    pid = os.getpid()
    msg_count = 0
    print( "%s pid=[%s]: Starting..." % (proc_name, pid) )
    limit = 40
    slp = 1.2 
    ## Write to the queue
    for i in range(0, limit):
      msg = "[%s] %s %s" % (pid, proc_name, i)
      if i % 5 == 0:
        mpql.log('DEBUG', msg) 
      else:
        mpql.log('INFO', msg) 
      msg_count += 1 
      time.sleep(slp)
    print( "%s: Finished. Messages sent: %d" % (proc_name, msg_count) )

def worker2(mpql):
    proc_name = multiprocessing.current_process().name
    pid = os.getpid()
    msg_count = 0
    print( "%s pid=[%s]: Starting..." % (proc_name, pid) )
    limit = 90 
    slp = 0.7
    ## Write to the queue
    for i in range(0, limit):
      msg = "[%s] %s %s" % (pid, proc_name, i)
      if i % 7 == 0:
        mpql.log('WARNING', msg) 
      else:
        mpql.log('INFO', msg) 
      msg_count += 1 
      time.sleep(slp)
    print( "%s: Finished. Messages sent: %d" % (proc_name, msg_count) )

#----------------------------------------------------------

if __name__=='__main__':
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
