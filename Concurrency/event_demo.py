#!/usr/bin/env python3

"""

 Example of using an Event object - one of the simplest mechansims for communication/synchronization between threads.
 One thread signals an event and the other threads with for it.  Threads sharing the event instance can check if the
 event is set, set the event, clear (un-set) the event, or wait for the event to be set

 Key concepts:
  * Create a shared "event" object and pass it to all threads. It will be in an "un-set" state.
  * The event object can be "set" via the event.set() method (not used in example below).
  * Threads can check event.is_set() to determine if they should do things, or they can call event.wait() to wait for
    the event object to be set (by main). This allows one thread to block the other thread's work until a specific time.
  * A “timeout” argument can be passed to the wait() function which will limit how long a thread is willing to wait for
    the event to be marked as set.
  * Event object can be "un-set" via the event.clear() method (not used in example below).

  Play around with diffent values of MAIN_BLOCK_TIME_SECS and THREAD_WAIT_TIME_SECS to observe how various scenarious
  can be coded.

"""
import sys
from time import sleep
from random import random
from threading import Event, Thread, currentThread

MAIN_BLOCK_TIME_SECS = 6  # how long main thread waits to set event object
THREAD_WAIT_TIME_SECS = 3  # how long child threads wait for event object to be set before timing out

def worker_task(event, number):
    """
     Target "task" function.
     Takes a tuple of args - in this case the "event" object and the iteration number.
     Task work is triggered by the setting of the event object. Work is just a random value sleep.
    """
    tname = currentThread().getName()  # could have just used something like f"worker-{(i+1)}"
    id = f" Thread-{number} ({tname})"

    def _do_my_work():
        print(f" {id}: Starting my work...")
        value = random()
        sleep(value)
        print(f" {id}: got random value={value}")


    # I will block here while waiting for the event to be "set". When the event has been
    # set, this is my trigger to start doing things.
    print(f" {id}: Listening/waiting for set()")

    # If event-wait-timeout is None, I will wait indefinitely for event to be set. Otherwise, I will stop waiting.
    # The wait() function will return True if the event was set while waiting. Otherwise a value of False is returned
    # indicating that the event was not set and the call timed-out.
    set = event.wait(timeout=THREAD_WAIT_TIME_SECS)

    if set:
        # begin processing
        _do_my_work()
    else:
        print(f" {id}: Got tired of waiting after {THREAD_WAIT_TIME_SECS} secs...")
        if number == 3:
            print(f" {id}: I'm a rebel and am going to do my thing even though I never got permission!")
            _do_my_work()


if __name__ == '__main__':

    if len(sys.argv) > 1:
        MAIN_BLOCK_TIME_SECS = int(sys.argv[1])

    # Create a shared event object
    event = Event()

    # Create a suite of threads, and start them.  Sort of redundant to pass the name kwarg, as we can just as easily
    # pass something in args tuple and construct a name in the thread itself.
    for i in range(5):
        thread = Thread(target=worker_task, name=f"worker-{(i+1)}", args=(event, i))
        thread.start()

    # Main thread continues...
    # Block for a moment, before setting the event object. Meanwhile, all child threads are waiting for the event to be set.
    print(f"Main: blocking all threads from starting for {MAIN_BLOCK_TIME_SECS} secs...")
    sleep(MAIN_BLOCK_TIME_SECS)

    # Set the event object - trigger the start of processing in all threads
    print('Main: Setting event...')
    event.set()

    # Main thread waits for all the threads to finish...
