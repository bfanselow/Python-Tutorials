

"""

 File: utils.py
 Author: Bill Fanselow
 
 Description:
 Generic utility functions
 
 Requires: 
   pip install jmespath

"""

##----------------------------------------------------------
## Python2 compatiblity
from __future__ import (division, print_function)
##----------------------------------------------------------

import sys
import hashlib
import datetime
import jmespath
import random
import getpass
import logging
import traceback
import shutil
import re 
from getpass import getuser 

myname = 'utils.py'

DEBUG = 2 

#------------------------------------------------------------------------
def stderr_notify(caller, msg, d_args=None):

  ## Simple exception handler for printing exception info to STDERR. 
  ## d_args is optional and can have any of the following:
  ##   1) 'exc': <excObject> 
  ##      If this is present the exception info will be printed to STDERR. 
  ##      Otherwise only <msg> is printed to STDERR
  ##            
  ##   2) 'exit': <exit_code> 
  ##      If this is present the method will call sys.exit(<ecode>).
  ##      Otherwise STDERR is printed but no exiting. 
  ##
  ## Example usage (typically after ... except Exception as e: )
  ## 1) Notice with exception-info AND exit:    exc_stderr(myname, "<error-msg>", {'exc': <excObj>, 'exit':2}) 
  ## 2) Notice with NO exception-info AND exit: exc_stderr(myname, "<error-msg>", {'exit':2})          
  ## 3) Notice with Exception-info and NO exit: exc_stderr(myname, "<error-msg>", {'exc': <excObj>} )         
  ## 4) Notice ONLY: exc_stderr(myname, "<error-msg>" )         

  exc = None
  exit = None

  if d_args:
    if 'exc' in d_args:
      exc = d_args['exc']
    if 'exit' in d_args:
      exit = str(d_args['exit'])

  ## print to STDERR
  if exc:
    sys.stderr.write("%s: Exception-Caught: %s: %s\n" % (caller, msg, str(exc))) 
    ## more with traceback
    tb = exc.__traceback__
    traceback.print_tb( tb ) ## also goes to stderr
  else:
    sys.stderr.write("%s: %s\n" % (caller, msg)) 
    
  ## exit? 
  if exit:
    try:
      exit = int(exit)
    except:
      sys.stderr.write("%s: ERROR - Invalid exit code: %s:\n" % (myname, str(exit))) 
    finally:
      sys.stderr.write("%s: Exiting with code=%s\n" % (myname, str(exit))) 
      sys.exit(exit)

#------------------------------------------------------------------------
def makeUniqHash(input_text=None):

  username = get_user_name() 
  ##timestamp = unicode(datetime.datetime.now()) ## python2
  timestamp = str(datetime.datetime.now())
  randint = int(random.random() * sys.maxsize)
    
  hash_data = "%s:%s:%d:%s" % (username, timestamp, randint, input_text)
  hash_text = hash_data.encode('utf-8')

  m = hashlib.md5(hash_text)
  hash = m.hexdigest()

  return(hash)

#------------------------------------------------------------------------
def isExecutable(path):
  ##
  ## Check if <path> is on system and executable by caller
  ## 

  status = shutil.which(path)

  return(status)

#------------------------------------------------------------------------
def getDataType(obj, mode="specific"):
  ##
  ## Simplify the tedious process of determining data-type. If default mode
  ## (mode="specific") is overridden with mode="generic" several data-types
  ## (str,int,float,bool) are combined into a single new type called "scaler".
  ## Return: data-type
  ##
  type = None
    
  l_scalar_types = ['str', 'int', 'float', 'bool' ]

  if isinstance( obj, dict ):
    type = 'dict'
  elif isinstance( obj, list ):
    type = 'list'
  elif isinstance( obj, str ):
    type = 'str'
  elif isinstance( obj, tuple ):
    type = 'tuple'
  elif isinstance( obj, int ):
    type = 'int'
  elif isinstance( obj, float ):
    type = 'float'
  elif isinstance( obj, bool ):
    type = 'bool'

  if mode == 'generic':
    if type in l_scalar_types:
      type = 'scalar'

  return(type) 

#------------------------------------------------------------------------
def getStrNumericType(str):
  ##
  ## Identify the numeric type of a number which has been cast in string from. 
  ## Example: Suppose we have the string "3.03". We don't want to know the
  ##          obvious - that it is actually type=string, we want to know what
  ##          numeric type (INT or FLOAT) is contained in this string.
  ##           
  ## Return: Numeric data-type. Returns None if string is not a number (ether INT or FLOAT)
  ##
  numeric_type = None

  m = re.match("^(\d+)$", str)
  if m:
    numeric_type = 'int'
  else:
    m = re.match("^(\d+\.\d+)$", str)
    if m:
      numeric_type = 'float'

  return(numeric_type) 

#------------------------------------------------------------------------
def castStrNumericType(str):
  ##
  ## Identify the numeric type of a number which has been cast in string from
  ## and cast it to the appropriate numeric type.
  ## Example: Suppose we have the string "3.03". We need to identify that the
  ##          numeric-type is a float and cast it as a float. Same logic for int. 
  ##           
  ## Return: Number appropriately casted to its type. Returns None if string is not a number (ether INT or FLOAT)
  ##
  casted_number = None

  m = re.match("^(\d+)$", str)
  if m:
    casted_number = int(str)
  else:
    m = re.match("^(\d+\.\d+)$", str)
    if m:
      casted_number = float(str)

  return(casted_number) 

