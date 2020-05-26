""""
  adjacent_chars.py

  Problem:
   Given a string, check if the letters can be rearranged so that no two characters that are the same.

  Examples:
    "aab"    => "aba"
    "abc"    => "abc"
    "aabbcc" => "abcabc"
    "aaac"   => None 

"""
from copy import deepcopy


def need_to_move(n, check_char, list_chars):
  move = False
  j = n+1
  for c in list_chars[j:]:
    if check_char == c:
      print("DUP-ADJ: %s" % c)
      move = True 
      break
  return move

def find_new_index(n, check_char, list_chars):
  new_idx = None 
  j = n+1
  for i in range(j,len(list_chars)):
    c = list_chars[i]
    print("finding new idx: i=(%d), compare=[%s]  for char: %s" % (i,c,check_char))
    if check_char != c:
      print("FOUND-NEW-IDX (%d) for: %s" % (i,c))
      new_idx = i
      break
  return new_idx 

def reshuffle(input_str):
  l_chars = [c for c in input_str ]
  l_fixed_chars = deepcopy(l_chars)
  last_idx = len(l_fixed_chars) - 1
  for i in range(len(l_fixed_chars)):
    ## does it need to move?
    c = l_chars[i]
    print("idx=(%d) char=[%s]" % (i,c)) 
    if need_to_move( i, c, l_chars ):
      new_idx = find_new_index(i, c, l_chars)
      if new_idx is not None:
        print("pop: [%s] from i=[%d]" % (c, i)) 
        print('POP: {}'.format(l_chars)) 
        l_chars.pop(i)
        if new_idx == last_idx:
          print("append: [%s] to new idx=[%d]" % (c, new_idx)) 
        else:
          print("insert: [%s] to new idx=[%d]" % (c, new_idx)) 
        l_chars.insert(new_idx, c )
        print('SUB: {}'.format(l_chars)) 
      else:
        print("Can't find new idx for [%d] char: [%s]" % (i,c))
        break
  final = "".join(l_chars)
  return final

for str in [
    'aab',
    'abc',
    'aabbcc',
    'aaac'
  ]:
  new = reshuffle(str)
  print("ORIG: (%s)  FINAL (%s)" % (str, new))

