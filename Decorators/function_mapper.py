
"""

  Demonstrating use of mapping execution of a function based on a (string) name.
  This pattern provides a nice way to avoide the responsibility of keeping function
  names in sync with dictionary keys.

"""


tasks = {}
task = lambda f: tasks.setdefault(f.__name__, f)


@task
def task1():
    print("Executing task1")

@task
def task2():
    print("Executing task2")


def func_wrapper(key):
    tasks[key]()

for task in ['task1', 'task2', 'task3']:
    try:
        func_wrapper(task)
    except KeyError:
        print(f"ERROR - No such task: {task}")
