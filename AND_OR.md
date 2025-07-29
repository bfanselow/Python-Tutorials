## OR expressions

#### These are intuitive
```
>>> False or False
False
>>> True or True
True
>>> True or False
True
>>> False or True
True
```

#### But, the operends on each side of the and/or do not need to be Boolean objects. Every Python object is either *truthy* or *falsy*. When you pass a *truthy* object to the built-in bool(), you get True. When you pass a *falsey* object to bool(), you get False. When evaulating expressions, Python will use the object's truthiness value if the object isn't a Boolean.
```
>>> 1 or 0
1
>>> 0 or 1
1
>>> 1 or 'a'
1
>>> 1 or ''
1
>>> '' or 1
1
>>> '' or 0
0
```
## WAIT! What happened on this last one?  That's not so intuitive!
#### When Python evaluates an OR expression, it only needs one of them to be true (truthy) for the whole expression to be true (truthy). Python also does "lazy evaulation" or short-circuiting. Python first looks at the first operand. If it's truthy, so OR expression simply gives back this value. It doesn't need to bother with the second operand - Python only needs one operand to be truthy. But what if the first operand is falsy, as in the last two examples ('' or 1, '' or 0)?  In both cases, the first operend is falsy, so the OR expression must look at the second operend. In the second-to-last case ('' or 1) the second operend is truthy and the OR expression returns a truthy value. However, the OR expression doesn't return the second operand because the second operand is truthy. This is critical! It's returning the second operand because the first operand is falsy. When the first operand in an OR expression is falsy, the result of the expression is entirely determined by the second operand. If the second operand is truthy, then the OR expression is truthy. But if the second operand is falsy, the whole OR expression is falsy.

#### This can be summarized with two rules for OR expressions:
* or always evaluates to the first operand when the first operand is truthy
* or always evaluates to the second operand when the first operand is falsy

#### What about this?
```
1 or 5/0
>>> 1
```

#### WTF!?  Shouldn't this raise ZeroDivisionError?  Recall "lazy evaluation"?   Python doesn't even look at the second operend when the first is truthy.  You want to see the ZeroDivisionError?
```
>>> '' or 1/0
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ZeroDivisionError: division by zero
```












