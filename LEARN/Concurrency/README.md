# Concurrency

### Demonstration script (*webscrape_comparison.py*) require:
 * Python 3.6+ 
 * pip install -r requirements.txt

---

### Concurrency basically means *"progressing at the same time"*, which is not necessarily in a true *parallel* fashion.

### Three types of concurrency in Python
 * **multi-processing**
 * **multi-threading**
 * **asynio**

To demonstrate all three types and compare the duration for downloading content from numerous websites:
```
 $ ./webscrape_comparison.py
Reading url list from file: ./url_list
Starting Serial download of 80 sites...
Serial download of 80 sites - Duration: 13.019717931747437 seconds

Starting Multi-Threading download of 80 sites...
Multi-Threaded download of 80 sites - Duration: 2.2723982334136963 seconds

Starting Multi-Processing download of 80 sites...
System CPU count: 2
Multi-Processing download of 80 sites - Duration: 7.227595329284668 seconds

Starting Asyncio download of 80 sites...
AsyncIO download of 80 sites - Duration: 1.2234148979187012 seconds
```

## Concurrency Discussion
Each type of concurrency has its own strenghts and weaknesses. Choosing which type to use depends on the type of problem:
 - **multi-processing** is best suited for CPU bound problems (multi-processing)
 - **multi-threading** and **asyncio** are best suited for I/O bound problems. They actaully slow things down for CPU bound problems! 

### multi-processing
  Separate *processes* can progress at the same time. They can even  be *statrted* and progress in **parallel** on a multi-core system.  On a single core system the processes will progress at the same time by context swithing (i.e. time sharing).  If the processes are CPU bound (cpu instensive, very little cpu waiting) then there is no real benefit. However, if the processes have I/O bound (cpu spends lots of time idle waiting for I/O operations), then there can be signficate time savings on either single or multi core system.

**ADVANTAGES**:   
 * True parallelism IF the system has multiple processors (i.e. multi-core). Both other forms of concurrency only utilize a single core (due to Python's GIL).
 * Huge time savings when dealing with CPU bound problems.

**DISADVANTAGES**:   
 * Higher resource cost than threads since a full copy of the resources (code, file-handles, memory-stack, etc) is mades for each process.
 * Generally not as fast as multi-threading or asyncio (due to extra overhead) when dealing with I/O bound problems.
 * Compared to multi-threaing much harder to communicate between the multiple processes than between threads.

-----------
### multi-threading (a.k.a. pre-emptive multi-tasking)
  Separate *threads* can progress at the same time. In Python (due to GIL) threads are not actaully started (or progressing) in parallel. Rather, OS performs context switching between them on a single core. For I/O heavy processes this can be a big time savings (much like multi-processing on a single core).  Multi-tasking is "pre-emptive" meaning the OS decides when to switch regradless of where the thread is in the code - this can be somewhat inefficient especially as thread count goes up. Imagine 5 threads which each will perform a heavy IO tasks and then process the IO result:  T1,T2,T3,T4,T5 are started, with OS switching between each thread in a loop using a time-sharing mechanism. Suppose it switches to T1 which is still waiting on some I/O task. Just as it switches to T2, T1 finishes it's IO task but the next task in T1 cannot proceed. The OS context-switches to T3 (still waiting on IO), then T4 (still waiting), then T5 still (waiting). Finally it gets back around to T1. T1 is n o longer waiting and the next task in T1 can be executed. However, lots of time was spent on the pre-emptive context-switching. 

**ADVANTAGES**:   
 * Lower resource cost than processes as a single copy of code/memory stack is shared among all threads.
 * Compared to mutli-processing is far easier to communicate between the various threads.
 * Compared to mutli-processing is generally faster for I/O bound problems.
 * Compared to asyncio, context-switching is done for you which can be nice in simple scenarios.

**DISADVANTAGES**:   
  * Threads can interact in ways that are subtle and hard to detect. In particular, race conditions often result in random, 
    intermittent bugs that are difficult to find. Proper usage of thread-locks (or thread-local) variables is critical.
  * Compared to asyncio, context-switching is pre-emptive which can be less efficient is some scenarios. 

-----------
### asyncio (a.k.a cooperative multi-tasking)
 Separate *tasks* can progress at the same time. Much like multi-threading tasks are not actaully started (or progressing) in parallel. The OS performs context-switching between them on a single core (due to GIL).  However, unlike multi-threading asyncio uses "cooperative" multi-tasking in which tasks accounce that they are ready to be swithced out. This can be extra work for the programmer, but they will always know where in the code the tasks will be swapped.  (Requires python 3.4+) 

**ADVANTAGES**:    
  * Compared to multi-threading, allows you to know exactly where the code will shift from one task to the next making code less prone to race conditions. 
  * Compared to multi-threading less resource usages since each thread needs to have its own stack. With async code, all the code shares the same stack and the stack is kept small due to continuously unwinding the stack between tasks.
**DISADVANTAGES**:    
  * Difficult to learn, complex to code correctly. 


### See each **ws_<concurrency_type>.py** script for additional documentation on each concurrency type.
