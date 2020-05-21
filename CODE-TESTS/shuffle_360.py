"""

  shuffle_360.py

  Problem: 
   Given a list of names, shuffle the names as many times as required to
   return (360-degress) back to the original order of the names list

   Try this with smaller and larger lists

"""
from copy import deepcopy
import random

def shuffle_list(l_input):
  """ Take an input list, shuffle it and return a shuffled copy of the list """
  l_shuffled = deepcopy(l_input)
  random.shuffle(l_shuffled)
  print(" shuffled: %s" % l_shuffled)
  return(l_shuffled)


def shuffle_until_match(l_original):
  """ Take in input list and continue shuffling it until we return to the original order """
  print("ORIGINAL: %s" % l_original)
  N_attempts = 0
  while True:
    N_attempts +=1
    l_shuffled = shuffle_list(l_original)
    if l_shuffled == l_original:
      print("We have a return to original after %d attempts" % (N_attempts))
      break
    else:
      l_shuffled = shuffle_list(l_shuffled)


if __name__ == '__main__':

  full_list = ["Bill", "Joe", "Mark", "Alice", "Lisa"]
  n = 4 
  list = full_list[:n]
  shuffle_until_match(list)
  

