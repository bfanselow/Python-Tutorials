  
tasks = {}
task = lambda f: tasks.setdefault(f.__name__, f)

class TaskHandler():
  def __init__(self):
      self.cname = self.__class__.__name__
      print("%s: Finished initialization" % (self.cname))


  @staticmethod
  @task
  def task1(*args):
      print(f"Executing task1 {args}")

  @staticmethod
  @task
  def task2(*args):
      print(f"Executing task2 {args}")

  def func_wrapper(self, key):
      arg1 = 'foobar'
      tasks[key](arg1)


if __name__ == '__main__':
  th = TaskHandler()
  for task in ['task1', 'task2', 'task3']:
      try:
          th.func_wrapper(task)
      except KeyError:
          print(f"ERROR - No such task: {task}")
