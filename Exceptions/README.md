## Do's and Don'ts of Python Exception Handling
The key to writing Python exception patterns is to understand well what the application should do when it encounters an error with your *try* statement.  Do you need to know about the exception at all at this point?  If not, why not just avoid try/catch altogether and let the parent/caller handle it; if the caller doesn't handle it, it will eventually bubble all the way up and your program will abort with a traceback.  Maybe you don't need to handle it at the level of the try, but you do want to log something.  Maybe you want to handle it (say with some cleanup tasks) but still let the parent address whether or not to abort.  Maybe you want to peform some cleanup tasks on both success and failure.  Decide what you want to do when an error occurs at this point, see what the caller will do (if anything) with an exception raised by your try. Also, decide how to proceed if successful.  From these decisions you should be able to construct a useful recipe.


#### The absolute worst python anti-pattern: catching all exceptions and silently continuing (a.k.a. "swallowing" all exceptions).
```
try:
  do_something()
except Exception as e:
  pass
```

By doing this you are totally hiding all errors and throwing away the stack trace - good luck troubleshooting.

Whenever we *catch* an exception with "except", we have three choices:
1) **Swallow** it - handle it and keep running.
2) Do something (i.e. logging) and re-raise the same exception to let higher levels handle it.
3) Raise a different exception instead of the original

---
### 1) Swallowing the Exception
Swallowing an exception only makes sense if we are catching **specific** exceptions that we know we can recover from (or take an alternate processing path) and when we deliberately do not want to terminate from the current processing.  Suppose we are iterating over a list of input objects and processing. We typically don't want to terminate processing if there is a *known* type of processing error with one of the input objects. It may be preferrable to catch and handle specific errors so that we can continue processing the other objects. 
```
for o in object_list:
    try: 
        process_object(o)
    except ValueError: 
        recover()
    except KeyError:
        alternate_route()
```
Note, in this case all other exceptions will be raised and handled by the calling code.

You should **NEVER** swallow all Exceptions no matter how thorough you think your **recover()** method is. 
```
try: 
    do_something()
except Exception: 
    recover()
```

Also, whenever you **swallow** an exception, there should be an associated (timestamped) log message (with full stack trace) regardless of how you handle it. Using Python's logging module makes this simple as each logger object has an exception() method, taking a message string. If called in the except block, the caught exception will automatically be fully logged, including the stack trace.
```
try: 
    do_something()
except ValueError as e: 
    logging.exception(f'Caught exception: {e}')
    recover()
```

If you are working with someone else's code that does not use the logging module and you don't want to refactor everyting, write your own logging method such as the following:
```
class ExceptionLogger():
    ...
    def log(msg)
        """ wrties timestamped log message ... """
        raise NotImplementedError

import traceback
def log_traceback(ex):
    """ l"""
    tb_lines = traceback.format_exception(ex.__class__, ex, ex.__traceback__)
    tb_text = ''.join(tb_lines)
    exception_logger.log(tb_text)

try:
    do_something()
except ValueError as e: 
    log_traceback(ex)
    recover()
```

---
If some code path must broadly catch all exceptions then it should log the exception (with timestamp and stack-track) and either:  
  * Re-raise the same exception to be handled by calling code
  * Raise a different exception (instead of the original) to be handled by calling code

### 2) Re-raise same exception
Use this approach if you want to provide some local handling (such as logging), but also want the higher-level code to perform some additonal handling.
```
try: 
    do_something()
except Exception as e: 
    logging.exception(f'Caught exception: {e}')
    raise
finally:
    cleanup()
```

### 3) Raise new exception
Use this if want to group multiple different low-level exceptions into a single category that is handled uniformly by higher-level code.  Be sure to pass the Exception object back so that the calling function has access to the original stack-trace.
```
class RobotError(Exception):
    pass

class Robot():
    def __init_(self,x):
        self.x = x
    def perform(self):
        try: 
            do_something()
        except Exception as e: 
            msg = "do_something() failed"
            logging.exception(msg)
            raise RobotError( "%s: %s" % (msg, e) ) 
```



## Other exception recipes

#### use "finally" for performing (cleanup) tasks regardless of success or failure without aborting
```
try:
    do_some_file_operations(some_arg)
except Exception as e:
    log.exception(f"Some errors occured when passing arg: {some_arg}")
finally:
    cleanup_all_files()
```

#### Use "else" for performing cleanup tasks only on success. Here, w only log on failure, but don't abort
```
try:
    do_some_file_operations(some_arg)
except Exception as e:
    log.exception(f"Some errors occured. All files left in current state")
else:
    cleanup_all_files()
```

-----
#### Exceptions are often used in Python for the "easier to ask for forgiveness than permission" (EAFP) principle.  Example, suppose you need a function that takes positive numbers as strings and converts them to int
```
>>> def to_integer(value):
...     if value.isdigit():
...         return int(value)
...     return None
...

>>> to_integer("42")
42
>>> to_integer("one") is None
True
```
#### This works fine, but there’s some hidden repetition in this function. The call to int() internally performs all the required checks to convert the input string to an actual integer number.  Because the checks are already part of int(), testing the input string with .isdigit() duplicates the checks already in place. To avoid this unnecessary repetition and its corresponding overhead, you can use the EAFP style and do something like this:
```
>>> def to_integer(value):
...     try:
...         return int(value)
...     except ValueError:
...         return None
...

>>> to_integer("42")
42
>>> to_integer("one") is None
True
```
