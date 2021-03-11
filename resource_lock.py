
""" 
  This class provides a resource-locking object that allows multiple 
  simultaneous SHARED locks and a single EXCLUSIVE lock for use in 
  scenarios like the “One-writer, many-readers” problem.

  Concepts taken from: 
    https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s04.html
  
  Usage:
    ...
    def check_resource_without_modfication():
        # mutliple threads can call this method concurrently which 
        # will block on any thread trying to modify the resource.
        with ResourceLock('shared') as slock:
           ...
    
    ...
    def modify_resource():
        # a single thread can call this method which will block 
        # any others threads from accessing the resource.
        with ResourceLock('exclusve') as xlock:
           ...

  Discussion:
  It is often convenient to allow unlimited threads to access a resource when
  it is not being modified while keeping resource-modification access exclusive. 
  In other words, multiple threads (i.e. "Readers") can share a shared (S) 
  lock which blocks other threads  from modifying the resource (i.e. "Writers"),
  while only one (Writer) thread can acquire an exclusive (X) lock which 
  blocks all other threads from all resource access.
  
  The class keeps track of the number of current shared-lock holders.  The 
  acquire_shared() and release_shared() methods increment/decrement this number.
  Synchronization is performed by a threading.Condition object created in 
  __init__() around thread Lock object.
  
  The notifyAll() method of a Condition object wakes up all threads that are 
  on a "wait" condition on the object. The only way a thread can get into such
  a wait is in the acquire_exclusive() method, when it finds there are 
  shared-lock holders active after acquiring the  lock. The wait call on the
  Condition object releases the underlying lock, so release_shared() methods
  can execute, but reacquires it again before waking up - acquire_exclusive()
  can safely keep checking whenever it wakes up to check if it’s finally in a
  "no-shared-lock-holders" situation. When that happens, acquire_exclusive()
  returns to its caller, but keeps the lock, so no other shared or exclusive
  lock can be acquired, until the release_exclusive() is called, which lets
  the lock go again.

  Note that this recipe offers no guarantee against a "starvation" situation
  where a Writer waits indefinitely, blocked by a steady stream of Readers
  arriving (even if no Reader keeps its shared lock for very long). If this
  is a problem in your specific application, you can avoid starvation by
  adding logic to ensure that new Readers don’t enter their lock if they
  notice that a Writer is waiting. However, this can result in penalizing
  Reader performance by making several Readers wait for one Pending writer.
  In most cases you can count on having periods when no Readers are holding
  shared locks and starvation is not an issue. 
 """

import threading

class ResourceLock:

    def __init__(self, type="shared"):
        self.lock = threading.Condition(threading.Lock())
        self.lock_type = type
        self.shared_lock_holders = 0

    def __enter__(self):
        if self.lock_type == "shared":
            self.acquire_shared()
        else:
            self.acquire_exclusive()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.lock_type == "shared":
            self.release_shared()
        else:
            self.release_exclusive()
        return False  # raise the exception if exited due to an exception

    def acquire_shared(self):
        """
        Acquire a SHARED lock. Blocks only if a thread has
        acquired the EXCLUSIVE lock.
        """
        self.lock.acquire()
        try:
            self.lock_holders += 1
        finally:
            self.lock.release()

    def release_shared(self):
        """ Release the SHARED lock. """
        self.lock.acquire()
        try:
            self.shared_lock_holders -= 1
            if not self.shared_lock_holders:
                self.lock.notifyAll()
        finally:
            self.lock.release()

    def acquire_exclusive(self):
        """
        Acquire hte EXCLUSIVE lock. 
        Blocks until there are no acquired EXCLUSIVE or SHARED locks.
        """
        self.lock.acquire()
        while self.shared_lock_holders > 0:
            self.lock.wait()

    def release_exclusive(self):
        """ Release the EXCLUSIVE lock. """
        self.lock.release()
