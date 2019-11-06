Python
=========

A random collection of python scripts, modules, and apps

/ LEARN
---------
Simple scripts written for the purpose of learning and understanding python concepts, tools, tricks, etc.

* **Concepts**: some of the more powerful, but trickier concepts in Python.
  - ``args_kwargs.py``
  - ``list_comprehension.py``
  - ``list_slicing.py``
  - ``DecoratorDemos.py``
  
* **Tools**: simple tests of various tools/libs
  - ``numpy_demos.py``
  - ``pandas_dataframe.py``

Fun Samples
------------

List Comprehension: building a list of prime numbers up to 60. (BTW: [1 is NOT a prime number!](https://blogs.scientificamerican.com/roots-of-unity/why-isnt-1-a-prime-number/))

    >>> l_non_primes = [j for i in range(2,8) for j in range(2*i, 60, i)]
    >>> l_primes = [p for p in range(2,60) if p not in l_non_primes]
    >>> l_primes
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]



List Slicing: simple/quick way to reverse the order of a string with slice notation \[::-1]

    >>> palindrome = 'Step on no pets'
    >>> l_chars_reverse = list(palindrome)[::-1]
    >>> print(''.join(l_chars_reverse))
    'step on no petS'
    
![python](https://user-images.githubusercontent.com/24737190/68251048-94c15980-ffdf-11e9-97bd-98b4df9ee1fe.png)
