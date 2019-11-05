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


>List Slicing using (start:stop:step) syntax: reverse the order of a list with \[::-1]
