"""

  Class: ErrorHandler()
  Subclass of parent-class: StdApp() 
  
  A Python3 Error-handling Class
  Instantiate an ErrorHandler object which can be used to simplify
  the handling of the multiple tasks you typically group and execute
  upon failures (such as email-alerts, lockfiles, etc.).

  The following 3 objects can be passed to init(). Otherwise DEFAULTS are used:

   1) log_h for logging:
      a) Default LogFacility: log_h = 'STDOUT' 
      b) LogFacility handler instance which exposes the log(<level>, <msg>) method
         Currently supported LogFacility classes:
          * LogFacility_file()   => log to file
          * LogFacility_db()     => log to database
          * LogFacility_api()    => log to api
          * LogFacility_stdout() => log to stdout/stderr
          * LogFacility_multiChannel() => log to multiple of the above

   2) lock_h = LockfileHandler() for lock-file management
      a) lock_h = 'DEFAULT' (create a default lockfile instance inside this class)
      b) lock_h = o_LockfileHandler() (previously instantiated lockfile object)
      Default: 'DEFAULT'

   3) email_h = Emailer() for handling email notifications 
      a) email_h = 'DEFAULT' (create a default email-handler instance inside this class)
      b) email_h = o_Emailer() (previously instantiated Emailer object)
      Default: 'DEFAULT'
 
  Current error types and associated behavior:
   1) self.warning(<msg>)
      * send email alert to specified users or default "admin" list
   2) self.critical(<msg>)
      * send email alert to specified users or default "admin" list
   3) self.fatal(<msg>)
      * send email alert to specified users or default "admin" list
      * create a LOCKFILE 

  USAGE: see TEST __main__ at bottom of page

"""

import os
import sys

## custom libs
import utils 
from CustomExceptions import ReqArgError, InitError, InvalidLogHandle, InvalidLockfileState
from LockfileHandler import LockfileHandler 
from Emailer import Emailer 
from StdApp import StdApp 

##-----------------------------------------------------------------------------
##
## Defaults
##

DEBUG = 3

## Default recipient list for fatal-error emails
DEFAULT_APP_ADMINS = ["william.fanselow@level3.com"]

##-----------------------------------------------------------------------------
class ErrorHandler(StdApp):

  def __init__(self, caller, d_init_args):

    try:
      StdApp.__init__(self, d_init_args) ## sets up logging
    except Exception as e:
      raise
 
    self.cname = self.__class__.__name__
    self.caller = caller

    self.LOCK_H = None
    self.EMAIL_H = None

    self.DEBUG = DEBUG
    if 'debug' in d_init_args:
      self.DEBUG = d_init_args['debug']

    if 'session_id' in d_init_args:
      self.session_id = d_init_args['session_id']
    else:
      raise InitError("%s: Missing required init arg: [session_id]" % (self.cname))

    ##################################################
    ## LOCKFILE RESOURCE
    ##
    if 'lock_h' in d_init_args:
      lock_h = d_init_args['lock_h']
    else:
      lock_h = 'DEFAULT'

    if str(lock_h) == 'DEFAULT':
      try:
        lock_h = self.__createDefaultLockHandler()
      except InvalidLockfileState:
        errmsg = "%s: INVALID LOCK STATE" % (self.cname)
        utils.stderr_notify(self.cname, errmsg, {'exc':e, 'exit':2})
      except Exception as e:
        raise
    else:
      if not isinstance(lock_h, LockfileHandler):
        raise InitError("%s: Invalid required init() arg: [lock_h] (%s)" % (self.cname, type(lock_h)))
      
    self.LOCK_H = lock_h

    ##################################################
    ## EMAIL RESOURCE
    ##
    if 'email_h' in d_init_args:
      email_h = d_init_args['email_h']
    else:
      email_h = 'DEFAULT'

    if str(email_h) == 'DEFAULT':
      try:
        email_h = self.__createDefaultEmailer()
      except Exception as e:
        raise
    else:
      if not isinstance(email_h, Emailer):
        raise InitError("%s: Invalid required init() arg: [email_h] (%s)" % (self.cname, type(email_h)))

    self.EMAIL_H = email_h

    ##################################################
    msg = "%s: init(): Initialization complete" % (self.cname)
    if self.DEBUG > 2:
      self.log("DEBUG", msg)

  ##-----------------------------------------------------------------------------
  ## internal creation of default LockfileHandler() 
  def __createDefaultLockHandler(self):
    
    self.log('INFO', "%s: Creating DEFAULT lockfile-handler" % (self.cname))

    ## build lock-handler (passing log_h) and check for lockfile
    d_lock_args = { 'log_h': self.LOG_H, 'session_id': self.session_id }
    try:
      lock_h = LockfileHandler(self.caller, d_lock_args)
      lock_filepath = lock_h.getPath()
      self.log('INFO', "%s: DEFAULT LOCKFILE PATH: %s" % (self.cname, lock_filepath))
    except Exception as e:
      errmsg = "%s: LockfileHandler().init() failed with exception" % (self.cname)
      self.log('ERROR', errmsg)
      utils.stderr_notify(self.cname, errmsg, {'exc':e, 'exit':2})
  
    contents = lock_h.check()
    if contents != '':
      errmsg = "%s: Lockfile already exists: [%s]" % (self.cname, contents)
      utils.stderr_notify(self.cname, errmsg)
      self.log('ERROR', errmsg)
      raise RuntimeError(errmsg)

    return( lock_h )

  ##-----------------------------------------------------------------------------
  ## internal creation of default Emailer() 
  def __createDefaultEmailer(self):
    self.log('INFO', "%s: Creating DEFAULT email-handler" % (self.cname))
    d_email_args = {'session_id': self.session_id }
    try:
      email_h = Emailer(d_email_args)
    except Exception as e:
      errmsg = "%s: Emailer().init() failed with exception" % (self.cname)
      utils.stderr_notify(self.cname, errmsg, {'exc':e, 'exit':2})
      self.log('ERROR', errmsg)

    return( email_h )

  ##-----------------------------------------------------------------------------
  def warning(self, msg):
    ##
    ## WARNING: logging only 
    ##

    tag = self.cname + '.' + self.caller
    self.log("WARNING","%s: %s" % (tag, msg))
  
  ##-----------------------------------------------------------------------------
  def critical(self, msg, d_email_args=None):
    ##
    ## CRITICAL-ERROR: logging and email-message 
    ##
    tag = self.cname + '.' + self.caller

    ## LOGGING
    self.log("ERROR","%s: %s" % (tag, msg))

    ## EMAIL 
    with self.EMAIL_H as eh:
      l_recipients = DEFAULT_APP_ADMINS
      subject = "CRITICAL-ERROR from %s" % (tag) 
      body = msg 
      if d_email_args:
        if 'subject' in d_email_args:
          subject = d_email_args['subject'] 
        if 'recipients' in d_email_args:
          l_recipients = d_email_args['recipients'] 
        if 'body' in d_email_args:
          body = body + "\n\n" + d_email_args['body'] 
 
      body = body + "\n\nDO NOT REPLY" 
      try:
        eh.send({'subject':subject, 'body':body, 'recipients': l_recipients })
      except Exception as e:
        utils.stderr_notify(self.cname, "Emailer().send() failed with exception", {'exc':e})
        raise

  
  ##-----------------------------------------------------------------------------
  def fatal(self, msg, d_email_args=None):
    ## 
    ## FATAL-ERROR: logging, email-message and lockfile
    ## 
    tag = self.cname + '.' + self.caller 
    
    ## LOGGING
    self.log("CRITICAL","%s: %s" % (tag, msg))

    ## LOCKFILE
    self.LOCK_H.create(msg, tag)

    ## EMAIL 
    with self.EMAIL_H as eh:
      l_recipients = DEFAULT_APP_ADMINS
      subject = "FATAL-ERROR from %s" % (tag) 
      body = msg 
      if d_email_args:
        if 'subject' in d_email_args:
          subject = d_email_args['subject'] 
        if 'recipients' in d_email_args:
          l_recipients = d_email_args['recipients'] 
        if 'body' in d_email_args:
          body = body + "\n\n" + d_email_args['body'] 
 
      body = body + "\n\nDO NOT REPLY" 
      try:
        eh.send({'subject':subject, 'body':body, 'recipients': l_recipients })
      except Exception as e:
        utils.stderr_notify(self.cname, "Emailer().send() failed with exception", {'exc':e})
        raise
  
