## CPython GIL

#### TL;DR
* GIL enforces that only a single thread is running at any given time. As such, python threads run in a (timeslicing) concurrency environment, instead of a true parallel environment.
* GIL prevents most, but not all race-conditions.
* When in doubt, use a lock whenever multiple threads can modify the same resource.


#### Race Condition
A race condition occurs when the behaviour of the system or code relies on the sequence of execution that is defined by uncontrollable events. In thread-safe code, the final result of operations performed by multiple threads is independent of the order in which the threads run.

#### Global Interpreter Lock (GIL)
This is exactly what the CPython GIL does. It prevents (most) race conditions by ensuring that only a single thread is running at any given time. This makes life easier for some Python programmers but at the same time it imposes a limitation since multi-core systems cannot be exploited in the context of threading.
Due to the GIL, there is only ever one thread per process active to execute Python bytecode; the bytecode evaluation loop is protected by it.
The lock is released every ```sys.getswitchinterval()``` seconds, at which point a thread switch can take place. This means that for Python code, a thread switch can still take place, but only between byte code instructions. Any code that relies on thread safety needs to take this into account. Actions that can be done in one bytecode can be thread safe, everything else is not.


Due to the GIL, a Python process cannot run threads in parallel but it can run them concurrently through context switching during I/O bound operations. Note that parallelism and concurrency may sound equivalent terms but in practice they are not.
If you want to take advantage of the computational power of multi-processor and multi-core systems, you may need to take a look at the multiprocessing package that allows processes to be executed in parallel. This is typically useful when it comes to executing CPU-bound tasks.

Multi-processing side-steps the Global Interpreter Lock as it allows for every process spawned to have its own interpreter and thus its own GIL.

The concept of GIL is not ideal given that in certain scenarios modern multiprocessor systems cannot be fully exploited. At the same time though, many long-running or blocking operations are being executed outside the GIL. Such operations include I/O, image processing and NumPy number crunching. Therefore, a GIL becomes a bottleneck only in multithreaded operations that spend time inside the GIL itself.

Having the GIL does **NOT** mean you can write code without thinking about race conditions.  For example:
this code is absolutely, demonstrably not threadsafe. It fails consistently.

```
import threading

i = 0

def test():
    global i
    for x in range(100000):
        i += 1

threads = [threading.Thread(target=test) for t in range(10)]
for t in threads:
    t.start()

for t in threads:
    t.join()

assert i == 1000000, i
```

i += 1 resolves to four opcodes: load i, load 1, add the two, and store it back to i. The Python interpreter switches active threads (by releasing the GIL from one thread so another thread can have it) every 100 opcodes. (Both of these are implementation details.) The race condition occurs when the 100-opcode preemption happens between loading and storing, allowing another thread to start incrementing the counter. When it gets back to the suspended thread, it continues with the old value of "i" and undoes the increments run by other threads in the meantime.
Making it threadsafe is straightforward; add a lock:

```

import threading

i = 0
i_lock = threading.Lock()

def test():
    global i
    i_lock.acquire()
    try:
        for x in range(100000):
            i += 1
    finally:
        i_lock.release()

threads = [threading.Thread(target=test) for t in range(10)]
for t in threads:
    t.start()

for t in threads:
    t.join()

assert i == 1000000, i
```

Due to the internals of the Cpython implementation, it is hard to determine what is thread-safe. For example, even though ``` i += 1``` is not thread-safe,  ```l += [1]```  is thread-safe, but ```l = l + [1]``` is not.
This is because ```+=``` compiles to an INPLACE_ADD bytecode. However, the implementation of INPLACE_ADD for list objects is written entirely in C (no Python code is on the execution path, so the GIL can't be released between bytecodes).

There's no way to know without becoming an expert on each implementation: testing alone can never prove the absence of race-related bad behaviors. For example, there have been subtle threading bugs in CPython's implementation that went undiscovered for years, until some unlikely combination of HW, OS and workload just happened to provoke races that were always possible but were just never seen before.

#### Bottom line!
Instead of guessing at the undocumented implementation details of CPython, use a mtuex/lock when in doubt.
A **lock** allows only one thread to enter the part that's locked and the lock is not shared with any other processes.
A **mutex** is the same as a lock but it can be system wide (shared by multiple processes).

#### Note on threading.lock
By default, ```lock.acquire()``` will block execution of the thread until the lock is released by a different thread. If you pass ```blocking=False``` to the function, the call will not block, and will return immediately. Its return value specifies whether or not your thread has actually acquired the lock. This can be useful in some locking scenarios.


