#!/usr/bin/env python3

"""

  File: listComprehension.py
  Description:
    Simple tests to demonstrate the list-comprehension concept

  Author: Bill Fanselow
  Date:   11-04-2019

"""
#------------------------------------------------------------
## create simple list of x^2 where x in range(start,stop)
def squares(start=0, stop=10):
  ##
  ## This is equivelent to:
  ##   l_sq = []
  ##   for x in range(start, stop):
  ##     l_sq.append(x**2)
  ##
  l_sq = [x**2 for x in range(start,stop)]
  return(l_sq) 

#------------------------------------------------------------
## create list of 2^x where x in range(start,stop)
def doubler(start=0, stop=10):
  l_db = [ 2**x for x in range(start,stop)]
  return(l_db) 

#------------------------------------------------------------
## create list of non-prime numbers from 4 to stop 
## (note that 1 is NOT considered a prime number)
def nonprimes(stop):
  ##
  ## This is a complex (nested) list comprehension.
  ## This is equivelent to 2 nested for() loops:
  ##   l_np = []
  ##   for i in range(2, 8): ## start with first for(): 2,3,4,5,6,7
  ##     for j in range(i*2, 50, i): ## nested for() with stop=50: 4,6,8,10,...,3,6,9,12,...,8,12,16,20,...,10,15,20,25,...
  ##       l_np.append(j)
  ##
  l_np = [j for i in range(2,8) for j in range(i*2, stop, i)]
  return(l_np) 

#------------------------------------------------------------
## create list of prime numbers from 4 to stop
def primes(stop):
  l_nonprimes = nonprimes(stop)
  l_p = [x for x in range(2,stop) if x not in l_nonprimes]
  return(l_p) 

#------------------------------------------------------------
## perform multiple string operations on a sentance 
def word_parse(sentance=None):
  if not sentance:
    sentance = "Hello my name is Bill and I am pleased to meet you"
  l_words = sentance.split()
  l_parsed = [[w.upper(), w.lower(), len(w)] for w in l_words]
  return(l_parsed) 

#------------------------------------------------------------
## Recursive quicksort of a list of integers 
def quick_sort(l_integers):

  if len(l_integers) <= 1:
    return(l_integers)
  ## Get the number associated with the mid-point index of the list
  midpoint = l_integers[len(l_integers) // 2 ] 

  ## Get all numbers with value less than the mid-point number
  l_left_of_midpoint = [ x for x in l_integers if x < midpoint] 
  
  ## This line seems unnecessary at first glance - why not just do l_midpoints = [midpoint]
  ## On deeper look you see that this works but has the effect of removing duplicated entries.
  l_midpoints = [ x for x in l_integers if x == midpoint] 

  ## Get all numbers with value greater than the mid-point number
  l_right_of_midpoint = [ x for x in l_integers if x > midpoint] 
  l_sorted = quick_sort(l_left_of_midpoint) + l_midpoints + quick_sort(l_right_of_midpoint)

  return(l_sorted) 

#------------------------------------------------------------
if __name__ == "__main__":
  print("\n\nList-comprehension tests:\n")

  print("List of x^2 where x in [0..8]")
  print( squares(0, 9) )
  
  print("\nList of 2^x where x in [0..11]")
  print( doubler(0, 12) )
  
  print("\nLost of Non-prime numbers from 4 to 60")
  print( nonprimes(60) )
  
  print("\nList of Prime numbers from 4 to 60")
  print( primes(60) )

  print("\nParse a sentance and do some word-analysis")
  print(word_parse())

  l_ints = [23,2,6,19,110,3,5,1,6,6,6,2,50,30,60]
  print("\nQuick-sort a list of unsorted ints: %s" % str(l_ints))
  print( quick_sort(l_ints) )
