#!/usr/bin/env python3

"""
  File: map_function.py
  Description:
    Simple tests to demonstrate the map() function 
  Author: Bill Fanselow
  Date:   11-04-2019


  Basic function syntax:  results = map(function, iterables)
   Return a list of results after applying a given funtion to each item
   of a given iterable (list, tuple, etc.). The returned "results" value
   can then be passed to functions like list() or set().

"""

#------------------------------------------------------------
## Helper functions
#------------------------------------------------------------
def square(x):
  ## return x^2 for passed x 
  return(x**2) 

#------------------------------------------------------------
def double(x):
  ## return 2*x for passed x 
  return(x*2) 

#------------------------------------------------------------
if __name__ == "__main__":
  print("\n\nMap function tests:\n")

  results = map(square, range(0,6)) 
  print("List of x^2 where x in %s" % (list(range(0,6))))
  print( " ", list(results), end="\n" )

  results = map(double, range(1,6)) 
  print("List of x*2 where x in %s" % (list(range(1,6))))
  print( " ", list(results), end="\n" )

  ## Using lambda functions 
  l_x = list(range(1,5)) ## 1,2,3,4
  l_y = l_x[::-1]        ## 4,3,2,1

  results = map(lambda x, y: x + y, l_x, l_y) 
  print("List of x+y where x,y in %s, %s" % (l_x, l_y))
  print( " ", list(results), end="\n" )

  results = map(lambda x,y: x**y, l_x, l_y) 
  print("List of x**y where x,y in %s, %s" % (l_x, l_y))
  print( " ", list(results), end="\n" )


