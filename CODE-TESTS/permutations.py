"""
  permutations.py

  Given a list of integers find all the possible ways to order the
  list differently. The number of permutations is know to be N!

  Example:
   Input: [1, 2, 3]
   Output: [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
   Num-perms: 3! = 3*2*1 = 6

  Permuatations of a list of elements [a,b,c,d...] is found by recursion:
    permutations([a,b,c,...]) = [a + permutations([b,c,...]), b + permutations([a,c,..]), ...]

  Easy way is to use itertools.permutations()

"""
import math
from itertools import permutations

def get_permutations(l_nums):
   """

   """

   if len(l_nums) == 1:
     return [l_nums]

   perm_list = [] # resulting list
   for n in l_nums:
     remaining_elements = [x for x in l_nums if x != n]
     plist = get_permutations(remaining_elements) # permutations of sublist

     for p in plist:
       perm_list.append([n] + p)

   return perm_list


if __name__ == '__main__':

  l_input = [3,4,5,6]
#  l_input = [1,2,3]
  length = len(l_input)
  fct = math.factorial(length)
  perms = get_permutations(l_input)
  total = len(perms)
  if total != fct:
    raise ValueError("Factorial does not match answer")
  print("TOTAL=%d" % total)
  print("%s" % str(perms))

  easy_perms = [list(p) for p in list(permutations(l_input))]
  if perms != easy_perms:
    print(easy_perms)
    #raise ValueError("itertools.permutations() does not match answer")
