### Demystifying Python's class methods, static methods, and regular instance methods.


Consider the following class:
```
class Circle:
    def __init__(self, radius):
        self.pi = 3.14159
        self.radius = radius

    def area(self):
        return self.pi * self.radius**2

    def circumference(self):
        return 2*self.pi * self.radius
```
