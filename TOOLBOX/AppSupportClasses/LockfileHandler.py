"""

  Class: LockfileHandler()
  Subclass of parent-class: StdApp()

  A Python3 application "lock" handler class

  Instantiate a Lockfile-handler object.  This is useful for ensuring
  that a resource is locked or indicating a previous fatal error that
  should prevent future executions of the same process. 

  A LogFacility handler instance which exposes the log(<level>, <msg>) method can be 
  passed to init().  Otherwise default "logging" (print to STDOUT) is used.
  Currently supported LogFacility classes:
    * LogFacility_file()   => log to file
    * LogFacility_db()     => log to database
    * LogFacility_api()    => log to api
    * LogFacility_stdout() => log to stdout/stderr
    * LogFacility_multiChannel() => log to multiple of the above

  USAGE: see TEST __main__ at bottom of file

"""

import os
import sys
import time
import datetime
import getpass

## custom libs
import utils
from CustomExceptions import ReqArgError, InitError, InvalidLockfileState
from StdApp import StdApp 

##-----------------------------------------------------------------------------
##
## Defaults
##

DEBUG = 2

## !!!!!!
## NOTICE: Default lockfile path: Set by init() using "caller" variable
## self.lock_filepath = "./%s.LOCK" % (self.caller) 
## !!!!!!

##-----------------------------------------------------------------------------
class LockfileHandler(StdApp):

  ## init() ##
  def __init__(self, caller, d_init_args):

    try:
      StdApp.__init__(self, d_init_args) ## sets up logging
    except Exception as e:
      raise
   
    ## class-name 
    cname = self.__class__.__name__
    self.cname = cname
    self.caller = caller
    
    self.user = getpass.getuser() 

    self.session = None 
    if 'session_id' in d_init_args:
      self.session_id = d_init_args['session_id']
    else:
      raise InitError("%s: Missing required init arg: [session_id]" % (self.cname))

    self.DEBUG = DEBUG
    if 'debug' in d_init_args:
      self.DEBUG = d_init_args['debug']

    if 'lock_filepath' in d_init_args:
      self.lock_filepath = d_init_args['lock_filepath']
    else:
      self.lock_filepath = "./%s.LOCK" % (self.caller) 

    ##################################################
    msg = "%s: init(): Initialization complete" % (self.cname)
    if self.DEBUG > 2:
      self.log("DEBUG", msg)

  #----------------------------------------------------------------------------- 
  ## Get the full path of the lockfile
  def getPath(self):
    return(self.lock_filepath)
 
  #----------------------------------------------------------------------------- 
  ## Check for lockfile. Return contents if found, empty string if not
  def check(self):
    
    contents = ''
    self.log("DEBUG", "%s: Checking for lockfile: [%s]" % (self.cname, self.lock_filepath))

    if os.path.isfile(self.lock_filepath):
      self.log("DEBUG", "%s: Found existing LOCKFILE: %s" % (self.cname,self.lock_filepath) )

      fh = open(self.lock_filepath, 'r') 
      contents = fh.read()
      fh.close() 

      if contents == '': 
        raise InvalidLockfileState("%s: Empty lockfile contents [%s]" % (self.cname, self.lock_filepath))

    return( contents )
 
  #----------------------------------------------------------------------------- 
  ## Create a new lockfile
  def create(self, msg, caller=None):
 
    self.log("DEBUG", "%s: Preparing to make new lockfile: [%s]" % (self.cname, self.lock_filepath) )
    lf_contents = self.check()
    if lf_contents != '':
      raise InvalidLockfileState("%s: Lockfile already exists: [%s]" % (self.cname, self.lock_filepath))

    else:
      if caller is None:
        caller = self.caller
      else:
        caller = self.cname + '.' + self.caller

      self.log("INFO", "%s: Making new lockfile for [%s]: [%s]" % (self.cname, caller, self.lock_filepath) )

      ts = time.time()
      timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

      with open(self.lock_filepath, 'w') as fh:
        fh.write("TS: %s\n" % (timestamp)) 
        fh.write("USER: %s\n" % (self.user)) 
        fh.write("CREATOR: %s\n" % (caller)) 
        fh.write("SESSIONID: %s\n\n" % (self.session_id)) 
        fh.write("%s\n" % msg) 

    return( 1 )
  #----------------------------------------------------------------------------- 
  ## Remove lockfile
  def remove(self):
      
    lf_contents = self.check()
    if lf_contents == '':
      self.log("INFO", "%s: No lockfile to remove: [%s]" % (self.cname, self.lock_filepath) )

    else:
      self.log("INFO", "%s: Removing lockfile: [%s]" % (self.cname, self.lock_filepath) )
      os.remove(self.lock_filepath)
 
##------------------------------------------------------------------------------
##------------------------------------------------------------------------------
## TEST
if __name__ == '__main__':
  from LogFacility_file import LogFacility_file

  myname = 'lockfile_test'
  lockpath = "./%s.LOCK" % (myname)
  logpath = "./%s.log" % (myname)

  session_id = utils.makeUniqHash(myname)

  ## build log-handle
  d_log_args = {'log_filepath': logpath, 'caller': myname, 'session_id': session_id}
  try:
    LF = LogFacility_file(d_log_args)
  except Exception as e:
    utils.stderr_notify(self.cname, "LogFacility_file().init() failed with exception", {'exc':e, 'exit':2})

  with LF as log_h:
    ## build lock-handler, passing established log_h object 
    d_lock_args = { 'lock_filepath': lockpath, 'log_h': log_h, 'session_id': session_id }
    try:
      lock_h = LockfileHandler(myname, d_lock_args)
    except Exception as e:
      utils.stderr_notify(myname, "LockfileHandler().init() failed with exception", {'exc':e, 'exit':2})

    print("%s: Checking for existing lockfile" % (myname))
    contents = lock_h.check() 
    if contents != '':
      utils.stderr_notify(myname, "WARNING: Lockfile already exists: [%s]" % (contents))
    else:
      print("%s: Creating new lockfile" % (myname))
      lock_h.create("Something bad happened", "lockfile_test.create") 

################################################
#  ## OR build lock-handler (no log_h)
#  d_lock_args = { 'lock_filepath': lockpath, 'session_id': session_id }
#  try:
#    lock_h = LockfileHandler(myname, d_lock_args)
#  except Exception as e:
#    utils.stderr_notify(myname, "LockfileHandler().init() failed with exception",  {'exc':e, 'exit':2})
#
#  print("%s: Checking for existing lockfile" % (myname))
#  contents = lock_h.check() 
#  if contents != '':
#    utils.stderr_notify(myname, "WARNING: Lockfile already exists: [%s]" % (contents))
#  else:
#    print("%s: Creating new lockfile" % (myname))
#    lock_h.create("Something bad happened", "lockfile_test.create") 
################################################
