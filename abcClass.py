#!/usr/bin/env python3

from abc import ABC, abstractmethod
 
class AbstractClassExample(ABC):
 
    def __init__(self, value):
        self.value = value
        print(f"Inside {__class__.__name__} Parent Class. Initialized start-value={self.value}")
   
    # all methods decorated with abstractmethod must be implemented by child classes 
    @abstractmethod
    def do_math(self):
        pass

    # we can have a non-abstract method implemented here which the child classes can call
    def do_non_abstract(self):
        print(f" +PARENT {__class__.__name__} Doing something non-abstract!")
        


class Add42(AbstractClassExample):
    def __init__(self, value):
        self.value = value
        print(f"Inside {__class__.__name__} Child Class. Initialized start-value={self.value}")
        super().__init__(value)

    def do_math(self):
        value = self.value + 42
        print(f" =CHILD {__class__.__name__} Doing math value={value}")
        return value
    
class Mul42(AbstractClassExample):
    def __init__(self, value):
        self.value = value
        print(f"Inside {__class__.__name__} Child Class. Initialized start-value={self.value}")
        super().__init__(value)
   
    def do_math(self):
        value = self.value * 42
        #super().do_non_abstract() # super() not need tho it is sometimes seen here in this context
        self.do_non_abstract()
        print(f" =CHILD {__class__.__name__} Doing math value={value}")
        return value

my_num = 10
print(f"Start with num={my_num}")
x = Add42(my_num)
y = Mul42(my_num)

print(x.do_math())
print(y.do_math())
