#!/usr/bin/env python
"""
  File: webscrape_comparison.py

  Description:  
   Web-scraping from a list of URL's provides a great scenario for demonstrating the benefits
   of concurrent processing.
   Due to the heavy I/O nature of web-scraping (lots of idle
   CPU time) we can demonstrate the huge reduction in processing time using various
   concurrent processing techniques. This script will demonstrate the the following processing 
   models:
     * Serial processing - to establish the (worst-case) baseline for scraping a list of URL. 
     * Multi-Threaded 
     * Multi-Processing 
     * Async-IO 

   See documentation within each download_all_sites_<method> for more details of each method.

   Usage: ./webscrape_comparison.py -f <url-list-file>

"""

import requests
import time
import asyncio
import socket
from urllib.parse import urlparse

from utils import *
from ws_serial import download_all_sites_SERIALLY 
from ws_multithreading import download_all_sites_MULTITHREADING
from ws_multiprocessing import download_all_sites_MULTIPROCESSING
from ws_asyncio import download_all_sites_ASYNCIO

DEBUG = 0 

##-------------------------------------------------------------------------------------------------
def read_url_file(filepath):
  l_url_list = []
  dprint(1,DEBUG, "Reading file: %s" % (filepath) )
  with open(filepath, 'r') as f: 
    for url in f:
      if url.startswith("#"):
        continue
      ## Remove endlines and whitespaces from the URL 
      l_url_list.append(url.strip())
  return(l_url_list)

##-------------------------------------------------------------------------------------------------
def get_dns_from_url(url):
  """ 
   Extract the dns name from a URL
  """ 

  dns_name = None 
    
  try:
    o = urlparse(url)
    dns_name = o.netloc
    port = o.port
  except UnicodeError as e:  ## most commonly: "label too long" error
    print("ERROR - DNS: Could not extract DNS name from url %s: %s" % (url, e) )
  except Exception as e:
    print("ERROR - DNS: Could not extract DNS name from url %s: %s" % (url, e) )
    
  dprint(2,DEBUG, "URL=[%s] DNS=[%s]" % (url, dns_name) )

  return(dns_name)

##-------------------------------------------------------------------------------------------------
def filter_unresolving_sites(l_sites):
  """ 
   Identify sites that do not resolve in DNS. 
   Python requests lib does not handle DNS errors well - throws error from lower-level socket 
   libs.  We will explicity catch this.
  """ 
  l_resolving_sites = []
  for url in l_sites:

    dns_name = get_dns_from_url(url) 
    if dns_name:
      dprint(2,DEBUG, "Resolving url: %s" % (url) )
      if dns_lookup(dns_name):
        l_resolving_sites.append(url)
   
  return( l_resolving_sites )

##-------------------------------------------------------------------------------------------------
def dns_lookup(dns_name):
  """
   Determine if DNS name resolves
  """
  _PORT = 80 ## default
  try:
    socket.getaddrinfo(dns_name, _PORT)
  except socket.gaierror:
    print("ERROR - DNS: Could not resolve name %s" % (dns_name) )
    return( False )

  return( True )

##=================================================================================================
if __name__ == "__main__":
   
    ##
    ## Creat a list of URL's
    ##  
    url_file_path = "./url_list"
    ## read and filter the target site (url) data 
    print("Reading url list from file: %s" % (url_file_path))
    l_reachable_urls = read_url_file( url_file_path ) 
    dprint(1,DEBUG, "Retrieved %d reachable url's from file" % (len(l_reachable_urls)))

    l_urls = filter_unresolving_sites(l_reachable_urls) * 10
    N_sites = len(l_urls)

    ##
    ## Demonstrate scraping with each model  
    ##

    ##
    ## Serial processing
    ##
    print("Starting Serial download of %d sites..." % (N_sites))
    start_time = time.time()
    N = download_all_sites_SERIALLY(l_urls)
    duration = time.time() - start_time
    print("Serial download of %d sites - Duration: %s seconds\n" % (N, duration))

    ##
    ## Multi-Threading
    ##
    print("Starting Multi-Threading download of %d sites..." % (N_sites))
    start_time = time.time()
    download_all_sites_MULTITHREADING(l_urls)
    duration = time.time() - start_time
    print("Multi-Threaded download of %d sites - Duration: %s seconds\n" % (N_sites, duration))
   
    ##
    ## Multi-Processing
    ##
    ## Notice that this is not as fast as Multi-Threading or Asyncio, which makes sense as I/O bound 
    ## problems are not where multiprocessing excels (best for CPU bound problems).
    print("Starting Multi-Processing download of %d sites..." % (N_sites))
    start_time = time.time()
    download_all_sites_MULTIPROCESSING(l_urls)
    duration = time.time() - start_time
    print("Multi-Processing download of %d sites - Duration: %s seconds\n" % (N_sites, duration))
   
    ## 
    ## Asyncio
    ## 
    print("Starting Asyncio download of %d sites..." % (N_sites))
    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(download_all_sites_ASYNCIO(l_urls))
    duration = time.time() - start_time
    print("AsyncIO download of %d sites - Duration: %s seconds" % (N_sites, duration))
