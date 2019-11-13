"""

 Demonstating a custom Excpetion which handles args


"""

class MyException(BaseException):
    pass

class NonPositiveIntegerError(MyException):
    def __init__(self, x, y):
        super(NonPositiveIntegerError, self).__init__()
        if x<=0 and y<=0:
            self.msg = 'Unsupported negative values for both x and y: x={}, y={}'.format(x, y)
        elif x<=0:
            self.msg = 'Unsupported negative value for x: x={}'.format(x)
        elif y<=0:
            self.msg = 'Unsupported negative value for y: y={}'.format(y)

    def __str__(self):
        return self.msg


if __name__ == "__main__":

  def average(x, y):
    if x<=0 or y<=0:
      raise NonPositiveIntegerError(x, y)
    return (x+y)/2

  try:
    average(-3, 1)
  except MyException as e:
    print(e)
  try:
    average(1, -1)
  except MyException as e:
    print(e)
  try:
    average(-2, -1)
  except MyException as e:
    print(e)
