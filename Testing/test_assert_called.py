"""

 Demonstration of the pytest *_called_* methods to mock system calls of Class method calls.

 Normal operation of Something Class:
    >>> from test_assert_called import Something
    >>> sm = Something("New")
    >>> sm.do()
    Doing Something New
    >>> sm.ls()
    Listing files...
    ['README.md', 'sqlite_test.py', 'mapper.py', 'calltest.py', 'mocktest.py', 'call_by_str.py']

 pytest: 
 $ python3 -m pytest -sxv test_assert_called.py


"""
import os
from mock import patch, call, Mock


class Something():
    def __init__(self, mode="Old"):
        self.mode = mode

    def do(self):
        print(f"Doing Something {self.mode}")
    
    def lsd(self, useless_arg):
        print(f"Listing files... Got arg={useless_arg}")
        l = os.listdir()
        print(l)


class Nothing():
    def __init__(self, sm: Something = None):
        self._sm = sm 

    def happens(self, myarg="something"):
        if self._sm:
            print("Something will happen")
            self._sm.lsd(myarg)
        else: 
            print("Nothing happens!")
    


@patch('os.makedirs')
@patch('os.listdir')
def test_something_system_call(listdir, makedirs):
    """ 
      Here we mock a system call using @patch decorator.
      Notice the order of patch directions relative to the order of args to test_() 
    """
    sm = Something("New")
    sm.lsd('foo')
    listdir.assert_called_once()


def test_something_cls_method_call():
    """ Here we mock a Class method using assert_has_calls() """
    sm: Something = Mock()
    no = Nothing(sm) 
    no.happens()
    no.happens('again')
    no._sm.lsd.assert_has_calls([call('something'), call('again')]) 


