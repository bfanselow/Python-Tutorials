### What’s the problem with this function?

```
def add_item(name, item_list=[]):
    # print(f">>Initial-item-list: {item_list}")
    item_list.append(name)
    # print(f"++NEW: {item_list}")
    return item_list

>>> list1 = add_item("apple", ["grape"])
>>Initial-item-list: [‘grape']
++NEW: ['grape', 'apple']
>>> list1
['grape', 'apple']
>>> 
>>> list1 = add_item("apple", ["grape"])
>>Initial-item-list: [‘grape']
++NEW: ['grape', 'apple']
>>> 
>>> list1
['grape', 'apple']
```

### So, what’s the problem? Seems to work great, every time!
### What happens when we don’t pass item_list to the method?

```
>>> list2 = add_item("apple")
>>Initial-item-list: []
++NEW: ['apple']
>>> list2
['apple']
>>> 
>>> 
>>> list3 = add_item("apple")
>>Initial-item-list: [‘apple']
++NEW: ['apple', 'apple']
>>> 
>>> list3
['apple', 'apple']
>>> list2
['apple', 'apple']
```

Yikes! What’s going on here?

In this case, the default value is used.  However, in Python, default arguments are evaluated ONLY ONCE when the function is defined, NOT each time the function is called.

That means if you use a mutable data type (such as list or dict) as a default value, the value can be different each time the function is called.

This can be demonstrated by NOT passing the item_list, such that the default value is used.
