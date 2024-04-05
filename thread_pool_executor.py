#!/usr/bin/env python3

from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from concurrent.futures import TimeoutError

"""
 The ThreadPoolExecutor in Python provides a pool of reusable threads for executing ad hoc tasks.
 You can submit tasks to the thread pool by calling the submit() function and passing in the name of
 the function you wish to execute on another thread.  Calling the submit() function will return a
 Future object that allows you to check on the status of the task and get the result from the task
 once it completes.  In some applications, you may need to process results from tasks in the order
 that tasks finish their execution, and not in the order that tasks were submitted to the thread pool.
 This is where the as_completed() method and Future object come in.  This will allow your program to
 be more responsive to the tasks and perhaps show progress and results to the user sooner than process
 results in the order that tasks were submitted

 as_completed() takes an optional timeout to limit the amount of time to wait for the first completed
 task If the first task takes more than the timeout number of seconds to complete after calling the
 as_completed() function, then a TimeoutError will be raised that may need to be handled.
 A task is “completed” for one of three reasons; they are:
 * The task was completed successfully.
 * The task was cancelled.
 * The task raised an exception that was not handled.
 The function takes a collection of Future objects and will return the same Future objects in the
 order that their associated tasks are completed.

 Expected results:
 * with timeout set:
   Timed out waiting for a result: 10 (of 10) futures unfinished
 * with timeout not set:
   Task=worker-7: 0.24
   Task=worker-8: 0.30
   Task=worker-6: 0.36
   Task=worker-3: 0.43
   Task=worker-5: 0.60
   Task=worker-4: 0.64
   Task=worker-2: 0.68
   Task=worker-9: 0.80
   Task=worker-1: 0.85
   Task=worker-0: 0.96

"""

N_workers = 10  # total number of workers in the thread pool
as_completed_timeout_secs = 0.05
#as_completed_timeout_secs = None

# custom task that will sleep for a variable amount of time
def task(name):
    # sleep for less than a second
    value = random()
    sleep(value * 10)
    return f'Task={name}: {value:.2f}'
 
# start the thread pool
with ThreadPoolExecutor(N_workers) as executor:
    # submit tasks and collect futures
    futures = [executor.submit(task, f"worker-{i}") for i in range(N_workers)]
    # handle a timeout waiting for the first result
    try:
        # process task results as they are available
        for future in as_completed(futures, timeout=as_completed_timeout_secs):
            # retrieve the result
            result = future.result()
            print(result)
    except TimeoutError as e:
        print(f'Timed out waiting for a result: {e}')
