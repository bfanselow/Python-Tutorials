"""

  stdlib_mock_test.py

  Demonstration of mocking method calls from Python's standard library.

  Usage:
   $ python3 -m pytest -v Python/mocktest.py

"""
import os.path
import pytest
from unittest.mock import patch



FAKE_FILE = './fakefile'
SIZE = 2*1024*1024

def my_isfile(filename):
    """Test function which calls (mocked) os.path.isfile"""
    if os.path.isfile(filename): #  returns True from mocking
        return "Yes"
    else:
        return "No"


@patch('os.path.getsize')
@patch('os.path.isfile')
def test_isfile_return_value(mock_isfile, mock_getsize):
    """
    Mocking os.path.isfile and using return_value.
    Note the order of args to test method - think of the patch "stack" as tipping over to the right
    to give the arg order.
    """
    mock_isfile.return_value = True
    mock_getsize.return_value = SIZE 
    assert os.path.isfile(FAKE_FILE) is True
    assert os.path.getsize(FAKE_FILE) == SIZE
    assert my_isfile(FAKE_FILE) == 'Yes'


@patch('os.path.isfile')
def test_isfile_side_effect(mock_isfile):
    """Mocking os.path.isfile with using side_effect"""
    def side_effect(filename):
        if filename == 'foo':
            return True
        else:
            return False

    mock_isfile.side_effect = side_effect
    assert my_isfile('foo') == 'Yes'
    assert my_isfile(FAKE_FILE) == 'No'
