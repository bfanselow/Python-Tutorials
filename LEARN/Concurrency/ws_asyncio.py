#!/usr/bin/env python
"""
  File: ws_asyncio.py

  Description:  
   Perform web-scraping from a list of URL's using AsynIO 
   Used by webscrape_comparison.py 
   
   NOTES: 
   * Uses "aiohttp" lib instead of "requests".
  
   SUMMARY
   asyncio basically provides an "event loop" which is a programming construct that waits 
   for and dispatches events or messages in a program. In other words, an event loop watches 
   out for when something occurs, and when something that the event loop cares about happens 
   it then calls any code that cares about what happened.  "async" and "await" are fancy 
   generators that we call "coroutines". Generators are bascially functions whose execution can 
   be paused. Defining a method with "async def" makes it a coroutine.  There are various ways to 
   create and start the event loop. In this script we use the syntax:
     asyncio.get_event_loop().run_until_complete(*tasks)

   WARNING
   Proper use asyncio can be very difficult to learn and understand, especially with its 
   numerous different ways of achieving the same result and the syntax changes over various
   Python versions.  For trivial examples such as the one below in this script it makes 
   sense - a function that needs to hit many separate API endpoints.  However, beyond 
   these trivial examples, figuring out all the subtle differences in the various methods 
   across AbstractEventLoops, the asyncio module, Futures, Tasks, etc, it gets complicated 
   really fast.

 
   Usage: 
    l_urls = ['https://www.nike.com', 'https://www.jython.org/' ] 
    N = len(l_urls)
    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(download_all_sites_ASYNCIO(l_urls))
    duration = time.time() - start_time
    print("\nAsync download of %d sites - Duration: %s seconds" % (N, duration))

"""
import asyncio
import time
import aiohttp
from utils import *

DEBUG = 1

##=================================================================================================
## "async" keyword in from of function indicates this function is a "coroutine"
## The "await" keyword is used to mark where execution flow will be released - when/where to 
## context switch

async def download_site(session, url):
  async with session.get(url) as response:
    if response:
      dprint(1,DEBUG, "Read %s bytes from %s" % ( len(response.content), url) )
    else:
      print(1,DEBUG, "Site not found: %s" % (url))
  return( response )

##-------------------------------------------------------------------------------------------------
async def download_all_sites_ASYNCIO(sites):
  """
   Download site content from multiple sites using AsyncIO.
  """
  count = 0
  async with aiohttp.ClientSession() as session:
    tasks = []
    for url in sites:
      task = asyncio.ensure_future(download_site(session, url))
      tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)

  return( count )

##=================================================================================================
if __name__ == "__main__":
    
    url_file_path = "./url_list"

    l_urls = ['https://www.nike.com', 'https://www.jython.org/' ] 
    N = len(l_urls)
    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(download_all_sites_ASYNCIO(l_urls))
    duration = time.time() - start_time
    print("\nAsyncIO download of %d sites - Duration: %s seconds" % (N, duration))
