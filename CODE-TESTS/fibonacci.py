"""

  fibonacci.py

  ## [ 0, 1, 1, 2, 3, 5, 8, 13,21]

"""
import time

def get_nth_fib(n):
  """ expensive version """
  if n < 2:
    return n
  fib_nums = [0,1]
  for i in range(2,n+1):
    fib = fib_nums[i-1] + fib_nums[i-2]
    fib_nums.append(fib)
  return fib_nums[n]

def fib_generator(n):
  """ generator version """
  a, b = 0, 1
  for _ in range(n+1):
    yield a
    a, b = b, a + b

if __name__ == '__main__':
  MAX = 20
  ## expensive
  ts1 = time.perf_counter()
  for i in range(MAX):
    print("N=%d: %d" % (i, get_nth_fib(i)))
  ts2 = time.perf_counter()
  print("ELAPSED=%f" % (ts2-ts1))
    
  ## generator 
  ts1 = time.perf_counter()
  for i in range(MAX):
    print(list(fib_generator(i)))
  ts2 = time.perf_counter()
  print("ELAPSED=%f" % (ts2-ts1), end="\n")
