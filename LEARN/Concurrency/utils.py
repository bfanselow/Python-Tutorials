#!/usr/bin/env python
"""
  File: utils.py

  Description:
   Common utility methods for the ConcurrencyWebScraping demo 

"""

##-------------------------------------------------------------------------------------------------
def dprint(level,debug_level, msg):
  """
   Debug output based on level
  """
  if level <= debug_level:
    print("  (%d) %s" % (level,msg))


