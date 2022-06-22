"""

 A "generator" is a "lazy iterator" - "lazy", meaning they don't calculate their result before they are requested.
 Ideal for when you use the values once then throw them away, or if you don't iterate through the whole thing.
 They can be iterated through just like a list with for x in ..., or by using islice to get a portion of it
 (as you can with any iterable, but you can't subscript generators so it's needed here). You can also chain
 generators, which is super cool.
 You can use “generator comprehension” which can often save time and memory over list comprehension.

 EXAMPLES:
 Don't do this! It will store the whole list in memory
 Sometimes this is needed but if you only need values once (or don't need all
 values), there's a better option

   expr = [intensive_operation(x) for x in range(really_big_number)]
   for item in expr:
      ...

 Do this instead! Nothing is saved to memory, and you don't waste any time making a list you'll just throw away.
 Imagine if your function exits after the first 10 items - you'd have wasted really_big_number - 10 calls to
 intensive_operation with the list option

   expr = (intensive_operation(x) for x in range(really_big_number))
   for item in expr:
      ...

 Also - generator expressions are the correct replacement for map() and filter(), which the creator of Python wanted to remove.

"""

# Equivalent expressions; second option avoids extra lambda function call
# next() just gets the next (in this case first) item in an iterator, if you're unaware
# Timeit shows second option (no filter) is a whopping 36% faster on my computer
# And is arguably somewhat more readable
next(filter(lambda x: x % 1000 == 0, range(1, 10000)))
next(x for x in range(1, 10000) if x % 1000 == 0)

# Equivalent expressions: second option uses generator to avoid lambda calls
# Not as impressive as with filter, but second option is still 19% faster for me
# Also arguably more readable
list(map(lambda x: x * x, range(10000)))
list(x * x for x in range(10000))

expr1 = (a**4 for a in range(10000000000))
expr2 = (b + 2000 for b in expr1 if b > 8000)
expr3 = (f"Result: {c}" for c in expr2)
list(itertools.islice(expr3, 2, 6))

# Returns:
# ['Result: 22736', 'Result: 30561', 'Result: 40416', 'Result: 52625']
# Try this again replacing the generator (...) with list's [...] and notice how it takes a LONG time calculating
# all values for 10000000000 that you don't need
