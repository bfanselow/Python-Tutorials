#!/usr/bin/env python3

"""

 Given an array containing a list of integers, such that the full range has some missing numbers,
 find the missing numbers in the input array (i.e. gaps in the integer range).

 So, if the input is list: [ 3, 4, 5, 10, 1, 15, 14]
  the full range is: [1:15]
  and the full un-gapped list is: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
 Therefore, the missing numbers are: [2, 6, 7 ,8, 9, 11, 12 ,13]

"""

def find_missing_numbers(list_of_ints):
    sorted_ints = sorted(list_of_ints)
    uniq_sorted = set(sorted_ints)
    missing = []
    # print(f"RANGE: {sorted_ints[0]} -> {sorted_ints[-1]}")
    for i in range(sorted_ints[0], sorted_ints[-1]):
        if i not in uniq_sorted:
            missing.append(i)
    return missing


if __name__ == '__main__':
    input = [ 3, 4, 5, 10, 1, 15, 14]
    missing = find_missing_numbers(input)
    print(f"Input: {input}")
    print(f"Missing: {missing}")
