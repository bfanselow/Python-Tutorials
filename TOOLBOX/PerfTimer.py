"""

  File: PerfTimer.py
  Class: PerfTimer

  Description:
    Simple "timer" class for code performance timing

  Usage: 
    See main() at bottom of page

  Author: Bill Fanselow
  Created: 10-07-2020

"""
 
import time
 
#----------------------------------------------------------------------------
class TimerError(Exception):
  pass
 
#----------------------------------------------------------------------------
class PerfTimer:
  def __init__(self, d_init=None):

    self.start_time = None
    self.end_time = None
    self.elapsed_time = None
    self.sigfigs = 4 

    if not d_init:
      d_init = {}

    if 'sigfigs' in d_init:
      self.sigfigs = d_init['sigfigs'] 

  ##------------------------------------------------------------------------- 
  def start(self):
    """ 
    Start a new timer
    """
    if self.start_time is not None:
      raise TimerError("Timer is running. Use .stop() to stop it")
 
    self.start_time = time.perf_counter()
 
  ##------------------------------------------------------------------------- 
  def stop(self):
    """
    Stop the timer
    Return the elapsed time
    """
    if self.start_time is None:
      raise TimerError("Timer is not running. Use .start() to start it")
    
    self.end_time = time.perf_counter()
 
    elapsed_time = self.end_time - self.start_time

    self.elapsed_time = "%.*f" % (self.sigfigs, elapsed_time) 

    return(self.elapsed_time) 
 
  ##------------------------------------------------------------------------- 
  def reset(self, d_args=None):
    """
    Reset/zero-out all time attributes.
    Optionally reset some init attributes
    """
    self.start_time = None
    self.end_time = None 
    self.elapsed_time = None

    if not d_args:
      d_args = {}

    if 'sigfigs' in d_args:
      self.sigfigs = d_args['sigfigs'] 

#----------------------------------------------------------------------------
if __name__ == "__main__":

  t = PerfTimer({'sigfigs': 5} )

  t.start()
  for i in range(1,5000):
    s = i*5.0987 / (i+1)*16.7890
    r = s*s / (i + s)
  et = t.stop()
  print("Operation 1 elapsed time: %s seconds" % (et))

  t.reset({'sigfigs':2})

  t.start()
  l_2x = [2**x for x in range(1,40000)] 
  et = t.stop()
  print("Operation 2 elapsed time: %s seconds" % (et))
