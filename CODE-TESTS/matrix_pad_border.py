"""

 Problem:  Given an NxM martrix, construct an algorthim to pad the entire outside of the
           matrix with zeros

 Example:  Given Matrix
   M = [[1,3,5,6,7],
        [5,3,7,6,9],
        [8,2,9,9,6],
        [4,3,9,1,5]]

 Padded result is an (N+2)x(M+2) matrix which looks like:

  PM = [[0,0,0,0,0,0,0],
        [0,1,3,5,6,7,0],
        [0,5,3,7,6,9,0],
        [0,8,2,9,9,6,0],
        [0,4,3,9,1,5,0]]
        [0,0,0,0,0,0,0]]


>>> M = [[1, 3, 5, 6, 7], [5, 3, 7, 6, 9], [8, 2, 9, 9, 6], [4, 3, 9, 1, 5] ]

# Pad top and bottom with an list of zeros of length len(M[]) + 2
>>>[0]*(len(M[0])+2)
[0,0,0,0,0,0,0]

## Pad each sub-list in M with a zero and start and end
>>>[ [0, *M[i], 0] for i in range(len(M)) ]
[[0, 1, 3, 5, 6, 7, 0], [0, 5, 3, 7, 6, 9, 0], [0, 8, 2, 9, 9, 6, 0], [0, 4, 3, 9, 1, 5, 0]]

# Put it all together
>>> [[0]*(len(M[0])+2), *[ [0, *M[i], 0] for i in range(len(M)) ], [0]*(len(M[0])+2)]
[[0, 0, 0, 0, 0, 0, 0], [0, 1, 3, 5, 6, 7, 0], [0, 5, 3, 7, 6, 9, 0], [0, 8, 2, 9, 9, 6, 0], [0, 4, 3, 9, 1, 5, 0], [0, 0, 0, 0, 0, 0, 0]]


## Using function below
>>> from matrix_pad_border import pad_matrix_border
>>> M = [[1, 3, 5, 6, 7], [5, 3, 7, 6, 9], [8, 2, 9, 9, 6], [4, 3, 9, 1, 5] ]
>>> pad_matrix_border(M,'x')
BEFORE: [[1, 3, 5, 6, 7], [5, 3, 7, 6, 9], [8, 2, 9, 9, 6], [4, 3, 9, 1, 5]]
AFTER: [['x', 'x', 'x', 'x', 'x', 'x', 'x'], ['x', 1, 3, 5, 6, 7, 'x'], ['x', 5, 3, 7, 6, 9, 'x'], ['x', 8, 2, 9, 9, 6, 'x'], ['x', 4, 3, 9, 1, 5, 'x'], ['x', 'x', 'x', 'x', 'x', 'x', 'x']]
[['x', 'x', 'x', 'x', 'x', 'x', 'x'], ['x', 1, 3, 5, 6, 7, 'x'], ['x', 5, 3, 7, 6, 9, 'x'], ['x', 8, 2, 9, 9, 6, 'x'], ['x', 4, 3, 9, 1, 5, 'x'], ['x', 'x', 'x', 'x', 'x', 'x', 'x']]

# Try a single element "matrix"
>>> pad_matrix_border('1')
BEFORE: 1
AFTER: [[0, 0, 0], [0, '1', 0], [0, 0, 0]]
[[0, 0, 0], [0, '1', 0], [0, 0, 0]]
>>>


"""

def pad_matrix_border(matrix, pad_char=0):
    """ Pad the border of a matrix with character <pad_char>
     Returns: new padded matrix
    """
    print("BEFORE: %s" % (matrix))
    padded_matrix = [[pad_char]*(len(matrix[0])+2), *[ [pad_char, *matrix[i], pad_char] for i in range(len(matrix)) ], [pad_char]*(len(matrix[0])+2)]
    print("AFTER: %s" % (padded_matrix))
    return padded_matrix
