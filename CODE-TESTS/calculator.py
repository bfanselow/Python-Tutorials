
"""
 Implement a calculator function such that we can pass an operator and two numbers and get back the result

  >>> calculator('+', 2, 2)
  4
  >>> calculator('-', 5, 2)
  3
  >>> calculator('*', 5, 2)
  10
  >>> calculator('/', 6, 2)
  3.0

  What about edge cases (i.e. division by zero, etc.)?

"""

# One simple solution

def calculator(operator, x, y):
    return {
        '+': lambda: x + y,
        '-': lambda: x - y,
        '*': lambda: x * y,
        '/': lambda: x / y
    }.get(operator, lambda: None)()
