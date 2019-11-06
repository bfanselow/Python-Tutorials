#!/usr/bin/env python3

"""

  File: args_kwargs.py
  Description:
   Demonstration of using *args, **args

  Bill Fanselow
  11-06-2019

"""
from functools import wraps

#--------------------------------------------------------------
def visual_bookends(func):
  ##
  ## Function decorator which prints lines around the output of the passed function 
  ## and include the passed function name. 
  ##
  @wraps(func)
  def func_wrapper(*args, **kwargs):
    fname = func.__name__
    print("---------------------------------------------------") 
    print("%s():" % (fname)) 
    func(*args, **kwargs)
    print("---------------------------------------------------\n") 

  return func_wrapper

#--------------------------------------------------------------
@visual_bookends
def test_args(a1, *args):
  ## 
  ## "a1" is required, followed by any number of optional args
  ## 
  print("REQ-ARG: a1=%s" % (a1))
  for a in args:
    print(" OPT-ARG: a=%s" % (a))
  print("type(args): %s" % (type(args)))

#--------------------------------------------------------------
@visual_bookends
def test_kwargs(a1, **kwargs):
  ## 
  ## "a1" is required, followed by any number of optional keyword args 
  ## 
  print("REQ-ARG: a1=%s" % (a1))
  for k,v in kwargs.items():
    print(" OPT-KWARG: [%s]={%s]" % (k,v))
  print("type(kwargs): %s" % (type(kwargs)))

#--------------------------------------------------------------
@visual_bookends
def test_both(*args, **kwargs):
  ## 
  ## "a1" is required, followed by any number of optional *args and **kwargs 
  ## 
  for a in args:
    print(" OPT-ARG: a=%s" % (a))
  for k,v in kwargs.items():
    print(" OPT-KWARG: [%s]={%s]" % (k,v))

#--------------------------------------------------------------
if __name__ == "__main__": 

  ## test_args()
  test_args('BILL', 'joe', 'bob', 'fred') 

  ## test_kwargs(): with keyword args
  test_kwargs('BILL', lastname='fanselow', age=53, height=183, weight=155) 
  
  ## test_kwargs(): with dict 
  d_args = {'lastname': 'fanselow', 'age': 53, 'height': 183, 'weight': 155 }
  test_kwargs('BILL', **d_args) 

  ## test_both(): with args and kwargs
  test_both('BILL', 'joe', 'bob', lastname='fanselow', age=53, height=183, weight=155) 
  
  ## test_both(): with only kwargs
  test_both(firstname='william', lastname='fanselow', age=53, height=183, weight=155) 

