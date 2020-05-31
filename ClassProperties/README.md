## Class Properties, *Getters* and *Setters*

Getters (aka 'accessors') and setters (aka 'mutators') are used in most object oriented programming languages to ensure the principle of **data encapsulation**. In some languages using getters and setters to make all class attributes private is considered good practice. The Pythonic way to introduce class attributes is to make them public. If they will never (and must never) be used directly by users of the class then make them private (i.e. self.__attr).

The exception to this is when we have an attribute which has some constraints on what values it can have (or whose value is conditianl on other attributes).  We don't want to allow a public attribute to be set to a value that is not allowed.  In this scenario it can be helpful to make the attribute private and provide a setter() method.  
```
class Letter():

    def __init__(self,x):
        self.set_x(x)

    def get_x(self):
        return self.__x

    def set_x(self, x):
        if x < 0:
            self.__x = 0
        elif x > 1000:
            self.__x = 1000
        else:
            self.__x = x
```
However, what if this class had originally been designed to expose the "x" attribute publically and users are already accessing it directly:
```
>>>ltr = Letter(42)
>>>ltr.x = 100
```
How can we change our implementaion of the class without breaking the interface? Python offers class **property** method to handle this situration. The property() method returns an attribute as a class property. Every time x is accessed, it will pass through the get_x() method and every time it's value is changed it will pass through set_x(). Most importantly, for users of the class, properties are syntactically identical to ordinary attributes. Therefore, even attributes that were previously accessed directly can be made into properties.
```
class Letter:
    def __init__(self,x):
        self.set_x(x)

    def get_x(self):
        return self.__x

    def set_x(self, x):
        if x < 0:
            self.__x = 0
        elif x > 1000:

    x = property(get_x, set_x)

>>>ltr = Letter(42)
>>>ltr.x = 1005
>>>ltr.x
1000
```
A more Python way to do this, so that we don't provide two different ways of accessing x (either direct or via get_x()), is to make the getter and setter private: __get_x() and __set_x(). An even more Pythonic (and more compact) way of doing this same thing is with the @property decorator. 
```
class Letter:
    def __init__(self,x):
        self.x = x

    @property
    def x(self):
        return self.__x
    @x.setter
    def x(self, x):
        if x < 0:
            self.__x = 0
        elif x > 1000:
            self.__x = 1000
        else:
            self.__x = x
```
#### When to use class properties
Suppose we are building a new class with an attribute **X**:

Will the value of **X** be needed by any of the users of out class?
  * If not, we can (and should) make it a private attribute to keep things as simple as possible.
  * If it's value has to be accessed, we should make it accessible as a public attribute.
    We will define it as a private attribute with the corresponding property, if and only if there are value contraints such that we have to perform checks or transformation of the data.
