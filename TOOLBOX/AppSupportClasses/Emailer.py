"""

   Class: Emailer()
   Subclass of parent-class: StdApp()

   A Python3 Class for simplifying sending of emails.

   Since we are working with sendmail connections, we use 
   a context-manager so that all resources are properly released.
   The __enter__() method returns the Class instance, so no "as"
   target is specified in the "with" statement.

  USAGE: see TEST __main__ at bottom of file

"""

##------------------------------------------------------------------------------

import sys
import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText

## custom libs
import utils
from CustomExceptions import ReqArgError, InitError
from StdApp import StdApp 

##------------------------------------------------------------------------------

DEBUG = 1 
DEFAULT_MAIL_SERVER = 'scanmail.level3.com'
DEFAULT_FROM_ADDR = 'root@localhost'

##------------------------------------------------------------------------------
class Emailer(StdApp):

  def __init__(self, d_init_args):

    try:
      StdApp.__init__(self, d_init_args) ## sets up logging
    except Exception as e:
      raise

    self.cname = self.__class__.__name__

    self.mail_server = DEFAULT_MAIL_SERVER 
    self.sm_conn = None  ## sendmail server connection 
    self.DEBUG = DEBUG 
    self.session_id = None 

    if not d_init_args:
      raise InitError("%s: Missing required init args" % (self.cname)) 

    if 'session_id' in d_init_args:
      self.session_id = d_init_args['session_id'] 
    else:
      raise InitError("%s: Missing required init arg: [session_id]" % (self.cname)) 

    if 'debug' in d_init_args:
      self.DEBUG = d_init_args['debug'] 

    if 'mail_server' in d_init_args:
      self.mail_server = d_init_args['mail_server'] 
    
    msg = "%s: init(): Initialization complete. Sendmail-server=[%s]" % (self.cname, self.mail_server)
    if self.DEBUG:
      self.log("DEBUG", msg)

  ##------------------------------------------------------------------------------
  def __enter__(self):
    msg = "%s: __ENTER__: Returning Context-Manager type=SELF..." %  (self.cname)
    if self.DEBUG > 2:
      self.log("DEBUG", msg)
    return( self )

  ##------------------------------------------------------------------------------
  def __exit__(self, exc_type, exc_value, exc_traceback):
    if exc_value is None:
      msg = "%s: __EXIT__: Cleaning up on normal close with no exceptions" % (self.cname)
    else:
      msg = "%s: __EXIT__: Cleaning up on exception: EXC=[%s] EXCVAL=[%s] TRACE=[%s]" % (self.cname, exc_type, exc_value, exc_traceback)
    self.log("DEBUG", msg)
    self.resourceCleanup() 

  ##------------------------------------------------------------------------------
  def __is_sm_connected(self):
  ## check sendmail server connection
    try:
      status = self.sm_conn.noop()[0]
    except:
      status = -1

    if status == 250:
      return True 
    else:
      return False 
  
  ##------------------------------------------------------------------------------
  def resourceCleanup(self): 
    ##
    ## Clean up all resources
    ##
    tag = "%s.resourceCleanup" % (self.cname)
    self.log("DEBUG", "%s Cleaning up all class resources..." % (tag))
    if self.__is_sm_connected():
      self.sm_conn.quit()

  ##------------------------------------------------------------------------------
  def send(self, d_args):
    ##
    ## Send a message
    ##
    tag = "%s.send" % (self.cname)
    
    if 'subject' in d_args: 
      subject = d_args['subject']
    else:
      raise ReqArgError("%s: Missing required arg: [subject]" % (self.cname)) 

    if 'recipients' in d_args: 
      l_recipients = d_args['recipients']
      type = utils.getDataType(l_recipients)
      if type != 'list':
        raise ReqArgError("%s: Invalid data type for arg: [recipients]" % (self.cname)) 
    else:
      raise ReqArgError("%s: Missing required arg: [recipients]" % (self.cname)) 

    if 'body' in d_args: 
      body = d_args['body'] 
    else:
      raise ReqArgError("%s: Missing required arg: [body]" % (self.cname)) 

    from_addr = DEFAULT_FROM_ADDR   
    if 'from_addr' in d_args: 
      from_addr = d_args['from_addr']

    if not self.__is_sm_connected():
      self.sm_conn = smtplib.SMTP(self.mail_server) 
      self.sm_conn.starttls()

    ## For debugging
    #self.sm_conn.set_debuglevel(True) ## show communication with the server
 
    for to_addr in l_recipients:
      msg = MIMEMultipart() 
      msg['Subject'] = subject 
      msg['To'] = to_addr 
      msg['From'] = from_addr 

      msg.attach(MIMEText(body, 'plain'))
      text = msg.as_string()

      self.log("DEBUG", "%s Sending email to [%s]" % (tag, to_addr))

      self.sm_conn.sendmail(from_addr, to_addr, text)
      self.sm_conn.quit()

##------------------------------------------------------------------------------
##------------------------------------------------------------------------------
## TEST
if __name__ == '__main__':

  from LogFacility_file import LogFacility_file 
  myname = 'email_test'
 
  session_id = utils.makeUniqHash(myname)
 
  log_filepath = "%s.log" % (myname) 
  d_log_args = {'log_filepath': log_filepath, 'session_id': session_id, 'caller':myname}
  try:
    print("%s: Setting up logging to file: [%s]" % (myname, log_filepath))
    log_h = LogFacility_file(d_log_args)
  except Exception as e:
    utils.stderr_notify(myname, "LogFacility_file().init() failed with exception", {'exc':e, 'exit':2})
 
  print("%s: Initializing Emailer()" % (myname))
  d_init_args = {'mail_server':'scanmail.level3.com', 'log_h': log_h, 'session_id':session_id} 
  try:
    email_h = Emailer(d_init_args)
  except Exception as e:
    utils.stderr_notify(myname, "Emailer().init() failed with exception", {'exc':e, 'exit':2})

  with email_h:
    body = "This is a whole chunck\nofBODY text!\n\n DOT NOT REPY"
    subject = "Test of %s" % (myname) 
    try: 
      email_h.send({'subject':subject, 'body':body, 'recipients': ['william.fanselow@level3.com'] }) 
    except Exception as e:
      utils.stderr_notify(myname, "Emailer().send() failed with exception", {'exc':e, 'exit':2})
      
  sys.exit(0)
