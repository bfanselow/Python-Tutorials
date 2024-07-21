"""

  monkey_patching.py

  "Mocking" and "monkeypatching" are very similar in the context of testing.  Monkeypatching
  can be used as a form of test mocking, but also has a broader scope than just testing.

  This script will deomonstrate the use of monkeypatching (in pytest) to mock services.

  Execution:
    $ python3 -m pytest -v monkey_patching.py
    ===================== test session starts ===============================================
    platform linux -- Python 3.4.3, pytest-4.6.9, py-1.8.1, pluggy-0.13.1 -- /usr/bin/python3
    cachedir: .pytest_cache
    rootdir: /home/wfanselow/CODE-TESTS
    plugins: mock-2.0.0
    collected 3 items
    monkey_patching.py::test_get_current_directory PASSED                              [ 33%]
    monkey_patching.py::test_get_httpbin_origin_success PASSED                         [ 66%]
    monkey_patching.py::test_get_httpbin_origin_failure PASSED                         [100%]
    ===================== 3 passed in 0.14 seconds ===========================================

"""
import os
import requests

##========================================================================================
## Define some functions whose implementation details we will MOCK in our tests
##========================================================================================
def get_current_dir():
    """
     Retrieve the current directory
     Returns: Current directory
    """
    current_path = os.getcwd() ## this gets mocked
    return current_path

#---------------------
def get_httpbin_origin():
    """
    Call requests.get() for 'http://httpbin.org/get' and return some values from response
    Returns:
      * Status Code of the HTTP Response
      * "origin" from the HTTP Response
    """
    BASE_URL = 'http://httpbin.org'
    r = requests.get(BASE_URL + '/get') ## this get mocked
    key = "origin"

    ## this is what we will test below...
    if r.status_code == 200:
        response_data = r.json()
        return r.status_code, response_data[key]
    else:
        return r.status_code, ''

##========================================================================================
## Define our tests which will MOCK the above services
##========================================================================================
def test_get_current_directory(monkeypatch):
    """
     Using a monkeypatched version of os.getcwd() when get_current_dir() is called
     check the current directory returned
    """
    MOCKED_CWD = '/opt/env1/app'
    def mock_getcwd():
        return MOCKED_CWD

    monkeypatch.setattr(os, 'getcwd', mock_getcwd)
    assert get_current_dir() == MOCKED_CWD

#------------------------------------------------
def test_get_httpbin_origin_success(monkeypatch):
    """
     When calling get_httpbin_origin(), instead of actually making a request to
     to the URL specified in that method we will use a use a monkeypatched version
     of requests.get() to test if get_httpbin_origin() properly handles the response
     object when the request is successful
    """
    FAKE_IP = '4.68.55.4'
    class MockResponse(object):
        def __init__(self):
            self.status_code = 200
            self.headers = {'key': '1234'}

        def json(self):
            return {'user': 'irrelevant', 'origin': FAKE_IP}

    def mock_get(url):
        """ mock requests.get by returning a mocked response"""
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_get)
    assert get_httpbin_origin() == (200, FAKE_IP)

#------------------------------------------------
def test_get_httpbin_origin_failure(monkeypatch):
    """
     When calling get_httpbin_origin(), instead of actually making a request to
     to the URL specified in that method we will use a use a monkeypatched version
     of requests.get() to test if get_httpbin_origin() properly handles the response
     object when the request fails
    """
    class MockResponse(object):
        def __init__(self):
            self.status_code = 404
            self.headers = {'key': '1234'}

        def json(self):
            return {'errors': 'too many to return'}

    def mock_get(url):
        """ mock requests.get by returning a mocked response"""
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_get)
    assert get_httpbin_origin() == (404, '')
