"""

  max_contiguous.py

  Problem:
   Given an input list of ints, find the sub-array of contiguous numbers having
   the maximum length. Contiguous numbers apply even if list is not sorted.

  Example:
   Input:  [ 1,2, 5,6,7,8,9, 13, 19, 21, 30,31,32,33, 35,36 ]
   Result: [ 5, 6, 7, 8, 9 ]

"""


def get_max_contiguous(l_input):

  ## sort
  l_input_sorted = sorted(l_input)

  ## find all contiugous sub-arrays
  l_all_subs = []
  l_sub = []
  for i in range(len(l_input)-1):
    #print(i)
    v = l_input[i]
    v_next = l_input[i+1]
    if v_next - v == 1:
      l_sub.append(v)
    else:
      l_sub.append(v)
      l_all_subs.append(l_sub)
      l_sub = []

  ## Identify which sub-array is longest:
  ## sort by length and take last element of sorted
  srtd_list = sorted(l_all_subs, key=len)
  max_consec_sub = srtd_list[-1]

  return max_consec_sub

if __name__ == '__main__':

   input = [ 1,2, 5,6,7,8,9, 13, 19, 21, 30,31,32,33, 35,36 ]
   expected_result = [ 5, 6, 7, 8, 9 ]

   result = get_max_contiguous(input)
   print(result)
   if result != expected_result:
     assert False
