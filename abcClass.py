#!/usr/bin/env python3

from abc import ABC, abstractmethod
 
class AbstractClassExample(ABC):
 
    def __init__(self, value):
        self.value = value
        super().__init__()
   
    # all methods decorated with abstractmethod must be implemented by child classes 
    @abstractmethod
    def do_something(self):
        pass

    # we can have a non-abstract method implemented here which the child classes can call
    def do_non_abstract(self):
        print(f"Inside {__class__.__name__} Parent Class. Initialized start-value={self.value}")
        


class DoAdd42(AbstractClassExample):

    def do_something(self):
        value = self.value + 42
        print(f"Inside {__class__.__name__} Child Class. value={value}")
        return value
    
class DoMul42(AbstractClassExample):
   
    def do_something(self):
        value = self.value * 42
        super().do_non_abstract()
        print(f"Inside {__class__.__name__} Child Class. value={value}")
        return value

my_num = 10
print(f"Start with num={my_num}")
x = DoAdd42(my_num)
y = DoMul42(my_num)

print(x.do_something())
print(y.do_something())
