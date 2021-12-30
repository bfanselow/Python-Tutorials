#!/usr/bin/env python3
"""

 Demonstrate how to skip an individual test case conditionally or unconditionally, as well as how 
 to mark a test as an expected failure (still fails but now counted as a failure in TestResult)


 Expected utput:

sFsxs
======================================================================
FAIL: testadd (__main__.suiteTest)
Add
----------------------------------------------------------------------
Traceback (most recent call last):
  File "Desktop/code/Python/testing_skip_fail.py", line 29, in testadd
    self.assertEqual(result,100)
AssertionError: 90 != 100

----------------------------------------------------------------------
Ran 5 tests in 0.001s

FAILED (failures=1, skipped=3, expected failures=1)

"""

import unittest

# helper function to test 
def add(x,y):
    return x+y


# TESTING CODE
class SimpleTest(unittest.TestCase):
    @unittest.skip("demonstrating skipping")
    def testadd1(self):
        self.assertEquals(add(4,5),9)

class suiteTest(unittest.TestCase):
   a = 50
   b = 40
   
   def testadd(self):
      """Add"""
      result = self.a+self.b
      self.assertEqual(result,100)

   @unittest.skipIf(a>b, "Skip over this routine")
   def testsub(self):
      """sub"""
      result = self.a-self.b
      self.assertTrue(result == -10)
   
   @unittest.skipUnless(b == 0, "Skip over this routine")
   def testdiv(self):
      """div"""
      result = self.a/self.b
      self.assertTrue(result == 1)

   @unittest.expectedFailure
   def testmul(self):
      """mul"""
      result = self.a*self.b
      self.assertEqual(result == 0)

if __name__ == '__main__':
    unittest.main()
