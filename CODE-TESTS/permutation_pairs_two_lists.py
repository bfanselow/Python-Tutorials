"""
  
  permutation_pairs_two_lists.py

  Given two lists of equal length find all the possible permuations for pairing
  two elements, one from each list. In case the lists have an element that is the
  same in both, we ignore the duplication that is created by the base algorithm.

  Example:
   Input: [1, 2, 3], ['a', 'b', 'c']
   Output: [[1, 'a'], [1, 'b'], [1, 'c'], [2, 'a'], [2, 'b'], [2, 'c'], [3, 'a'], [3, 'b'], [3, 'c']]

  We use itertools.product(l1, l2) which returns the "Cartesion Product" of two lists

"""
import itertools

def list_permutations(l1, l2):
   perm_list = [ list(cp) for cp in itertools.product(l1,l2) if cp[0] != cp[1] ]
   return perm_list

if __name__ == '__main__':

  l1 = [1,2,3]
  l2 = ['a','b','c']
  perms = list_permutations(l1, l2)
  print("%s" % str(perms))
