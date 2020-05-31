#!/usr/bin/env python
"""
  File: ws_multiprocessing.py

  Description:  
   Perform web-scraping from a list of URL's using Multi-Processing
   Used by webscrape_comparison.py 
  
  Notes: 
   The multiprocessing.Pool object creates a number of separate Python interpreter processes 
   and has each one run the function specified by first map() arg on some of the items in the 
   iterable arg (list of sites). The communication between the main process and the other 
   processes is handled by the multiprocessing module for you.

   Below we do not specify how many processes to create in the Pool, although that is an optional 
   parameter to the Pool method. By default, multiprocessing.Pool() will determine the number of 
   CPUs in your computer and match that. This is usually the best setting.

   Typically, increasing the number of processes beyond the default does not make things faster. 
   In fact, it usually slows things down because the cost for setting up and tearing down all 
   those processes is larger than the benefit of doing the I/O requests in parallel.

   Notice the "initializer=set_global_session" arg in multiprocessing.Pool(). Since each process 
   in the Pool has its own memory space, they cannot share things like a Session object. You don’t 
   want to create a new Session each time the function is called, but create one for each process.

   There is not a way to pass a return value back from the initializer to the function called by 
   the download_site() process, but you can initialize a global session variable to hold the 
   single session for each process. Because each process has its own memory space, the global 
   for each one will be different.

 
   Usage: 
    import time
    ...
    l_urls = ['https://www.nike.com', 'https://www.jython.org/' ] 
    N = len(l_urls)
    start_time = time.time()
    download_all_sites_MULTIPROCESSING(l_urls)
    duration = time.time() - start_time
    print("\nMultiprocessing download of %d sites - Duration: %s seconds" % (N, duration))

"""
import os 
import time
import multiprocessing
import requests

from utils import *

DEBUG = 0 

session = None ## GLOBAL

##=================================================================================================
def get_cpu_count():
  """
   Get the number of CPUs in the system using 
  """
  cpu_count = os.cpu_count() 
  return( cpu_count )

##-------------------------------------------------------------------------------------------------
def set_global_session():
  global session
  if not session:
    session = requests.Session()

##-------------------------------------------------------------------------------------------------
def download_site(url):
  with session.get(url) as response:
    name = multiprocessing.current_process().name
    if response:
      dprint(1,DEBUG, "(%s) Read %s bytes from %s" % ( name, len(response.content), url) )
    else:
      print(0,DEBUG, "ERROR - Site not found: %s" % (url))

##-------------------------------------------------------------------------------------------------
def download_all_sites_MULTIPROCESSING(sites):
  """
   Download site content from multiple sites using Multi-processing.
  """
  count = 0
  dprint(1,DEBUG, "Scraping all sites using Multi-Processing..." )
  cpu_count = get_cpu_count()
  print("System CPU count: %d" % (cpu_count))
  with multiprocessing.Pool(initializer=set_global_session) as pool:
    pool.map(download_site, sites)
  return( count )

##=================================================================================================
if __name__ == "__main__":
    
    l_urls = ['https://www.nike.com', 'https://www.jython.org/' ] 
    N = len(l_urls)
    start_time = time.time()
    download_all_sites_MULTIPROCESSING(l_urls)
    duration = time.time() - start_time
    print("\nMultiprocessing download of %d sites - Duration: %s seconds" % (N, duration))
