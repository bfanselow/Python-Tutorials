#!/usr/bin/env python3

"""

  Function wrapper, demonstrating how functions and their args can be passed (i.e. "callbacks")

"""


def func_wrapper(func, arglist):
   print(f"FUNC: {func}")
   print(f"ARGLIST: {arglist}")
   print("=======BEFORE=======")
   func(*arglist)
   print("=======AFTER=======")


def do_something(*args):
    for i,a in enumerate(args):
        print(f"doing-something {i}: {a}")

def test_wrapper():
    func_wrapper(do_something, ['a1', 'a2', 'a3', 'a4'])


if __name__ == '__main__':
    test_wrapper()
