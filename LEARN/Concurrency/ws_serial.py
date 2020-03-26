#!/usr/bin/env python
"""
  File: ws_serial.py

  Description:  
   Perform web-scraping from a list of URL's in a SERIAL fashion.
   Used by webscrape_comparison.py 
    
   Usage: 
    import time

    l_urls = ['https://www.nike.com', 'https://www.jython.org/' ] 
    N = len(l_urls)
    start_time = time.time()
    N = download_all_sites_SERIALLY(l_urls)
    duration = time.time() - start_time
    print("\nSerial download of %d sites - Duration: %s seconds" % (N, duration))

"""
import time
import requests

from utils import *

DEBUG = 0 

##-------------------------------------------------------------------------------------------------
def download_site(url, session, count):
  """
   Make GET request to the url using session.  This is the heavy I/O method that should
   be making use of concurrency.
  """
  dprint(1,DEBUG, "(%d) Downloading site content with session: [%s]..." % (count, url) )
  response = None

  with session.get(url) as response:
    ## This Truth value test works because __bool__() is an overloaded method on Response.
    ## The default behavior of Response has been redefined to take the status code into
    ## account when determining the truth value of the object. True if status_code
    ## between 200 and 400, False otherwise.
    if response:
      dprint(1,DEBUG, "Read %s bytes from %s" % ( len(response.content), url) )
    else:
      print(1,DEBUG, "Site not found: %s" % (url))

  return( response )

##=================================================================================================
def download_all_sites_SERIALLY(sites):
  """
   Download site content SERIALLY from each site. This is only for demonstration purposes.
   While the CPU sits idle waiting for I/O response, we could be triggering other downloads.
  """
  count = 0
  dprint(1,DEBUG, "Scraping all sites SERIALLY..." )
  with requests.Session() as session:
    for url in sites:
      resp = download_site(url, session, count)
      if resp:
        count += 1
  return( count )

##=================================================================================================
if __name__ == "__main__":
    
    l_urls = ['https://www.nike.com', 'https://www.jython.org/' ] 
    start_time = time.time()
    N = download_all_sites_SERIALLY(l_urls)
    duration = time.time() - start_time
    print("\nSerial download of %d sites - Duration: %s seconds" % (N, duration))
