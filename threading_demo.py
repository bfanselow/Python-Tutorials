import argparse
import threading
import time
import logging
"""

  Illustration of Thread join([timeout])
  Wait until the thread terminates. This blocks the calling thread until termination of the thread whose join() method
  is called – either normally or through an unhandled exception – or until the optional timeout occurs.


  without join:
  +---+---+------------------                     main-thread
      |   |
      |   +...........                            child-thread(short)
      +..................................         child-thread(long)

  with join
  +---+---+------------------***********+###      main-thread
      |   |                             |
      |   +...........join()            |         child-thread(short)
      +......................join()......         child-thread(long)

  with join and daemon thread
  +-+--+---+------------------***********+###     parent-thread
    |  |   |                             |
    |  |   +...........join()            |        child-thread(short)
    |  +......................join()......        child-thread(long)
    +,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,     child-thread(long + daemonized)

  '-' main-thread/parent-thread/main-program execution
  '.' child-thread execution
  '#' optional parent-thread execution after join()-blocked parent-thread could
      continue
  '*' main-thread 'sleeping' in join-method, waiting for child-thread to finish
  ',' daemonized thread - 'ignores' lifetime of other threads;
      terminates when main-programs exits; is normally meant for
      join-independent tasks


 Daemon threads are abruptly stopped at shutdown. As such, their resources (such as open files, database transactions, etc.)
 may not be released properl

"""


logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)


def short_work(sleep=1):
    logging.debug('Starting')
    time.sleep(sleep)
    logging.debug('Exiting')

def long_work(sleep=5):
    logging.debug('Starting')
    time.sleep(5)
    logging.debug('Exiting')


def test_daemon_no_join():
    """
    Output:

    Notice we do not get an "Exiting" message from the daemon thread, since all of the non-daemon
    threads (i.e. main thread) exit before the daemon thread wakes up from its sleep.
    """
    print("\nTEST-DAEMON-NO-JOIN")

    d_thread = threading.Thread(name='daemon', target=long_work)
    d_thread.setDaemon(True)
    d_thread.start()

    print("[main] all threads started")
    short_work(2)
    print("[main] done with main work")

def test_daemon_with_join():
    """
    Output:

    Notice "main" work doesn't start until spawned thread has returned.
    We do get an "Exiting" message from the daemon thread since the join() blocks the calling thread
    (main thread) until the thread (whose join() method is called) is terminated.

    """
    print("\nTEST-DAEMON-WITH-JOIN")
    d_thread = threading.Thread(name='daemon', target=long_work)
    d_thread.setDaemon(True)
    d_thread.start()
    print("[main] all threads started")

    short_work(2)
    print("[main] done with main work")
    d_thread.join()  # blocks until d_thread is returned

def test_non_daemon_with_join():
    """
    Output:

    This looks identical to the output of test_daemon_with_join().

    """
    print("\nTEST-NON-DAEMON-WITH-JOIN")
    n_thread = threading.Thread(name='non-daemon', target=long_work)

    n_thread.start()
    print("[main] all threads started")

    n_thread.join()  # blocks until n_thread has returned

    short_work(2)
    print("[main] done with main work")

def test_non_daemon_no_join():
    """
    Output:
    """
    print("\nTEST-NON-DAEMON-NO-JOIN")
    n_thread = threading.Thread(name='non-daemon', target=long_work)

    n_thread.start()
    print("[main] all threads started")
    short_work(2)
    print("[main] done with main work")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--dnj", action='store_true')   # daemon-no-join
    parser.add_argument("--dwj", action='store_true')   # daemon-with-join
    parser.add_argument("--ndwj", action='store_true')  # non-daemon-with-join
    parser.add_argument("--ndnj", action='store_true')  # non-daemon-no-join
    args = parser.parse_args()

    if args.dnj:
        test_daemon_no_join()
    elif args.dwj:
        test_daemon_with_join()
    elif args.ndnj:
        test_non_daemon_no_join()
    elif args.ndwj:
        test_non_daemon_with_join()
    else:
        print("No test-id provided")
