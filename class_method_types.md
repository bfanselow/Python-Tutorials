## Demystifying Python's class vs instance variables, and class-methods vs instance-methods vs static_methods:


#### Class vs instance attributes
Consider the following class:
```
import math

class Circle:
    def __init__(self, radius):
        self.pi = math.pi
        self.radius = radius

    def area(self):
        return self.pi * self.radius**2

    def circumference(self):
        return 2*self.pi * self.radius
```
Here, both *pi* and *radius* are defined as an *instance* attributes. They belong to a specific instance of the Circle class. If you change the attributes of an instance, it won’t affect other instances.

Alternatively, let's define *pi* as a class attribute:
```
import math

class Circle:
    pi = math.pi

    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return pi * self.radius**2

    def circumference(self):
        return 2*pi * self.radius
```

The class attribute can be accessed from the class itself, as opposed to the instance attribute can only be accessed on an *instance* of the class.
When you access an attribute via an instance of the class, Python searches for the attribute in the instance attribute list. If the instance attribute list doesn’t have that attribute, Python continues looking up the attribute in the class attribute list.

```
>>> from my_class import Circle, MyClass
>>>
>>>
>>>
>>> Circle.pi
3.141592653589793
>>> Circle.radius
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: type object 'Circle' has no attribute 'radius'
>>>
>>> c = Circle(3)
>>> c.pi
3.141592653589793
>>> c.radius
3
```

### Which is better?
On the surface, both approaches can be nearly equivelent functionally.  Using instance attributes for all attributes works just fine in most cases.
Using the *class attribute* approach can be useful simply to communicate the something about the attribute. For example, class attributes are useful for storing class *constants*, as a way of communicating that this constant is independent of any instance, such as *pi*. It also allows access to the attribute without needing to instantiate the class.

```
$ Circle().pi
3.141592653589793
```

### WARNING
When using class attributes, you should be very mindful of mutable (list, dict, set, class) vs immutable variables.  In nearly all cases, you should NOT use mutable attributes as a class attribute:
```
import math
class Circle:
    pi = math.pi
    some_data = []  # <== very dangerous!!

    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return pi * self.radius**2

    def circumference(self):
        return 2*pi * self.radius
```

The issue here is that changing the attribute will affect ALL instances of the class (even if those that were instantiated BEFORE the change), which is typically NOT what you want.

```
>>> c1 = Circle(1)
>>> c2 = Circle(2)
>>> c1.radius = 3
>>> c2.radius
2
# ^^^ other instances not affected

>>> c1.pi = 3.4
>>> c2.pi
3.141592653589793
# ^^^ other instances not affected

>>> c2.some_data.extend(0,1,2,3)
>>> c1.some_data
[0,1,2,3]
# ^^^ other instances are affected!

>>> Circle.some_data
[0,1,2,3]
# ^^^ generic class is affected!


### Class-methods vs static-methods vs instance-methods
