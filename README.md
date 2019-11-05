Python
=========

A random collection of python scripts, modules, and apps

/ LEARN
---------
Simple scripts to test/demonstrate some of the powerful, but trickier concepts in Python
- [listComprehension.py](https://github.com/bfanselow/Python/blob/master/LEARN/listComprehension.py)
- ``listSlicing.py``
- ``pandas_dataframe.py``

Fun Examples
------------

>List Comprehension: building a list of prime numbers up to 60. ([1 is NOT a prime number!](https://blogs.scientificamerican.com/roots-of-unity/why-isnt-1-a-prime-number/))

    >>> l_noprimes = [j for i in range(2,8) for j in range(2*i, 60, i)]
    >>> l_primes = [p for p in range(2,60) if p not in l_noprimes]
    >>> l_primes
    
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]



>List Slicing: reverse the order of a list with \[start:stop:step] => \[::-1]

    >>> sentance = 'This is a test sentance'
    >>> l_chars = list(sentance)
    >>> l_chars_reverse = l_chars[::-1]
    >>> l_chars_reverse
    ['e', 'c', 'n', 'a', 't', 'n', 'e', 's', ' ', 't', 's', 'e', 't', ' ', 'a', ' ', 's', 'i', ' ', 's', 'i', 'h', 'T']
    >>> rsentance = ' '.join(l_chars_reverse)
    >>> rsentance
    'e c n a t n e s   t s e t   a   s i   s i h T'

    >>> palindrome = 'step on no pets'
    >>> l_chars_reverse = list(palindrome)[::-1]
    >>> l_chars_reverse
    ['s', 't', 'e', 'p', ' ', 'o', 'n', ' ', 'n', 'o', ' ', 'p', 'e', 't', 's']
    >>> rsentance = ' '.join(l_chars_reverse)
    >>> rsentance
    's t e p   o n   n o   p e t s'
