# Testing in Python

***Something that is untested is broken*** --unkown

## Any Testing process can be broken into two steps:
1) Test Step
2) Test Assertion

Suppose you are testing the headlights on your car.
  1) Test-step: turn on the headlight switch
  2) Test-assertion: get out of your car and go see if the headlights are on.

Testing can be put into one of two categories:
  * **Unit-testing**: testing an individual component.
  * **Integration Testing**: testing 2 or more of the components of a system in combination, making sure all components are working together end-to-end.

The headlight test is an **integration** test as there are many different components that all have to be working together properly in order for the lights to go on. If the lights did not come on, we would have to break things down into unit tests. Perhahps the battery is no longer producing a charge. Perhaps the lightbulbs are not functioning.  Maybe the actual switch to turn on the lights is malfunctioning. 

---
## Software Testing in Python
The simplest unit-test can be achived with the assert() statement. For example, let's unit-test the **sum()** method
```
assert sum([0, 3, 5]) == 8, "Sum should be 8"
```

If the assertion fails, we get 
```
>>> assert sum([0, 1, 2]) == 8, "Sum should be 8"
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AssertionError: Sum should be 8 
```
---
### Test Runners
Writing tests in the above way is fine for a simple check, but can be tedious.  To make the testing process more automated and sclalable we use something called a **test runner** - an application designed for running tests, checking the output, and providing tools for debugging and diagnosing tests and applications.

Python provides several test runners as modules. The most commonly used testing modules can be used for either *integration* testing or *unit* testing.
* **unittest**
* **pytest**

### **unittest**
The *unittest* module is built into the Python standard library. It requires two basic steps:
unittest requires that:
 * Put your tests into classes as methods.
 * Use special assertion methods in the unittest.TestCase class to peform a test. 
Example: see **test_sum_unittest.py** file
Execute wtih:
```
$ python test_sum_unittest.py
```
Instead of providing the name of a module containing tests, **unittest** can auto-discovery it's test targets with the following:
```
$ python -m unittest discover
```
This will search the current directory for any files named test*.py and run the tests. Multiple test modules can be placed in a **tests/** directory, such that unittest will run all tests in a single test plan: 
```
$ python -m unittest discover -s tests
```

If your source code is not in the directory root or contained in a subdirectory, unittest may not be able to import necessary modules for the tests. Use the **-t* falg to specify a location in which to perform the tests:
```
$ python -m unittest discover -s tests -t src
```
unittest will change to the src/ directory, scan for all test*.py files inside the the tests directory, and execute them.

### **pytest**
While **pytest** is not part of the standard library, it has become a popular a testing module providing more a robust testing framework with a more comapct testing sytax, thus allowing for less code required for creating/running tests.
#### Install
```
  pip install -U pytest
```
This will also create a system executable (typically installed in **/usr/local/bin/pytest**)

Example execution:
```
Run all test:
$  pytest test_sum_pytest.py  (OR python -m pytest test_sum_pytest.py)

Test a specific function:
$  pytest test_sum_pytest.py::test_sum_list  (OR python -m pytest test_sum_pytest.py::test_sum_list)

Test a group of functions:
Either by functions markers (marked by @my_marker):
$  pytest -m my_marker 
Or by matching function name substring:
$ pytest -k <substr>

Test several test files in a directorty
$ pytest tests/  (OR python -m pytest tests/)

Test with results sent to logfile
$ python -m pytest --resultlog=testlog.log tests/ 
```
---
## Advanced Testing (with pytest)
#### For testing large applications, it is useful to take advantage of some of the testing framework's more adnvanced features. 

There are the three basic steps for every test you create:
  1) Create your inputs
  2) Execute the code, capturing the output
  3) Compare the output with an expected result

It’s not always as easy as creating a static value for the input like a string or a number. Sometimes, your application will require an instance of a class or a context.  Data that you create as an input is known as a **fixture**. It’s common practice to create fixtures and reuse them for numerous different tests.  If you’re running the same test and passing different values each time and expecting the same result, this is known as **parameterization**.

#### Handling Expected Failures
Sometimes we want to validate that our error-handling code handles errors as expected.  Within your test method use a special pytest.raises context manager. Inside the **with** block execute the test steps:   
Example:
Suppose we have a method that should raise a **TypeError** under certain conditions and we want to validate that it does that correctly. Using the context-manager syntax, if test steps produce the same Exception as you expected, the test will PASS.
```
def test_sum_NAN():
   with pytest.raises(TypeError):
      sum([1, 2, 'bad'])
```

---

### Side-Effects and Mocking
Often, executing a piece of code uses internal or external dependancies (a.k.a "Collaborators") such as system calls or database access.  Such operations can be time-consuming at the very least, or even have undesirable **side-effects** in which other things in the environment are altered, such as a file on the filesystem, or a value in a database. Side effects make unit testing difficult since each time a test is run, it might give a different result, or one test could impact the state of the application and cause another test to fail. 

NOTE: If you find that a single unit of code you are testing has lots of different side effects, you might be breaking the **Single Responsibility Principle** - this unit of code is doing too many things and should be refactored. 

To speed up testing and minimize side-effects, one can replace the real collaborator dependancies with fake ones, using **Mocking**. The precise definition of mocking is highly debated and hard to pin down. Simpy put, **mocking** the replacement of one or more function calls or objects with mock calls or objects.A mock function call (often referred to as a **stub**) returns a predefined value immediately, without doing any work.  If the code under test uses a collaborator for input data and the goal of the test is simply to ensure the code behaves properly when interacting with the collaborate or to test the handling of the data response, use a **Stub** to mock the function. 

Example: Suppose the code being unit-tested depends on an API call that returns a JSON object. The call can take several seconds to complete and perhaps we are limited on how many total API calls we can make without being charfed. Rather than relying on the API being up and waiting for the call to return in each test and hitting our call limit, you can replace its real implementation with **stub** that returns hard-coded stduent-grade values. 
Perhaps our test hits an API which has a limit on the number of calls we make and we don't want to exhaust that limit.

If the goal of the test to verify the contract between the code under test and a collaborator, use a **Mock** object. With a mock object we can test more complicated interactions with the collaborator. For example:
 * verifying that the collaborator's method is called the correct number of times.
 * verifying that the collaborator's method is called with the correct parameters.

