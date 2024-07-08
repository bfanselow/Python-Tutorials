# Python Generators

## Summary
A generator is a function that returns an iterator that produces a sequence of values when iterated over. Generators are useful when we want to produce a large sequence of values, but we don't want to store all of them in memory at once. A Generator function is defined just like a regular function, using the *def* keyword, but instead of a *return* statement it uses the *yield* statement.
```
def generator_name(arg):
    # statements
    yield something
```
When the generator function is called, it does not execute the function body immediately. Instead, the generator function returns a "generator object" (of type "iterator") which supports the iteration protocol methods - automatically supporting a \_\_next\_\_() method..  You can loop over the generator object with __next__() like a list. However, unlike lists, these "lazy iterators" do not store their contents in memory.  You only compute the next value when required. This makes generators memory and compute efficient; they refrain from saving long sequences in memory or doing all expensive computations upfront. On encountering the yield statement, the iterator returns the provided value and suspends the function's execution, preserving all local variables. Execution resumes on the following call to the iterator's next() method, picking up after the yield statement.

**Examples:**
```
>>> def letters_gen(word):
...    for c in word:
...        yield c

>>> gen = letters_gen('hello')
>>> next(gen)
'h'
>>> next(gen)
'e'
>>> next(gen)
'l'
>>> next(gen)
'l'
>>> next(gen)
'o'
>>> next(gen)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

```
def double_gen(n):
    for x in range(n):
        a = 2 * x
        yield a
        print(f"last value: {a}", end=', ')

gen = double_gen(3)

print(f"curr value: {next(gen)}") 
# curr value: 0
print(f"curr value: {next(gen)}") 
# last value: 0, curr value: 2
print(f"curr value: {next(gen)}") 
# last value: 2, curr value: 4
print(f"curr value: {next(gen)}") 
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# StopIteration
# last value: 4,
```

```
def power_two_gen(max=0):
    n = 0
    while n < max:
        yield 2 ** n
        n += 1
```


Generators can also be written as **expressions** with a syntax similar to list comprehensions.  Whereas list comprehensions return full lists, generator expressions return generators. Generators work the same whether they’re built from a function or an expression. Using an expression syntax allows you to define simple generators in a single line, with an assumed yield at the end of each inner iteration.


**Example:**
```
>>> squares_generator = (i * i for i in range(5))
>>> squares_generator
<generator object <genexpr> at 0x7fc84808ff90>
>>> for i in squares_generator
...     print(i)
...
0
1
4
9
16
```
---

## When to use Generators

### Handling large data streams or files
One common use case of generators is to work with data streams or large files, for example handling large CSV files.
What if you wanted to know the number of rows in a CSV file? You might write something like this: 
```
def csv_reader(file_name):
    file = open(file_name)
    result = file.read().split("\n")
    return( result )

csv_gen = csv_reader("huge_csv.txt")
row_count = 0
for row in csv_gen:
    row_count += 1
print("Row count is: %d" % (row_count))
```

However, what if the file is larger than your system's available memory? Even though *open()* returns a generator object (which you can lazily iterate through line by line), *file.read().split()* loads everything into memory causing a MemoryError() exception.  

This is one scenario where Python Generators can be extremely useful.  
Consider a new csv_reader() function:
```
def csv_reader(file_name):
    for row in open(file_name, "r"):
        yield row
```
This code will produce the correct result with no memory errors. You’ve turned csv_reader() into a generator function. 
It opens a file, loops through each line, and "yields" each row, rather than returning it.
The keyword **yield** indicates where a value is sent back to the caller just like "return". However unlike return, you don’t exit the function afterward.  Instead, the state of the function is remembered so that when next() is called on the generator object, the next iterable result is yielded.


### Creating infinite sequences
Another common use case for generators is for generating an infinite sequence. The function range(12) provides a finite sequence. However, to get an inifite sequence, Generators are required.

**Example:**
```
def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1
```

Try this function in a for loop to demonstrate that it is, in fact, infinite. It continue to execute until you stop it manually. 
```
>>> for i in infinite_sequence():
...     print(i, end=" ")
...
0 1 2 3 4 5 6 7 8 9 10
[...]
1004 1005 1006
KeyboardInterrupt
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
``` 

Or try calling __next__() on the generator object directly on the console (useful for testing a generator):
```
>>>
>>> from examples import infinite_sequence
>>> gen = infinite_sequence()
>>> gen.__next__()
0
>>> gen.__next__()
1
>>> gen.__next__()
2
>>> gen.__next__()
3
>>> gen.__next__()
4
```
An alternative syntax can also be used: next(gen) just calls gen.\_\_next\_\_()
```
>>> next(gen)
0
>>> next(gen)
1
>>> next(gen)
2
```
---

## Generator Details

When you call **next()** on a generator, the code within the function is executed up to yield.  When the Python yield statement is hit, the program suspends function execution and returns the yielded value. (In contrast, return stops function execution completely.) When a function is suspended, the "state" of that function is saved. This includes any variable bindings local to the generator, the instruction pointer, the internal stack, and any exception handling.  This allows you to resume function execution whenever you call one of the generator’s methods. In this way, all function evaluation picks back up right after yield. This can be demonstrated by using multiple Python yield statements:
```
def multi_yield():
    yield_1 = "This is result of first yield"
    yield yield_1
    yield_2 = "This is result of second yield"
    yield 2 

