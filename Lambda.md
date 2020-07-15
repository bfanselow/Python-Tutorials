## Fun with lambda functions
---

#### Silence the print function.
 * You’re not redefining print() - you’re defining another print() that shadows the built-in one. 
 * To return to using the original print(),  delete your custom one with **del print**.
```
>>> print = lambda *args, **kwargs: None
>>> print("hello")
>>> del print
>>> print("hello")
```

Or turn it into a grumpy arse:
>>>
>>> print = lambda *args, **kwargs: "shutup!"
>>> print("hello")
'shutup!'
```
