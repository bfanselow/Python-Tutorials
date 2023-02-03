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

The class attribute can be accessed from the class itself, as opposed to the instance attribute can only be accessed on an *instance* of the class. When you access an attribute via an instance of the class, Python searches for the attribute in the instance attribute list. If the instance attribute list doesn’t have that attribute, Python continues looking up the attribute in the class attribute list. Python classes and instances of classes each have their own distinct namespaces represented by the pre-defined attributes MyClass.__dict__ and instance_of_MyClass.__dict__, respectively. When you try to access Python attributes from an instance of a class, it first looks at its instance namespace. If it finds the attribute, it returns the associated value. If not, it then looks in the class namespace and returns the attribute (if it’s present, otherwise throwing an error).

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
**Instance Methods**
The first method on MyClass, called method, is a regular instance method. That’s the basic, no-frills method type you’ll use most of the time. You can see the method takes one parameter, self, which points to an instance of MyClass when the method is called (but of course instance methods can accept more than just one parameter).

Through the self parameter, instance methods can freely access attributes and other methods on the same object. This gives them a lot of power when it comes to modifying an object’s state.

Not only can they modify object state, instance methods can also access the class itself through the self.__class__ attribute. This means instance methods can also modify class state.

**Class Methods**
Let’s compare that to the second method,  MyClass.classmethod. I marked this method with a @classmethod decorator to flag it as a class method.

Instead of accepting a self parameter, class methods take a cls parameter that points to the class—and not the object instance—when the method is called.

Because the class method only has access to this cls argument, it can’t modify object instance state. That would require access to self. However, class methods can still modify class state that applies across all instances of the class.

**Static Methods**
The third method, MyClass.staticmethod was marked with a @staticmethod decorator to flag it as a static method.

This type of method takes neither a self nor a cls parameter (but of course it’s free to accept an arbitrary number of other parameters).

Therefore a static method can neither modify object state nor class state. Static methods are restricted in what data they can access - and they’re primarily a way to namespace your methods.


Which type of method to use is often just a good way to communicate something about the method.  Both static and class methods communicate that the method is essentailly unrelated to any specific instance of the class.  However, a static method further communicates that the method does not involve any data related to the class.  Class methods are a nice and clean way to provide for "factory functions".
```
import math
class Pizza:
    def __init__(self, ingredients):
        self.ingredients = ingredients

    def __repr__(self):
        return f'Pizza({self.ingredients!r})'

    def cook(self):
        # refulat "instance" method: cook the pizza
        pass

    @classmethod
    def margherita(cls):
        return cls(['mozzarella', 'tomatoes'])

    @classmethod
    def prosciutto(cls):
        return cls(['mozzarella', 'tomatoes', 'ham'])
        
    @staticmethod
    def circle_area(r):
        # circle "area" is not specific to "pizza"!
        return r ** 2 * math.pi
```

```
>>> Pizza.margherita()
Pizza(['mozzarella', 'tomatoes'])

>>> Pizza.prosciutto()
Pizza(['mozzarella', 'tomatoes', 'ham'])
```
