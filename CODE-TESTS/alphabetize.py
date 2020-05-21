"""
  alphabetize.py

  Given a list of names (First Last), sort them in alphabetical order by last-name

  1) Create a mapping of sortable versions of the name to the actual name 

  2) Quick-sort the sortable name "keys' from 1
    2.1) find the value at the (length) midpoint of the list
    2.2) get a values below this MP and recursively sort them
    2.3) get a values at this MP 
    2.4) get a values above this MP  and recursively sort them
    2.5) compile lists 2.2, 2.3, 2.4 into new list
  
  3) Map back to the original names from the sortable name "keys'


"""
import sys
import re

def create_name_map(list_of_names):
  """create dict of cleaned name.lower()=>name"""
  d_map = {}
  for name in list_of_names:
    cleaned_name = re.sub('[\'\"\- ]', '', name)
    key = cleaned_name.lower()
    d_map[key] = name 
  return(d_map)
  
def quick_sort(sortable_keys):

  if len(sortable_keys) <= 1:
    return(sortable_keys)

  # find mp
  mp = sortable_keys[len(sortable_keys)//2]

  # find left of mp
  left_of_mp = [k for k in sortable_keys if k < mp]
  # find dups at mp
  dups_at_mp = [k for k in sortable_keys if k == mp]
  # find right of mp
  right_of_mp = [k for k in sortable_keys if k > mp]

  # recursive sort
  sorted_keys = [] 
  sorted_keys.extend( quick_sort(left_of_mp) )
  sorted_keys.extend( dups_at_mp )
  sorted_keys.extend( quick_sort(right_of_mp) )
  return(sorted_keys)


def alphabetize(list_of_names):

  d_map = create_name_map(list_of_names) ## maps sortable-name=>original-name
  sortable_name_keys = list(d_map.keys()) ## list of sortable -name
#  sorted_name_keys = quick_sort(sortable_name_keys)
## Or we can just use sorted()
  sorted_name_keys = sorted(sortable_name_keys)
  list_sorted_names = [d_map[key] for key in sorted_name_keys]
  return(list_sorted_names)

if __name__ == '__main__':
  full_names = [
    "John Smith",
    "Bob Smith",
    "Kara Smith",
    "Bill O'Reilly",
    "Bob Almond",
    "Bill O-Shay"
  ]
  print("Original:\n%s" % (full_names))
  print("Sorted:\n%s\n" % alphabetize(full_names))
