"""

  Class: cached()
  Author: Bill Fanselow 2020-06-01
  Description:
    Provides a @cached decorator which will return a function's cached
    return value (rather than re-evaluating)  if called with previously
    stored (hashable) input.

    Decorator method does check that we have not exceeded a max cache
    size as measured by the number of keys in the cache dict object as
    this is the real measure of a dict storage size. The key-value pairs
    themselves aren’t stored in a dict itself.  Rather, a reference to
    the place in memory that holds the keys and values is stored.

    !!! WARNING !!!
    1) Only use this decorator with IDEMPOTENT functions/methods - an
       operation that has no additional effect if it is called more than
       once with the same input parameters. Using this on a NON-IDEMPOTENT
       function/method, such as one which makes a (non-idempotent) database
       call, will obviously have unexpected/undesirable consequences.
    2) Storing all previously processed input and outputs can place
       a load on memory such that this outweighs the time-savings of not having
       to re-evaulate an operation. Use this decorator carefully, and monitor
       system load with tests while adjusting MAX_KEYS. Use this only when
       there are observable advanatages to caching which out-weigh the dis-
       advantage of memory load. For example, when processing time is very
       large and the number of unique function inputs is small.
    !!! YOU HAVE BEEN WARNED !!!

"""
import collections
import functools

MAX_KEYS = 1000  # max number of keys stored in our cache dict


class cached(object):
    """Instantiates a @cached decorator.
     Use this on any method or function to force
     caching of return value.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        do_caching = True

        # Check if all inputs are hashable.
        if not isinstance(args, collections.Hashable):
            do_caching = False
        for v in kwargs.values():
            if not isinstance(v, collections.Hashable):
                do_caching = False
                break

        # Check that we have not exceeded max cache size
        if len(self.cache.keys()) > MAX_KEYS:
            # or we could do self.cache = {} to reset ???
            do_caching = False

        if not do_caching:
            return self.func(*args, **kwargs)

        cache_key = str(args) + str(kwargs)
        if cache_key in self.cache:
            return self.cache[cache_key]
        else:
            value = self.func(*args, **kwargs)
            self.cache[cache_key] = value
            return value

    def __repr__(self):
        """Return the function docstring"""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods"""
        return functools.partial(self.__call__, obj)


if __name__ == '__main__':
    """
     Try these with and without the @cached decorator to compare speed.

     fibonacci(35) without caching:
       python3 cached.py
       9227465
       Elapsed time (secs): 4.74
     fibonacci(35) with caching:
       python3 cached.py
       9227465
       Elapsed time (secs): 0.0
    """
    import time

    @cached
    def fibonacci(n):
        """Return the nth fibonacci number"""
        if n in (0, 1):
            return n
        return fibonacci(n-1) + fibonacci(n-2)

    N = 35
    ts_1 = time.perf_counter()
    print(fibonacci(N))
    ts_2 = time.perf_counter()
    ts_elapsed = ts_2 - ts_1
    print("fibonacci(): Elapsed time (secs): %s" % (round(ts_elapsed, 2)))

    # This example will take 5 seconds without caching and 1 second with
    @cached
    def sleepy_str_op(*args, **kwargs):
        if 'sleep' in kwargs:
            time.sleep(kwargs['sleep'])
        return(str(args) + str(kwargs))

    ts_1 = time.perf_counter()
    for i in range(5):
        print(sleepy_str_op(('abc', 'xyz'), sleep=1.0))

        # try this and notice it will not cache as input is not all hashable
        # print(sleepy_str_op(('abc', 'xyz'), sleep=1.0, mlist=[1,2,3] ))
    ts_2 = time.perf_counter()
    ts_elapsed = ts_2 - ts_1
    print("sleepy_str_op(): Elapsed time (secs): %s" % (round(ts_elapsed, 2)))
