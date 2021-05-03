#!/usr/bin/env python3

"""

  Suppose we have the following directory structure where we are trying to
  import a module (pylib.py) from two directories up within our import.py script.

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    test_parent_parent_parent
        |
        + __init__.py
        + pylib.py
        + test_parent_parent
            |
            + test_parent
                |
                + import_test.py
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How can we do a "relative" import that is still portable?

Module contents:
$ cat test_parent_parent_parent/pylib.py

    +--------------------------------------------+
    | class SomeClass():                         |
    |     def __init__(self):                    |
    |        self.name = self.__class__.__name__ |
    |                                            |
    |    def say_hello(self):                    |
    |        print(f"Hello from {self.name}")    |
    +--------------------------------------------+

"""

import os
import sys


file = os.path.abspath(__file__)
dir = os.path.dirname(file)
parent = os.path.dirname(dir)
parent_parent = os.path.dirname(parent)
rootdir = os.path.abspath(parent_parent)
# If you like one-liners:
# rootir = os.path.abspath(os.path.dirname((os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(rootdir)


print(sys.path)
from pylib import SomeClass 

print( f"FILE={file}" )
print( f"DIR={dir}" )
print( f"PARENT={parent}" )
print( f"PARENT-PARENT={parent_parent}" )
print( f"ROOT={rootdir}" )

sc = SomeClass()
sc.say_hello()
