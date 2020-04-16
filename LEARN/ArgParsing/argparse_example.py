#!/usr/bin/env python3
"""
  File: argparse_example.py
  Description: Example of using "argparse" module to parse input args
  Test with $./argparse_example.py -h

  Pros: Less manual coding necessary. More built-in logic
  Cons: Less customizable than working with getopt

"""

import argparse

import os
import sys

myname = os.path.basename(__file__)

DEBUG = 0
VERBOSITY = 0
MY_VAR = None

# Create the parser with a description of what the script does, optional prog-name, and optional usage
my_parser = argparse.ArgumentParser( prog=myname, 
                                     usage='%(prog)s [options] <path>',
                                     description='List content of specified path'
                                    )

# Add the arguments
my_parser.add_argument(
                        'Path',                  ## input arg gets assigned to this args.<property> 
                        metavar='path',
                        type=str,                ## input arg data-type
                        help='the path to list'
                      )

my_parser.add_argument(
                        '-d', '--debug',                 
                        required=False,
                        metavar='debug',
                        type=int,
                        choices=[0,1,2],
                        help='set debug level'
                      )
my_parser.add_argument(
                        '-v',
                        required=False,
                        action='count',
                        help='set verbosity level'
                      )
my_parser.add_argument(
                         '-l', '--long',
                         action='store_true',
                         help='enable the long listing format'
                      )
## Required named args are not supported by argparse by default as it considers this bad practice
## and that named args should be optional, vs required args as positional.
## This can be overridden with the following:
requiredNamed = my_parser.add_argument_group('required named arguments')
requiredNamed.add_argument(
                           '--myvar',
                           action='store',
                           required=True,
                           metavar='myvar',
                           type=str,
                           choices=['heads', 'tails', 'fails'],
                           help='set a required test-var'
                         )

# Execute the parse_args() method
args = my_parser.parse_args()
print("%s: INPUT-ARGS: %s" % (myname, vars(args)))

input_path = args.Path
if args.debug:
  DEBUG = args.debug

if args.v:
  VERBOSITY = args.v

if not os.path.isdir(input_path):
    print('The path specified does not exist')
    sys.exit()

if VERBOSITY >= 2:
  print("Contents of dir: \"%s\"" % (args.Path))

for line in os.listdir(input_path):
    if args.long:  # Simplified long listing
        size = os.stat(os.path.join(input_path, line)).st_size
        mode = os.stat(os.path.join(input_path, line)).st_mode
        line = '%10d  %10d  %s' % (mode, size, line)
    print(line)
