"""
  File: PerfTimer.py
  Class: PerfTimer
  Description:
    Simple "timer" class for code performance timing.
    Uses time.perf_counter() by default, but can use time.process_time() if specified in init().
    The difference is that perf_counter() returns absolute time including system time when your
    Python process is not running (thus subject to system load). Instead, process_time() returns
    only user time (excluding system time), which is only the time of your process.
  Author: Bill Fanselow
  Created: 10-07-2020

  Usage: See main() at bottom of page
"""

import time

TIMERS =  ['perf_counter', 'process_time']

#----------------------------------------------------------------------------
class TimerError(Exception):
  pass

#----------------------------------------------------------------------------
class PerfTimer:
  """
  Instantiate a code performace-timing object for profiling code.

  Init-Args:
    d_init (dict): Initialization args (optional)
      * sigfigs (int): Store number of significant figures for timing data (default=2)
      * mode (str): timing-mode - perf_counter or process_time (default=perf_counter)

  Attributes:
    sigfigs: (see above)
    timer: (func): time.<timing-method> - time.perf_counter() or process_time()
    start_time: (float) time returned by first call to time.perf_counter() or time.process_time()
    end_time: (float) time returned by first call to time.perf_counter() or time.process_time()
    elsapsed_time: (float) diff between end_time and start_time
  """

  def __init__(self, d_init=None):

    self.start_time = None
    self.end_time = None
    self.elapsed_time = None

    ## defaults
    self.sigfigs = 2
    self.timer = time.perf_counter

    if d_init:
      self.configure(**d_init)

  ##-------------------------------------------------------------------------
  def start(self):
    """
    Start a new timer, and store the start_time.
    Returns None
    """
    if self.start_time is not None:
      raise TimerError("Timer is running. Use .stop() to stop it")

    self.start_time = self.timer()

  ##-------------------------------------------------------------------------
  def stop(self):
    """
    Stop the timer, store the end-time and calculate elsapsed time.
    Raises TimerError() if start() has not yet been called.
    Return the elapsed time.
    """
    if self.start_time is None:
      raise TimerError("Timer is not running. Use .start() to start it")

    self.end_time = self.timer()

    elapsed_time = self.end_time - self.start_time

    self.elapsed_time = "%.*f" % (self.sigfigs, elapsed_time)
    self.start_time = None

    return(self.elapsed_time)

  ##-------------------------------------------------------------------------
  def configure(self, **kwargs):
    """
    (Re)configure some attributes available from init().
    Keyword args:
      * sigfigs (int): Store number of significant figures for timing data (default=2)
      * mode (str): timing-mode - perf_counter or process_time (default=perf_counter)
    Returns None
    """

    if 'sigfigs' in kwargs:
      sigfigs = kwargs['sigfigs']
      if not isinstance(sigfigs, int):
        raise AttributeError("sigfigs must be an integer")
      self.sigfigs = sigfigs
    if 'mode' in kwargs:
      mode = kwargs['mode']
      if mode not in TIMERS:
        raise AttributeError("Mode must be one of: %s" % (TIMERS))
      if mode == 'process_time':
        self.timer = time.process_time
      else:
        self.timer = time.perf_counter

#----------------------------------------------------------------------------
if __name__ == "__main__":

  def op_1():
    for i in range(1,5000):
      s = i*5.0987 / (i+1)*16.7890
      r = s*s / (i + s)

  def op_2():
    l_2x = [2**x for x in range(1,40000)]

  t = PerfTimer({'sigfigs': 5} )

  ## Time with perf_counter()
  t.start()
  op_1()
  et = t.stop()
  print("Operation 1: perf_counter() elapsed time: %s seconds" % (et))

  t.configure(sigfigs=4)
  t.start()
  op_2()
  et = t.stop()
  print("Operation 2: perf_counter() elapsed time: %s seconds" % (et))

  ## Time with process_time()
  t.configure(sigfigs=3, mode='process_time')
  t.start()
  op_1()
  et = t.stop()
  print("Operation 3: process_time() elapsed time: %s seconds" % (et))

  t.start()
  op_2()
  et = t.stop()
  print("Operation 4: process_time() elapsed time: %s seconds" % (et))
