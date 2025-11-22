#!/usr/bin/env python3

"""

 Create a N x M matrix of monotonically increasing values

=======5x5=========
[[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20], [21, 22, 23, 24, 25]]
=======3x7=========
[[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18], [19, 20, 21]]
=======5x4=========
[[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20]]

"""

def create_matrix(row_count, col_count):
    matrix = []
    sublist = []
    num_items = row_count * col_count
    for i in range(num_items):
        sublist.append(i+1)
        if (i+1) % row_count == 0:
            matrix.append(sublist)
            sublist = []
    return matrix

print("=======5x5=========")
print(create_matrix(5,5))

print("=======3x7=========")
print(create_matrix(3,7))

print("=======5x4=========")
print(create_matrix(5,4))
