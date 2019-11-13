"""

 File: utils_datetime.py
 Author: Bill Fanselow
 
 Description:
   Date/Time handling functions


"""

##----------------------------------------------------------
## Python2 compatiblity
from __future__ import (division, print_function)
##----------------------------------------------------------
import re
import sys
import datetime
import time

myname = 'utils_datetime.py'

DEBUG = 2 


#------------------------------------------------------------------------
class MethodInputError(Exception):
  pass

#------------------------------------------------------------------------
def datetime_duration(ts_start, ts_end, units="seconds"):
  
  ##
  ##  Calculate the time duration between two input dates.
  ##  Args:
  ##      * timestamp-start (datetime string) 
  ##      * timestamp-end (datetime string) 
  ##      * Optional units (default seconds) 
  ##  Return:
  ##    Duration value between timestamps in specified units 
  ##
    tag = 'datetime_duration()'

    m = re.match(r'^(\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2})$', ts_start)
    if not m:
      m = re.match('^(\d{4}\-\d{2}\-\d{2})$', ts_start)
      if m:
        ts_start = ts_start + ' 00:00:00'
      else:
        raise MethodInputError("%s: Invalid timestamp string for ts_start: (%s)" % (tag, ts_start))

    m = re.match(r'^(\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2})$', ts_end)
    if not m:
      m = re.match(r'^(\d{4}\-\d{2}\-\d{2})$', ts_end)
      if m:
        ts_end = ts_end + ' 00:00:00'
      else:
        raise MethodInputError("%s: Invalid timestamp string for ts_end: (%s)" % (tag, ts_end))

    o_start = datetime.datetime.strptime(ts_start, '%Y-%m-%d %H:%M:%S')
    o_end = datetime.datetime.strptime(ts_end, '%Y-%m-%d %H:%M:%S')
 
    dt_diff = o_end - o_start
   
    duration_seconds = dt_diff.total_seconds()

    if units == 'seconds':
      duration = duration_seconds
    elif units == 'minutes':
      duration = duration_seconds / 60
    elif units == 'hours': 
      duration = duration_seconds / 3600
    elif units == 'days': 
      duration = duration_seconds / 86400 
    else:
      raise MethodInputError("%s: Unsupported duration units: [%s]" % (tag, units))

    duration = round( duration, 2 )

    return(duration)

#------------------------------------------------------------------------
def datetime_duration_from_now(timestamp, units="seconds"):
  
  ##
  ##  Calculate the time duration between one input datetime string and now(),
  ##  where the timestamp is the start of the window and now() is the end.
  ##  Args:
  ##      * timestamp (datetime string) 
  ##      * Optional units (default seconds) 
  ##  Return:
  ##    Duration value between timestamp and now() in specified units 
  ##
    tag = 'datetime_duration_from_now()'

    ts_now = gmt_now()

    duration = datetime_duration(timestamp, ts_now, units)

    return(duration)

#------------------------------------------------------------------------
def gmt_now_with_delta(d_delta, format=None):
  ## 
  ##  Get the current timestamp string in UTC with a time delta.
  ##  Args:
  ##   * Dict of delta units=>values (seconds,minutes,hours,days,months)
  ##      Example: d_delta = {'seconds': 10, 'minutes': 20, 'days': 2 } 
  ##   * Optional datetime formatting.
  ##  Return:
  ##    String representation of the timestamp in UTC timezone.
  ##

  tag = 'gmt_now_with_delta()' 
 
  default_format = "%Y-%m-%d %H:%M:%S"
  if format is None:
    format = default_format

  o_dt = datetime.datetime.now() - datetime.timedelta(**d_delta)

  timestamp = o_dt.strftime(format)

  return(timestamp)

#------------------------------------------------------------------------
def gmt_now(format=None):
  ## 
  ##  Get the current timestamp string in UTC.
  ##  Args:
  ##   * Optional datetime formatting.
  ##  Return:
  ##    String representation of the timestamp in UTC timezone.
  ## 

  tag = 'gmt_now()'

  default_format = "%Y-%m-%d %H:%M:%S"
  if format is None:
    format = default_format

  o_dt = datetime.datetime.now()
  gmtime_now = o_dt.strftime(format) 

  return(gmtime_now)

#------------------------------------------------------------------------
def timestamp_to_str(timestamp):
  ## 
  ##   Convert epoch timestamp to a time string in UTC.
  ##   Args:
  ##     * timestamp: The epoch time, in seconds, to convert.
  ##   Return:
  ##      String representation of the timestamp in UTC timezone.
  ## 
    
    tag = 'timestamp_to_str()'

    if not timestamp:
        return ''
    if timestamp == sys.maxsize:
        # sys.maxsize represents infinity.
        return 'inf'
    utc = pytz.timezone('UTC')
    return datetime.datetime.fromtimestamp(timestamp, tz=utc).strftime('%Y-%m-%d %H:%M:%S %Z')


#------------------------------------------------------------------------
def str_to_timestamp(time_str):
  ## 
  ##  Convert a time string to epoch timestamp.
  ##  Args:
  ##    * time_str: String representation of the timestamp in UTC timezone.
  ##  Returns
  ##   The epoch time, in seconds.
  ##

    tag = 'str_to_timestamp()'

    date = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S %Z')
    return calendar.timegm(date.utctimetuple())

#------------------------------------------------------------------------
## UNIT-TEST EACH METHOD() 
##

if __name__ == '__main__':

  print("\n%s: TEST 1: gmt_now(): Get current time in GMT" % (myname))
  ts_now = gmt_now()
  print(" >  %s" % (ts_now))
  
  print("\n%s: TEST 2a: gmt_now_with_delta(): Get current time in GMT with Delta (3 minutes, 30 seconds back)" % (myname))
  d_delta = {'minutes': 3, 'seconds': 30 }
  ts = gmt_now_with_delta(d_delta) 
  print(" >  %s" % (ts))
  print("%s: TEST 2b: gmt_now_with_delta(): Get current time in GMT with Delta (1 day, 4 hours forward)" % (myname))
  d_delta = {'days': -1, 'hours': -4 }
  ts = gmt_now_with_delta(d_delta) 
  print(" >  %s" % (ts))

  d_delta = {'days': 2 } 
  ts_start =  gmt_now()
  ts_end = gmt_now_with_delta(d_delta)
  dur_hours = datetime_duration(ts_end, ts_start, "hours")
  print("\n%s: TEST 3a: datetime_duration(): Get time-duration between end=(%s) and start=(%s)" % (myname, ts_end, ts_start))
  print(" > DUR-HOURS %s" % (dur_hours))
  d_delta = {'hours': 2, 'minutes': 30 } 
  ts_start =  gmt_now()
  ts_end = gmt_now_with_delta(d_delta)
  dur_minutes = datetime_duration(ts_end, ts_start, "minutes")
  print("%s: TEST 3b: datetime_duration(): Get time-duration between end=(%s) and start=(%s)" % (myname, ts_end, ts_start))
  print(" > DUR-MINUTES %s" % (dur_minutes))

  d_delta = {'days': 2 } 
  timestamp = gmt_now_with_delta(d_delta)
  print("\n%s: TEST 4: datetime_duration_from_now(): Get time-duration between timestamp=(%s) and gmt_now()" % (myname, timestamp))
  duration_days = datetime_duration_from_now(timestamp, "days")
  print(" > DUR-DAYS %s" % (duration_days))

