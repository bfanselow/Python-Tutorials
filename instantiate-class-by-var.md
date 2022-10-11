#### There are two simple ways to instantiate a  class using a variable name:
#### Suppose we have an ABC Fruit class a some concrete fruits child classes in the file **variable_class_name.py**

```
from abc import ABC


class Fruit(ABC):
    def __init__(self, msg):
        print(f"Instantiating fruit \"{self.__class__.__name__}\": {msg}")

class Strawberry(Fruit):
    def __init__(self, msg):
        super().__init__(msg)

class Apple(Fruit):
    def __init__(self, msg):
        super().__init__(msg)

class Orange(Fruit):
    def __init__(self, msg):
        super().__init__(msg)

```

#### Now we want to instantiate a specific fruit by a (string) name. One way to do this is with globals() - a function which returns the dictionary of current global symbol table. The Symbol table is a data structure which contains all necessary information about the program. These include variable names, methods, classes, etc. Therefore, ```globals()['Strawberry']``` will refer to the Strawberry class

```
from <some-lib> import Strawberry, Apple, Orange

for name in ['Strawberry', 'Apple', 'Orange']:
    fruit = globals()[name]('hello')

% python3 variable_class_name.py
  Instantiating fruit "Strawberry": hello
  Instantiating fruit "Apple": hello
  Instantiating fruit "Orange": hello
```

#### Another way to do this such that we can use an arbitrary variable name to reference the Class names, is to use Enum which maps a arbitrary name to its assocated Class

```
from enum import Enum
from <some-lib> import Strawberry, Apple, Orange

class FruitMap(Enum):
  strawberry = Strawberry
  apple = Apple
  orange = Orange

for name in ['strawberry', 'apple', 'orange']:
    fruit_class = FruitMap[name].value
    fruit = fruit_class('bonjour!')
```

#### The advantage with this approach is that we can use arbitrary names instead of having to use the Class names.
