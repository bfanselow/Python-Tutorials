"""
 quicksort.py

 Take a list of numbers and return a sorted list

 Design:
  1) find the mid-point number 
  2) get all numbers below the mp and pass that back into method recursively
  3) get all numbers equal to mid-point - there may be more than one!
  4) get all numbers above the mp and pass that back into method recursively
  5) assemble these back together  

"""
def quick_sort(number_list):
  print(number_list)
  if len(number_list) <= 1:
    return(number_list)

  ## get number associated with midpoint of list 
  mp = number_list[len(number_list) // 2]
  print(f"MP={mp}"
  nums_below_mp = [x for x in number_list if x < mp] 

  nums_at_mp = [x for x in number_list if x == mp] 
 
  nums_above_mp = [x for x in number_list if x > mp] 

  sorted = []
  sorted.extend( quick_sort(nums_below_mp) )
  sorted.extend( nums_at_mp )
  sorted.extend( quick_sort(nums_above_mp) )
  print(f"RETURN={sorted}"

  return(sorted)
