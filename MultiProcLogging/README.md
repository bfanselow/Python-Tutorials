Description
===========
Python3 Class used to instantiate multiprocessing-queue logging objects. Such objects can then be passed to multiprocessing workers to provide a single, common file-logging facility for all the multiprocessing workers. 

Usage
======
(see __\_\_main\_\___ at bottom of MpQLogger.py for details)
1) Instantiate an MpQLogger object: mpql = MpQlogger(d_init)
2) Spawn multiprocess workers, passing the MPQL object to each one.
3) Each multiproc worker can log to shared logfile using syntax: mpql.log('\<LEVEL>\', \<msg>\)

Background
-----------
Using python (stdlib) logging is thread-safe, allowing mulitple threads (running in a single process) to write to single file. However, logging to a single file from multiple processes is not supported since there is no standard way to serialize access to a single file across multiple processes in Python. Passing a shared logger object to multiple sub-processes will appear (on the surface) to work just fine in simple low-load tests, but heavy logging from many processes (particularly with a RotatingFileHandler) is vulnerable to logfile corruption as multiple processes will invariably attempt to write to the file concurrently leading to interleaved writes by different processes.  There are a few options if you need to log to a single file from multiple processes. One method is to have all the processes log to a SocketHandler.  A simpler approach is to start up a multiprocessing Queue.  All sub-process objects put() their log message onto this queue while a queue listener will get() incoming messages off the queue write them to a single file using Logger. Since all concurreny issues are handled by the Queue, there is no danger of curruption. There are some gotchas associated with queue deadlocks which must be considered with this approach. I haven't considered all of these scenarios yet.
