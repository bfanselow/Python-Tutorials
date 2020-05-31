## Do's and Don'ts of Python Exception Handling

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
Swallowing an exception only makes sense if we are catching **specific** exceptions that we know we can recover from (or take any alternate processing path) and when we deliberately do not want to terminate from the current processing.  Suppose we are iterating over a list of input objects and processing. We typically don't want to terminate processing if there is an error with one of the input objects. It may be preferrable to catch and handle specific errors so that we can continue processing the other objects. 
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

Also, whenever you **swallow** an exception, there should be an associated (timestamped) log message (with full stack trace) regardless of how you handle it. Using Python's logging module this is simple as each logger object has an exception() method, taking a message string. If called in the except block, the caught exception will automatically be fully logged, including the stack trace.
```
try: 
    do_something()
except ValueError as e: 
    logging.exception(f'Caught exception: {e}')
    recover()
```

If you working with someone else's code that does not use the logging moudle and you don't want to refactor everyting, write your own logging method such as the following:
```
class ExceptionLogger():
    ...
    def log(msg)
        """ wrties timestamped log message ... """
        raise NotImplementedError

import traceback
def log_traceback(ex):
    """ logging with stacktrack, compaticalbe with Python2 and 3"""
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
  2) Re-raise the same exception to be handled by calling code
  3) Raise a different exception (instead of the original) to be handled by calling code

### 2) Re-raise same exception
Use this approach if you want to provide some local handling (such as logging), but also want the calling function to perform additonal handling.
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
