"""

>>> import ticker
>>> import datetime 
>>> gen = ticker.ticker(datetime.datetime(2020, 1, 1, 15, 0, 0), datetime.timedelta(seconds=90))
>>> next(gen)
datetime.datetime(2020, 1, 1, 15, 0)
>>> next(gen)
datetime.datetime(2020, 1, 1, 15, 1, 30)
>>> next(gen)
datetime.datetime(2020, 1, 1, 15, 3)
>>> next(gen)
datetime.datetime(2020, 1, 1, 15, 4, 30)
>>> next(gen)
datetime.datetime(2020, 1, 1, 15, 6)

"""

def ticker(start, interval):
    """Generate an infinite stream of datetimes in fixed intervals.
    Useful to test processes which require datetime for each step.
    """
    current = start
    while True:
        yield current
        current += interval