#------------------------------------------------------------------------
def print_line_sep(char, count, pre_nl_count=0, post_nl_count=0):

  ## print a character multiples times on a line

  if pre_nl_count > 0:
    print( "\n" * post_nl_count )
 
  print( char * count )

  if post_nl_count > 0:
    print( "\n" * post_nl_count )


#------------------------------------------------------------------------
def get_obj_val(d_obj, find_expr):

  ## Determine if input is valid dict 
  ## If valid dict, apply the jmespath parsing and return matched value(s) 
  ## The matched value(s) could be any datatype (dict, list, str, int, etc.) 
  ## If more than one match is found, match will be a list of matched objects.
  ## If invalid dict, return False  
  ## TODO: if input is invalid, raise expcetion

  tag = myname + '.get_obj_val'

  if isinstance( d_obj, dict ):
    if DEBUG > 1:
      print( "%s: Getting value of \"%s\" in object" % (tag, find_expr))
    c_expr = jmespath.compile(find_expr)
    match = c_expr.search( d_obj ) 
    return(match)
  
  else:
    print( "%s: ERROR - Invalid input obj. Cannot perform jmespath operation" % (tag))
    print( d_obj )
    return False 


#------------------------------------------------------------------------
def get_user_name():
  ##return( getpass.getuser() )
    try:
      return getuser()
    except KeyError:
      return "unknown"

#------------------------------------------------------------------------
def dataDump(data, title=None):
  ## Mimic Perl's data Dumper()

  if title is None:
    title = 'DataDump'

  print("--START: %s-----------------" % (title) )
  print(data)
  print("--END-----------------------" )

#------------------------------------------------------------------------
def printTodo(text, title=None):
  ## print a "TODO" statement (for use during development)

  if title is None:
    print("\n\n--TODO-----------------" )
  else:
    print("\n\n--TODO: %s-----------------" % (title) )
  print(text)
  print("----------------------------\n\n" )
 
#------------------------------------------------------------------------

##
## UNIT-TEST EACH METHOD() 
##

if __name__ == '__main__':
  
  print("\n======================================================") 
  print("%s: TEST.get_obj_val: get value from object" % (myname))
  d_obj = {"foo": [{"bar": 1}, {"bar": 2}]}
  r = get_obj_val(d_obj, 'foo[*].bar') 
  print( r )
  print_line_sep('=', 15, 0, 0)
 
  print("\n======================================================") 
  print( "%s: TEST.getDataType: get data type" % (myname) )
  d_obj = {"foo": [{"bar": 1}, {"bar": 2}]}
  type = getDataType(d_obj) 
  print( "  Expected=[dict]. Found=[%s]" % (type) )
  l_obj = [{"bar": 1}, {"bar": 2}]
  type = getDataType(l_obj) 
  print( "  Expected=[list]. Found=[%s]" % (type) )
  s = "i am a string" 
  type = getDataType(s) 
  print( "  Expected=[str]. Found=[%s]" % (type) )
  n = 5 
  type = getDataType(n) 
  print( "  Expected=[int]. Found=[%s]" % (type) )
  n = 1.0 
  type = getDataType(n) 
  print( "  Expected=[float]. Found=[%s]" % (type) )
  t = (1, 0) 
  type = getDataType(t) 
  print("  Expected=[tuple]. Found=[%s]" % (type) )
  print_line_sep('=', 15, 0, 0)

  print("\n======================================================") 
  print("%s: TEST.getStrNumericType: Identify numeric type when casted as string" % (myname))
  str = "3"
  ntype = getStrNumericType(str)
  print("  Passed-string=\"%s\". Numeric-Type=[%s]" % (str, ntype) )
  str = "3.04"
  ntype = getStrNumericType(str)
  print("  Passed-string=\"%s\". Numeric-Type=[%s]" % (str, ntype) )
  str = "hello-world"
  ntype = getStrNumericType(str)
  print("  Passed-string=\"%s\". Numeric-Type=[%s]" % (str, ntype) )
 
  print("\n======================================================") 
  print("%s: TEST.castStrNumericType: Identify numeric type when casted as string, and cast to appropriate type" % (myname))
  str = "3"
  num = castStrNumericType(str)
  print("  Passed-string=\"%s\". Casted=[%s]" % (str, num) )
  str = "3.04"
  num = castStrNumericType(str)
  print("  Passed-string=\"%s\". Casted=[%s]" % (str, num) )
  str = "hello-world"
  num = castStrNumericType(str)
  print("  Passed-string=\"%s\". Casted=[%s]" % (str, num) )
 
  print("\n======================================================") 
  print("%s: TEST.exc_stderr: simple stderr-exception handler" % (myname))
  try:
    raise ValueError("Some exception was raised")
  except Exception as e:
    stderr_notify(myname, "ERROR - Notice-with-exception-with-info-and-exit", {'exc': e, 'exit':2}) 
    #stderr_notify(myname, "ERROR - Notice-with-exception-with-no-info-and-exit", {'exit':2})
    #stderr_notify(myname, "WARNING - Notice-with-exception-with-info-and-no-exit", {'exc':e} )
    #stderr_notify(myname, "Notice-only" ) 

