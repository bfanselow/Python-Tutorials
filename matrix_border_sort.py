"""
 Problem: Given an R x C Matix (R-rows)x(C-columns), write an algorithm to sort the border elements
   only in clockwise order.


 Example:
  M = [[1, 2, 3, 4, 0], [1,1,1,1,2], [1,2,2,2,4], [1,9,3,1,7]]
  # [[1, 2, 3, 4, 0],
     [1, 1, 1, 1, 2],
     [1, 2, 2, 2, 4],
     [1, 9, 3, 1, 7]]

  Clockwise border elements are: [1, 2, 3, 4, 0, 2, 4, 7, 1, 3, 9, 1, 1, 1]
  Sorting these results in: [0, 1, 1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 7, 9],
  Now, positioning these sorted elements back into Matrix border in clockwise direction
  results in new martix:
   [[0, 1, 1, 1, 1]
    [9, 1, 1, 1, 1
    [7, 2, 2, 2, 2
    [4, 4, 3, 3, 2]]


## Soltuion:

## First we use a specific matix and then create a generic solution

## Matrix
>>> M = [[1, 2, 3, 4, 0], [1,1,1,1,2], [1,2,2,2,4], [1,9,3,1,7]]

## Clockwise, border indices
>>> border_idcs = [(0,0), (0,1), (0,2), (0,3), (0,4), (1,4), (2,4), (3,4), (3,3), (3,2), (3,1), (3,0), (2,0), (1,0)]

## Clockwise border values
>>> border_vals = [M[i][j] for i,j in border_idcs]

## Zip togther the clockwise border indices and (sorted) border values
>>> d = dict(zip(border_idcs, sorted(border_vals)))
>>> d
{(0, 0): 0, (0, 1): 1, (0, 2): 1, (0, 3): 1, (0, 4): 1, (1, 4): 1, (2, 4): 2, (3, 4): 2, (3, 3): 3, (3, 2): 3, (3, 1): 4, (3, 0): 4, (2, 0): 7, (1, 0): 9}

## Now reset the border values in clockwise order using the sorted values
>>> for t_idx, v in d.items():
...     M[t_idx[0]][t_idx[1]] = v
...
>>> M
[[0, 1, 1, 1, 1], [9, 1, 1, 1, 1], [7, 2, 2, 2, 2], [4, 4, 3, 3, 2]]


## Now, to our generic case
>>> C = 5 # columns
>>> R = 4 # rows

## Clockwise border indeces can be identified generically for any C, R as:

>>>border_idcs = [(0,i) for i in range(5)] + [(i, C-1) for i in range(1,R-1)] + [(R, i) for i in range(0,C-1,-1)] + [(R-1, i) for i in range(C-1,-1,-1)] + [ (i,0) for i in range(R-1,0,-1) ]
>>>border_idcs
[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4), (3, 3), (3, 2), (3, 1), (3, 0), (3, 0), (2, 0), (1, 0)]

## Given any R x C martix, clockwise border values can be expressed as:
>>> border_vals = [M[i][j] for i,j in border_idcs]

## Zip togther the clockwise border indices and (sorted) border values
>>> d = dict(zip(border_idcs, sorted(border_vals)))

## Now reset the border values in clockwise order using the sorted values
>>> for t_idx, v in d.items():
...     M[t_idx[0]][t_idx[1]] = v
...

"""

## So, a generic matrix-border-sort function could look like this:

def matrix_border_sort(matrix):
    """ Perfrom clockwise sort of matrix border elements"""

    print("BEFORE: %s\n" % (matrix))

    R = len(matrix)
    C = len(matrix[0])
    border_idcs = [(0,i) for i in range(5)] + [(i, C-1) for i in range(1,R-1)] + [(R, i) for i in range(0,C-1,-1)] + [(R-1, i) for i in range(C-1,-1,-1)] + [ (i,0) for i in range(R-1,0,-1) ]
    border_vals = [matrix[i][j] for i,j in border_idcs]
    d = dict(zip(border_idcs, sorted(border_vals)))
    for t_idx, v in d.items():
        matrix[t_idx[0]][t_idx[1]] = v
    # don't need to return matrix as list are pass by value

    print("AFTER: %s\n" % (matrix))