>>> from examples import multi_yield
>>> gen = multi_yield()
>>> print(next(gen))
This is result of first yield 
>>> print(next(gen))
This is result of second yield 
>>> print(next(gen))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```
---

## Generators used to define Context-Managers
Context managers are objects that define a context in which to perform a set of operations. Context managers can be defined by generators using the *@contextmanager* decorator, in which case, the *yield* keyword used in generator acts more like a separator between the code for entering and exiting the context manager.
**Example**
```
from contextlib import contextmanager

@contextmanager
def file_opener(filename, mode):
    try:
        # enter context manager
        f = open(filename, mode)
        yield f
        # exit context manager
    finally:
        f.close()

with file_opener("hello_world.txt", "w") as f:
    f.write("Hello World")
```
Here have defined a file_opener() context manager using the @contextmanager decorator. The file_opener function is a generator function that yields a file object. The *try* block opens the file. The yield statement produces the file object, and temporarily suspends the generator function, allowing the calling code to resume execution. The calling code can use the file object to read or write data to the file. The finally block ensures that the file is closed properly when the context is exited, even if an exception is raised during execution.

NOTE: You may also see the *yield* statement show up in other contexts, for example: coroutines, and asynchronous programming.


```
---

A generator object exposes some other methods that can be invoked to manipulate the generator. 
 * **send()**
 * **throw()**
 * **close()**

These additional methods turn generators from one-way producers of information into both producers and consumers.

### send()
The **yield** statement is actually an expression which returns a value that can be assigned to a variable or otherwise operated on:
val = (yield i). Values are sent into a generator by calling its send(value) method. The generator's code is then resumed and the yield expression returns the specified value. If the regular next() method is called, the yield returns None.
```
def gen_counter_with_send(max):
    i = 0
    while i < max:
        val = (yield i)
        # If value provided via send(), change counter
        if val is not None:
            i = val
        else:
            i += 1

>>> from examples import gen_counter_with_send
>>> gen = gen_counter_with_send(10)
>>> next(gen)
0
>>> next(gen)
1
>>> next(gen)
2
>>> gen.send(7)
7
>>> next(gen)
8
>>> next(gen)
9
>>> next(gen)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

### throw() 
throw() allows you to throw exceptions with the generator.  Here is test of send() and throw()

### close() 
Calling close() is roughly equivalent to throw(GeneratorExit()). As its name suggests, it can be used to terminate the iteration.

**Example of send() and throw()**
```
>>> from examples import talk_gen
>>> gen = talk_gen('Bill')
>>> next(gen)
'Hi there Bill'
>>> next(gen)
'How are you Bill?'
>>> next(gen)
'Bye-bye Bill'
>>> next(gen)
'Hi there Bill'
>>> gen.send('jack')
'How are you jack?'
>>> next(gen)
'Bye-bye jack'
>>> next(gen)
'Hi there jack'
>>> gen.throw(ValueError("Shut up!"))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/wfanselow/Generators/examples.py", line 39, in talk_gen
    val = (yield "Hi there %s" % (talk_to))
ValueError: Shut up!
>>> next(gen)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
>>> gen.send('jack')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

**Example of close()**
```
>>> from examples import talk_gen
>>> gen = talk_gen('Bill')
>>> next(gen)
'Hi there Bill'
>>> gen.send('Joe')
'How are you Joe?'
>>> next(gen)
'Bye-bye Joe'
>>> gen.send('Jim')
'Hi there Jim'
>>> gen.send('Jim')
'How are you Jim?'
>>> gen.close()
>>> next(gen) 
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```
