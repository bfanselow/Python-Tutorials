#!/usr/bin/env python3
"""
  File: getopt_example.py 
  Description: Example of using "getopt" module to parse input args

  Pros: More customizable than working with argparse. 
  Cons: More manual logic-coding necessary. Less built-in logic

"""
import sys
import os
import getopt

myname = os.path.basename(__file__)

## Defaults
DEBUG = 0
MY_VAR = None

#--------------------------------------------------------------------------
def usage(exit_code=None):
  print( "\nUSAGE:")
  print( "$ ./%s -m <myvar> [options]" % (myname))
  print( "  OPTIONS:")
  print( "    -d <debug>  (change debug level. Default=0)")

  if exit_code is not None:
    sys.exit(exit_code)
 
#--------------------------------------------------------------------------
if __name__ == "__main__":

  ## Process command line
  if DEBUG:
    print("%s: INPUT:  %s" % (myname,  str(sys.argv)))

  try:
    opts, args = getopt.getopt(sys.argv[1:],"hd:m:", [ 'help','debug=', 'myvar='])
  except getopt.GetoptError as err:
    print( "%s: ERROR - Command Line Error - %s" % (myname, err) )
    usage(2)

  ## args (single args without a preceeding -opt key)
  ##print( "ARGS:", args )
  ## We do NOT expect any single-arg input so error if any found
  for arg in args:
    ##print( ">>>>> ARG=[%s]" % (arg) )
    print( "%s: ERROR - Command Line Error. Unsupported single arg: [%s]" % (myname,arg) )
    usage(2)

  ## opts (pairs of opt/arg in form: -<opt> <arg>)
  ##print( "OPTS:", opts )
  for opt, arg in opts:
    ##print( ">>>>> OPT=[%s]  ARG=[%s]" % (opt, arg) )
    if opt in ('-h', '--help'):
      usage(0)
    elif opt in ('-d', '--debug'):
      DEBUG = arg
    elif opt in ('-m', '--myvar'):
      MY_VAR = arg
    else:
      print( "%s: ERROR - Command Line Error - Unrecognized opt-arg: [%s %s]" % (myname, opt, arg) )
      usage(2)


  if not MY_VAR:
      print( "%s: ERROR - Missing required input: [my_var]" % (myname) )
      usage(2)
