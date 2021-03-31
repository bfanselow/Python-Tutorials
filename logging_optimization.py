import logging

"""
  Simple demonstration of optimized logging.

  Python logging methods like logging.debug() take a message string
  argument along with optional args and kwargs. Args are used for message
  formatting. Formatting of these arguments is deferred until it cannot
  be avoided which means the final message is not evaluated if its log
  level is below the logger’s log level. On the other hand, using f-string
  or %(tuple) style formatting is just an expression that is evaluated at
  runtime and it lacks logging’s optimizations.

  Do not use these:
   * log.debug(f"fstring formatted msg: {msg}")
   * log.debug("%(tuple) formatted msg: %s" % msg)

  Instead, use:
   * log.debug("log-arg formatted msg: %s", msg)


"""
logging.basicConfig(level=logging.INFO)

log = logging.getLogger(None)

class LogArgsInterpolater():
    def __init__(self, s):
        self.s = s

    def __str__(self):
        print(f"I am stringifying {self.s}")
        return f"<LogArgsInterpolater: {self.s}>"


log.info("str %% test: %s" % LogArgsInterpolater("info % formatting test"))
log.info(f"f-string test: {LogArgsInterpolater('info fstring test')}")
log.info("log %%s test: %s",  LogArgsInterpolater("info %s args test"))

log.debug("str %% test: %s" % LogArgsInterpolater("debug  % formatting test"))
log.debug(f"f-string test: {LogArgsInterpolater('debug fstring test')}")
log.debug("log %%s test: %s",  LogArgsInterpolater("debug %s args test"))
