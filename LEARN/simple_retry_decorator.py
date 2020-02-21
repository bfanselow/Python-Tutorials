#!/usr/bin/env python3

"""
 File: simple_retry_decorator.py

 Description:
  Simple decorator that sets up retries around a piece of code and returns the first
  successful value, or gives up and raises the most recent exception after <N> attempts.
  The @ symbol is basically a syntactic sugar for passing in the decorated function as
  an argument to the decorator.

  Author: Bill Fanselow 2020-02-21

"""
import random

RETRIES = 2
FIXED_DENOMINATOR = 4

## Define a "retry" decorator
def decorator_retry(func):
    tag = 'decorator_retry()'
    def retried_function(*args, **kwargs):
        for i in range(RETRIES):
            print("%s: [%s] Attempting func: %s" % (tag, i, func.__name__))
            try:
               return func(*args, **kwargs)
            except Exception as exc:
               print("%s: Exception raised while calling %s with args: %s, kwargs: %s - [%s]" % (tag, func.__name__, args, kwargs, exc))
               if i == RETRIES:
                 raise
    return( retried_function )

## decorate our function
@decorator_retry
def do_something_risky(min, max):
  """
   Divide a fixed-numerator int by a random denominator int between min and max.
   Since random-denominator could be Zero we need to do some retries
   if we try to divide by zero
  """
  tag = 'do_something_risky()'
  fixed_numerator = FIXED_DENOMINATOR
  random.seed() ## uses system clock if no arg
  print(" > %s: Finding random-int between %d - %d" % (tag, min, max))
  random_denominator = value = random.randint(min, max)
  print(" > %s: Computing %d/%d" % (tag, fixed_numerator, random_denominator))
  division_result = fixed_numerator / random_denominator
  return(division_result)


if __name__ == '__main__':

  ## Call the decorated function
  result = do_something_risky(0,3)
  print("RESULT: %s" % (result))
