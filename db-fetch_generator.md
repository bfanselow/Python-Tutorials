## USE GENERATORS FOR FETCHING LARGE DB RECORD SETS

When using the python DB API, it's tempting to always use a cursor's fetchall() method so that you can easily iterate through a result set.
For very large result sets though, this could be expensive in terms of memory (and time to wait for the entire result set to come back).
You can use fetchmany() instead, but then you have to manage looping through the intemediate result sets.

To iterate through the result of a query, you often see code like this:

```
cursor = con.cursor()
cursor.execute('select * from HUGE_TABLE')
for result in cursor.fetchall():
    do_something_with(result)
```

This is fine if fetchall() returns a small result set, but not so great if the query result is very large, or takes a long time to return.
'very large' and 'long time' are relative of course, but in any case it's easy to see that cursor.fetchall() is going to need to allocate
enough memory to store the entire result set in memory at once. In addition, the doSomethingWith function isn't going to get called until
that entire query finishes as well.

Doing it one at a time with cursor.fetchone() is an option, but doesn't take advantage of the database's efficiency when returning multiple
records for a single (as opposed to multiple) queries.

To address this, there's a cursor.fetchmany() method that returns the next 'n' rows of the query, allowing you to strike a time/space compromise
between the other two options.

Let's create a results_iterator() function to simplify the processing:
```
from typing import Interator

def ResultIter(cursor, arraysize=1000) -> Iterator[dict]:
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result
```

Now we can use this like so:
```
cursor = con.cursor()
cursor.execute('select * from HUGE_TABLE')

for result in results_iterator(cursor):
    do_something_with(result)
```

This looks similar to code above, but internally the results_iterator() generator is chunking the database calls into a series of fetchmany() calls.
The default here is that a 1000 records at a time are fetched, but you can change that according to your own requirements (either by changing the
default, or just using the second parameter to results_iterator(). As always, trying different values with the profiler is probably a good idea.
