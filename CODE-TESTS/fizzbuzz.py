"""

 Problem:
   Write a function which converts numbers according to the following logic
   * If N is evenly divisiable by 3, map to "fizz"
   * If N is evenly divisiable by 5, map to "buzz"
   * If N is evenly divisiable by both 3 and 5, map to "fizzbuzz"

  Example:
  >>> l_numbers = [1,2,3,4,5,6,7,8,9,10,12,15,22,30]
  >>> fizz_buzz(l_numbers)
  [1, 2, 'fizz', 4, 'buzz', 'fizz', 7, 8, 'fizz', 'buzz', 'fizz', 'fizzbuzz', 22, 'fizzbuzz']

"""

def fizz_buzz(l_numbers):

  l_fb = []
  for n in l_numbers:
    if (n % 3 == 0) and (n % 5 == 0):
      N = 'fizzbuzz' 
    elif n % 3 == 0:
      N = 'fizz' 
    elif n % 5 == 0:
      N = 'buzz' 
    else:
      N = n
    l_fb.append(N)
  return(l_fb)

if __name__ == '__main__':
  numbers = [1,2,3,4,5,6,7,8,9,10]
  m = fizz_buzz(numbers)
  print(m)
