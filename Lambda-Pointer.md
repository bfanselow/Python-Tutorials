### Functions are just objects in python and can be passed as an arg to other functions. This allows us do things like a function repeater:

```
>>> def repeat(func, count):
...     for _ in range(count):
...         func()
...
>>> def howdy():
...    print("Howdy partner!")
...

>>> howdy()
Howdy partner!
>>> repeat(howdy, 6)
Howdy partner!
Howdy partner!
Howdy partner!
Howdy partner!
Howdy partner!
Howdy partner!
```

### But waht if we want to pass an arg in the function that is being passed as an arg?

```
>>> def howdy(name="partner"):
...     print(f"Howdy {name}")
...
>>> howdy()
Howdy partner

>>> howdy('Bill')
Howdy Bill

>>> repeat(howdy, 6)
Howdy partner
Howdy partner
Howdy partner
Howdy partner
Howdy partner
Howdy partner
```

### This syntax won't work as you are passing the RETURN of the executed function, which is None in this case
```
>>> repeat(howdy('Bill'), 6)
Howdy Bill
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 3, in repeat
TypeError: 'NoneType' object is not callable
```

### SOLUTION: Use lambda
```
>>> repeat(lambda: howdy('Bill'), 6)
Howdy Bill
Howdy Bill
Howdy Bill
Howdy Bill
Howdy Bill
Howdy Bill
>>>
```

### NOTE: Could also use functools.partial
```
from functools import partial
repeat(partial(howdy, 'Bill'), 6)
```
