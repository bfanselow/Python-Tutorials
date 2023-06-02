# Threading, Race-conditions and Locks
A **thread** is the smallest unit of processing that can be performed in an Operating System. Both processes and threads are created and managed by the operating system. A process consists of one or more threads - each one a sequence of such instructions within the program that can be executed independently of other codes. 

Every Python program has at least one thread of execution called the *main thread*. Sometimes we may need to create additional threads in our program in order to execute code concurrently.

We can create and manage new Python threads via the **threading** module and the **threading.Thread** class.

When writing concurrent programs we may need to share data or resources between threads.  Multi-threaded code that shares a resource is vulnerable to **race conditions**.  A race condition is a bug in concurrency programming. It is a failure case where the behavior of the program is dependent upon the order of execution by two or more threads. This means, the behavior of the program will not be predictable, possibly changing each time it is run. 

Any section of code that may be executed by two or more threads concurrently may be at risk of a race condition. There are many types of race conditions, although a common type of race condition is when two or more threads attempt to change the same data variable.

**NOTE**: Race conditions can be a problem in Python when using mutlitple threads, even in the presence of the global interpreter lock (GIL). After learning about the global interpreter lock (GIL), many new Python programmers assume they can forgo using mutual-exclusion locks (see below) in their code altogether. If the GIL is already preventing Python threads from running on multiple CPU cores in parallel, it must also act as a lock for a program’s data structures, right? Some testing on types like lists and dictionaries may even show that this assumption appears to hold. But beware, this is not truly the case. The idea that there are no race conditions in Python because of the GIL is dangerously wrong. Even the simplest operations running concurrently by multiple threads can be vunerlable. For example, one thread may be adding values to a variable, while another thread is subtracting values from the same variable.

Let’s call them an adder thread and a subtractor thread. 
```
...
# addder thread
variable = variable + 10
```
```
...
# subtracter thread
variable = variable + 10
```
The operating system controls what threads execute and when, performing a **context switch** to pause the execution of a thread and store its state, while unpausing another thread and restoring its state.

The adding or subtracting from the variable is actually composed of at least three steps:

 1. Read the current value of the variable.
 2. Calculate a new value for the variable.
 3. Write a new value for the variable.

The risk of race conditions is that a context switch between threads may occur at any point in this task. At some point, the operating system may context switch from the adding thread to the subtracting thread in the middle of updating the variable. Perhaps right at the point where it was about to write an updated value with an addition, say from the current value of 100 to the new value of 110. The subtracting thread runs and reads the current value as 100 and reduces the value from 100 to 90. The operating system context switches back to the adding thread and it picks up where it left off writing the value 110. This means that in this case, one subtraction operation was lost and the shared balance variable has an inconsistent value - a race condition.

There are many ways to fix race conditions. One common way is to synchronize the access to the shared resource between the two threads using a **lock**, typically referred to as *mutual exclusion lock*, or **mutex** for short.

A critical section can be protected by a mutex lock which will ensure that one and only one thread can access the variable at a time. This can be achieved by first creating a **threading.Lock** instance.
```
...
# create a lock
lock = threading.Lock()
```
When a thread is about to execute the critical section, it can acquire the lock by calling the **acquire()** function. It can then execute the critical section and release the lock by calling the **release()** function on the lock.
```
...
# acquire the lock
lock.acquire()
# add to the variable
variable = variable + 10
# release the lock
lock.release()
```
This can be made simpler using the threading.Lock as a context manager:
```
...
# acquire the lock
with lock:
	# add to the variable
	variable = variable + 10
# release the lock automatically
```

If one thread has acquired the lock, another thread cannot acquire it, therefore cannot execute a critical section and in turn cannot update the shared variable. Instead, any threads attempting to acquire the lock while it is acquired must wait until the lock is released. This waiting for the lock to be released is performed automatically within the call to acquire() - no need to do anything special. If the lock has not been acquired, we might refer to it as being in the “unlocked” state. Whereas if the lock has been acquired, we might refer to it as being in the “locked” state.
 * **Unlocked**: The lock has not been acquired and can be acquired by the next thread that makes an attempt.
 * **Locked**: The lock has been acquired by one thread and any thread that makes an attempt to acquire it must wait until it is released.

