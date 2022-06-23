#!/usr/bin/env python3

"""
 A context-manager is used for resource allocation in a "with" statement.
 When code reaches a "with" statement it allocates resources temporariliy. When
 the with statement blocks finsihes all the resources consumed by the with statement
 are relesed.

 A Context Manager requires two basic functions, __enter__() and __exit__().
 By defining these functions in a class we can use it alongside a "with" statement
 to provide optional resource allocation.


class CustomFileHandler():
    def __init__(self, fname, method):
        """Called when the object is instantiated"""
        print("I'm in contructor")
        self.file_obj = open(fname, method)
    def __enter__(self):
        """
        Called when the "with" statement is entered.
        The with statement will bind this method’s return value to the target(s) specified
        in the as clause of the statement, if any.
        """
        print("I'm in ENTER block")
        return self.file_obj
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this object (when the with block finishes)
        The parameters describe the exception that caused the context to be exited.
        If the context was exited without an exception, all three arguments will be None.
        If an exception is supplied, and the method wishes to suppress the exception
        (i.e., prevent it from being propagated), it should return a true value. Otherwise,
        the exception will be processed normally upon exit from this method.
        """
        print("I'm in EXIT block")
        self.file_obj.close()

with CustomFileHandler("some_file.txt", "w") as example:
  ######### read write statements #########
  print("I'm in WITH block")
  pass

# expected output:
#  I'm in contructor
#  I'm in ENTER block
#  I'm in WITH block
#  I'm in EXIT block

"""

# Implement the same pattern with @contextmanager decorator
#
#  * The section above the yield statement does what an __enter__() method does.
#  * The yield statement returns an iterator to the target in the with statements as clause.
#    At this stage, the control is passed to the with statement.
#  * The section below the yield statement does what an __exit__() method does.

from contextlib import contextmanager

@contextmanager
def myFileHandler(fname, method):
  print("This is the implicit ENTER block")
  my_file = open(fname, method)

  yield my_file

  print("This is the implicit EXIT block")
  my_file.close()


with myFileHandler("this_file.txt", "w") as example:
  ######### read write statements #########
  print("I'm in WITH block")
  pass
