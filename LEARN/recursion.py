#!/usr/bin/env python3

"""
  
 File: recursion.py
 Author: Bill Fanselow
 Date: 11-13-2019  
 Description:
   Quick demo of recursive functions.
   Recursive functions must have 2 cases:
    * recursive case (smaller version of the original problem)
    * "base" case (smallest version of the problem). Stops the recursion.

 Example: factorials
    5! = 5 * 4! 
    Here, 4! is a smaller version of the original problem
     4!=4*3!,  3!=3*2!, 2!=2*1!, 
     1! is the "base" (smallest) case 

 NOTICE!!!!!!!: 
   Python will save you from forgetting the base case and raise an
   RecursionError() exception if the maximum recursion depth is
   exceeded.  However, keep in mind that recursive functions can
   often become extremely expensive/time-consuming. Therefore, careful 
   consideration of the function logic is critical to avoid costly
   processing.  For example, compare the two different Fibonacci 
   functions below. The "fast" version is 42,000 times faster than
   the "slow" one!!! 

"""
import time

##--------------------------------------------------------------------
def func_timer(func):
  def time_it(*args, **kwargs):
    ts_start = time.time()
    result = func(*args, **kwargs)
    t_diff = time.time() - ts_start
    print("   >>%s(%s):  %2.2f ms" % (func.__name__, args[0], (t_diff*1000)))
    return result
  return time_it

##--------------------------------------------------------------------
def factorial_recursion(n):
  if n == 1:   ## "base" case
    return(n)
  return n * factorial_recursion((n-1)) ## recursive case

##--------------------------------------------------------------------
def fibonacci_recursion_slow(n):
  ## F(n) = F(n-1) + F(n-2) where F(0) = 0 and F(1) = 1
  ## Sequence: 0,1,1,2,3,5,8,13,...
  if n == 0:   ## "base" case
    return(0)
  elif n == 1:  ## another "base" case
    return(1)
  return fibonacci_recursion_slow((n-1)) + fibonacci_recursion_slow((n-2))  ## recursive case

##--------------------------------------------------------------------
d_fibo = {0:0, 1:1} ## a memory dict outside of recursion
def fibonacci_recursion_fast(n):
  if not n in d_fibo:   
    d_fibo[n] = fibonacci_recursion_fast((n-1)) + fibonacci_recursion_fast((n-2))
  return d_fibo[n]

##--------------------------------------------------------------------
@func_timer
def timed_fibonacci_recursion_slow(n):
  ## made a seperate function so that the timing decorator is not called on each recursion, rather only
  ## times the total time for all calculations
  return fibonacci_recursion_slow(n)

##--------------------------------------------------------------------
@func_timer
def timed_fibonacci_recursion_fast(n):
  ## made a seperate function so that the timing decorator is not called on each recursion, rather only
  ## times the total time for all calculations
  return fibonacci_recursion_fast(n)

##--------------------------------------------------------------------
if __name__ == "__main__":

  ## Factorials 
  l_nums = [ 3, 5, 10, 20, 30 ]
  print("\nFactorials for x in %s" % (l_nums))
  for n in l_nums:
    r = factorial_recursion(n)
    print(" %s!=%d" % (n,r))
  
  ## Fibonacci (slow)
  print("\nFibonacci numbers up to 20 (slow)")
  l_f = [fibonacci_recursion_slow(n) for n in range(0,21)]
  print(" %s\n" % (l_f))

  ## Timed Fibonacci (slow)
  N = 30 
  print("Fibonacci(%s) (slow)" % N)
  timed_fibonacci_recursion_slow(N)
 
  ## Fibonacci (faster)
  print("\nFibonacci numbers up to 20 (fast)")
  l_f = [fibonacci_recursion_fast(n) for n in range(0,21)]
  print(" %s\n" % (l_f))
  
  ## Timed Fibonacci (fast)
  N = 30 
  print("Fibonacci(%s) (fast)" % N)
  timed_fibonacci_recursion_fast(N)
 
