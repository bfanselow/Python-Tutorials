#!/usr/bin/env python3

""" 
 Quick demo of using list slice notation: [start:stop:step]
 
 Selection of items goes from "start" index up to (but NOT including) "stop" index in increments of "step". 
  * default start=0 if start is None.
  * default step=1 if step is None.
  * negative start, stop can be used in same way but index is counted from "tail" of list.
  * negative step can be used in same way but implies stepping in reverse (right-to-left).  
"""

l_nums = [10, 20, 30, 40, 50, 60, 70, 80, 90]
print("\n\n========================================================")
print("LIST-SLICING DEMO")
print(" Number-List: %s" % (str(l_nums)))
print("========================================================\n")

print("Select a subset of the numbers: [2:7]")
l_subset = l_nums[2:7]
print(" %s\n" % l_subset)

print("Select the third-to-last number: [-3]") 
n = l_nums[-3]
print(" %s\n" % n)

print("Select the last 3 numbers: [-3:]") 
l_subset = l_nums[-3:]
print(" %s\n" % l_subset)

print("Select every 3rd number: [::3]") 
l_subset = l_nums[::3]
print(" %s\n" % l_subset)

print("Select a subset of 2 numbers using negative start/stop: [-3:-1]")
l_subset = l_nums[-3:-1]
print(" %s\n" % l_subset)

print("Select the last 5 numbers, but skip every other one: [-5::2]") 
l_subset = l_nums[-5::2]
print(" %s\n" % l_subset)

print("Reverse the number list: [::-1]")
l_subset = l_nums[::-1]
print(" %s\n" % l_subset)

print("Select \"last\" 3 numbers of the reversed list: [:-4:-1]")
l_subset = l_nums[:-4:-1]
print(" %s\n" % l_subset)

print("Reverse a string:  list(<string>)[::-1]")
sentance = 'This is a test sentance'
print(" " + sentance)
l_chars = list(sentance)
l_chars_reverse = l_chars[::-1]
l_chars_reverse
print(" " + ''.join(l_chars_reverse), end="\n\n")

print("Reverse a palindrome string:  list(<string>)[::-1]")
palindrome = 'Step on no pets'
print(" " + palindrome)
l_chars_reverse = list(palindrome)[::-1]
l_chars_reverse
print(" " + ''.join(l_chars_reverse), end="\n\n")