The thread attempting to acquire the lock will block until the lock is acquired, such as if another thread currently holds the lock then releases it.
We can attempt to acquire the lock without blocking by setting the “blocking” argument to False. If the lock cannot be acquired, a value of False is returned.
```
...
# acquire the lock without blocking
lock.acquire(blocking=false)
```
We can also attempt to acquire the lock with a timeout, that will wait the set number of seconds to acquire the lock before giving up. If the lock cannot be acquired, a value of False is returned.
```
...
# acquire the lock with a timeout
lock.acquire(timeout=10)
```
We can also check if the lock is currently acquired by a thread via the locked() function.
```
...
# check if a lock is currently acquired
if lock.locked():
    # ...
```

#### Example:
First, we can define a target task function that takes a lock as an argument and uses the lock to protect a critical section. In this case, the critical section involves reporting a message and blocking for a fraction of a second.
```
# work function
def task(lock, identifier, value):
    # acquire the lock
    with lock:
        print(f'>thread {identifier} got the lock, sleeping for {value}')
        sleep(value)
```
We can then create one instance of the threading.Lock shared among the threads, and pass it to each thread that we intend to execute the target task function.
```
...
# create a shared lock
lock = Lock()
# start a few threads that attempt to execute the same critical section
for i in range(10):
    # start a thread
    Thread(target=task, args=(lock, i, random())).start()
```
Tying this together:
```
# SuperFastPython.com
# example of a mutual exclusion (mutex) lock
from time import sleep
from random import random
from threading import Thread
from threading import Lock
 
# work function
def task(lock, identifier, value):
    # acquire the lock
    with lock:
        print(f'>thread {identifier} got the lock, sleeping for {value}')
        sleep(value)
 
# create a shared lock
lock = Lock()
# start a few threads that attempt to execute the same critical section
for i in range(10):
    # start a thread
    Thread(target=task, args=(lock, i, random())).start()
# wait for all threads to finish...
```
Running the example starts ten threads that all execute a custom target function. Each thread attempts to acquire the lock, and once they do, they report a message including their id and how long they will sleep before releasing the lock. Your specific results may vary given the use of random numbers.
```
>thread 0 got the lock, sleeping for 0.8859193801237439
>thread 1 got the lock, sleeping for 0.02868415293867832
>thread 2 got the lock, sleeping for 0.04469783674319383
>thread 3 got the lock, sleeping for 0.20456291750962474
>thread 4 got the lock, sleeping for 0.3689208984892195
>thread 5 got the lock, sleeping for 0.21105944750222927
>thread 6 got the lock, sleeping for 0.052093068060339864
>thread 7 got the lock, sleeping for 0.871251970586552
>thread 8 got the lock, sleeping for 0.932718580790764
>thread 9 got the lock, sleeping for 0.9514093969897454
```

## Advanced lock types

#### Re-entrant Lock (RLock)
An RLock differs from a regular (primitive) Lock in a few major ways:
 * *ownership* - a regular lock is not owned by a thread. It is "owned" by the block of code that aquires it.
 * *recursion level* - Each time a thread acquires the lock it must also release it, meaning that there are recursive levels of acquire and release for the owning thread.
 * *speed* - operations on regular locks can be slightly faster, though this is not usually enough to be important.
 
A regular Lock can only be acquired once. It cannot be acquired again, even by the same thread, until it is released. An RLock on the other hand, can be acquired multiple times, by the same thread. A counter is incremented each time it is acquired by the same thread. It needs to be released the same number of times in order to be "unlocked". Another difference is that an acquired Lock can be released by any thread, while an acquired RLock can only be released by the thread which acquired it.  A regular lock is susceptible to **deadlocks**. We can imagine critical sections spread across a number of functions, each protected by the same lock. A thread may call across these functions in the course of normal execution and may call into one critical section from another critical section.

A limitation of a (non-reentrant) mutex lock is that if a thread has acquired the lock that it cannot acquire it again. In fact, this situation will result in a deadlock as it will wait forever for the lock to be released so that it can be acquired, but it holds the lock and will not release it.

#### Example
A simple example can be seen with recursive code. Suppose a lock is used in a factorial function:
```
from threading import Lock

lock = Lock()

def factorial(n):
    assert n > 0
    if n == 1:
        return 1
    
    with lock:       
        out = n * factorial(n - 1)

    return out
```
This function will cause a dead lock due to the recursive call. If we use RLock instead, however, the recursive calls can reenter the same lock as many times as needed. Hence the name reentrant (or recursive) lock.


#### Read/Write Locks
https://github.com/bfanselow/Python-Tutorials/blob/master/resource_lock.py
