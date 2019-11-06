#!/usr/bin/env python3

"""

 File: decorator_demos.py

 Description:
   Demonstation of the function/method decorator capability using
   various decorator approaches.

 Requires:
   # pip3 install decorator
   # pip3 install wrapt 

 Bill Fanselow
 11-06-2019

"""
from decorator import decorator
import functools
import wrapt
import inspect

#------------------------------------------------------------------------
# DECORATORS
#------------------------------------------------------------------------
def decorate_by_hand(func_to_decorate):
    ##
    ##  Remember, functions are just objects and can be passed to other functions.
    ##  A decorator is just a function that accepts another function as parameter,
    ##  so as to "wrap" itself around the other function. This allows you to
    ##  perform some operations before and/or after executing the function.
    ##
    ## Pros: inutitive, fast
    ## Cons: doesn't easily handle function args and function signatures such as func_to_decorate.__name__
    ##
    tag = 'decorate_by_hand'
    print("%s: Decorating function (%s) by hand..." % (tag, func_to_decorate.__name__))

    def func_wrapper(*args):
      print("  Executing (pre) tasks before running function...")
      # Call the function here (using parentheses)
      func_to_decorate()
      print("  Executing (post) tasks after running function...")

    print("%s: Finished decorating function" % (tag))
    # Return the wrapper function.
    return( func_wrapper )

#------------------------------------------------------------------------
def decorator_with_args(func_to_decorate):
    ##
    ## Pros: simple, fast
    ## Cons: doesn't easily handle function signatures such as func_to_decorate.__name__
    ##
    tag = 'decorator_with_args'
    print("%s: Decorating function with args..." % (tag))
    def func_wrapper_with_args(*args, **kwargs):
      print("  ARGS: %s" % (args))
      print("  KARGS: %s" % (kwargs))
      print("  Executing (pre) tasks before running function...")
      func_to_decorate(*args, **kwargs)
      print("  Executing (post) tasks after running function...")
    print("%s: Finished decorating function" % (tag))
    return( func_wrapper_with_args )

#------------------------------------------------------------------------
def decorator_with_wraps(func_to_decorate):
    ##
    ## Pros: easier to use. Handles func_to_decorate._name__ 
    ## Cons: Breaks funtion introspection a can be seen with inspect.getfullargspec( test_func_3 )) 
    ##       This may seem like a non-issue, but there are some bugs that can arise from 
    ##       broken-introspection. 
    @functools.wraps(func_to_decorate)
    def wrapper(*args, **kwargs):
      print("  [@wraps.wrapper]: Executing (pre) tasks before running function...")
      return func_to_decorate(*args, **kwargs)
      print("  [@wraps.wrapper]: Executing (post) tasks after running function...")
    return wrapper

#------------------------------------------------------------------------
@decorator
def decorator_decorator(func_to_decorate, *args, **kwargs):
    ##
    ## Pros: Easier syntax 
    ## Cons: Slower than previous approaches, though unlikely to be noticed 
    ##
    print("[decorator_decorator}: Calling decorated function...")
    text = func_to_decorate(*args, **kwargs)
    return( text )

#------------------------------------------------------------------------
@wrapt.decorator
def wrapt_decorator(wrapped, instance, args, kwargs):
    print(" [wrapt.decorator}: Calling decorated function")
    return wrapped(*args, **kwargs)

#------------------------------------------------------------------------
#------------------------------------------------------------------------
# Dummy test functions
#------------------------------------------------------------------------
def test_func_1():
  print(">>test_func_1:  I am a simple test funtion <<")

#------------------------------------------------------------------------
@decorator_with_args
def test_func_2(*args, **kwargs):
    ## Simple funtion decorated with shortcut syntax: @<decorator> above function
    print(">>test_func_2():  I am a function decoratored with @<decorator> syntax. Args=(%s) KwArgs=(%s)<<" % (args, kwargs))

#------------------------------------------------------------------------
@decorator_with_wraps
def test_func_3(*args, **kwargs):
    ## Simple funtion decorated using @functools.wraps 
    print(">>test_func_3():  I am a function decoratored with @functools.wraps. Args=(%s) KwArgs=(%s)<<" % (args, kwargs))

#------------------------------------------------------------------------
@decorator_decorator
def test_func_4(*args, **kwargs):
    ## Simple funtion decorated using @decorator module
    text = ">>test_func_4():  I am a function decoratored with @decorator module. Args=(%s) KwArgs=(%s)<<" % (args, kwargs)
    return(text)

#------------------------------------------------------------------------
@wrapt_decorator
def test_func_5(*args, **kwargs):
    ## Simple funtion decorated using @wrapt module
    text = ">>test_func_5():  I am a function decoratored with @wrapt module. Args=(%s) KwArgs=(%s)<<" % (args, kwargs)
    return(text)

#------------------------------------------------------------------------
# CLASSES
#------------------------------------------------------------------------
class ClassDecorators(object):
  @decorator
  def some_method_decorator(func, *args, **kwargs):
    self = args[0]
    print("%s.some_method_decorator:  Decorating method..." % (self.cname))
    results = func(*args, **kwargs)
    print("%s.some_method_decorator:  Done decorating method" % (self.cname))
    return(results)

class ClassDecoratorTest():
  def __init__(self):
    self.cname = self.__class__.__name__
    print("%s: Finished initialization" % (self.cname))

  @ClassDecorators.some_method_decorator  
  def some_method(self, text):
    return("<b>%s</b>" % (text))

#------------------------------------------------------------------------
#------------------------------------------------------------------------
if __name__ == "__main__":
  
  print("\n<START>\n")
    
  ## Test hand-crafted 
  decorated_method = decorate_by_hand(test_func_1)

  print("TEST 1: Clunky hand-crafted syntax")
  decorated_method()
  print("NAME1 (not useful!): %s" % decorated_method.__name__)

  ## Test hand-crafted with shortcut syntax: @<decorator>
  print("\n==================================================")
  print("TEST 2: Using @<decorator> syntax")
  test_func_2('arg1', kwa1=1, kwa2=2 )
  print("NAME2 (not useful!): %s" % test_func_2.__name__)

  ##################################################################
  ## NOTICE: the order of the following printed messages (particularly before "START >>") is even printed
  #   decorator_with_args: Decorating function with args...
  #   decorator_with_args: Finished decorating function
  #   <START>
  #   decorate_by_hand: Decorating function (test_func_1) by hand...
  #   decorate_by_hand: Finished decorating function
  ##################################################################

  ## Test @functools.wraps syntax
  print("\n==================================================")
  print("TEST 3: Using @functools.wraps syntax")
  test_func_3('arg1', kwa1=1, kwa2=2 )
  print("NAME3 (much more useful!): %s" % test_func_3.__name__)

  ## Test @decorator module
  print("\n==================================================")
  print("TEST 4: Using @decorator module")
  print(test_func_4('arg1', kwa1=1, kwa2=2 ))
  print("NAME4: %s" % test_func_4.__name__)

  ## Test @wrapt module 
  print("\n==================================================")
  print("TEST 5: Using @wrapt module")
  print(test_func_5('arg1', kwa1=1, kwa2=2 ))
  print("NAME5: %s" % test_func_5.__name__)


  ## Test use of @decorator inside a class 
  print("\n==================================================")
  print("TEST 6: Using @decorator module inside a class")
  try:
    CDT = ClassDecoratorTest()
  except Exception as e:
    raise
  bold_text = CDT.some_method('Please make me bold')
  print(bold_text)
  
  print("\n<END>\n")