##-----------------------------------------------------------------------------
## TEST
if __name__ == '__main__':

  import sys
  import utils
  
  sys.path.append('./config')
  import DATABASE as config_db
  
  from LogFacility_file import LogFacility_file
  from LogFacility_multiChannel import LogFacility_multiChannel
 
  myname = 'errorhandler_test'
  d_email_args = {'recipients': ["william.fanselow@level3.com"] }

  session_id = utils.makeUniqHash(myname)
  log_filepath = "./%s.log" % (myname)

###################################
## Using LogFacility_file 
#
#  d_log_args = {'log_filepath': logpath, 'min_log_level': 'DEBUG', 'caller': myname}
#  try:
#    log_h = LogFacility_file(d_log_args)
#  except Exception as e:
#    utils.stderr_notify(myname, "LogFacility_file().init() failed with exception", {'exc':e, 'exit':2})
###################################

###################################
## Using multiChannel file and db loggers

  log_storage_id = "workflow_applog"
  ## Configure file and database logging facilities for LogFacility_multiChannel()
  d_log_config = {
      "File": {"file_path":  log_filepath, "min_log_level": 'INFO', 'session_id': session_id, 'caller': myname},
      "Db":   {"storage_id": log_storage_id, "config_module": config_db, "min_log_level": 'DEBUG', 'session_id': session_id, 'caller': myname}
  }
  try:
    log_h = LogFacility_multiChannel(d_log_config)
  except Exception as e:
    utils.stderr_notify(myname, "LogFacility_multiChannel().init() failed with exception", {'exc':e, 'exit':2})
###################################

  ## create error handler under log_h context-manager
  with log_h:

    log_h.log("*", "INFO", "%s: TESTING LogFacility..." % (myname))

    d_err_args = {'log_h': log_h, 'email_h':'DEFAULT', 'lock_h':'DEFAULT', 'session_id': session_id}

    try:
      print( "%s: Creating ErrorHandler() with DEFAULT emailer and filelocking" % (myname))
      err_h = ErrorHandler(myname, d_err_args)
    ##  print( "%s: Creating ErrorHandler() with DEFAULT logger, emailer and filelocking" % (myname))
    ##  err_h = ErrorHandler(myname, {})
    except Exception as e:
      utils.stderr_notify(myname, "ErrorHandler().init() failed with exception", {'exc':e, 'exit':2})
    
    try:
      err_h.warning("This is a WARNING")
    except Exception as e:
      utils.stderr_notify(myname, "ErrorHandler().warning() failed with exception", {'exc':e})
      raise

    try:
      err_h.critical("Found a serious error", d_email_args)
    except Exception as e:
      utils.stderr_notify(myname, "ErrorHandler().critical() failed with exception", {'exc':e})
      raise
    try:
      err_h.fatal("Hit a FATAL error", d_email_args)
    except Exception as e:
      utils.stderr_notify(myname, "ErrorHandler().fatal() failed with exception", {'exc':e})
      raise

  sys.exit(0)
