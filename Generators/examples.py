"""

  Example generator functions

"""

##---------------------------------------------------------
def gen_counter (max):
    i = 0
    while i <= max:
        yield i
        i += 1

##---------------------------------------------------------
def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1

##---------------------------------------------------------
def spell_word(word):
    for c in word:
        yield c 

##---------------------------------------------------------
def multi_yield():
    yield_1 = "This is result of first yield"
    yield yield_1
    yield_2 = "This is result of second yield"
    yield yield_2

##---------------------------------------------------------
def gen_counter_with_send(max):
    """
     Same as gen_counter() function above, but with send() support
    """
    i = 0
    while i < max:
        val = (yield i)
        # If value provided, change counter
        if val is not None:
            i = val
        else:
            i += 1

##---------------------------------------------------------
def ticker( start, interval):
    """Generate an unending stream of datetimes in fixed intervals.
    Useful to test processes which require datetime for each step.
    """
    current = start
    while True:
        yield current
        current += interval

##---------------------------------------------------------
def talk_gen(name):
    """
     Simple example to test send(), throw() and close()
     Notice we have to put the "if val is not None" after every yield - it only works for those yields that it follows.
    """
    talk_to = name
    while True:
      val = (yield "Hi there %s" % (talk_to))
      if val is not None:
         talk_to = val
      val = (yield "How are you %s?" % (talk_to))
      if val is not None:
         talk_to = val
      val = (yield "Bye-bye %s" % (talk_to))
      if val is not None:
         talk_to = val

