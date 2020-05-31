#!/usr/bin/env python
"""
  File: ws_multithreading.py

  Description:  
   Perform web-scraping from a list of URL's using Multi-Threading 
   Used by webscrape_comparison.py 

   NOTES:
    In Python 2, multi-threading involved several objects and functions (Thread.start(), 
    Thread.join(), and Queue) to manage the details of threading.  These are all still 
    available in Python3, and can still be used to get more fine-grained control of how 
    your threads are run. However, starting with Python 3.2, the standard library added 
    a higher-level abstraction called "Executors" that manage many of the details if you 
    don’t need such fine-grained control.
    Notice that each thread needs to create its own requests.Session() object.  This is 
    one of the interesting and difficult issues with threading. Because the operating 
    system is in control of when your task gets interrupted and another task starts, any data that is shared between the threads needs to be protected, 
  or thread-safe. Unfortunately requests.Session() is not thread-safe.  There are several strategies for 
  making data accesses thread-safe depending on what the data is and how you’re using it. One of them is 
  to use thread-safe data structures like Queue from Python’s queue module.  These objects use low-level 
  primitives like threading.Lock to ensure that only one thread can access a block of code or a bit of 
  memory at the same time. You are using this strategy indirectly by way of the ThreadPoolExecutor object.
  Another strategy to use here is something called thread-local storage. Threading.local() creates an object 
  that look like a global but is specific to each individual thread.
    
   Usage: 
    import time

    l_urls = ['https://www.nike.com', 'https://www.jython.org/' ] 
    N = len(l_urls)
    start_time = time.time()
    download_all_sites_MULTITHREADING(l_urls)
    duration = time.time() - start_time
    print("\nSerial download of %d sites - Duration: %s seconds" % (N, duration))

"""
import concurrent.futures
import time
import requests
import threading

from utils import *

DEBUG = 0 

thread_local = threading.local()

##-------------------------------------------------------------------------------------------------
def get_thread_session():
  if not hasattr(thread_local, "session"):
    thread_local.session = requests.Session()
  return( thread_local.session )

##-------------------------------------------------------------------------------------------------
def download_site(url):
  """
   Make GET request to the url using the thread-local session.  
  """
  dprint(1,DEBUG, "Download site content with thread-local session: [%s]..." % (url) )
  #time.sleep(1)
  session = get_thread_session()
  response = None

  with session.get(url) as response:
    if response:
      dprint(1,DEBUG, "Read %s bytes from %s" % ( len(response.content), url) )
    else:
      print(1,DEBUG, "Site not found: %s" % (url))

  return( response )

##=================================================================================================
def download_all_sites_MULTITHREADING(sites):
  """
   Download site content from multiple sites using Multi-threading.
  """
  count = 0
  dprint(1,DEBUG, "Scraping all sites using Multi-Threading..." )

  MAX_WORKERS = 10 

  ## The Executor controls how and when each of the threads in the pool will run.
  with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    ## The map() method runs the passed-in function on each of the sites in the list. It automatically 
    ## runs them concurrently using the pool of threads it is managing.
    r = executor.map(download_site, sites)

  return( count )

##=================================================================================================
if __name__ == "__main__":
    
    l_urls = ['https://www.nike.com', 'https://www.jython.org/' ] 
    N - len(l_urls)
    start_time = time.time()
    download_all_sites_MULTITHREADING(l_urls)
    duration = time.time() - start_time
    print("\nMulti-threaded download of %d sites - Duration: %s seconds" % (N, duration))
