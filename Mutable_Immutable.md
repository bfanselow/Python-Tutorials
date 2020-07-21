# Mutable and Immutable Objects

### Identity   
An object's *identity* (equivelent to the object's memory address) in Python never changes once it has been created.
The identity of an object can be found with the **id()** function.
```
>>> s = 'abc'
>>> id(s)
139884406490368
```

The **is** operator can be used to compare the identity of objects
```
>>> s2 = s
>>> s2 is s
True
>>> id(s2)
139884406490368
```
### Immutable Objects (int, float, decimal, bool, string, tuple, and range)
We say that a Python object is immutable if its **identity* changes when we change its value
>>> a = '1234'
>>> id(a)
139884406490368
>>> a = '12345'
>>> id(a)
139884406490424   # we actually created a new object rather than modifying the original!

>>> N = 34
>>> id(N)
139884405705664
>>> N +=1
>>> N
35
>>> id(N)
139884405705696  # we actually created a new object rather than modifying the original!

### Mutable Objects  (list, dictionary, set and user-defined classes) 
We say that a Python object is mutable if we can change its value without changing its *identity*
>>> l = [1, 2, 3]
>>> id(l)
>>> l = [1, 2, 3]
>>> id(l)
139884406486664
>>> l.append(4)
>>> id(l)
139884406486664  # We changed the value of the object without changing its identity!


### Comparing an object's **value** vs the object's identity   
The **==** operator compares object values, not identities.
Notice the the difference between immutable and mutable objects
```
# Immutable object's with same value share the same identity
>>> s3 = 'abc'
>>> s == s3
True
>>> s is s3
True

# Mutable object's with the same value do not necessarily share the same identity
>>> l = [1,2,3]
>>> l1 = [1,2,3]
>>> l == l1
True
>>> l is l1
False
```

### Copying immutable objects
If we copy mutable objects, they have the same identity. However, when we change one of the copies, it does not change the other since the change actually created a new object as we saw above.
```
>>> s = 'abc'
>>> id(s)
139884407143312
>>> s1 = s
>>> id(s1)
139884407143312
>>> s1 = 'abcd'
>>> s
'abc'

# Notice, the value of s was not changed when we modified s1.
# That is because by changing s1's value, we actually changed its identity
>>> id(s1)
139884406490704
```


### Copying mutable objects   
Beware when using copying mutable objects as changing one changes both!
```
>>> l = [1, 2, 3]
>>> id(l)
139884406488136
>>> l1 = l

# By copying we create a new object with same identity

>>> id(l1)
139884406488136

# Change one changes BOTH since the change did not create a new object with different identity

>>> l.append(4)
>>> l1
[1, 2, 3, 4]
```

