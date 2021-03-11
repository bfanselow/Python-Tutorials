
"""
  Module: resource_lock.py
  Primary Class: ResourceLock
  Support Classes: SharedLock, ExclusiveLock

  This class provides a resource-locking object that allows multiple
  simultaneous SHARED locks and a single EXCLUSIVE lock for use in
  scenarios like the “One-writer, many-readers” problem.

  Concepts taken from:
    https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s04.html

  Usage:
    from resource_lock import ResourceLock
    ...

    #
    # Using direct acquire/release:
    #
    rl = ResourceLock
    def multi_reader_operations():
        # multiple threads can call this method concurrently which
        # will block on any thread trying to modify the resource.
        rl.acquire_shared()
        ...do shared-lock work
        rl.release_shared()
    ...
    def single_writer_operations():
        # a single thread can call this method to modify the resource
        # which will block any others threads from accessing the resource.
        rl.acquire_exclusive()
        ...do exclusive-lock work
        rl.release_exclusive()
    #
    # Or using context-managers by instantiating supporting classes of ResourceLock
    #
    rl = ResourceLock
    def multi_reader_operations():
        with SharedLock(rl) as slock:
           ...do shared-lock work
    ...
    def single_writer_operations():
        with ExclusiveLock(rl) as xlock:
           ...do exclusive-lock work

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
  on a "wait" condition on the object. In this recipe the only way a thread
  can get into such a wait is in the acquire_exclusive() method, when it
  finds there are shared-lock holders active after acquiring the lock. The
  wait call on the Condition object releases the underlying lock, so
  release_shared() methods can execute, but reacquires it again before waking
  up. So, acquire_exclusive() can safely keep checking whenever it wakes up
  to see if it’s finally in a "no-shared-lock-holders" situation. When that
  happens, acquire_exclusive() returns to its caller, but keeps the lock,
  so no other shared or exclusive lock can be acquired, until the
  release_exclusive() is called, which lets the lock go again.

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
import logging
import threading

logger = logging.getLogger(__name__)


class ResourceLock:

    def __init__(self):
        self.lock = threading.Condition(threading.Lock())
        self.shared_lock_holders = 0

    def acquire_shared(self):
        """
        Acquire a SHARED lock. Blocks only if a thread has
        acquired the EXCLUSIVE lock.
        """
        self.lock.acquire()
        try:
            self.shared_lock_holders += 1
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
        Acquire the EXCLUSIVE lock.
        Blocks until there are no acquired EXCLUSIVE or SHARED locks.

        wait() can only be called when the calling thread has the lock.
        It is used to block the thread and make it wait until some
        other thread notifies it by calling notify() or notifyAll()
        on the same condition object or until the timeout occurs.
        It returns True if it is released by notify*() or False on timeout.
        """
        self.lock.acquire()
        while self.shared_lock_holders > 0:
            logging.debug("WAITING on shared-lock holders to release")
            self.lock.wait()  # TODO: could add timeout to wait

    def release_exclusive(self):
        """ Release the EXCLUSIVE lock. """
        self.lock.release()


class SharedLock():
    """provide context manager for SHARED ResourceLock"""
    def __init__(self, resource_lock):
        self.lock = resource_lock

    def __enter__(self):
        self.lock.acquire_shared()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.lock.release_shared()
        return False  # raise exception if exited due to an exception


class ExclusiveLock():
    """provide context manager for EXCLUSIVE ResourceLock"""
    def __init__(self, resource_lock):
        self.lock = resource_lock

    def __enter__(self):
        self.lock.acquire_exclusive()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.lock.release_exclusive()
        return False  # raise exception if exited due to an exception


# TESTING
if __name__ == '__main__':

    import time
    from random import randrange

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s: (%(threadName)-9s) %(message)s',)

    def reader_job(tname, lock):
        sleep = 1
        logging.debug("%s: Reader started job (%d seconds)" % (tname, sleep))
        print(lock.__dict__)
        time.sleep(sleep)
        logging.debug("%s: Reader finished" % tname)

    def writer_job(tname, lock):
        sleep = randrange(4)
        logging.debug("%s: Writer started job (%d seconds)" % (tname, sleep))
        print(lock.__dict__)
        time.sleep(sleep)
        logging.debug("%s: Writer finished" % tname)

    #
    # test use of ResourceLock object directly with acquire/release methods
    #
    def multi_reader_operations(tname, lock):
        logging.debug("%s: Reader checking lock..." % tname)
        lock.acquire_shared()
        reader_job(tname, lock)
        lock.release_shared()
        logging.debug("%s: Reader leaving" % tname)

    def single_writer_operations(tname, lock):
        logging.debug("%s: Writer checking lock..." % tname)
        lock.acquire_exclusive()
        reader_job(tname, lock)
        lock.release_exclusive()
        logging.debug("%s: Writer leaving" % tname)

    #
    # test use SharedLock, ExclusiveLock objects as context managers
    #
    def cm_multi_reader_operations(tname, lock):
        logging.debug("%s: Reader checking lock..." % tname)
        with SharedLock(lock) as slock:
            reader_job(tname, slock.lock)
        logging.debug("%s: Reader leaving" % tname)

    def cm_single_writer_operations(tname, lock):
        logging.debug("%s: Writer checking lock..." % tname)
        with ExclusiveLock(lock) as xlock:
            writer_job(tname, xlock.lock)
        logging.debug("%s: Writer leaving" % tname)

    rl = ResourceLock()
    for i in range(50):
        pick = randrange(12)

        # create a small number of writers occasionally
        if pick < 3:
            name = f'writer-{i}'
            # writer = threading.Thread(name=name, target=single_writer_operations, args=(name, rl, ))
            writer = threading.Thread(name=name, target=cm_single_writer_operations, args=(name, rl, ))
            writer.start()
        # create lots of readers freqently
        else:
            name = f'reader-{i}'
            # reader = threading.Thread(name=name, target=multi_reader_operations, args=(name, rl, ))
            reader = threading.Thread(name=name, target=cm_multi_reader_operations, args=(name, rl, ))
            reader.start()
            if pick > 9:
                time.sleep(3)
