# setdefault()
### Python’s setdefault() function basically allows you to short-circuit a check for dictionary key
```
>>> values = {'a': 5, 'b': 4, 'c': 1}
```

### Instead of this
```
>>> if 'd' not in values:
...    values['d'] = 0
... 
>>> values
{'a': 5, 'b': 4, 'c': 1, 'd': 0}
>>> 
>>> 
```

### we can just do this:
```
>>> values.setdefault('e', 0)
0
>>> values
{'a': 5, 'b': 4, 'c': 1, 'd': 0, 'e': 0}
```

### This becomes super useful when building dictionary “accumulators”, iterating over data that is used to accumulated in some way in a final dict, such that we’re having to check for the existence of a dict key multiple times
```
>>> data = [
...     {'a': 1},
...     {'b': 2},
...     {'a': 3},
...     {'c': 1},
...     {'a': 0},
...     {'c': 3},
...     {'a': 1},
... ]
>>> 
>>> # Get list of values for each key
>>> acc = {}
>>> data = [
...     {'key': 'a', 'value': 1},
...     {'key': 'b', 'value': 1},
...     {'key': 'a', 'value': 2},
...     {'key': 'c', 'value': 0},
...     {'key': 'a', 'value': 2},
...     {'key': 'b', 'value': 0},
...     {'key': 'c', 'value': 1},
...     {'key': 'b', 'value': 3},
... ]
>>> for d in data:
...     acc.setdefault(d['key'], []).append(d['value'])
... 
>>> acc
{'a': [1, 2, 2], 'b': [1, 0, 3], 'c': [0, 1]}
>>>
>>> # Get sum of values for each key
>>> sums = {}
>>> 
>>> for d in data:
...     sums[d['key']] = sums.setdefault(d['key'], 0) + d['value']
... 
>>> sums
{'a': 5, 'b': 4, 'c': 1}
```

### Another example - counting characters in a string
```
str = "the quick red fox jumped over the lazy brown dog"

for c in list(str):
     char_counts[c] = char_counts.setdefault(c, 0) + 1 

print(char_counts)
{'h': 3, 'e': 6, 'l': 4, 'o': 6, ' ': 10, 'w': 2, 'r': 4, 'd': 4, 't': 2, 'q': 1, 'u': 2, 'i': 1, 'c': 1, 'k': 1, 'f': 1, 'x': 1, 'j': 1, 'm': 1, 'p': 1, 'v': 1, 'a': 1, 'z': 1, 'y': 1, 'b': 1, 'n': 1, 'g': 1}
```

# defaultdict
### Using defaultdict is very similar, in that any time you try to access a non-existent key, a “factory function” which initializes all values, is used.
```
acc = deafultdict(<factory_function>)
```
### Factory functions take no arguments. They can be any of the built-in types (int, list, set, dict), custom-functions or lamda functions.

### In the second example above (summing all the values associated with a specific key), it’s probably simpler to use a defaultdict to initialize all values to zero.
```
from collections import defaultdict

sales_data = [
    {'region': 'North', 'sales': 150},
    {'region': 'South', 'sales': 200},
    {'region': 'North', 'sales': 75},
    {'region': 'West', 'sales': 300},
    {'region': 'South', 'sales': 120},
]

# Create a defaultdict that provides 0 as the default value for new keys
total_sales_dd = defaultdict(int)

for record in sales_data:
    region = record['region']
    sales = record['sales']
    
    # If 'region' doesn't exist, it is created with a value of 0,
    # then the sales value is added.
    total_sales_dd[region] += sales

print(dict(total_sales_dd)) # NOTE: have to convert a defaultdict back to regular dict for printing
{'North': 225, 'South': 320, 'West': 300}
```
