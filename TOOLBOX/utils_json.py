

"""

 File: utils_json.py
 Author: Bill Fanselow
 
 Description:
   json parsing/handling functions

 Requires: 
   pip install jmespath

"""

##-----------------------------------------------------------
## Python2 compatiblity
from __future__ import (division, print_function)
##-----------------------------------------------------------

import json
import jmespath
from datetime import date, datetime

myname = 'utils_json.py'

DEBUG = 2 

#----------------------------------------------------------
def value_converter(obj):
  """
   Convert any json values which are not serializable
   Usage:  json.dumps(obj, default=value_converter)
  """
  ## datetime object: json.dumps() throws "TypeError: Object of type 'datetime' is not JSON serializable"
  if isinstance(obj, (datetime, date)):
    return obj.isoformat()

  raise TypeError ("Type %s not serializable" % type(obj))

#----------------------------------------------------------
def dict_to_json(d_input):
  """ Convert dict to json with automatic conversions which would normally fail in default json.dumps()"""
  json_str = None
  try:
    json_str = json.dumps(d_input, default=value_converter)
  except Exception as e:
    raise 

  return(json_str)

#----------------------------------------------------------
def json_to_dict(json_str):
  """ Convert json to dict"""
  d_dict = None
  try:
    d_dict = json.loads(json_str)
  except Exception as e:
    raise 

  return(d_dict)

#----------------------------------------------------------
def is_json(json_str):
  """Determine if a string is valid json"""
  
  tag = myname + '.is_json'
 
  if DEBUG > 1:
    print( "%s: Checking json: %s" % (tag, json_str))

  try:
    d_json = json.loads(json_str)
  except ValueError as e:
    print( ">>>>>>>>>>>>>>>>>>NOT a json object" )
    return False
  return True

#----------------------------------------------------------
def read_json_config(cfg_file_path):
  """
   Read a json config file
   If valid json, return a dict containing the data  
   If invalid json, return False  
  """
  tag = myname + '.read_json_config'
  
  if DEBUG > 1:
    print( "%s: Reading config file (%s)..." % (tag, cfg_file_path))
  try:
    with open(cfg_file_path, 'r') as cfg_file:
      db_config = json.load(cfg_file)
  except Exception as e:
    print( "%s: ERROR - %s" % (tag, e))
    return False

  return( db_config )

#----------------------------------------------------------

def get_json_val(json_str, find_expr):
  """
   If valid json, apply the jmsepath parsing and return the matched value(s) 
   The matched value(s) could be any datatype found in a json (dict, list, str, int, etc.) 
   If more than one match is found, match will be a list of matched objects.
   If invalid json, return False  
   TODO: if input is invalid, raise expcetion
  """
  tag = myname + '.get_json_val'
 
  if is_json(json_str):
    if DEBUG > 1:
      print( "%s: Getting value of \"%s\" in json string" % (tag, find_expr))
    d_json = json.loads(json_str)
    c_expr = jmespath.compile(find_expr)
    match = c_expr.search(d_json )  ## match could be any datatype found in a json (dict, list, str, int, etc.) 
    return( match )
  else:
    print( "%s: ERROR - Invalid input json str. Cannot perform jmespath operation" % (tag))
    return False 

##----------------------------------------------------------
##
## UNIT-TEST EACH METHOD() 
##

if __name__ == '__main__':

  import utils as utils

  print( "\n%s: TEST 1: test for valid json" % (myname))
  test_json = '{ "key1": "value1", "key2": "value2" }' 
  if is_json( test_json ):  
    print( "VALID JSON")
  else:
    print("INVALID JSON")
  utils.print_line_sep('=', 15, 0, 0)

  print( "\n%s: TEST 2: read config file" % (myname))
  test_config_file = '/home/wfanselow/PYTHON/config/DB_CONFIG'
  db_config = read_json_config( test_config_file ) 
  if db_config:
    if DEBUG > 1:
      print( db_config )
  else:
    print( "%s: ERROR - Invalid json from file: %s"  % (myname, test_config_file) )
  utils.print_line_sep('=', 15, 0, 0)
  
  print( "\n%s: TEST 3: get value from json" % (myname) )
  test_json = '{"foo": [{"bar": 1}, {"baz": 2}]}' 
  r = get_json_val(test_json, 'foo[*].bar') 
  print( r )
  utils.print_line_sep('=', 15, 0, 0)
