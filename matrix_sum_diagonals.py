"""
 Find a generic formula for calulcating the sum of the diagonal elements of an NxN matrix M

 Note:
  * I f len(M) is odd, the two diagnoals will cross on an element
    (which should not be counted twice).
  * I f len(M) is even, the two diagnoals will NOT cross on an element.

>>> M = [[1, 2, 3, 4, 0], [1, 1, 1, 1, 2], [1, 2, 2, 2, 4], [1, 9, 3, 1, 7], [6, 4, 6, 7, 1]]
>>> M
[[1, 2, 3, 4, 0], [1, 1, 1, 1, 2], [1, 2, 2, 2, 4], [1, 9, 3, 1, 7], [6, 4, 6, 7, 1]]

# [[1, 2, 3, 4, 0],
#  [1, 1, 1, 1, 2],
#  [1, 2, 2, 2, 4],
#  [1, 9, 3, 1, 7],
#  [6, 4, 6, 7, 1]]

# Identify diagonal matrix indices trom top-left to bottom right
>>> diagonal_idcs_tl_br = [(i,i) for i in range(len(M))]

# Identify diagonal matrix indices trom bottom-left to top right (ignoring center element which is already counted)
>>> diagonal_idcs_bl_tr = [(i,j) for i,j in zip(range(4,-1,-1), range(5)) if i != j ]

>>> diagonal_idcs_tl_br + diagonal_idcs_bl_tr
[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (4, 0), (3, 1), (1, 3), (0, 4)]

# All diagonal indices (counting each element only once)
>>> diagonal_idcs = diagonal_idcs_tl_br + diagonal_idcs_bl_tr

# Get values for these indices
>>> [M[i][j] for i,j in diagonal_idcs]
[1, 1, 2, 1, 1, 6, 9, 1, 0]

# Calculate sum of diagonal values
>>> sum([M[i][j] for i,j in diagonal_idcs])
22

"""

## Putting this all together as a function

def sum_matrix_diagonals(matrix):
    """Sum the values of the diagonal elements of a matrix
     Matrix must be symetrical.
     If size of matrix is odd, we must not double count the central element.
     Return the sum.
    """

    # Identify diagonal matrix indices trom top-left to bottom right
    diagonal_idcs_tl_br = [(i,i) for i in range(len(matrix))]

    # Identify diagonal matrix indices trom bottom-left to top right
    if len(matrix) % 2 == 0: # size is even
        diagonal_idcs_bl_tr = [(i,j) for i,j in zip(range(4,-1,-1), range(5)) ]
    else: # size is odd (must ignore central element)
        diagonal_idcs_bl_tr = [(i,j) for i,j in zip(range(4,-1,-1), range(5)) if i != j ]

    diagonal_idcs = diagonal_idcs_tl_br + diagonal_idcs_bl_tr
    diag_sum = sum([matrix[i][j] for i,j in diagonal_idcs])

    return diag_sum
