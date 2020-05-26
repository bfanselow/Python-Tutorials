"""
  primes.py

  Function to calaluate prime numbers (up to a limit)

"""
import math

def list_primes(stop, start=2):
  """ list all primes between an interval"""
  l_primes = []
  for num in range(start, stop+1):
    prime = False
    for i in range(2,num):
      if num % i == 0:
        break
      else:
        prime = True
    if prime: 
      l_primes.append(num)
  return l_primes 

def is_prime(n):
  if n < 2:
    return False
  for i in range(2, int(math.sqrt(n))+1):
    if n % i == 0:
      return False 
  return True 

def gen_prime(n):
    i = 2
    while i < n :
        prime = True # reset the prime variable before the inner loop
        for a in range(2, i):
            if i%a == 0:
                prime = False
                break
        if prime:    
            yield i
        i += 1 # don't forget to advance i

if __name__ == '__main__':

  end = 30
  print(list_primes(end)) 
  
