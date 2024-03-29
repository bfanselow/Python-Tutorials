#!/usr/bin/env python3


# Given a list of lists, remove ALL duplicate items (not just all duplicate sublists or set(sublists)).
# In other words, for any item in any list, only keep the first instance of that item.
# Example:
# Given this list of lists
#   lol = [
#     ['a', 'b', 'c'],
#     [1, 3, 5],
#     ['a', 'X', 3],
#     ['c'],
#     [1, 2, 3],
#   ]
# The reduced list of lists whould be
#   ulol = [
#     ['a', 'b', 'c'],
#     [1, 3, 5],
#     ['X'],
#     [2],
#   ]


def prune(lol):
    # rm empty sublists from a list of lists
    for i, sl in enumerate(lol):
        if not sl:
            del lol[i]

def rm_dup_items(lol):
    for i, subl in enumerate(lol):
        set_subl = set(subl) # rm dup items within a list
        lol[i] = list(set_subl)
        # rm dups in the remaining sub-lists
        for j, next_subl in enumerate(lol[i+1:], start=1):
            if set_subl.intersection(next_subl):
                lol[(i + j)] = list(set(next_subl).difference(subl))
    prune(lol)

# test with these tuples of input/expected-output pairs
tpl_lols = [
 (
  [
    ['a', 'b', 'c'],
    [1, 3, 5],
    ['a', 'X', 3],
    ['c'],
    [1, 2, 3]
  ],
  [
    ['a', 'b', 'c'],
    [1, 3, 5],
    ['X'],
    [2],
  ]
 ),
 (
  [
    [],
    [1, 3, 5, 3, 5],
    ['a', 'X', 3],
    ['c', 'c'],
    [1, 2, 3]
  ],
  [
    [1, 3, 5],
    ['a', 'X'],
    ['c'],
    [2],
  ]
 ),
]

for tpl in tpl_lols:
    print("INPUT:")
    print(tpl[0], "\n")
    print("EXPECTED:")
    print(tpl[1], "\n\n")

    rm_dup_items(tpl[0])
    if [set(l) for l in tpl[0]] == [set(l) for l in tpl[1]]:
       print(" ++ SUCCESS!")
    else:
       print(" -- FAILURE")
    print("OUTPUT:")
    print(tpl[0], "\n\n")
