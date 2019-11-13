#!/usr/bin/env python3

"""

 Quick demo of recursive functions.
 Recursive functions must have 2 cases:
  * recursive case (smaller version of the original problem)
  * "base" case (smallest version of the problem). Stops the recursion.

  Example: factorials
    5! = 5 * 4! 
    Here, 4! is a smaller version of the original problem
     4!=4*3!,  3!=3*2!, 2!=2*1!, 
     1! is the "base" (smallest) case 

"""

##--------------------------------------------------------------------
def factorial_recursion(n):
  if n == 1:   ## "base" case
    return(n)
  return n * factorial_recursion((n-1)) ## recursive case

##--------------------------------------------------------------------
def fibonacci_recursion(n):
  ## F(n) = F(n-1) + F(n-2) where F(0) = 0 and F(1) = 1
  ## Sequence: 0,1,1,2,3,5,8,
  if n == 0:   ## "base" case
    return(0)
  elif n == 1:  ## another "base" case
    return(1)
  return fibonacci_recursion((n-1)) + fibonacci_recursion((n-2))  ## recursive case

##--------------------------------------------------------------------
if __name__ == "__main__":

  ## Facitorials 
  l_nums = [ 3, 5, 10, 20, 30 ]
  print("\nFactorials for x in %s" % (l_nums))
  for n in l_nums:
    r = factorial_recursion(n)
    print(" %s!=%d" % (n,r))
  
  ## Fibonacci
  print("\nFibonacci numbers up to 20")
  l_f = [fibonacci_recursion(n) for n in range(0,21)]
  print(" %s\n" % (l_f))
