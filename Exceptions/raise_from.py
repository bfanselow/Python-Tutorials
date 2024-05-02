#!/usr/bin/python3

"""
 python2 doesn't support raise from sytnax, so here's a solution to do the equivalent 
 in python2
"""


import traceback
import logging
import sys


class MyCustomException(Exception):
    pass

def raise1():
    raise ValueError("This error reported from raise1")


def raise2():
    try:
        raise1()
    except Exception as e:
        if sys.version_info.major == 2:
            tb = traceback.format_exc()
            raise MyCustomException("This error reported from raise2", tb)
        raise MyCustomException("This error reported from raise2") from e

if __name__ == '__main__':
    try:
        raise2()
    except Exception:
        logging.exception("This log from main")
