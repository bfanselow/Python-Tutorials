"""

 Threading with Events

 Key concepts:
  * Event
    An event manages a flag that can be set to true with the set() method and reset to false with the
    clear() method. Threads making a wait() call will block until the flag is true. The flag is initially
    false.

  * wait(timeout=None)
    Block until the internal flag is true. If the internal flag is true on entry, return immediately.
    Otherwise, block until another thread calls set() to set the flag to true, or until the optional
    timeout (floating point number) occurs.  Returns True if and only if the internal flag has been
    set to true, either before the wait call or after the wait starts, so it will always return True
    except if a timeout is given and the operation times out.

"""

import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-9s) %(message)s',)
                    
def wait_for_event(e):
    logging.debug('wait_for_event starting')
    event_is_set = e.wait()
    logging.debug('event set: %s', event_is_set)

def wait_for_event_timeout(e, t):
    while not e.isSet():
        logging.debug('wait_for_event_timeout starting')
        event_is_set = e.wait(t)
        logging.debug('event set: %s', event_is_set)
        if event_is_set:
            logging.debug('processing event')
        else:
            logging.debug('doing other things')

if __name__ == '__main__':
    e = threading.Event()
    t1 = threading.Thread(name='blocking', 
                      target=wait_for_event,
                      args=(e,))
    t1.start()

    t2 = threading.Thread(name='non-blocking', 
                      target=wait_for_event_timeout, 
                      args=(e, 2))
    t2.start()

    logging.debug('Waiting before calling Event.set()')
    time.sleep(8)
    e.set()
    logging.debug('Event is set')
